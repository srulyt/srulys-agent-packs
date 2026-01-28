# Product Feedback Gatherer

A multi-agent system for gathering actionable product feedback from public online sources, synthesizing findings into quantified reports with highlights/lowlights, and tracking long-term trends.

## Overview

The Product Feedback Gatherer automates the process of collecting and analyzing product feedback from various online platforms. It provides:

- **Multi-Source Collection**: Searches blogs, Reddit, Twitter/X, forums, podcasts, and feedback sites
- **Quality Scoring**: Each feedback item is scored on sentiment, confidence, credibility, and overall quality
- **Highlight/Lowlight Synthesis**: Groups positive and negative feedback into actionable categories
- **Trend Tracking**: Long-term memory tracks issues and sentiment trends across sessions
- **Actionable Output**: Quantified insights with recommendations

## Use Cases

- Monitor product perception across social platforms
- Track customer satisfaction trends over time
- Identify recurring issues before they escalate
- Gather competitive intelligence from public sources
- Prepare for product roadmap decisions with data

## Agent Roster

### 🎯 Feedback Orchestrator (`feedback-orchestrator`)

**Role**: Central coordinator managing the feedback gathering lifecycle

**Responsibilities**:
- Accept product info and optional configuration from user
- Initialize session with STM
- Route through discovery → collection → synthesis phases
- Generate final summary report
- Handle errors and recovery gracefully

**Reports To**: User

### 🔍 Source Scout (`feedback-source-scout`)

**Role**: Discovers relevant public sources for product feedback

**Responsibilities**:
- Search for product-related discussions across platforms
- Identify high-value sources (active discussions, recent feedback)
- Evaluate source relevance and accessibility
- Return structured source list, not content

**Reports To**: Feedback Orchestrator

### 📊 Feedback Collector (`feedback-collector`)

**Role**: Collects and scores individual feedback items

**Responsibilities**:
- Visit each source and extract feedback items
- Score each item on sentiment, confidence, credibility, quality
- Classify as highlight (positive) or lowlight (negative)
- Capture key quotes and context

**Reports To**: Feedback Orchestrator

### 📈 Insight Synthesizer (`feedback-synthesizer`)

**Role**: Analyzes collected feedback and manages LTM

**Responsibilities**:
- Analyze patterns across all collected feedback
- Generate highlight/lowlight groupings
- Identify recurring themes and issues
- Compare against LTM for trend detection
- Update LTM with new findings

**Reports To**: Feedback Orchestrator

## Orchestration Flow

```
                    ┌─────────────────────┐
                    │        User         │
                    └──────────┬──────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │   🎯 Feedback Orchestrator   │
                │   Phase 0: Intake            │
                └──────────────┬───────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────────┐  ┌──────────────────────┐
│ 🔍 Source Scout │  │ 📊 Feedback Collector│  │ 📈 Insight Synthesizer│
│  Phase 1        │  │    Phase 2          │  │      Phase 3          │
└────────┬────────┘  └──────────┬──────────┘  └───────────┬───────────┘
         │                      │                         │
         ▼                      ▼                         ▼
    sources.json          feedback-items/          synthesis-report.md
                       aggregated-feedback.json      + LTM updates
                               │
                               ▼
                ┌──────────────────────────────┐
                │   🎯 Feedback Orchestrator   │
                │   Phase 4: Summary           │
                └──────────────┬───────────────┘
                               │
                               ▼
                          summary.md
```

## Workflow Phases

### Phase 0: Intake

The orchestrator receives product information and initializes the session:

- Generates session ID (format: `YYYY-MM-DD-{8-char-hex}`)
- Creates STM directory structure
- Parses configuration (thresholds, filters, output options)
- Determines if custom sources are provided

### Phase 1: Discovery

Source Scout searches for relevant sources:

- Platform types: blogs, Reddit, Twitter/X, forums, feedback sites, podcasts
- Evaluates relevance, recency, and estimated feedback volume
- Returns structured source list

### Phase 2: Collection

Feedback Collector visits each source:

- Extracts individual feedback items
- Applies quality scoring methodology
- Classifies as highlight/lowlight/neutral
- Aggregates into session summary

### Phase 3: Synthesis

Insight Synthesizer analyzes patterns:

- Groups themes across sources
- Compares to historical LTM data
- Identifies trends and recurring issues
- Updates LTM with new findings

### Phase 4: Summary

Orchestrator generates final output:

- Executive summary
- Key metrics table
- Highlight/lowlight tables
- Trend analysis
- Actionable recommendations

## Quality Scoring Methodology

### Sentiment Score (-1.0 to +1.0)

| Range | Classification |
|-------|----------------|
| +0.5 to +1.0 | Strong Positive |
| +0.1 to +0.5 | Mild Positive |
| -0.1 to +0.1 | Neutral |
| -0.5 to -0.1 | Mild Negative |
| -1.0 to -0.5 | Strong Negative |

