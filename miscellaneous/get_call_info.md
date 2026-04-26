# get_call_info

## Description

Get detailed information about a specific call. Use get_client_communication first to retrieve the call_id.

## Protocol

# GET CALL INFO PROTOCOL

**Escalation behavior:** When any rule in this protocol says **ESCALATE**, do not draft a customer-facing response. Instead, output only: **HUMAN AGENT ACTION REQUIRED** — followed by the reason from the rule. The human agent will handle the query manually.


