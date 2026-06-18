#!/usr/bin/env python3
"""Build a self-contained protocol_viewer.html from all active protocol .md files.

Embeds every active tool's markdown (JSON) into the template so the viewer works
offline by just opening the file (no server needed). Re-run after protocol edits.

Usage:  python3 prototypes/build_viewer.py
"""
import json, re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUBDIRS = ["console_reports","mf_reports","crux_reports","kite_admin","crm","cashier_reports","miscellaneous"]
DISABLED = {"console_eq_tradebook","console_fno_tradebook","referral_payout","demat_freeze_status",
            "get_call_info","get_client_contact","get_client_interactions","st_reports"}
# stamp passed in via env-free constant (Date.now() unavailable in some sandboxes); set at build time
import datetime
GENERATED = datetime.date.today().isoformat()

protocols = {}
for sub in SUBDIRS:
    for f in sorted((REPO/sub).glob("*.md")):
        if f.stem in DISABLED:
            continue
        protocols[f.stem] = {"cat": sub, "md": f.read_text(encoding="utf-8")}

tools = sorted(set(protocols) | {"settlement_date_calculator", "get_all_client_data"})
data = {"generated": GENERATED, "tools": tools, "protocols": protocols}
payload = json.dumps(data, ensure_ascii=False)
assert "</script>" not in payload, "content contains </script>"

template = (REPO/"prototypes/protocol_viewer_template.html").read_text(encoding="utf-8")
out = template.replace("__DATA__", payload)
(REPO/"prototypes/protocol_viewer.html").write_text(out, encoding="utf-8")
print(f"Built prototypes/protocol_viewer.html — {len(protocols)} protocols, {len(out)} bytes, generated {GENERATED}")
