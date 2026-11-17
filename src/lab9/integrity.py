"""Validate report evidence and prevent a same-version weakening of the spec."""
import math
import re

from lab9.eval import aggregate
from lab9.graders import GRADERS


def finite_number(value):
    return isinstance(value, (int, float)) and math.isfinite(value)


def ratchet(spec, base_spec):
    if base_spec is None or spec.get("eval_set_version") != base_spec.get("eval_set_version"):
        return []
    problems = []
    for section, key in (("metrics", lambda x: x["id"]),
                         ("slices", lambda x: (x["name"], x["metric"]))):
        old = {key(rule): rule for rule in base_spec.get(section, [])}
        new = {key(rule): rule for rule in spec.get(section, [])}
        if len(new) != len(spec.get(section, [])):
            problems.append(f"RATCHET duplicate {section} rules")
        for identity, before in old.items():
            after = new.get(identity)
            label = f"RATCHET {section}:{identity}"
            if after is None:
                problems.append(f"{label} removed")
                continue
            if before.get("blocking") and not after.get("blocking"):
                problems.append(f"{label} blocking disabled")
            first = before.get("threshold", {}) if section == "metrics" else before
            second = after.get("threshold", {}) if section == "metrics" else after
            for threshold in ("min", "max", "max_increase"):
                if threshold not in first:
                    continue
                a, b = first[threshold], second.get(threshold)
                if not finite_number(b) or (b < a if threshold == "min" else b > a):
                    problems.append(f"{label} {threshold} loosened or removed")
            if first.get("no_significant_drop") and not second.get("no_significant_drop"):
                problems.append(f"{label} no_significant_drop disabled")
            if section == "metrics":
                for field in ("kind", "level", "grader"):
                    if field in before and after.get(field) != before[field]:
                        problems.append(f"{label} {field} changed")
    for field in ("eval_set", "labels", "adversarial_pack", "bootstrap"):
        if field in base_spec and spec.get(field) != base_spec[field]:
            problems.append(f"RATCHET {field} changed on the same eval-set version")
    for field in ("seeds", "pass_k"):
        if field in base_spec and not set(base_spec[field]).issubset(spec.get(field, [])):
            problems.append(f"RATCHET {field} coverage reduced")
    return problems


