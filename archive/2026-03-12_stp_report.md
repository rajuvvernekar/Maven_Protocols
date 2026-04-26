# Proposed Changes: stp_report
Date: 2026-03-12
Feedback entries: 2 issues

## Issue #1: Rule 5 — minor wording update
**Problem**: Clarify that target fund is not available to select in the UI.
**Current protocol** (exact section):
> `**if:** Client cannot create STP, OR setup fails because target fund is not available`
**Proposed fix**:
```
**if:** Client cannot create STP, OR setup fails because target fund is not available to select
```
**Root cause**: Ambiguous trigger

---

## Issue #2: Rule 6 — NEW: STP Setup Error / Source Fund Navigation
**Problem**: No guidance for STP setup errors beyond "target fund not in holdings." Clients trying to create STPs from the target fund page or with pledged units in the source fund had no handling.
**Current protocol**: No existing Rule 6.
**Proposed fix** (append as new Rule 6):
```
### Rule 6: STP Setup Error — Source Fund Navigation
**if:** Client reports an error when trying to set up an STP, OR cannot find the Create STP option, AND target fund is already in holdings (Rule 5 does not apply)
**then:**
1. Check **console_mf_holdings** for the intended source fund (the fund from which money will be transferred):
   - `available` units > 0 AND `margin` = 0 → source fund is ready. Issue is likely navigation. Guide client: "To set up an STP on Coin web, go to Dashboard → Mutual Funds → select the **source fund** (the fund you want to transfer FROM) in your holdings → click the menu icon → select Create STP. The STP must be initiated from the source fund — not the target fund."
   - `margin` > 0 → pledged units present. "Please unpledge units in [source fund] first before creating an STP: Console → Portfolio → Holdings → [fund] → Unpledge. Once unpledged, try creating the STP again."
   - `available` = 0 → no free units. "The fund you are trying to transfer from has no available units. Please check the source fund selection."
2. If error persists after correct navigation → escalate with screenshot.
```
**Root cause**: Missing rule
