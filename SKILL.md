---
name: compliance-mcp-brief
description: Generate a Markdown compliance brief for any of 718 compliance frameworks, with auditor evidence requirements, common gaps, and source citations. Calls the TheArtOfService Compliance API (human-edited, source-grounded corpus).
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
