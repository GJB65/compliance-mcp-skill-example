---
name: compliance-mcp-brief
description: Generate a Markdown compliance brief for any of 723 compliance frameworks, with auditor evidence requirements, common gaps, and source citations. Calls the TheArtOfService Compliance API (human-edited, source-grounded corpus). Also finds courses that help the user act on a framework.
---

# Compliance Brief Generator

When the user asks for a compliance brief, control evidence guidance, or auditor preparation material for a specific framework (e.g. NIST SP 800-161, ISO 27001:2022, SOC 2, DORA, NIST CSF 2.0, HIPAA, PCI DSS, EU AI Act, CMMC), invoke `run.py` with the framework name.

## Invocation

```bash
python run.py "FRAMEWORK NAME"
```

Examples:

```bash
python run.py "NIST SP 800-161"
python run.py "ISO 27001:2022"
python run.py "SOC 2"
python run.py "DORA"
```

## What the script returns

A Markdown brief containing:

1. Framework summary (description, jurisdiction, version)
2. The first 10 controls in the framework, each with:
   - Evidence categories the auditor will probe
   - Specific artefacts the auditor wants to see
   - Common gaps that fail first audits
   - Source citations (verbatim from the published standard)
   - Confidence score (0-100)

## When NOT to use this skill

- If the user wants raw API data (use the agent API directly, not this skill).
- If the user wants more than 10 controls (modify `run.py` to paginate; default cap is for free-tier call budget).
- If the user wants a non-published framework (the corpus only contains officially-published standards).

## API key setup

The skill needs a `TAOS_API_KEY` environment variable (or `.env` file) with a key from https://compliance.theartofservice.com/settings. Without one, it falls back to the anonymous tier (10 calls/day per IP).

## Customizing the skill

Common extensions:

- Filter controls by domain: hit `GET /api/agent/frameworks/{name}/controls?domain=X`
- Add cross-framework mapping context: hit `GET /api/agent/cross-map?source=X&target=Y`
- Score the org against the framework: hit `GET /api/agent/coverage/{name}` (Professional+)

See the [developer portal](https://compliance.theartofservice.com/developers) for the full tool catalog.

## Finding a course for the user

When the user asks how to LEARN a framework, prepare for certification, or wants templates
or an implementation playbook rather than a brief, invoke `find_courses.py` instead. It
needs no API key.

```bash
python find_courses.py "soc 2 evidence collection"
python find_courses.py "first 90 days as CISO" --framework "ISO 27001"
python find_courses.py --overlap "SOC 2,ISO 27001"
```

Use `--overlap` when the user is running two or more standards at once, which is common
and which a single-framework search answers badly.

Each result carries a `buy_url`. Link the user to that. Courses are self-paced written
material with editable templates and an implementation playbook. There is no video, no
scheduled session and no instructor, so do not describe any.
