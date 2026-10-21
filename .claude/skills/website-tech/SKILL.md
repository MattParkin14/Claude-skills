---
name: website-tech
description: Infrastructure and integration playbook for standing up a new small-business website on the Astro + Cloudflare stack these projects use. Covers the database (D1), file/image storage (R2), automatic resizing of uploaded photos, the reusable photo library, how images are referenced, admin auth, the secrets model, and the Resend (email) and Stripe (payments) integrations — including the "bring your own API key" pattern where the site owner pastes their own key into the admin. Contains ZERO design, styling, layout or copy guidance. Use when scaffolding a new site, adding a backend feature, wiring up email or payments, letting owners upload photos, or deciding how to store and serve images.
---

# Website tech playbook

The reusable, design-free technical blueprint behind these sites. Every concept
here is already implemented in one of the two reference repos — this file tells
you what the moving parts are, why they exist, and how to reproduce them on a new
site. Nothing about look, feel, fonts, colour, layout or wording lives here on
purpose.

## The stack in one breath

- **Astro 6** in `output: 'server'` mode with the **`@astrojs/cloudflare`**
  adapter, deployed as a **Cloudflare Worker**. Public pages are server-rendered
  but read almost entirely from the database, so they feel static while staying
  editable.
- **Cloudflare D1** (SQLite) holds all editable content.
- **Cloudflare R2** holds all uploaded/served images (and any media).
- **Cookie-based admin** (HMAC-signed session) gates a `/admin` content manager.
- **Resend** (REST) sends transactional email. **Stripe** (REST) takes payments —
  only on sites that sell something.
- **`wrangler`** is the CLI for D1 migrations, R2, secrets and deploys.

Build/deploy scripts (from `package.json`) are identical across sites:

```
dev:               astro dev                    # local, http://localhost:4321
build:             astro build
preview:           wrangler dev                 # run the built Worker locally
db:migrate:local:  wrangler d1 migrations apply <db-name> --local
db:migrate:remote: wrangler d1 migrations apply <db-name> --remote
db:seed:local:     wrangler d1 execute <db-name> --local  --file seed/seed.sql
db:seed:remote:    wrangler d1 execute <db-name> --remote --file seed/seed.sql
deploy:            astro build && wrangler deploy -c dist/server/wrangler.json
```

`wrangler deploy` on its own fails by design: the root `wrangler.jsonc` has no
entry point; the Astro build emits the real deployable config at
`dist/server/wrangler.json`, which is what `deploy` points at. If you use
Cloudflare "Workers Builds" (git integration) set build = `npm run build` and
deploy = `npx wrangler deploy -c dist/server/wrangler.json`.

## Guiding principle: progressive setup / graceful degradation

The single most important pattern. **Every integration is optional and announces
itself when unconfigured** instead of crashing. A site can go live before its
database is seeded, before R2 is enabled, before email is connected, before
Stripe exists — each feature quietly steps aside:

