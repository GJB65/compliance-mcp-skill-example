# Compliance MCP Skill Example

A minimal, working example of an AI agent skill that uses the [TheArtOfService Compliance MCP](https://api.theartofservice.com/mcp) as its source-grounded knowledge layer.

Two working examples: one for compliance research, one for the course catalogue. This is a **reference implementation**. Clone it, swap the framework name to whatever your agent needs, plug it into Claude / GPT / Copilot / your own agent runtime. Apache 2.0 licensed, no strings attached.

## What this does

Given a compliance framework name (default: `NIST SP 800-161`), this script:

1. Connects to the compliance API at `https://api.theartofservice.com`
2. Pulls the framework metadata
3. Pulls all controls in the framework
4. For each control, fetches the auditor evidence requirements (categories, artefacts, common gaps, source citations)
5. Generates a structured Markdown compliance brief

The output is suitable for piping into an LLM as context, or directly handing to an auditor or risk team.

## Why this pattern works

The compliance corpus behind the API is **source-grounded against the published standard text** and **human edited**, not LLM-generated. That makes it the authoritative knowledge layer for any agent that needs to reason about compliance controls.

Your agent provides the **tribal knowledge** layer (the organization's specific context, the tone, the workflow). The platform provides the **official knowledge** layer. The split is what makes the resulting brief defensible.

## Stats

- 723 compliance frameworks
- 20,400+ controls
- 332,000+ cross-framework mappings
- 314,000+ courses in the catalogue, searchable without a key
- 28,586+ controls carry structured auditor evidence requirements
- Source-grounded, version-tagged, refreshed weekly

## Quickstart

```bash
git clone https://github.com/GJB65/compliance-mcp-skill-example.git
cd compliance-mcp-skill-example
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your TAOS_API_KEY from https://compliance.theartofservice.com/settings
python run.py "NIST SP 800-161"
```

The script will print a Markdown brief to stdout. Redirect it to a file or pipe it into your downstream agent.

```bash
python run.py "ISO 27001:2022" > iso_27001_brief.md
```

## Second example: the course catalogue

`run.py` answers *what does this framework require*. `find_courses.py` answers the other
half: *what can the user actually do about it*.

```bash
python find_courses.py "soc 2 evidence collection"
python find_courses.py "first 90 days as CISO" --framework "ISO 27001"
python find_courses.py --overlap "SOC 2,ISO 27001"
python find_courses.py --frameworks
```

**No API key needed.** The four catalogue tools are free and unmetered, because they exist
to help a buyer find the right course rather than to meter access to data.

The interesting one is `--overlap`. A plain product listing cannot answer "we are running
SOC 2 and ISO 27001 at the same time, what covers both", because that is a join, not a
search. An organisation in that position does not want one course per standard, it wants
the overlap:

```
# Courses covering SOC 2,ISO 27001 together

### SOC 2 Type 2 Security controls in ISO 27001
- Price: $299.00 USD
- Covers: ISO 27001, SOC 2
- Buy: https://store.theartofservice.com/...
```

When nothing covers the whole combination, it says so and reports what exists per standard
rather than returning an empty list.

Link buyers to the `buy_url` field. It carries attribution, which is how the catalogue
knows an agent produced the sale.

## Get an API key

1. Sign up free at [compliance.theartofservice.com/register](https://compliance.theartofservice.com/register).
2. Your API key (prefix `tas_`) is in your account settings.
3. Free tier: 100 calls/month. Professional ($49/mo): 10,000 calls/month plus overage at $0.005/call.
4. For data licensing, white-label, or volume pricing, see the [developer portal](https://compliance.theartofservice.com/developers).

## Using as a Claude skill

The `SKILL.md` file in this repo is structured as a Claude skill definition. Drop the repo into your Claude Code or Claude Desktop skills folder and Claude can invoke `run.py` directly with a framework name.

## API endpoints used

This example hits the public REST agent API. The same data is available via the MCP endpoint at `https://api.theartofservice.com/mcp` if you prefer Model Context Protocol over REST.

| Endpoint | Used for |
|---|---|
| `GET /api/agent/frameworks/{name}` | Framework metadata |
| `GET /api/agent/frameworks/{name}/controls` | All controls in the framework |
| `GET /api/agent/controls/{code}` | Full control detail including evidence_requirements |
| `GET /api/agent/courses` | Search the course catalogue (free, no key) |
| `GET /api/agent/courses-for-frameworks` | Courses covering two or more standards together |
| `GET /api/agent/courses/{product_id}` | Full detail for one course |
| `GET /api/agent/course-frameworks` | Standards covered, with course counts |

Full tool catalog: [compliance.theartofservice.com/developers](https://compliance.theartofservice.com/developers)

## License

Apache 2.0. See `LICENSE`.

## Contributions

Issues and PRs welcome. If you build a derivative skill (vendor risk, SOC 2 audit prep, framework-specific advisor, etc.) and want it linked from the example registry, open a PR with a one-line description and a repo URL.