### Confidence Level (0.0 to 1.0)

How certain the scoring is about the sentiment assessment.

### Source Credibility (0.0 to 1.0)

Weighted formula:
```
credibility = (platform * 0.30) + (author * 0.20) + (engagement * 0.20) +
              (recency * 0.15) + (detail * 0.15)
```

### Feedback Quality Score (0.0 to 1.0)

Overall actionability:
```
quality = (|sentiment| * 0.20) + (confidence * 0.30) + (credibility * 0.30) +
          (actionability * 0.20)
```

### Classification

- **Highlights**: Sentiment > +0.3 AND Quality > 0.4
- **Lowlights**: Sentiment < -0.3 AND Quality > 0.4
- **Neutral**: Everything else

## Memory System

### Short-Term Memory (STM)

Location: `.feedback-stm/`

Stores session-specific data:
- Session state and configuration
- Product information
- Discovered sources
- Collected feedback items
- Synthesis report
- Final summary

### Long-Term Memory (LTM)

Location: `.feedback-ltm/`

Tracks data across sessions:
- Product metadata
- Session history (append-only JSONL)
- Tracked issues
- Trend history
- Theme evolution

## Installation

### Copy to Project

```bash
cp -r agent-packs/product-feedback-gatherer /path/to/your/project/
```

### Using Installer

```bash
npx agent-packs install product-feedback-gatherer
```

### Add to Gitignore

Add these entries to your project's `.gitignore`:

```gitignore
# Product Feedback Gatherer - session and history data
.feedback-stm/
.feedback-ltm/
```

## Usage

### Basic Usage

Activate **🎯 Feedback Orchestrator** and provide product info:

```
Gather feedback for "Slack"
```

### With Description

```
Analyze feedback for:
- Product: Slack
- Description: Team messaging and collaboration platform
- Company: Salesforce
- Keywords: messaging, collaboration, teams, chat
```

### With Custom Sources

```
Analyze feedback for "Slack" using these sources:
- https://www.g2.com/products/slack/reviews
- https://reddit.com/r/Slack
- https://www.capterra.com/p/135003/Slack/reviews/
```

### With Configuration

```
Gather feedback for "Slack" with:
- Minimum 50 feedback items
- Maximum 20 sources  
- Only last 90 days
- Minimum quality score 0.5
```

## Output Files

### Session Files (STM)

| File | Description |
|------|-------------|
| `session.json` | Session state and phase |
| `config.json` | Configuration with defaults |
| `product.json` | Product information |
| `sources.json` | Discovered sources |
| `feedback-items/*.json` | Individual scored items |
| `aggregated-feedback.json` | Session aggregation |
| `synthesis-report.md` | Theme analysis |
| `summary.md` | Final executive report |

### History Files (LTM)

| File | Description |
|------|-------------|
| `product-meta.json` | Product identification |
| `session-history.jsonl` | All sessions (append-only) |
| `issues/*.json` | Tracked recurring issues |
| `trend-history.jsonl` | Trend data points |
| `theme-evolution.jsonl` | Theme tracking |

## Configuration Defaults

```json
{
  "thresholds": {
    "min_feedback_items": 20,
    "max_feedback_items": 100,
    "min_sources": 3,
    "max_sources": 15
  },
  "filters": {
    "min_quality_score": 0.3,
    "recency_days": 365,
    "platforms": ["all"]
  },
  "output": {
    "include_raw_quotes": true,
    "include_source_urls": true,
    "max_highlights": 10,
    "max_lowlights": 10
  }
}
```

## Pack Structure

```
agent-packs/product-feedback-gatherer/
├── .roomodes                                    # Mode definitions
├── README.md                                    # Quick start guide
└── .roo/
    ├── rules-feedback-orchestrator/
    │   └── rules.md                             # Orchestrator behavior
    ├── rules-feedback-source-scout/
    │   └── rules.md                             # Source discovery rules
    ├── rules-feedback-collector/
    │   └── rules.md                             # Collection & scoring rules
    └── rules-feedback-synthesizer/
        └── rules.md                             # Synthesis & LTM rules
```

## Error Handling

The pack handles errors gracefully:

| Phase | Error Type | Recovery |
|-------|------------|----------|
| Discovery | No sources found | Prompt for manual sources |
| Discovery | Platform failed | Continue with remaining platforms |
| Collection | Source inaccessible | Skip source, continue |
| Collection | Below threshold | Warn, offer to continue |
| Synthesis | LTM read failure | Continue without historical context |
| Synthesis | LTM write failure | Log error, complete session |

## Limitations

- Requires browser tool for web access
- Only analyzes publicly accessible sources
- Cannot access content behind authentication
- Quality scoring is heuristic-based

## Related Packs

- **Customer Sentiment Analysis**: Similar pattern, focused on general sentiment
- **SaaS Design Studio**: Example of orchestrator pattern with STM