- No `MEDIA` (R2) binding → uploads return a friendly 503 ("Photo storage is not
  set up yet"); the rest of the site is fine.
- No `IMAGES` binding → the rare photo the owner's browser can't decode (HEIC on
  Windows) gets "save it as a JPG"; every other upload is resized as normal.
- No `RESEND_API_KEY` → email sends are a silent no-op; the enquiry/order is still
  saved to the database.
- No `STRIPE_SECRET_KEY` → the checkout button returns a 503 that points buyers at
  the contact page.
- Empty/unreachable database → public pages fall back to `src/lib/defaults.ts`.

Reproduce this everywhere: check the binding/secret, degrade with a clear
message, never let a missing optional dependency take down a page.

## Project layout (the parts that matter)

```
wrangler.jsonc          Bindings (D1, R2), public vars. NO secrets here.
astro.config.mjs        output: 'server' + cloudflare adapter
site.config.ts          Stable business facts + commerce settings (see below)
.dev.vars.example       Template for local secrets (copy to .dev.vars, gitignored)
migrations/             Numbered SQL migrations (0001_init.sql, ...)
seed/seed.sql           Starter content
src/env.d.ts            The Env type: every binding + secret the code reads
src/lib/env.ts          Single access point for Cloudflare bindings/secrets
src/lib/db.ts           Types + read helpers + settings/slug/image helpers + IMAGE_REFS
src/lib/media.ts        Image sizes, media src format, srcset helpers (shared everywhere)
src/lib/client/upload-photo.ts  Browser-side resize + upload (jSquash) — admin only
src/components/Img.astro        Renders any stored src with srcset/sizes
src/lib/auth.ts         HMAC session cookie create/verify
src/lib/email.ts        Resend integration
src/lib/stripe.ts       Stripe integration (commerce sites only)
src/middleware.ts       Guards /admin and /api/admin
src/pages/images/[...key].ts   Serves R2 objects
src/pages/api/          JSON endpoints (admin CRUD, upload, media library, contact, checkout, webhook)
src/pages/admin/        The content manager
```

## Database — Cloudflare D1

- Bound as `DB` in `wrangler.jsonc` (`binding: "DB"`, plus `database_name`,
  `database_id`, `migrations_dir: "migrations"`).
- **Schema lives in numbered migrations** in `migrations/` (`0001_init.sql`,
  `0002_...`). Apply local first, then remote. Migrations are the source of truth;
  keep `seed/seed.sql` and any `src/lib/defaults.ts` in step with them.
- **Access is raw SQL** via the D1 prepared-statement API — no ORM:
  `db.prepare('SELECT ... WHERE x = ?').bind(x).all<T>()` / `.first<T>()` /
  `.run()`. Batch writes with `db.batch([...])`.
- Typical content tables: `services`/`products`, `reviews`, `gallery_images`,
  `posts` (Markdown in `body_md`, rendered with `marked`), `messages` (contact
  enquiries), plus `orders`/`product_images`/`categories` on a shop.
- **Read helpers** live in `src/lib/db.ts` and return typed rows; **writes** live
  in the API routes. Keep that split.

### The `settings` key/value table — the workhorse

A single `settings (key TEXT PRIMARY KEY, value TEXT)` table backs two different
needs and is worth adding to every site:

1. **Editable page copy** — hero text, About paragraphs, intros, etc. Read with
   `getSettings(db, [keys])`; write with `saveSettings(db, {k: v})` (an
   `INSERT ... ON CONFLICT(key) DO UPDATE` upsert).
2. **Owner-supplied secrets** (the "bring your own key" pattern, below).

Because #2 exists, **`db.ts` keeps a `SECRET_KEYS` set** (e.g. `resend_api_key`,
and `stripe_secret_key` if you add it). `getAllSettings()` strips those keys so a
secret can never accidentally be serialised into a rendered page or a JSON
response. Secrets are only ever read server-side via an explicit `getSettings`
call. **Preserve this guard whenever you add a secret to `settings`.**

## File storage — Cloudflare R2

- Bound as `MEDIA` in `wrangler.jsonc` (`binding: "MEDIA"`, `bucket_name`).
- **Upload — photos are resized automatically.** Full design and tested code:
  **`image-pipeline.md`** in this skill folder — read it before touching uploads.
  The short version:
  - The owner's **browser** resizes before upload with **jSquash**
    (`@jsquash/resize` + `@jsquash/webp`, Apache-2.0): WebP copies at **1600, 800
    and 400 px wide** (never upscaled), quality 80/75, one re-encode if a copy is
    oversized. Invisible to the owner. Never resize on the Worker: 10 ms CPU on
    Free and 128 MB memory can't decode phone photos. Never encode WebP via
    canvas: Safari silently returns a PNG.
  - `src/pages/api/admin/upload.ts` (admin-only) receives the **untouched original
    + copies**, validates (original ≤ 20 MB; copies must be real WebP), writes
    `uploads/<id>/original.<ext>` (**private** — may contain GPS) and
    `uploads/<id>/<w>.webp` (public), where `<id>` = `2026-10-18-ab12cd34`, then
    indexes the photo in a **`media` table** and returns `{ id, src }`.
  - GIFs are stored as-is (`image.gif`) to keep animation. Files the browser
    can't decode fall back to the optional Cloudflare **Images binding**
    (`IMAGES`), else a clear "save it as a JPG" message.
- **Library & reuse**: every photo gets all sizes up front, so it can be reused
  anywhere at no cost. Admin image fields offer *upload new* or *choose from
  library* (`/api/admin/media`). Unlinking from a page never deletes files;
  deleting from the library is refused while `mediaUsage()` finds the photo in
  any `IMAGE_REFS` column.
