---
name: steerco-email-numbers
description: Update the EMAIL PROTECTION Calc workbook each month: pull new month's totals from the 'New' tab using the Mapping sheet, shift Old's rolling 3 months, and refresh Master for the SteerCo report.
---

## When to use
Trigger when the user says any of: "update SteerCo numbers", "run the email numbers", "do this month's email protection", "/steerco-email-numbers", or anything about refreshing the Email Protection Calc workbook with a new month of raw data.

Assumes the workbook has the standard structure: tabs named `New `, `Old`, `Master`, `Mapping`, `Instructions`. If any are missing, stop and tell the user.

## Inputs
- The user has already pasted the latest month's raw data into the `New ` tab (cols A–E, classifications in A3:A18, message counts in D3:D18, End Date in B22).

## Goal
- `Old` holds the most recent 3 months, with the oldest column shifted out and the newest month added as column D.
- `Master` reflects those same 3 months (already formula-driven — no manual edit needed).

## Steps

### 1. Compute the new month's totals from the New tab
Read `New !A3:A18` (classifications), `New !D3:D18` (message counts), `New !B22` (End Date), `New !B24` (Total Messages). Read `Mapping!A4:B19` for the lookup.

For each Old category in `Old!A4:A8`, compute SUMPRODUCT over New's D column where the classification's mapped value (via Mapping) equals that Old category. Compute the month label as `TEXT(New!B22, "mmm")`.

**Done when:** you have a `{month, total, spam, malicious, policyBreach, spoofing, phishing}` object ready.

### 2. Show the user the new month and ask to confirm
Present the computed values clearly (month name + each category total + grand total from `New!B24`). Ask the user to confirm before shifting Old.

**Confirm first:** wait for explicit confirmation before step 3. If the user spots something off, point them at the `Mapping` tab to fix the routing and re-run.

### 3. Shift Old's rolling 3 months
Read current values from `Old!B2:D8`. Write back:
- `Old!B2:B8` ← previous `C2:C8` (Feb becomes the new "3 months ago")
- `Old!C2:C8` ← previous `D2:D8`
- `Old!D2:D8` ← the new month (label in D2, total in D3, then the 5 categories in D4:D8)

Use `set_cell_range` with static values (not formulas) for D2:D8 so the new month is locked in. Preserve existing number formatting (`#,##0` for the counts, plain text for the month label).

**Done when:** `Old!B2:D2` shows three consecutive months ending with the new one, and the data rows match.

### 4. Verify Master refreshed
Read `Master!B2:D8`. Confirm the headers in row 2 match the new Old columns and the data ties out. Master uses HLOOKUP against Old's month headers, so it should update automatically.

**Done when:** Master's 3 month columns match Old's B/C/D, and `Master!D3` equals the new month's grand total.

### 5. Report
One short paragraph naming the new month added and the 3 months now visible. Cite `Master!A1:D8` as the range to copy into the report file.

## Rules
- Never write formulas into `Old!B:D` data cells — they must be static values so future months don't disturb history while it's the "latest 3".
- Don't touch the `Mapping` tab unless the user asks. If a classification in New isn't in Mapping, flag it in step 2 — don't silently drop it.
- If `New!B22` is empty or not a date, stop and ask the user for the month label.
