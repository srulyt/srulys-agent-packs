# Customer Sentiment Analysis Pack

A multi-agent system for discovering, collecting, and analyzing customer sentiment from public sources. Get actionable insights with trend tracking over time.

## Overview

The Customer Sentiment Analysis Pack automates the process of:
- **Discovering** relevant public sources where customers discuss your product
- **Collecting** individual sentiment items (posts, comments, reviews, issues)
- **Scoring** sentiment with polarity, magnitude, and confidence
- **Tracking** trends across analysis sessions
- **Generating** causal hypotheses and actionable recommendations

## Installation

```bash
npx agent-packs install customer-sentiment-analysis
```

Or manually copy the pack to your project's `.roo/` directory.

## Getting Started

### Basic Usage

1. Switch to the orchestrator mode: `@sentiment-orchestrator`
2. Provide product information:

```markdown
Analyze customer sentiment for:

Product: Acme Widget Pro
Company: Acme Corporation
Description: Enterprise widget management solution
Keywords: widget, automation, enterprise
```

### With Specific Sources

```markdown
Analyze sentiment for Acme Widget Pro using these sources:

- https://github.com/acme/widget-pro/issues
- https://twitter.com/search?q=acme%20widget%20pro
- https://reddit.com/r/SaaS/search?q=acme+widget
- https://news.ycombinator.com/item?id=12345678
```

## Agents

### Sentiment Orchestrator

**Mode**: `sentiment-orchestrator`

The central coordinator that manages the complete analysis workflow.

**Responsibilities**:
- Validates product information
- Creates and manages analysis sessions
- Delegates to specialized agents
- Aggregates results into final insights
- Handles session recovery

**When to use**: Start all sentiment analysis sessions with this mode.

### Source Discovery

**Mode**: `sentiment-source-discovery`

Discovers relevant public sources for sentiment analysis.

**Responsibilities**:
- Searches across multiple platforms
- Evaluates source relevance and accessibility
- Returns structured source catalogs

**Platforms searched**:
- GitHub Issues & Discussions
- Twitter/X
- Reddit
- Hacker News
- News sites
- Blogs (Medium, Dev.to)
- Review sites (G2, Capterra)

### Sentiment Analyzer

**Mode**: `sentiment-analyzer`

Collects and scores sentiment from sources.

**Responsibilities**:
- Visits each source and extracts content
- Scores sentiment (polarity, magnitude, confidence)
- Identifies themes and topics
- Captures representative quotes
- Handles rate limiting gracefully

**Scoring methodology**:
- **Polarity**: Positive (+0.3 to +1.0), Neutral (-0.3 to +0.3), Negative (-1.0 to -0.3)
- **Magnitude**: Intensity of sentiment (0.0 to 1.0)
- **Confidence**: Certainty of classification (0.0 to 1.0)

### Trend Analyst

**Mode**: `sentiment-trend-analyst`

Analyzes patterns and generates causal insights.

**Responsibilities**:
- Compares current session to historical data
- Identifies trends (improving, stable, declining)
- Generates causal hypotheses
- Updates long-term memory
- Creates actionable recommendations

