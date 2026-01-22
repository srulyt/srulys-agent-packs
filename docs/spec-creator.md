# Spec Creator Pack

> AI-powered product specification writing team for Microsoft Fabric

## Overview

The Spec Creator pack is a multi-agent system designed to produce comprehensive, high-quality product specifications for Microsoft Fabric. It transforms raw inputs (product briefs, strategy documents, customer feedback) into polished, professional specifications ready for stakeholder approval and engineering implementation.

## Location

`agent-packs/spec-creator/`

## Agents

The pack includes 10 specialized agents:

| Slug | Name | Role | Edit Capability |
|------|------|------|-----------------|
| `spec-orchestrator` | 🧭 Spec Orchestrator | Project manager coordinating the spec creation workflow | Markdown files |
| `domain-detective` | 🔍 Domain Detective | Market research, competitive analysis, and business context | Markdown files |
| `requirements-miner` | 📋 Requirements Miner | Functional requirements extraction and prioritization | Markdown files |
| `spec-formatter` | 🎨 Spec Formatter | Document formatting and consolidation | Markdown files |
| `nfr-quality-guru` | 🛡️ NFR & Quality Guru | Non-functional requirements (performance, security, scalability) | Markdown files |
| `test-sage` | 🧪 Test Sage | Acceptance criteria and test scenarios | Markdown files |
| `metrics-master` | 📊 Metrics Master | Success metrics and KPIs | Markdown files |
| `best-practices-buddy` | 🧠 Best Practices Buddy | Quality advisory and standards alignment | Read-only |
| `spec-reviewer` | 🔬 Spec Reviewer | Final QA gatekeeper before approval | Read-only |
| `researcher` | 🔬 Researcher | Web research support for gathering external context | Markdown files |

### Agent Details

#### 🧭 Spec Orchestrator

The project manager that coordinates all other agents. It:
- Determines the appropriate workflow (Autonomous or Helper mode)
- Delegates tasks to specialist agents
- Tracks progress and ensures quality gates are met
- Consolidates outputs into the final specification

#### 🔍 Domain Detective

Specialized research and business context analyst that:
- Analyzes product one-pagers, strategy documents, and business briefs
- Researches competitive landscape and market trends
- Develops problem statements and target audience definitions
- Creates the Background & Market Analysis section

#### 📋 Requirements Miner

Requirements engineer that:
- Extracts requirements from structured and unstructured sources
- Clarifies vague requests into specific, implementable requirements
- Prioritizes requirements (P0/P1/P2)
- Maintains traceability to user needs

#### 🎨 Spec Formatter

Documentation specialist that:
- Applies consistent formatting and structure
- Enforces Microsoft writing style guidelines
- Consolidates content from all agents into final spec
- Optimizes for both human readability and AI parsing

#### 🛡️ NFR & Quality Guru

Quality attributes specialist that:
- Defines feature-specific non-functional requirements
- Focuses on performance, security, scalability, and compliance
- Excludes baseline requirements covered by standard checkpoints
- Recommends quality assurance approaches

#### 🧪 Test Sage

Quality assurance expert that:
- Creates testable acceptance criteria for each requirement
- Designs test scenarios covering happy path and edge cases
- Defines validation strategies (unit, integration, E2E, performance)
- Maintains requirement coverage visibility

#### 📊 Metrics Master

Success metrics specialist that:
- Defines SMART metrics aligned with business goals
- Creates balanced scorecard of adoption, engagement, performance, and satisfaction metrics
- Specifies measurement methods and data sources
- Establishes success criteria and thresholds

#### 🧠 Best Practices Buddy

Quality advisor (read-only) that:
- Reviews specifications against quality checklists
- Recommends industry and Microsoft best practices
- Shares lessons learned from past specifications
- Ensures alignment with Microsoft SDL and Fabric standards

#### 🔬 Spec Reviewer

Final quality gatekeeper (read-only) that:
- Conducts comprehensive end-to-end reviews
- Verifies compliance with security, privacy, and accessibility standards
- Identifies blocking issues vs. minor improvements
- Provides approval recommendation (Approve/Revise/Reject)

