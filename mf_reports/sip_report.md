# sip_report

## Description

WHEN TO USE:

When customer asks about:
- SIP status (active/paused/cancelled/completed/failed)
- SIP not triggered or deducted this month
- SIP next date, frequency, amount
- Step-up not applied
- Mandate linked to SIP
- AMC SIP vs Zerodha SIP behavior
- SIP cancelled without customer action

TRIGGER KEYWORDS: "SIP", "SIP not triggered", "SIP cancelled", "SIP paused", "SIP amount", "step-up", "AMC SIP", "next SIP date", "coin"

## Protocol

# SIP REPORT PROTOCOL

## Knowledge Base

<knowledge_base>
<facts>
- Contains ALL SIPs (active, paused, cancelled, completed, failed)
- sip_type: sip (Zerodha, modifiable), amc_sip (BSE, delete-only), conditional, stp
- Zerodha SIP triggers 1:30 AM; AMC SIP triggers 3:15 AM
- SIPs trigger 2 days prior to the preferred_date. When client asks about upcoming SIP within next 5 days, check **mf_order_history** for already-placed orders.
- AMC SIP: setup must be ≥2 days before preferred_date to trigger in current month
- AMC SIP cannot be modified or paused. It can ONLY be deleted. To change amount/date/fund, delete the existing AMC SIP and create a new one. Deletion must be done ≥2 days before next instalment date.
- Zerodha SIP: initial lumpsum order must be allotted (T+1) and updated (T+2) before SIP triggers. If preferred_date is within 2 days of initial order, SIP skips current month. To trigger next month, pause and resume the SIP.
- AMC SIP cancelled after 3 consecutive payment failures (SEBI circular Apr 1 2024)
- fund_source shows mandate linkage: digio-mandates/UPI-mandates = mandate linked; pool/blank = no mandate
- public_id needed as input for sip_modification_log (mapped to sip_id there)
- Scheme name field is `name` (not `fund`)
- `last_sip_at` is the date of the last SIP order, NOT the pause/modify date. Always use **sip_modification_log** for pause/modify dates.
</facts>

<field_usage>
  <share>name (fund name) | amount | sip_status | frequency | preferred_date | next_sip_date | last_sip_at | created_at</share>
  <internal>sip_type | fund_source (mandate check) | public_id (for sip_modification_log input) | remarks</internal>
  <banned>id | client_id | transaction_mode | nav | intervals | pending_intervals | status (deprecated) | tag | sip_reg_num | mandate_details</banned>
</field_usage>

<sip_status_values>
  <active>Currently active, will trigger on next_sip_date</active>
  <paused>Stopped by client or AMC (scheme suspended lumpsum)</paused>
  <cancelled>Deleted by client</cancelled>
  <completed>All instalments completed</completed>
  <failed>SIP creation failed, never activated</failed>
</sip_status_values>
</knowledge_base>

---

## Business Rules

### Rule 0: Field Protection
Never share `<banned>` fields. Use `<internal>` fields for reasoning only.

### Rule 1: SIP Not Triggered — Sequential Check
**if:** Customer says SIP didn't trigger
**then:** Check in order:
0. Check `get_all_client_data`: if `client_acc_type` ≠ Individual AND `account_statuses` = deactivated → ESCALATE TO MF TEAM. Account type conversion may require fresh SIP setup.
1. **CRITICAL — Zerodha SIP initial investment check (perform this first if `sip_type` = sip):**
Check **mf_order_history** for a FRESH order (purchase_type = FRESH, variety = NRM/regular) for this fund.
   - FRESH order not found → "No initial investment found for this fund. Please place a lumpsum order first. Once allotted and settled (T+2), the SIP will begin triggering."
   - FRESH order found, status = Processing/Placed → "Your initial investment is still being processed. The SIP will trigger once the initial units are allotted and settled. Once allotted, pause and resume your SIP to update the next instalment date."
   - FRESH order found, status = Failed/Cancelled → "Your initial investment was not completed. Please place a fresh lumpsum order. Once the lumpsum is allotted, pause and resume your SIP on Coin to ensure it triggers from the next cycle."
   - FRESH order allotted → initial investment confirmed. Continue to Step 2.
2. `sip_status` ≠ Active → that's the answer.
3. `sip_type` = amc_sip AND cancelled → check `remarks` for consecutive rejection (3-failure rule).
4. `next_sip_date` is future → hasn't reached trigger date yet.
5. `fund_source` = blank or pool → no mandate linked. "Link a mandate for auto-debit."
5.1. **Mandate linkage verification:** ALWAYS check `fund_source` on the SIP record first:
   - `fund_source` = digio-mandates or upi-mandates → mandate is linked. Confirm auto-debit is set up.
   - `fund_source` = blank or pool → mandate is NOT linked to this SIP, regardless of whether a mandate exists elsewhere.
     → Check **mandate_report** to see if an active mandate exists:
       - Mandate active → "Your mandate is active but not yet linked to your SIP. Please link it. Refer: [What is a mandate and how to create them for SIPs on Coin?](https://support.zerodha.com/category/mutual-funds/payments-and-orders/coin-mandates/articles/sip-mandate-on-coin#:~:text=Linking%20a%20mandate%20to%20an%20existing%20SIP)"
       - No active mandate → "No mandate linked. Please create and link a mandate for auto-debit."
   **CRITICAL: NEVER confirm that auto-debit will happen unless `fund_source` is verified as digio-mandates or upi-mandates on this specific SIP.**