## Workflow Phases

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 0: INTAKE                                            │
│  → Validate product info, create session                    │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: DISCOVERY (if no sources provided)               │
│  → Search platforms, evaluate relevance                     │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: COLLECTION                                        │
│  → Visit sources, extract items, score sentiment            │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: TRENDING                                          │
│  → Analyze patterns, generate hypotheses, update LTM        │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: INSIGHTS                                          │
│  → Generate summary with recommendations                    │
└─────────────────────────────────────────────────────────────┘
```

## Memory Architecture

### Short-Term Memory (STM)

Session-specific data stored in `.sentiment-memory/runs/{session-id}/`:

| File | Purpose |
|------|---------|
| `session.json` | Session state and metrics |
| `product.json` | Product information |
| `sources.json` | Discovered/provided sources |
| `sentiment-items/*.json` | Individual sentiment items |
| `aggregated-sentiment.json` | Session summary statistics |
| `trend-report.md` | Trend analysis results |
| `summary.md` | Final insights document |

### Long-Term Memory (LTM)

Persistent cross-session data in `.sentiment-memory/ltm/`:

| File | Purpose |
|------|---------|
| `products/{slug}/product-profile.json` | Product metadata |
| `products/{slug}/sentiment-history.jsonl` | Sentiment snapshots over time |
| `products/{slug}/trend-history.jsonl` | Trend observations |
| `global/source-catalog.json` | Source effectiveness data |
| `global/theme-taxonomy.json` | Common themes across products |

### Session Pointer

The active session is tracked in `.sentiment-memory/current-session.json`:

```json
{
  "active_session": "2026-01-27-a1b2c3d4",
  "updated_at": "2026-01-27T10:00:00Z"
}
```

## Output Examples

### Summary Report

The final `summary.md` includes:

- **Executive Summary**: 2-3 sentence overview
- **Key Metrics**: Sources, items, overall sentiment
- **Sentiment Distribution**: Positive/neutral/negative breakdown
- **Top Themes**: Recurring topics with sentiment scores
- **Notable Quotes**: Most impactful feedback
- **Trend Analysis**: Historical comparison
- **Recommendations**: Actionable next steps

### Trend Report

The `trend-report.md` includes:

- **Trajectory**: Improving, stable, or declining
- **Delta**: Change from previous session
- **Theme Evolution**: Rising and fading topics
- **Causal Hypotheses**: Possible explanations with confidence levels
- **Historical Context**: Long-term patterns

## Configuration Options

### Product Information

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Product name |
| `description` | No | Brief description |
| `keywords` | No | Search terms (derived from name if not provided) |
| `company` | No | Company name |
| `competitors` | No | Competitor names for comparison |
| `custom_sources` | No | URLs to analyze directly |

### Example with All Options

```markdown
Analyze sentiment for:

Product: Acme Widget Pro
Company: Acme Corporation
Description: Enterprise widget management and automation platform
Keywords: widget, automation, workflow, enterprise
Competitors: WidgetMax, ProWidget, WidgetHub

Custom Sources:
- https://github.com/acme/widget-pro/issues
- https://g2.com/products/acme-widget-pro/reviews
```

## Session Recovery

If a session is interrupted, the orchestrator offers recovery options:

1. **Resume**: Continue from last completed phase
2. **Restart**: Archive current session, start fresh
3. **New Session**: Start with new product/parameters

Recovery state is preserved in `session.json` with checkpoint information.

## Error Handling

### Source Failures

- Individual source failures don't stop the analysis
- Failed sources are logged with error details
- Summary indicates partial data where applicable

### Rate Limiting

- Automatic 2-3 second delays between requests
- Browser timeouts are retried once
- Rate limit encounters are logged

### Data Quality

- Low-quality sources are flagged but included
- Confidence scores indicate classification certainty
- Partial results are clearly labeled

## Best Practices

### For Best Results

1. **Provide keywords**: More specific keywords yield better source discovery
2. **Include company name**: Helps distinguish from similar product names
3. **List competitors**: Enables comparative analysis
4. **Run regularly**: Build trend history for better insights

### Source Quality

- Public sources only (no authenticated APIs in MVP)
- Recent activity (past 90 days) preferred
- Mix of platforms for balanced perspective

### Trend Analysis

- Run at consistent intervals (weekly/monthly)
- Preserve `.sentiment-memory/ltm/` between sessions
- Compare against significant product events

## Troubleshooting

### No Sources Found

- Verify product name is publicly known
- Provide more specific keywords
- Add custom sources manually

### Low Item Count

- Add more diverse sources
- Expand search keywords
- Check if product has limited public discussion

### Trend Analysis Shows "Baseline"

- This is normal for first analysis
- Future sessions will enable comparison
- Preserve LTM for historical tracking

## File Structure

```
agent-packs/customer-sentiment-analysis/
├── .roomodes                    # Agent mode definitions
├── README.md                    # Quick start guide
└── .roo/
    ├── rules-sentiment-orchestrator/
    │   └── rules.md             # Orchestrator rules
    ├── rules-sentiment-source-discovery/
    │   └── rules.md             # Discovery rules
    ├── rules-sentiment-analyzer/
    │   └── rules.md             # Analyzer rules
    └── rules-sentiment-trend-analyst/
        └── rules.md             # Trend analyst rules
```

## Requirements

- **Browser Tool**: Required for source discovery and content collection
- **File Access**: Read/edit permissions for memory directories
- **MCP Tools**: Optional, used by orchestrator for enhanced coordination

## Limitations

- Public sources only (no API authentication)
- Browser-based collection (subject to rate limits)
- File-based memory (scales for typical use < 1000 sessions)
- English language focus (multilingual support not implemented)

## Contributing

This pack is part of the agent-packs repository. See the main repository README for contribution guidelines.

## License

MIT License - See repository LICENSE file.
