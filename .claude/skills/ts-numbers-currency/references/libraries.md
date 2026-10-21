# Library reference — money & decimal maths in TS/JS

Read this when choosing between libraries or writing code against one of them. Versions were checked in September 2026. Confirm them with `npm view <pkg> version` before pinning.

## Contents
1. Comparison table
2. Dinero.js v2 (default for money)
3. currency.js
4. big.js / decimal.js / bignumber.js
5. BigInt (native)
6. Storage & transport patterns

---

## 1. Comparison table

| Library | Internal model | Size | Best for | Watch out for |
|---|---|---|---|---|
| **Dinero.js 2.x** | Integer minor units + currency object; `number` or `bigint` calculator | Tree-shakeable | Multi-currency apps, invoices, payments, allocation, type-safe currency mixing | You pass minor units; no `divide`/`percentage`, use `allocate`/scaled `multiply`; `toFormat` removed (use `toDecimal` + Intl) |
| **currency.js 2.x** | Stores `intValue` (integer) and `value` | ~1 KB | Simple single-currency UI calculations | Accepts floats at the API edge; safe to ~90 trillion dollars; slow-moving project |
| **big.js 7.x** | Arbitrary-precision decimal | ~6 KB | Exact decimal maths: rates, FX, unit prices, tax engines | No trig/log; set `Big.DP`/`Big.RM` deliberately |
| **decimal.js 10.x** | Arbitrary precision (significant digits) | Heaviest | Needs `pow`, `ln`, `exp`, trig, non-integer powers | Precision is significant digits, not decimal places |
| **bignumber.js** | Arbitrary-precision decimal + other bases | Medium | Crypto, base conversion, heavy config needs | More API surface than big.js |
| **BigInt** (native) | Arbitrary-precision integer | 0 KB | Integers > 2^53 − 1, exact integer money maths | No decimals; can't mix with `number`; not JSON-serialisable |

**Default picks:** money → Dinero.js v2; non-money exact decimals → big.js; huge integers → BigInt.

---

## 2. Dinero.js v2

v2 went stable in March 2026, after years of alphas. It is a full TypeScript rewrite with standalone functions. Install `dinero.js`. The old `@dinero.js/*` alpha packages are deprecated. Dinero v1 had a different, chainable API (`Dinero({ amount }).add(...)`), so don't mix v1 examples into v2 code.

```ts
import {
  dinero, add, subtract, multiply, allocate, compare, equal, isZero,
  toDecimal, toSnapshot, transformScale, halfEven, halfUp,
} from "dinero.js";
import { NZD, USD, JPY, KWD } from "dinero.js/currencies";

const a = dinero({ amount: 1999, currency: NZD });   // $19.99 (exponent 2)
const y = dinero({ amount: 500, currency: JPY });    // ¥500   (exponent 0)
const k = dinero({ amount: 1500, currency: KWD });   // 1.500 KD (exponent 3)

add(a, dinero({ amount: 1, currency: NZD }));        // $20.00
// add(a, dinero({ amount: 1, currency: USD }))      // TypeScript error: currency mismatch

// Multiply by a decimal using a scaled integer: 0.15 = { amount: 15, scale: 2 }
const gst = multiply(a, { amount: 15, scale: 2 });   // scale grows to 4 internally
const gstCents = transformScale(gst, 2, halfEven);   // back to 2 dp with explicit rounding

// Split with no lost cents; ratios can be uneven, e.g. [70, 30]
allocate(dinero({ amount: 1000, currency: NZD }), [1, 1, 1]); // 334, 333, 333

// Output
toDecimal(a);                                        // "19.99" (string)
const fmt = new Intl.NumberFormat("en-NZ", { style: "currency", currency: "NZD" });
toDecimal(a, ({ value }) => fmt.format(value));      // "$19.99" — Intl accepts decimal strings
toSnapshot(a);                                       // { amount, currency, scale } for persistence
```

- Rounding helpers: `up`, `down`, `halfUp`, `halfDown`, `halfEven`, `halfOdd`, `halfTowardsZero`, `halfAwayFromZero`.
- For very large amounts use `import { dinero } from "dinero.js/bigint"` and pass `amount: 1999n`.
- Currency conversion uses `convert(d, NZD, { NZD: { amount: 165, scale: 2 } })`, with rates as scaled integers.
- Official agent skills exist: `npx skills add dinerojs/skills`.

## 3. currency.js

```ts
import currency from "currency.js";

currency(0.1).add(0.2).value;               // 0.3
currency("19.99").multiply(0.15).value;     // 3  (rounded to precision 2)
currency(10).distribute(3).map(c => c.value); // [3.34, 3.33, 3.33]
currency(1999, { fromCents: true }).format(); // "$19.99"
const nzd = (v: currency.Any) => currency(v, { symbol: "$", precision: 2 });
```

It is fine for simple, single-currency front-end maths. Prefer Dinero.js for multi-currency work, for persistence, or when you need compile-time currency safety.

## 4. big.js / decimal.js / bignumber.js

Always construct from **strings**.

```ts
import Big from "big.js";
Big.DP = 20;           // decimal places for division
Big.RM = Big.roundHalfEven;

new Big("0.1").plus("0.2").toString();             // "0.3"
new Big("19.99").times("0.15").round(2).toString(); // "3" → use toFixed(2) for "3.00"
new Big("1").div("3").toFixed(4);                  // "0.3333"
new Big(0.1);  // avoid — the float is already inexact before Big sees it
```

- **decimal.js**: `new Decimal("2").pow("0.5")`, `Decimal.set({ precision: 30, rounding: Decimal.ROUND_HALF_EVEN })`.
- **bignumber.js**: `new BigNumber("0.1").plus("0.2")`, `BigNumber.config({ DECIMAL_PLACES: 10 })`; it also accepts BigInt input.
- To get money back out of a decimal library, round to the currency exponent, then convert to minor units via string (`toFixed(exp)`), then parse with `toMinorUnits`.

## 5. BigInt

```ts
const id = BigInt("9007199254740993");       // exact
5n / 2n;                                      // 2n (truncates toward zero)
// 1n + 1                                     // TypeError: can't mix BigInt and number
JSON.stringify({ id }, (_k, v) => typeof v === "bigint" ? v.toString() : v); // '{"id":"9007199254740993"}'
```

Keep 64-bit IDs as strings unless you actually do arithmetic on them.

## 6. Storage & transport

- **Postgres/MySQL/SQL Server:** use `BIGINT` minor units + `CHAR(3)` currency, or `NUMERIC(19,4)` / `DECIMAL`. Never `FLOAT`/`REAL`. node-postgres returns `int8` and `numeric` as **strings** by design, so parse them with BigInt or a decimal library rather than `Number()` when they could be large.
- **JSON API shapes:** `{ "amount": 1999, "currency": "NZD" }` (integer minor units) or `{ "amount": "19.99", "currency": "NZD" }` (decimal string). Document which one you use and keep it consistent.
- **Payment APIs:** Stripe expects minor units (`1999` = $19.99, `500` = ¥500). Some currencies have processor-specific quirks, so check the provider's currency page.
- **Spreadsheets/CSV export:** export decimal strings produced from minor units. Don't export the result of a float calculation.