5.5. Mandate-linked AMC SIP showing "Pending mandate verification" → check **mandate_debit_report** for debit status AND **fund_allocation_report** for payment mapping.
6. `sip_type` = amc_sip AND `created_at` < 2 days before `preferred_date` → "AMC SIP must be set up ≥2 days before execution date."
6.5. **Initial allotment timing check (Zerodha SIP — if FRESH order confirmed allotted in Step 1):**
   - If FRESH order allotment date is on or after `preferred_date` → "Your initial investment was allotted after your SIP date, so this month's instalment was skipped. Please pause and resume your SIP to reset the next trigger date and ensure it runs from the next cycle."
   - If `preferred_date` is within 2 days of FRESH order placement date → "Since the SIP date was too close to the initial order, it won't trigger this month. Please pause and resume your SIP to ensure it triggers next month."
6.6. **Upcoming SIP check:** If next SIP date is within 5 days → check **mf_order_history** for an already-placed SIP order (SIPs trigger 2 days prior to preferred_date). If order exists, report its actual status instead of predicting future triggers.
7. All normal → check **mf_order_history** for SIP order. If exists → payment issue → **mandate_debit_report**.
8. No order found → get `public_id` → **sip_modification_log** for recent pause/modify.
   **CRITICAL:** Always check **sip_modification_log** when the SIP's expected trigger date falls within 2 days of any modification. If modification found within T-2 of trigger → "Your SIP was [modified/paused] on [modified_at], within 2 days of the execution date. The current instalment was skipped. It will trigger from the next SIP date." Do NOT rely on mf_order_history alone to conclude no action was taken.

### Rule 2: AMC SIP Auto-Cancelled
**if:** `sip_type` = amc_sip AND `sip_status` = Cancelled AND customer didn't cancel
**then:** Cross-check **mf_order_history** for 3 consecutive failed/rejected orders for this SIP. If confirmed → "Your AMC SIP was cancelled due to 3 consecutive payment rejections. The status will update within 24-48 hours. Please create a new AMC SIP." Do NOT suggest creating a Zerodha SIP for AMC SIP funds.

### Rule 3: AMC vs Zerodha SIP
**if:** Customer confused about SIP behavior, OR client asks to modify/pause AMC SIP
**then:** Check `sip_type`:
- sip = Zerodha (modify, pause, step-up, flexible frequency)
- amc_sip = AMC: **Cannot be modified or paused. Can ONLY be deleted.** To change amount, date, or fund, delete the existing AMC SIP and create a new one with the desired values. Deletion must be done ≥2 days before next instalment date. Auto-cancel on 3 consecutive failures.
**If AMC SIP deletion is technically failing** (client has followed correct steps but deletion is not succeeding) → ESCALATE TO MF TEAM immediately. Do not ask for screenshots or troubleshoot further. "We are unable to process this deletion from our end and are escalating this to our team. You can expect a resolution within 24-48 hours."
**CRITICAL:** `last_sip_at` is the date of the last SIP order execution, NOT the date the SIP was paused or modified. To determine when a SIP was paused, modified, or deleted, always check **sip_modification_log** using the SIP's `public_id`.
**Note:** If client wants to switch investments from one fund to another → suggest Systematic Transfer Plan (STP) via **stp_report** as an alternative to stopping one SIP and starting another.

### Rule 5: SIP Mandate Linkage Check
**if:** Customer asks about mandate linkage for SIPs, whether SIPs will auto-debit, OR SIP showing "pending mandate verification"
**then:**
**Step 1 — Verify if mandate is already linked BEFORE recommending creation:**
Check `fund_source` in sip_report for the relevant SIP:
- `digio-mandates` or `upi-mandates` → mandate already linked. Do NOT tell client to create a mandate. Check **mandate_report** for current status:
  - success/register_success → active. Check **mandate_debit_report** for debit attempt and **mf_order_history** for allotment status.
  - created/pending → "Your mandate is currently being verified. eNACH takes up to 3 working days; UPI autopay is typically immediate. Auto-debit will begin once verification is complete."
  - failed/register_failed → "Your mandate registration failed. Please create a new mandate. UPI autopay activates within minutes."
- blank or pool → no mandate linked. Direct client to link one: [What is a mandate and how to create them for SIPs on Coin?](https://support.zerodha.com/category/mutual-funds/payments-and-orders/coin-mandates/articles/sip-mandate-on-coin#:~:text=Linking%20a%20mandate%20to%20an%20existing%20SIP)
**Step 2 — For daily SIPs specifically:**
Orders for daily SIPs are placed on T-1 day in the system. Before concluding a daily SIP instalment is missing, check **mf_order_history** for T-1 day.

### Rule 6: SIP Deletion Failures
**if:** Client reports they cannot delete a SIP
**then:** ESCALATE TO AGENT immediately for manual handling. Do not ask for screenshots or troubleshoot further. "We are escalating this to our team for resolution. You can expect an update within 24-48 hours."
