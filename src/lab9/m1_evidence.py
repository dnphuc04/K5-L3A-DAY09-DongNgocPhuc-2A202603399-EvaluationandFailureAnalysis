"""Replay isolated failure mechanisms for M1; never change the supplied variants."""
from __future__ import annotations

import json

from lab8.console import utf8_stdio
from lab8.shapes import SHAPES
from lab9.trace_case import investigate
from lab9.variant_agent import make_shape


CASES = (
    ("leaky_trace", "C-004"),
    ("ignore_denied", "C-007"),
    ("ticket_trust", "C-002"),
    ("sum_parts", "C-014"),
    ("pre_deducted", "C-014"),
    ("stale_clause", "C-006"),
    ("sibling_refund", "C-010"),
    ("misreport", "C-008"),
)


def main() -> None:
    utf8_stdio()
    for bug, claim in CASES:
        shape = f"m1_{bug}"
        SHAPES[shape] = make_shape(shape, {"no_override", bug})
        for name in (shape, "fixed"):
            trial = investigate(name, claim, 11)["trial"]
            print(f"\n{name} {claim}@11 run_id={trial['result']['run_id']}")
            print("grade", trial["lab8_pass"], trial["lab8_reason"])
            print("ledger", trial["snapshot"], "unexpected_rows", trial["unexpected_rows"])
            for step, event in enumerate(trial["events"], 1):
                payload = event["payload"]
                if event["kind"] == "debug_claim_row":
                    payload = {"fields": sorted(payload), "secret_present": bool(payload.get("parent_secret"))}
                print(step, event["kind"], json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
