#!/usr/bin/env python3
"""Validate site/data.json so a bad agent run never reaches the deployed site."""
import json
import re
import sys

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2}|Z)?)?$")
BANNER_TYPES = {"character", "weapon", "chronicled"}

errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


def opt_str(obj, key, where):
    v = obj.get(key)
    check(v is None or isinstance(v, str), f"{where}.{key} must be a string or null")
    return v


def opt_date(obj, key, where):
    v = opt_str(obj, key, where)
    if isinstance(v, str):
        check(bool(DATE_RE.match(v)), f"{where}.{key} is not an ISO date: {v!r}")


def opt_url(obj, key, where):
    v = opt_str(obj, key, where)
    if isinstance(v, str):
        check(v.startswith("https://"), f"{where}.{key} must start with https://")


def str_list(obj, key, where):
    v = obj.get(key, [])
    check(isinstance(v, list) and all(isinstance(x, str) for x in v),
          f"{where}.{key} must be a list of strings")


def main(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"::error::cannot parse {path}: {e}")
        return 1

    check(isinstance(data, dict), "root must be an object")
    if errors:
        return report()

    opt_date(data, "updatedAt", "root")
    opt_str(data, "summary", "root")

    version = data.get("version")
    check(isinstance(version, dict), "version must be an object")
    if isinstance(version, dict):
        for k in ("current", "name"):
            opt_str(version, k, "version")
        for k in ("startDate", "endDate"):
            opt_date(version, k, "version")
        str_list(version, "highlights", "version")
        nxt = version.get("next")
        check(nxt is None or isinstance(nxt, dict), "version.next must be an object or null")
        if isinstance(nxt, dict):
            opt_str(nxt, "version", "version.next")
            opt_str(nxt, "note", "version.next")
            for k in ("startDate", "livestreamDate"):
                opt_date(nxt, k, "version.next")

    for key in ("banners", "events", "news"):
        check(isinstance(data.get(key), list), f"{key} must be a list")

    for i, b in enumerate(data.get("banners") or []):
        w = f"banners[{i}]"
        if not isinstance(b, dict):
            errors.append(f"{w} must be an object")
            continue
        check(b.get("type") in BANNER_TYPES, f"{w}.type must be one of {sorted(BANNER_TYPES)}")
        opt_str(b, "name", w)
        for k in ("startDate", "endDate"):
            opt_date(b, k, w)
        str_list(b, "featured5", w)
        str_list(b, "featured4", w)
        opt_url(b, "url", w)

    for i, e in enumerate(data.get("events") or []):
        w = f"events[{i}]"
        if not isinstance(e, dict):
            errors.append(f"{w} must be an object")
            continue
        check(isinstance(e.get("name"), str) and e["name"], f"{w}.name is required")
        for k in ("startDate", "endDate"):
            opt_date(e, k, w)
        opt_str(e, "rewards", w)
        opt_url(e, "url", w)

    news = data.get("news") or []
    check(len(news) <= 20, "news must have at most 20 items")
    for i, n in enumerate(news):
        w = f"news[{i}]"
        if not isinstance(n, dict):
            errors.append(f"{w} must be an object")
            continue
        check(isinstance(n.get("title"), str) and n["title"], f"{w}.title is required")
        opt_date(n, "date", w)
        opt_str(n, "summary", w)
        opt_url(n, "url", w)

    str_list(data, "sources", "root")
    return report()


def report():
    for e in errors:
        print(f"::error::{e}")
    if errors:
        return 1
    print("data.json OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "site/data.json"))
