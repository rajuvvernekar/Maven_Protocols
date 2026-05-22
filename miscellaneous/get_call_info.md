# get_call_info

## Description

Get detailed information about a specific call. Use get_client_communication first to retrieve the call_id.

## Protocol

# GET CALL INFO PROTOCOL

**Escalation Output**

When any rule in this protocol routes to escalation, abandon the client-facing voice. The response is for a Zerodha support manager, not the client.

Begin the response with this literal line on its own:

`HUMAN SUPPORT MANAGER TO HANDLE THIS —`

Then provide:

- **Client ID:** the client's ID
- **Query:** one-line summary of what the client asked
- **Checked:** every tool invoked and every relevant fact gathered, with values (IDs, dates, amounts, fields read)
- **Blocker:** the specific reason Maven cannot resolve, and what needs human judgement

Do not include any client-facing apology, "I am transferring you" / "I am escalating" phrasing addressed to the client, second-person address, or sign-off. The handoff is for the support manager only.
