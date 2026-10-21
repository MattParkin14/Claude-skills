---
name: ts-numbers-currency
description: Guidance for handling numbers correctly in TypeScript/JavaScript, above all currency and money values. JS `number` is a binary float (0.1 + 0.2 = 0.30000000000000004), so picking the right representation and library matters. Use this skill whenever writing, reviewing or debugging TS/JS code that touches prices, totals, invoices, budgets, tax/GST/VAT, discounts, percentages, exchange rates, payments (Stripe etc.), splitting amounts, decimal quantities, large IDs, or number formatting on a UI — and whenever someone asks "which library should I use for money/decimals", mentions Dinero.js, currency.js, big.js, decimal.js, bignumber.js or BigInt, or sees odd values like 19.990000000000002 or a total that is out by a cent. Trigger even if the user doesn't mention floating point.
---

# Numbers & Currency in TypeScript / JavaScript

## Why this matters

Every JS/TS `number` is an IEEE 754 64-bit binary float. TypeScript adds nothing at runtime. Decimal fractions like 0.1 cannot be stored exactly, so:

```ts
0.1 + 0.2;            // 0.30000000000000004
0.1 + 0.2 === 0.3;    // false
0.07 * 100;           // 7.000000000000001
(1.005).toFixed(2);   // "1.00"  (1.005 is stored as 1.00499999…)
```

Integers **are** exact up to `Number.MAX_SAFE_INTEGER` (2^53 − 1 ≈ 9 quadrillion). That is why the standard fix for money is to do the maths in whole-number minor units (cents), or to use a decimal library. The harm goes beyond ugly UI output: equality checks fail, totals drift by a cent, and `Math.ceil` can jump a whole step.

## Step 1 — choose the representation

Pick the approach before writing code, and say which one you chose and why.

| Situation | Use | Why |
|---|---|---|
| Money you store, sum, split, or send to a payment API | **Integer minor units**. Use **Dinero.js v2** for anything non-trivial, or plain integers for simple cases | Integer maths is exact; the currency object knows its decimal places |
| Simple single-currency UI maths (cart total, a form) where adding a dependency is fine | **currency.js** is acceptable | Tiny, stores integer internally, easy API; accepts floats at the edge |
| Exact decimals with arbitrary scale: FX rates, unit prices with >2 dp, interest, tax engines, decimal strings from an API | **big.js** (default), **decimal.js** (needs pow/log/trig), **bignumber.js** (other bases, crypto) | Arbitrary-precision decimal arithmetic |
| Integers beyond 2^53 − 1: 64-bit DB keys, snowflake IDs, crypto base units | **BigInt**, or keep as **string** if you only pass it through | `number` silently corrupts them |
| Measurements, percentages for display, charts, stats, counts | Plain **number** | Fine, as long as you round only at display and compare with a tolerance |

Decision shortcut: **Is it money? → minor units (Dinero.js). Is it an exact decimal that isn't money? → big.js. Is it a huge integer? → BigInt/string. Otherwise → number.**

For library details, versions, API examples and trade-offs, read `references/libraries.md`.

## Step 2 — money rules

1. **Store money as integer minor units + ISO currency code**, e.g. `{ amount: 1999, currency: "NZD" }` for $19.99. Decimal strings (`"19.99"`) are the other safe option. Never store money as a float in a JS variable, a JSON number with decimals, or a `FLOAT`/`REAL`/`DOUBLE` DB column. Use `INTEGER`/`BIGINT` minor units or `NUMERIC(p,s)`.
2. **Don't assume 2 decimal places.** Take the exponent from the currency: JPY/KRW have 0, NZD/USD/AUD have 2, KWD/BHD/OMR/JOD/TND have 3. Get it from Dinero's currency objects or:
   ```ts
   const exponent = new Intl.NumberFormat("en", { style: "currency", currency: code })
     .resolvedOptions().maximumFractionDigits ?? 2;
   ```
   Payment processors can differ from ISO 4217 (e.g. Stripe wants UGX/ISK sent as two-decimal). Check the provider's docs and map explicitly.