def inspect_report(report, spec, label):
    problems = []
    prefix = lambda message: problems.append(f"{label}: {message}")
    if not isinstance(report, dict):
        return [f"{label}: report must be an object"], set(), {}
    manifest, rows, metrics = report.get("manifest"), report.get("rows"), report.get("metrics")
    if not isinstance(manifest, dict) or not isinstance(rows, list) or not isinstance(metrics, dict):
        return [f"{label}: malformed report structure"], set(), {}
    items, seeds = manifest.get("items"), manifest.get("seeds")
    if (type(items) is not int or items < 1 or not isinstance(seeds, list) or not seeds
            or any(type(seed) is not int for seed in seeds) or len(set(seeds)) != len(seeds)):
        return [f"{label}: invalid manifest items/seeds"], set(), {}
    if not manifest.get("eval_set_sha"):
        prefix("missing eval_set_sha")
    if len(rows) != items * len(seeds):
        prefix(f"row count {len(rows)} != {items} items x {len(seeds)} seeds")
    if report.get("evaluator_failures"):
        prefix("evaluator_failures is nonempty")
    for mid, value in metrics.items():
        if value is not None and not finite_number(value):
            prefix(f"metric {mid} is nonnumeric or nonfinite")
    graded = {m["id"] for m in spec.get("metrics", [])
              if m["id"] in GRADERS or any(isinstance(r, dict) and m["id"] in r for r in rows)}
    for metric in spec.get("metrics", []):
        mid = metric["id"]
        if mid not in metrics or ((metric.get("blocking") or mid in graded) and not finite_number(metrics[mid])):
            prefix(f"missing or invalid metric {mid}")
    keys, slices = [], {}
    for index, row in enumerate(rows):
        if (not isinstance(row, dict) or not isinstance(row.get("item_id"), str)
                or not row["item_id"] or type(row.get("seed")) is not int):
            prefix(f"row {index} has invalid item_id/seed")
            continue
        cid, seed = row["item_id"], row["seed"]
        keys.append((cid, seed))
        if seed not in seeds:
            prefix(f"row {index} has seed outside manifest")
        tags = row.get("slices", [])
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags) or len(set(tags)) != len(tags):
            prefix(f"row {index} has invalid slice tags")
        else:
            tag_set = frozenset(tags)
            if cid in slices and slices[cid] != tag_set:
                prefix(f"item {cid} has inconsistent slices across seeds")
            slices[cid] = tag_set
        for mid in graded:
            value = row.get(mid)
            if not finite_number(value) or value not in (0, 1):
                prefix(f"row {index} metric {mid} missing, nonfinite, or not binary")
        if "cost" in row and (not finite_number(row["cost"]) or row["cost"] < 0):
            prefix(f"row {index} has invalid cost")
        if "cost_per_success" in metrics and "cost" not in row:
            prefix(f"row {index} missing cost")
    key_set = set(keys)
    if len(key_set) != len(keys):
        prefix("duplicate (item_id, seed) rows")
    item_ids = {cid for cid, _ in key_set}
    if len(item_ids) != items:
        prefix("distinct item count differs from manifest")
    if key_set != {(cid, seed) for cid in item_ids for seed in seeds}:
        prefix("incomplete item x seed Cartesian product")
    # Recompute before trusting the summary; a forged aggregate must not bypass
    # thresholds even when all original rows are still present.
    if not problems:
        normalized = [{**row, "cost": row.get("cost", 0.0)} for row in rows]
        try:
            k_values = set(spec.get("pass_k", []))
            for mid in metrics:
                match = re.fullmatch(r"pass_(?:at|hat)_(\d+)", mid)
                if match:
                    k_values.add(int(match.group(1)))
            computed = aggregate(normalized, sorted(graded), k_values=sorted(k_values))
            for metric in spec.get("metrics", []):
                mid = metric["id"]
                if metric.get("kind") == "safety" and mid in graded:
                    computed[mid] = sum(row[mid] for row in rows)
            for mid, expected in computed.items():
                if mid not in metrics:
                    continue
                actual = metrics[mid]
                if expected is None:
                    if actual is not None:
                        prefix(f"summary {mid} disagrees with rows (undefined)")
                elif not finite_number(actual) or not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-9):
                    prefix(f"summary {mid} disagrees with rows ({actual} != {expected})")
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
            prefix(f"cannot recompute aggregates: {exc}")
    return problems, key_set, slices


def validate_reports(pr, base, spec, base_spec=None):
    problems = ratchet(spec, base_spec)
    pr_problems, pr_keys, pr_slices = inspect_report(pr, spec, "PR")
    base_problems, base_keys, base_slices = inspect_report(base, base_spec or spec, "baseline")
    problems += pr_problems + base_problems
    if pr_keys != base_keys:
        problems.append("PR (item_id, seed) set differs from baseline")
    if pr_slices != base_slices:
        problems.append("PR item slice tags differ from baseline")
    pr_manifest = pr.get("manifest", {}) if isinstance(pr, dict) else {}
    base_manifest = base.get("manifest", {}) if isinstance(base, dict) else {}
    pr_manifest = pr_manifest if isinstance(pr_manifest, dict) else {}
    base_manifest = base_manifest if isinstance(base_manifest, dict) else {}
    if pr_manifest.get("eval_set_sha") != base_manifest.get("eval_set_sha"):
        problems.append("PR eval_set_sha differs from baseline")
    configured_seeds = spec.get("seeds")
    if configured_seeds is not None:
        for label, manifest in (("PR", pr_manifest), ("baseline", base_manifest)):
            seeds = manifest.get("seeds")
            if (not isinstance(seeds, list) or any(type(seed) is not int for seed in seeds)
                    or set(seeds) != set(configured_seeds)):
                problems.append(f"{label}: seeds differ from spec")
    return problems
