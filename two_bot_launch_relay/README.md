# Two-Bot Launch Relay

A multi-agent launch workflow built with **CrewAI** and **Ollama** for MLH Global Hack Week 2026 — Challenge 7: Two-Bot Launch Relay.

The project demonstrates how two specialist AI agents can collaborate through a structured handoff: one researches and verifies source information, while the other prepares launch materials. A final QA stage checks the generated deliverables before they are ready for human review.

## Challenge Overview

The workflow uses two specialist bots:

- **Source Editor:** Reviews the source, extracts relevant information, prepares a source brief, and obtains human approval before initiating the handoff.
- **Launch Producer:** Uses the approved brief to prepare an announcement draft and a run-of-show CSV.

After the Producer completes its work, the Source Editor reviews the deliverables and records the QA result.

**Important:** The workflow prepares drafts only. It does not publish announcements, send messages, or book tickets.

## Project Workflow

1. The Source Editor reviews the provided source.
2. A source brief is created and presented for human approval.
3. The user approves the brief.
4. The Source Editor hands the approved brief to the Launch Producer.
5. The Producer prepares:
   - `announcement-draft.md`
   - `run-of-show.csv`
6. The Source Editor reviews the generated files and writes `qa-notes.md`.
7. Structural validation checks the announcement word count, required call to action, CSV headers, and row structure.

## Source Used

**BookMyShow — Kolkata Events**

https://in.bookmyshow.com/explore/events-today-kolkata

The source brief records the event categories and discovery features available on the page. Specific event names, dates, venues, performers, ticket prices, and current availability were not treated as verified facts.

The source page was reviewed in a browser. Direct automated retrieval returned HTTP 403, so this limitation was recorded rather than bypassed or represented as successful automated access.

## Technology Stack

- Python
- CrewAI
- Ollama
- Qwen 3.5 2B
- LiteLLM
- Markdown and CSV

## Project Structure

```text
two_bot_launch_relay/
│
├── launch-desk/
│   ├── source-brief.md
│   ├── announcement-draft.md
│   ├── run-of-show.csv
│   ├── qa-notes.md
│   └── handoff-log.txt
│
├── src/
│   └── two_bot_launch_relay/
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── crew.py
│       └── main.py
│
├── .env.example
├── pyproject.toml
└── README.md
```

## Setup and Installation

### Prerequisites

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/)

### 1. Clone the repository

```bash
git clone <https://github.com/Ro-opkatha/mlh-builders-week-2026>
cd mlh-builders-week-2026/two_bot_launch_relay
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Download the local model

```bash
ollama pull qwen3.5:2b
```

Make sure the Ollama service is running before executing the project.

### 4. Configure environment variables

Copy `.env.example` to `.env` and configure the required values.

Do not commit your `.env` file or expose API keys, credentials, or other secrets.

### 5. Run the workflow

From the repository root:

```bash
uv run python -m two_bot_launch_relay.main
```

When prompted, review the source brief and enter `APPROVED` to initiate the Producer handoff.

## Deliverables

| File | Purpose |
|---|---|
| `source-brief.md` | Source information reviewed by the Source Editor |
| `announcement-draft.md` | Draft announcement prepared for the target audience |
| `run-of-show.csv` | Structured workflow schedule |
| `qa-notes.md` | QA findings and validation result |
| `handoff-log.txt` | Record of the agent handoff |

## Validation

The workflow includes structural checks for:

- Announcement word count: 120–180 words
- Presence of the exact required call to action
- Required CSV headers: `Time`, `Owner`, `Action`, `Status`
- Four fields per CSV row
- At least five run-of-show entries
- Presence of the source brief and source URL

The QA report and automated checks should be reviewed alongside the actual deliverables. A PASS result is not a substitute for human verification of factual claims.

## Evidence

Screenshots documenting the workflow and its outputs are included with the project submission.

They demonstrate:

- Source Editor initiating the handoff to the Launch Producer
- The Producer returning its result
- The generated launch-desk files
- The QA report and final validation status

## Scope and Limitations

- The system prepares launch materials; it does not publish or distribute them.
- Event-specific information is included only when supported by the reviewed source.
- Current event availability and ticket details must be checked on the source platform.
- Local model output may require editorial correction and human review.

## Author

Built for **MLH Global Hack Week 2026 — Challenge 7: Two-Bot Launch Relay**.