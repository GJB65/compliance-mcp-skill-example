#!/usr/bin/env python3
"""
Compliance MCP Skill Example.

Pulls a framework + its controls + evidence requirements from the
TheArtOfService Compliance API and emits a Markdown brief.

Usage:
    python run.py "NIST SP 800-161"
    python run.py "ISO 27001:2022"
    python run.py "SOC 2"
"""
import os
import sys
import textwrap
from typing import Any, Optional

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.environ.get("TAOS_API_KEY", "")
BASE = "https://api.theartofservice.com"
TIMEOUT = 30


def _headers() -> dict:
    h = {"Accept": "application/json"}
    if API_KEY:
        h["Authorization"] = f"Bearer {API_KEY}"
    return h


def get_framework(name: str) -> Optional[dict]:
    r = requests.get(f"{BASE}/api/agent/frameworks/{name}",
                     headers=_headers(), timeout=TIMEOUT)
    if r.status_code != 200:
        return None
    return r.json()


def list_controls(name: str) -> list:
    r = requests.get(f"{BASE}/api/agent/frameworks/{name}/controls",
                     headers=_headers(), timeout=TIMEOUT)
    if r.status_code != 200:
        return []
    data = r.json()
    if isinstance(data, dict) and "controls" in data:
        return data["controls"]
    return data if isinstance(data, list) else []


def get_control_detail(code: str) -> Optional[dict]:
    """Hit the agent-tier control endpoint (no auth required) which returns
    evidence_requirements inline. The /api/frameworks/controls/{code} endpoint
    is the licensing-tier sibling and requires a Bearer key."""
    r = requests.get(f"{BASE}/api/agent/controls/{code}",
                     headers=_headers(), timeout=TIMEOUT)
    if r.status_code != 200:
        return None
    return r.json()


def _bullets(items: list[str], indent: int = 2) -> str:
    if not items:
        return f"{' ' * indent}_(none recorded)_"
    return "\n".join(f"{' ' * indent}- {item}" for item in items)


def format_brief(framework: dict, controls_with_evidence: list[dict]) -> str:
    name = framework.get("name", "Unknown framework")
    description = framework.get("description") or "(no description in corpus)"
    jurisdiction = framework.get("jurisdiction") or "International"
    version = framework.get("version") or "current"
    total_controls = len(controls_with_evidence)

    out: list[str] = []
    out.append(f"# {name} compliance brief\n")
    out.append(f"**Jurisdiction**: {jurisdiction}  ")
    out.append(f"**Version**: {version}  ")
    out.append(f"**Controls covered in this brief**: {total_controls}\n")
    out.append(f"## Framework summary\n\n{description}\n")
    out.append("## Controls with auditor evidence\n")
    out.append(
        "Each control below carries the structured evidence guidance auditors "
        "look for first. Use this as input to your agent's evaluation pass.\n"
    )

    for c in controls_with_evidence:
        code = c.get("code", "")
        title = c.get("title", "(no title)")
        ev = c.get("evidence_requirements") or {}
        categories = ev.get("categories") or []
        artefacts = ev.get("artefacts") or []
        common_gaps = ev.get("common_gaps") or []
        sources = ev.get("sources") or []
        confidence = ev.get("confidence")

        out.append(f"### {code} — {title}\n")
        if categories:
            out.append(f"**Evidence categories**: {', '.join(categories)}\n")
        out.append("**Artefacts an auditor will want:**")
        out.append(_bullets(artefacts))
        out.append("\n**Common gaps:**")
        out.append(_bullets(common_gaps))
        if sources:
            out.append("\n**Sources cited:**")
            out.append(_bullets(sources))
        if confidence is not None:
            out.append(f"\n**Confidence**: {confidence}/100\n")
        out.append("")

    out.append("---\n")
    out.append(
        "Source: https://compliance.theartofservice.com  \n"
        "Corpus: 718 frameworks, 20,400+ controls, 332,000+ cross-framework "
        "mappings. Source-grounded against the published standard text. Human "
        "edited, not LLM-generated.\n"
    )
    return "\n".join(out)


def main() -> int:
    framework_name = sys.argv[1] if len(sys.argv) > 1 else "NIST SP 800-161"
    if not API_KEY:
        sys.stderr.write(
            "WARNING: no TAOS_API_KEY set. Falling back to anonymous tier "
            "(10 calls/day per IP). Set TAOS_API_KEY in .env for production "
            "use.\n\n"
        )

    framework = get_framework(framework_name)
    if not framework:
        sys.stderr.write(
            f"Could not find framework '{framework_name}'. Try "
            f"'NIST SP 800-161', 'ISO 27001:2022', 'SOC 2', or use the search "
            f"endpoint at /api/agent/frameworks?q=...\n"
        )
        return 1

    controls = list_controls(framework_name)
    if not controls:
        sys.stderr.write(f"No controls returned for '{framework_name}'.\n")
        return 1

    # Cap at 10 controls for the example to keep output readable and within
    # the free-tier call budget. In production, paginate or filter by domain.
    sample = controls[:10]
    enriched: list[dict] = []
    for c in sample:
        code = c.get("code") or c.get("control_code")
        if not code:
            continue
        detail = get_control_detail(code)
        if detail:
            enriched.append(detail)

    brief = format_brief(framework, enriched)
    sys.stdout.write(brief)
    return 0


if __name__ == "__main__":
    sys.exit(main())