- **Serve** (`src/pages/images/[...key].ts`): a catch-all GET fetches the object
  from `env.MEDIA`, streams the body, sets `Content-Type` from stored metadata,
  and — because keys are immutable — sends
  `Cache-Control: public, max-age=31536000, immutable` + `ETag`. It rejects keys
  containing `..` and 404s when R2 is absent. It also **404s any
  `…/original.<ext>` key** — originals are only downloadable through the
  admin-guarded `/api/admin/media/[id]/original`.
- R2 needs to be **activated on the Cloudflare account** before first use (accept
  the R2 terms in the dashboard). If it isn't yet, comment out the `r2_buckets`
  block so deploys succeed, and the upload route's 503 covers the gap until it's
  enabled.

## How to reference images (the three cases)

Every `<img src>` on the site resolves to one of three paths — **never** a raw R2
or external URL in the database:

1. **`/assets/...`** — static files shipped in the repo under `public/assets/`.
   Served directly by the platform. Good for a handful of build-time images.
2. **`/images/<key>`** — anything in R2: admin uploads (`/images/uploads/...`)
   and migrated starter photos (`/images/seed/...`). This is the default for all
   real content. Resized photos are stored as a **media src**:
   `/images/uploads/<id>/1600.webp#m=1600x1200:1600,800,400` — a real file plus
   a fragment recording the size and widths made. The fragment never reaches the
   server, so it needs no extra DB query and anything that ignores it still works.
   Use `plainSrc(src)` for og:image, Stripe and emails.
3. Validation: **`cleanImagePath(value)`** in `db.ts` accepts a string only if it
   starts with `/images/` or `/assets/`, otherwise returns `''`. Run untrusted /
   stored image values through it so bad data degrades to "no image" instead of a
   broken or hostile URL. Media srcs pass unchanged.

**Render every content image with `<Img src alt preset>`** (`src/components/Img.astro`).
It emits `srcset`/`sizes`/`width`/`height` for media srcs and a plain `<img>` for
anything else, so the browser fetches the smallest sharp copy per slot (hero → 1600,
card → 800, thumbnail → 400). Presets live in `media.ts` and must match how wide
each slot renders on that site. Mark only the main above-the-fold image `eager`.

**Moving starter ("OG") photos into R2** (so every image is served the same way):

- `scripts/prepare-images.mjs` uses **`sharp`** to turn `seed/raw/*` into the
  same layout as uploads — `seed/images/<name>/{1600,800,400}.webp`, EXIF
  rotation applied — and prints each photo's media src for `seed.sql` (code in
  `image-pipeline.md`). Design-neutral — it's just optimisation.
- `scripts/upload-seed-to-r2.mjs` pushes `seed/images/` into the bucket under the
  `seed/` prefix via `wrangler r2 object put` (`--local` or `--remote`), walking
  the per-photo subfolders with `--content-type image/webp`.
- A migration then repoints stored rows from the old static `/seed/...` path to
  `/images/seed/...`, e.g.
  `UPDATE product_images SET src = '/images/seed/' || substr(src, 7) WHERE src LIKE '/seed/%';`
- Optional: a `workflow_dispatch` GitHub Action (`.github/workflows/seed-media.yml`)
  runs the upload + migration from the Actions tab for non-terminal users, using a
  `CLOUDFLARE_API_TOKEN` repo secret (scoped to *Workers R2 Storage: Edit* + *D1:
  Edit*).

## Admin auth & the secrets model

- **Stateless HMAC-SHA256 session cookie** (`src/lib/auth.ts`). On login the
  password is compared (trimmed) against the `ADMIN_PASSWORD` secret; a signed
  `<expiry>.<hmac>` cookie is set (`HttpOnly; Secure; SameSite=Lax`, ~7 days). The
  signing key is `SESSION_SECRET`, falling back to `ADMIN_PASSWORD`. No session
  store / KV needed.
- **`src/middleware.ts`** verifies the cookie on every `/admin` and `/api/admin`
  request (except the login routes), sets `locals.isAdmin`, and redirects or
  returns 401 for the API. All admin write endpoints sit behind it.