3. **Convert user input by parsing the string**, not with `price * 100`. See `toMinorUnits` below.
4. **Split with allocation, never `total / n`.** Use Dinero `allocate` or currency.js `distribute` so the parts always add back to the total ($10 ÷ 3 → 3.34, 3.33, 3.33).
5. **Percentages and tax:** express rates as integers (basis points, or Dinero's scaled amounts `{ amount: 15, scale: 2 }` for 15%). Multiply first, divide last, round **once**. State the rounding mode (half-up vs half-even), because it is a business or legal decision. Decide per-line vs per-invoice tax deliberately, since the totals differ.
6. **Round only at display time**, with `Intl.NumberFormat`. Never round a value and then keep calculating with it.
7. **Compare money with `===` on integers** or the library's `equal`/`compare`, never with a float tolerance.

## Step 3 — display

Use a cached `Intl.NumberFormat`. Avoid `toFixed` for anything a user sees.

```ts
const nzd = new Intl.NumberFormat("en-NZ", { style: "currency", currency: "NZD" });
nzd.format(1999 / 100);   // "$19.99"  — dividing a safe integer by 100 once, for display, is fine

// Explicit rounding policy (Node 20.1+, all current browsers)
new Intl.NumberFormat("en-NZ", {
  style: "currency", currency: "NZD", roundingMode: "halfEven",
}).format(value);

// Exact values: Intl accepts decimal strings and BigInt without float conversion
nzd.format("19.995");
```

`toFixed` rounds the stored binary value, so `(2.55).toFixed(1)` is `"2.5"`. Also note that `Math.round(-20.5)` is `-20` (ties go toward +∞), which differs from C#, Excel and Python. Write an explicit rounding helper if you are porting logic.

## Reusable snippets

```ts
/** Parse a user/API decimal string into integer minor units without float maths. */
export function toMinorUnits(input: string, exponent = 2): number {
  const s = input.trim().replace(/,/g, "");
  const m = /^(-)?(\d+)(?:\.(\d+))?$/.exec(s);
  if (!m) throw new RangeError(`Not a valid amount: "${input}"`);
  const [, sign, whole, frac = ""] = m;
  if (frac.length > exponent) throw new RangeError(`Too many decimal places for this currency: "${input}"`);
  const minor = Number(whole + frac.padEnd(exponent, "0"));
  if (!Number.isSafeInteger(minor)) throw new RangeError("Amount exceeds safe integer range");
  return sign ? -minor : minor;
}
toMinorUnits("19.99");      // 1999
toMinorUnits("1,234.5");    // 123450
toMinorUnits("500", 0);     // 500 (JPY)

/** amount (minor units) × basisPoints / 10_000, rounded half away from zero — exact via BigInt. */
export function applyBasisPoints(amountMinor: bigint, bp: bigint): bigint {
  const num = amountMinor * bp, den = 10_000n;
  const q = num / den, r = num % den;
  return (r < 0n ? -r : r) * 2n >= den ? q + (num < 0n ? -1n : 1n) : q;
}
applyBasisPoints(1999n, 1500n); // 300n  (15% GST on $19.99 = 299.85 → 300 cents)

/** Scale-aware float comparison — for measurements only, NEVER for money. */
export function approxEqual(a: number, b: number, relTol = 1e-9, absTol = 1e-12): boolean {
  if (a === b) return true;
  if (!Number.isFinite(a) || !Number.isFinite(b)) return false;
  return Math.abs(a - b) <= Math.max(absTol, relTol * Math.max(Math.abs(a), Math.abs(b)));
}
```

Dinero.js v2 equivalent for typical money work:

```ts
import { dinero, add, multiply, allocate, toDecimal, halfEven, transformScale } from "dinero.js";
import { NZD } from "dinero.js/currencies";

const price = dinero({ amount: 1999, currency: NZD });           // $19.99 — pass minor units
const gst = multiply(price, { amount: 15, scale: 2 });           // × 0.15 as a scaled integer
const gstRounded = transformScale(gst, 2, halfEven);             // back to cents, explicit rounding
const total = add(price, gstRounded);
const [a, b, c] = allocate(total, [1, 1, 1]);                    // split without losing cents
toDecimal(total);                                                // "22.99" — string, format with Intl
```

## Other number pitfalls to check in review

- **Large IDs from JSON:** `JSON.parse('{"id":9007199254740993}').id` → `9007199254740992`. Keep 64-bit IDs as strings in APIs. Check untrusted integers with `Number.isSafeInteger`.
- **BigInt:** can't mix with `number` (`1n + 1` throws), truncates on division, and `JSON.stringify` throws on it. Serialise with a replacer that emits a string.
- **Parsing:** `parseFloat("1,234.56")` → `1`; `Number("")` → `0`. Validate with `Number.isFinite` and reject empty strings.
- **Decimal libraries:** construct from strings (`new Big("0.1")`), never from float literals, or you inherit the binary error.
- **Summing many floats (non-money):** `Math.sumPrecise` (ES2026) removes accumulation error where the runtime supports it. Feature-detect it.
- **Time maths:** apply the same principle. Work in integer milliseconds/minutes rather than fractional hours, and divide only for display.

## Review checklist

When writing or reviewing code that handles numbers, confirm:
- [ ] Money is integer minor units (or a decimal/money library), with a currency code alongside it
- [ ] No `* 100` / `/ 100` in calculation paths (only at the display/input boundary, via a helper)
- [ ] Currency exponent comes from the currency, not a hard-coded 2
- [ ] Splits use allocate/distribute; tax/percentages use integer rates and one explicit rounding step
- [ ] Display uses `Intl.NumberFormat`, not `toFixed`
- [ ] No `===` on computed floats; no float tolerance on money
- [ ] DB columns and JSON payloads carry no float money
- [ ] Large IDs are strings or BigInt
- [ ] Tests cover .5 ties, negative amounts, 1.005, a 0-decimal currency (JPY) and a 3-decimal currency (KWD)

## Not in scope / caveats

- The native `Decimal` type is still a TC39 Stage 1 proposal (2026). Don't plan around it, use a library.
- Library versions move. Check with `npm view <pkg> version` before pinning.
