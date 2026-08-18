#!/usr/bin/env python3
"""
Course catalogue example.

The compliance API tells an agent WHAT a framework requires. This example covers the other
half: what the user can actually do about it. Given a need, it finds courses and returns a
direct purchase link.

These four tools are free. No API key, no rate limit, because they exist to help a buyer
find the right course rather than to meter access to data.

Usage:
    python find_courses.py "soc 2 evidence collection"
    python find_courses.py "first 90 days as CISO" --framework "ISO 27001"
    python find_courses.py --overlap "SOC 2,ISO 27001"
    python find_courses.py --frameworks
"""
import sys
import textwrap
from typing import Optional

import requests

BASE = "https://api.theartofservice.com"
TIMEOUT = 30


def search_courses(need: str, framework: Optional[str] = None, limit: int = 10) -> list:
    """Find courses by what the buyer is trying to do."""
    params = {"q": need, "limit": limit}
    if framework:
        params["framework"] = framework
    r = requests.get(f"{BASE}/api/agent/courses", params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json().get("courses", [])


def courses_for_frameworks(frameworks: str, limit: int = 10) -> dict:
    """Courses covering two or more standards TOGETHER.

    This is the query a plain product listing cannot answer. An organisation running SOC 2
    and ISO 27001 at once does not want one course per standard, it wants the overlap.
    """
    r = requests.get(f"{BASE}/api/agent/courses-for-frameworks",
                     params={"frameworks": frameworks, "limit": limit}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def list_frameworks() -> list:
    """Every standard the catalogue covers, with a course count each."""
    r = requests.get(f"{BASE}/api/agent/course-frameworks", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json().get("frameworks", [])


def render(courses: list) -> str:
    if not courses:
        return "_No courses matched._\n"
    out = []
    for c in courses:
        out.append(f"### {c['name']}\n")
        price = c.get("price_usd")
        if price:
            out.append(f"- **Price**: ${price:.2f} {c.get('currency', 'USD')}")
        if c.get("frameworks"):
            out.append(f"- **Covers**: {', '.join(c['frameworks'])}")
        # buy_url carries attribution. Link the buyer to this, not the bare url.
        out.append(f"- **Buy**: {c['buy_url']}\n")
    return "\n".join(out)


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1

    if "--frameworks" in args:
        print("# Standards covered by the catalogue\n")
        for f in list_frameworks()[:40]:
            print(f"- {f['framework']}: {f['courses']} courses")
        return 0

    if "--overlap" in args:
        i = args.index("--overlap")
        if i + 1 >= len(args):
            print("--overlap needs a comma separated list, e.g. \"SOC 2,ISO 27001\"")
            return 1
        combo = args[i + 1]
        data = courses_for_frameworks(combo)
        print(f"# Courses covering {combo} together\n")
        if data.get("note"):
            print(f"> {data['note']}\n")
            for fw, n in (data.get("courses_per_framework") or {}).items():
                print(f"- {fw}: {n} courses individually")
            return 0
        print(render(data.get("courses", [])))
        return 0

    framework = None
    if "--framework" in args:
        i = args.index("--framework")
        framework = args[i + 1] if i + 1 < len(args) else None
        args = args[:i] + args[i + 2:]

    need = " ".join(a for a in args if not a.startswith("--"))
    courses = search_courses(need, framework)
    title = f"# Courses for: {need}"
    if framework:
        title += f" ({framework})"
    print(title + "\n")
    print(render(courses))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except requests.HTTPError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(2)