- **Secrets vs public vars.** Public, non-sensitive config (e.g. `SITE_URL`) goes
  in `wrangler.jsonc`'s `vars`. **Secrets are never committed** — set them with
  `wrangler secret put <NAME>` (or the dashboard) in production, and in a
  gitignored **`.dev.vars`** locally (template: `.dev.vars.example`).
- **`src/env.d.ts`** declares the `Env` type — every binding and secret the code
  may read (`DB`, `MEDIA?`, `SITE_URL?`, `ADMIN_PASSWORD?`, `SESSION_SECRET?`,
  `RESEND_*`, `OWNER_EMAIL?`, and `STRIPE_*` on a shop). **`src/lib/env.ts`** is
  the one place bindings are pulled off `cloudflare:workers` and cast to `Env`;
  import `env` from there rather than reaching into locals everywhere.

## Email — Resend

- **REST, no SDK** (`src/lib/email.ts`): `POST https://api.resend.com/emails` with
  `Authorization: Bearer <key>` and a JSON body (`from`, `to`, `subject`,
  `text`/`html`, optional `reply_to`).
- **No-op when unconfigured.** If there's no API key (or no recipient), sending
  silently returns — the enquiry/order is already saved to D1, so email is purely
  an *alert on top*. Wrap every send in try/catch: a failed email must never break
  a form submission, checkout or admin action.
- Config sources, in priority order: **database `settings` → Worker secrets**
  (`RESEND_API_KEY`, `RESEND_FROM`, `OWNER_EMAIL`). `from` must be a verified
  sending domain in Resend; before that you can use `onboarding@resend.dev`.

### Bring-your-own key (the Elite pattern — recommended default)

Elite lets the **owner paste their own Resend key** in `/admin/notifications`
instead of a developer setting a Worker secret. Reproduce it like this:

- Admin form posts `enabled`, `to`, `from`, and `api_key` to
  `/api/admin/notifications`. The key is written to `settings.resend_api_key`;
  the **blank field means "keep the existing key"** (never overwrite a saved
  secret with an empty string).
- A `loadNotifyConfig(env)` helper merges DB settings over env secrets so either
  setup works. `resend_api_key` is in `SECRET_KEYS`, so it's never sent back to
  the browser.
- A **"send test email"** endpoint (`/api/admin/notifications/test`) sends with
  the current config and surfaces Resend's exact response, so the owner can
  confirm it works. Always include this — it turns a silent misconfiguration into
  a clear yes/no.

## Payments — Stripe (commerce sites only)

- **Minimal REST client** (`src/lib/stripe.ts`), no `stripe` npm package, to keep
  the Worker bundle small. Two operations:
  - **Create Checkout Session**: `POST https://api.stripe.com/v1/checkout/sessions`
    (form-urlencoded), `mode=payment`, server-built `line_items` with
    `price_data` (name, `unit_amount`, currency), `success_url`/`cancel_url`,
    shipping options, and a `metadata.items` JSON blob recording what was bought.
    Returns a hosted Checkout `url` to redirect to.
  - **Verify webhook**: recompute the `stripe-signature` HMAC-SHA256 over
    `<timestamp>.<payload>` with the webhook signing secret, compare, and reject
    events older than 5 minutes (replay guard).
- **Prices come from the database, never the client.** The checkout endpoint
  (`/api/checkout`) re-reads each product by id, re-checks `active` and
  `stock_qty`, and builds line items server-side. The browser only sends
  `{id, qty}`. This is the security boundary — trust the DB, not the cart.
- **Fulfilment is webhook-driven** (`/api/webhook`, `checkout.session.completed`):
  verify signature → **idempotency check** (skip if `stripe_session_id` already in
  `orders`) → insert the order → decrement stock
  (`MAX(0, stock_qty - qty)`) → send confirmation + owner-alert emails. Never
  fulfil from the success page (the buyer can navigate there without paying).
- **Graceful degradation**: `stripeConfigured(env)` gates the checkout endpoint
  (503 → "order via the contact page"); the webhook 503s without
  `STRIPE_WEBHOOK_SECRET`. So a shop can launch with the catalogue live and
  payments switched on later.
- Product image URLs handed to Stripe must be **absolute `https://`** — build them
  from `SITE_URL` (`new URL(src, env.SITE_URL).href`) and skip anything not
  already `https://`.
