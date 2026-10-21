"""
invoice_io.py  --  Robust file I/O helpers for the monthly-invoice skill.
=========================================================================
Why this exists
---------------
The Invoicing folder is reached through a caching bridge between Windows and
the sandbox. When a PDF is edited *outside* the sandbox (e.g. a PO number typed
into a stamp in a PDF viewer) the bridge can keep serving a STALE or TRUNCATED
copy for that path: reads come back missing the final %%EOF, directory listings
go stale, and re-writing the same path fails. Brand-new filenames, by contrast,
are always served correctly.

These helpers make every read and write defensive against that:

  * read_pdf()        - open with pikepdf (recovers broken trailers that make
                        pypdf/pdfplumber throw "stream ended unexpectedly").
  * is_pdf_intact()   - integrity gate: file must end in %%EOF *and* parse.
  * safe_copy()       - copy with verify-after-write + retry.
  * safe_write_bytes()- write bytes with verify-after-write + retry.
  * safe_move()       - move via os.replace (rename) with retry; never uses
                        cp/mv, which the bridge's same-inode quirk breaks.
  * stage_local()     - copy a mount file to fast local disk, verified, before
                        parsing it, so parsing never touches the flaky path.

Every function raises IntegrityError on unrecoverable trouble rather than
silently returning wrong data.
"""
from __future__ import annotations
import os, time, shutil, tempfile

try:
    import pikepdf
except Exception:  # pragma: no cover
    pikepdf = None


class IntegrityError(Exception):
    """Raised when a PDF/file cannot be read or written intact."""


# --------------------------------------------------------------------------- #
# Integrity
# --------------------------------------------------------------------------- #
def file_bytes(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def has_eof_marker(data: bytes, window: int = 2048) -> bool:
    """A complete PDF ends with a %%EOF marker (possibly + trailing padding)."""
    return b"%%EOF" in data[-window:]


def pdf_parses(path: str) -> bool:
    """True if the PDF's object structure can be loaded (pikepdf recovers most
    slightly-malformed trailers; that's the point)."""
    if pikepdf is None:
        raise IntegrityError("pikepdf is not installed; run: pip install pikepdf")
    try:
        with pikepdf.open(path) as pdf:
            _ = len(pdf.pages)
        return True
    except Exception:
        return False


def is_pdf_intact(path: str) -> bool:
    """Integrity gate used before trusting any invoice PDF."""
    try:
        data = file_bytes(path)
    except Exception:
        return False
    if not data or not has_eof_marker(data):
        return False
    return pdf_parses(path)


# --------------------------------------------------------------------------- #
# Retry wrapper
# --------------------------------------------------------------------------- #
def _retry(fn, tries: int = 6, delay: float = 0.7, what: str = "operation"):
    last = None
    for _ in range(tries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(delay)
    raise IntegrityError(f"{what} failed after {tries} tries: {last}")


# --------------------------------------------------------------------------- #
# Reading
# --------------------------------------------------------------------------- #
def read_pdf(path: str):
    """Open a PDF robustly and return the pikepdf handle. Caller closes it."""
    if pikepdf is None:
        raise IntegrityError("pikepdf is not installed; run: pip install pikepdf")
    def _open():
        return pikepdf.open(path)
    return _retry(_open, what=f"open {os.path.basename(path)}")


def annotation_texts(path: str) -> list[str]:
    """All /Contents annotation strings on every page (this is where a typed
    PO number lives after a user edits a FreeText stamp)."""
    out: list[str] = []
    pdf = read_pdf(path)
    try:
        for page in pdf.pages:
            annots = page.get("/Annots")
            if not annots:
                continue
            for a in annots:
                try:
                    c = a.get("/Contents")
                    if c is not None:
                        out.append(str(c))
                except Exception:
                    continue
    finally:
        pdf.close()
    return out


# --------------------------------------------------------------------------- #
# Writing / moving
# --------------------------------------------------------------------------- #
def safe_write_bytes(data: bytes, dst: str, require_eof: bool = True) -> None:
    """Write bytes, then read them back and confirm they match (and, for PDFs,
    that %%EOF survived). Retries on the flaky bridge."""
    def _w():
        tmp = dst + ".part"
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, dst)                 # atomic swap into place
        back = file_bytes(dst)
        if back != data:
            raise IOError("verify: bytes differ after write")
        if require_eof and not has_eof_marker(data):
            raise IOError("verify: source data has no %%EOF")
        return True
    _retry(_w, what=f"write {os.path.basename(dst)}")


def safe_copy(src: str, dst: str, verify_pdf: bool = True) -> None:
    """Copy src -> dst with verify-after-write. If verify_pdf, also require the
    destination to pass the PDF integrity gate."""
    data = file_bytes(src)
    safe_write_bytes(data, dst, require_eof=verify_pdf and dst.lower().endswith(".pdf"))
    if verify_pdf and dst.lower().endswith(".pdf") and not is_pdf_intact(dst):
        raise IntegrityError(f"copied file failed integrity gate: {dst}")


def safe_move(src: str, dst: str) -> None:
    """Move within the mount using os.replace (rename). Never cp/mv."""
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    def _m():
        os.replace(src, dst)
        return True
    _retry(_m, what=f"move {os.path.basename(src)}")


def safe_remove(path: str) -> None:
    if not os.path.exists(path):
        return
    def _r():
        os.remove(path)
        return True
    try:
        _retry(_r, tries=4, what=f"remove {os.path.basename(path)}")
    except IntegrityError:
        pass  # deletion may be disabled; caller can decide to care


def stage_local(src: str, workdir: str | None = None) -> str:
    """Copy a mount PDF to local disk (verified intact) and return the local
    path. Parse the local copy, never the mount path, to dodge stale reads."""
    workdir = workdir or tempfile.mkdtemp(prefix="invstage_")
    os.makedirs(workdir, exist_ok=True)
    local = os.path.join(workdir, os.path.basename(src))
    # copy with retry; verify integrity on the local copy
    def _c():
        shutil.copyfile(src, local)
        if src.lower().endswith(".pdf") and not is_pdf_intact(local):
            raise IOError("staged copy failed integrity gate")
        return True
    _retry(_c, what=f"stage {os.path.basename(src)}")
    return local