#### 🔬 Researcher

General purpose web researcher that:
- Searches for relevant external information
- Gathers context from blogs, documentation, and news
- Supports other agents when additional context is needed
- Summarizes findings in clear, actionable format

## Workflow Modes

### Autonomous Mode

For creating new specifications from scratch:

1. **Domain Detective** gathers market context and background
2. **Requirements Miner** extracts and prioritizes requirements
3. **NFR & Quality Guru** defines quality attributes
4. **Test Sage** creates acceptance criteria
5. **Metrics Master** defines success metrics
6. **Spec Formatter** consolidates into final document
7. **Best Practices Buddy** provides improvement suggestions
8. **Spec Reviewer** conducts final quality review

### Helper Mode

For updating or extending existing specifications:

1. Orchestrator identifies which agents are needed
2. Only relevant agents are engaged
3. Spec Formatter updates the existing document
4. Spec Reviewer validates changes

## Included Resources

### Templates

- **Specification Template** (`.roo/templates/specification-template.md`): Canonical template for all specifications

### Skills

- **Synthesis Index Guide** (`.roo/rules/synthesis-index-guide.md`): Guidelines for agent output formatting to prevent context overflow

### Shared Rules

- **Research Agent** (`.roo/rules/research-agent.md`): Instructions for invoking the researcher agent

## Installation

### Option 1: Copy to Target Project

```bash
# Copy the entire pack to your project
cp -r agent-packs/spec-creator/ /path/to/your/project/
```

### Option 2: Open Pack Directly

Open `agent-packs/spec-creator/` directly in VS Code with Roo extension enabled.

## Usage

### Creating a New Specification

1. Activate the **🧭 Spec Orchestrator** mode
2. Provide your input:
   - Product brief, one-pager, or strategy document
   - Customer feedback or requirements documents
   - Any relevant context about the feature
3. The orchestrator will coordinate all agents to produce a complete specification

### Example Prompt

```
Create a specification for a new Data Lineage Visualization feature in Microsoft Fabric.

Context:
- Target users: Data engineers and analysts
- Goal: Help users understand data flow and dependencies
- Key requirements: Visual graph, search, filtering, export

Please review the attached product brief: [paste or reference document]
```

### Updating an Existing Specification

1. Activate the **🧭 Spec Orchestrator** mode
2. Reference the existing specification file
3. Describe the changes or additions needed
4. The orchestrator will engage only the relevant agents

## Output

The pack produces a comprehensive specification document including:

- **Executive Summary**: Problem, solution, and impact
- **Background & Market Analysis**: Context, competition, and target audience
- **Goals & Success Metrics**: Measurable outcomes with targets
- **Functional Requirements**: Prioritized requirements with rationale
- **Non-Functional Requirements**: Performance, security, scalability, compliance
- **Acceptance Criteria**: Testable conditions for each requirement
- **Test Scenarios**: End-to-end and edge case test scenarios
- **Dependencies & Assumptions**: External factors and prerequisites
- **Risks & Mitigations**: Identified risks with mitigation strategies

## Microsoft Fabric Focus

This pack is specifically designed for Microsoft Fabric product specifications and includes:

- Integration with OneLake, workspaces, and capacity models
- Alignment with Microsoft SDL (Security Development Lifecycle)
- WCAG 2.1 AA accessibility requirements
- GDPR and privacy compliance considerations
- Power BI and Azure integration patterns

## Best Practices

1. **Provide rich context**: The more input you provide, the better the specification
2. **Review intermediate outputs**: Check agent outputs before final consolidation
3. **Iterate as needed**: Use Helper Mode to refine sections
4. **Include stakeholder feedback**: Feed reviewer comments back into the process

## Related Documentation

- [Factory Pack](./factory.md) - The multi-agent factory that created this pack
- [Agentic Developer Pack](./agentic-developer.md) - Workflow-first development system
