# Customer Sentiment Analysis Pack

Analyze customer sentiment from public sources with automated discovery, collection, scoring, and trend analysis.

## Quick Start

1. **Install the pack** using the agent-packs installer
2. **Switch to** `@sentiment-orchestrator` mode
3. **Provide product information**:
   ```
   Analyze sentiment for:
   - Product: Acme Widget Pro
   - Company: Acme Corp
   - Keywords: widget, enterprise, automation
   ```

The orchestrator will:
- Discover relevant sources (or use provided ones)
- Collect and score sentiment from public posts
- Analyze trends against historical data
- Deliver actionable insights

## Agents

| Agent | Mode | Purpose |
|-------|------|---------|
| Orchestrator | `sentiment-orchestrator` | Coordinates workflow, manages sessions |
| Source Discovery | `sentiment-source-discovery` | Finds relevant public sources |
| Sentiment Analyzer | `sentiment-analyzer` | Collects and scores sentiment |
| Trend Analyst | `sentiment-trend-analyst` | Analyzes patterns, updates history |

## Workflow Phases

```
Phase 0: Intake      → Validate product info, create session
Phase 1: Discovery   → Find sources (if not provided)
Phase 2: Collection  → Gather and score sentiment items
Phase 3: Trending    → Analyze patterns, update LTM
Phase 4: Insights    → Generate summary with recommendations
```

## Memory Structure

```
.sentiment-memory/
├── current-session.json     # Active session pointer
├── runs/{session-id}/       # Session data (STM)
│   ├── session.json
│   ├── product.json
│   ├── sources.json
│   ├── sentiment-items/
│   ├── aggregated-sentiment.json
│   ├── trend-report.md
│   └── summary.md
└── ltm/                     # Persistent history
    └── products/{slug}/
        ├── sentiment-history.jsonl
        └── trend-history.jsonl
```

## Providing Sources Manually

Skip discovery by providing sources:

```
Analyze sentiment for Acme Widget Pro

Sources:
- https://github.com/acme/widget-pro/issues
- https://twitter.com/search?q=acme%20widget
- https://reddit.com/r/SaaS/search?q=acme
```

## Requirements

- Browser tool access (for discovery and collection)
- Read/edit file access
- MCP tools (optional, for orchestrator)

## Documentation

Full documentation: [docs/customer-sentiment-analysis.md](../../docs/customer-sentiment-analysis.md)
