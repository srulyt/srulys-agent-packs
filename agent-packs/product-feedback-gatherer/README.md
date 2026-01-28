# Product Feedback Gatherer

A multi-agent system for gathering actionable product feedback from public online sources, synthesizing findings into quantified reports with highlights/lowlights, and tracking long-term trends.

## Quick Start

### 1. Installation

Copy this pack to your project:

```bash
# Clone or copy the pack directory
cp -r agent-packs/product-feedback-gatherer /path/to/your/project/
```

Or use the agent-packs installer if available.

### 2. Usage

Activate the **🎯 Feedback Orchestrator** mode and provide product information:

```
Analyze feedback for "Notion"

Product: Notion
Description: All-in-one workspace for notes, docs, and collaboration
Company: Notion Labs
Keywords: productivity, notes, collaboration, wiki
```

The orchestrator will automatically:
1. **Discover** sources (Reddit, Twitter, G2, blogs, forums)
2. **Collect** feedback items with quality scoring
3. **Synthesize** insights with trend analysis
4. **Generate** a summary report with recommendations

### 3. Custom Sources

Optionally provide specific sources to analyze:

```
Analyze feedback for "Notion" using these sources:
- https://www.g2.com/products/notion/reviews
- https://reddit.com/r/Notion
- https://twitter.com/search?q=notion
```

### 4. Configuration

Override default thresholds:

```
Analyze feedback for "Notion" with:
- Minimum 30 feedback items
- Maximum 10 sources
- Only last 180 days
```

## Agents

| Agent | Role | Tools |
|-------|------|-------|
| 🎯 Feedback Orchestrator | Coordinates workflow, generates summary | read, edit |
| 🔍 Source Scout | Discovers relevant sources | read, edit, browser |
| 📊 Feedback Collector | Extracts and scores feedback | read, edit, browser |
| 📈 Insight Synthesizer | Analyzes patterns, manages LTM | read, edit |

## Output

The pack generates:

- **Summary Report** (`summary.md`) - Executive summary with highlights/lowlights
- **Synthesis Report** (`synthesis-report.md`) - Detailed theme analysis
- **Feedback Items** (`feedback-items/*.json`) - Individual scored items
- **Aggregated Data** (`aggregated-feedback.json`) - Session metrics

## Memory System

- **STM** (`.feedback-stm/`) - Session-specific data
- **LTM** (`.feedback-ltm/`) - Long-term trend tracking across sessions

Both directories are gitignored by default.

## Documentation

See [docs/product-feedback-gatherer.md](../../docs/product-feedback-gatherer.md) for complete documentation.