- Commerce settings (currency, locale, flat/free shipping thresholds, allowed
  countries) live in `site.config.ts`; money is stored and passed as **integer
  cents** and formatted with `Intl.NumberFormat`.

### Bring-your-own Stripe key — supported, with a safety note

You asked whether it's safe to let the owner paste their **own Stripe details** in
the admin, the way Elite does for Resend. **Yes, it can be done the same way, but
Stripe deserves more care than Resend** — so do it deliberately:

- **Why it's riskier than Resend.** A Resend key can only send email from a
  verified domain — low blast radius. A Stripe **secret key** (`sk_live_…`) can
  create charges, issue refunds, read customer PII and move money. It is stored as
  plaintext in D1 (your app doesn't encrypt it at rest), and because admin is a
  single shared password, **admin access = Stripe key access**. Treat that as the
  threat model.
- **If you implement it, do all of this:**
  1. Store `stripe_secret_key` (and `stripe_webhook_secret`) in `settings` and add
     both to `SECRET_KEYS` so they are never returned to any page or JSON. Use the
     **write-only, blank-means-keep** field pattern exactly like the Resend key.
  2. Merge **DB over env** (a `loadStripeConfig(env)` helper), so a
     higher-security deployment can still use a Worker secret and skip the DB copy.
  3. **Strongly prefer a Stripe *restricted* key (`rk_…`)** scoped to just
     `Checkout Sessions: write` (plus any reads you need) over the full secret key.
     Same UX, far smaller blast radius if leaked.
  4. Add a **"test connection"** action (mirror the Resend test button) that does a
     harmless authenticated call and reports Stripe's response.
  5. Make sure `ADMIN_PASSWORD` is strong and `SESSION_SECRET` is set — they are
     now guarding a payment credential.
- **Recommendation:** default to **bring-your-own for Resend** (do it — it's the
  owner's own low-risk key and saves a developer round-trip), and for **Stripe
  offer it but default to a restricted key**, keeping the Worker-secret path
  available for anyone who wants the key to never touch the database. Whichever the
  owner chooses, the account itself must be created in *their* name so payouts and
  tax go to them.

## Standing up a new site — checklist

1. Clone the closest reference repo (Elite = brochure + enquiries; Sara = shop).
2. Set names/ids: `wrangler.jsonc` (`name`, D1 `database_name`, R2 `bucket_name`),
   `package.json` script db names, `site.config.ts` facts.
3. `wrangler d1 create <db>` → paste the printed `database_id` into
   `wrangler.jsonc`. `wrangler r2 bucket create <bucket>` (accept R2 terms first).
4. Photo uploads: include the `media` migration, `src/lib/media.ts`,
   `upload-photo.ts`, `Img.astro`, the upload + media routes, and
   `vite.optimizeDeps.exclude: ['@jsquash/webp', '@jsquash/resize']` in
   `astro.config.mjs` (see `image-pipeline.md`). Optionally add the `IMAGES`
   binding; set `IMAGE_REFS` to the site's image columns.
5. `npm i` → `npm run db:migrate:local && npm run db:seed:local` →
   `cp .dev.vars.example .dev.vars` (set `ADMIN_PASSWORD`) → `npm run dev`.
6. Production: `db:migrate:remote` + `db:seed:remote`; `wrangler secret put
   ADMIN_PASSWORD` (+ `SESSION_SECRET`); optional `RESEND_*` / `OWNER_EMAIL`;
   `STRIPE_SECRET_KEY` + `STRIPE_WEBHOOK_SECRET` for a shop.
7. `npm run deploy`; set `SITE_URL` to the deployed URL (checkout redirects and
   email links depend on it); add the custom domain and re-point the Stripe
   webhook at the final URL.
8. If using R2 seed photos: `npm run media:seed:remote` then the repoint migration
   (or run the "Seed media to R2" Action).

## Other Cloudflare primitives (available, not currently used)

D1 + R2 cover these sites (plus the optional **Images** binding, used only as the
upload fallback in `image-pipeline.md`). If a future need appears: **KV** for hot key/value
lookups or edge caching, **Durable Objects** for coordination/real-time,
**Queues** for background jobs, **Hyperdrive** if you ever front an external
Postgres. None are needed for the standard content-site shape above — reach for
them only when D1/R2 genuinely can't express the need.
