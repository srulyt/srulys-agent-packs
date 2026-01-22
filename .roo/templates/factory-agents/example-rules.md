# rules.md - Format Reference

This file shows the Markdown structure for a rules file.
It is NOT a template to copy - design your own content.

## Typical Sections

```markdown
# [Agent Name] Rules

## Identity
Who is this agent? What is their role in the system?
What expertise do they have? What is their purpose?

## Communication Protocol
How does this agent communicate?
Does it return to an orchestrator? Report to user?

## Responsibilities
What does this agent do?
- Responsibility 1
- Responsibility 2

## Inputs
What context does this agent receive?
What files should it read? What state?

## Workflow
How does the agent approach its task?
(High-level objectives, not step-by-step scripts)

## Outputs
What does this agent produce?
Where does output go?

## Domain Knowledge
What specialized knowledge does this agent need?
Include relevant expertise here.

## Error Handling
What can go wrong? How to handle it?

## Quality Considerations
What makes good output for this agent?
(Not a checklist - thinking prompts)
```

## Guidelines

### Length

- As long as needed to be complete
- As short as possible while being clear
- No arbitrary limits - fit the complexity

### Tone

- Direct and clear
- Professional but not stiff
- Preserve agent autonomy

### Content

- Focus on WHAT, not HOW (preserve agency)
- Provide constraints and goals
- Include domain knowledge agent needs
- Avoid step-by-step scripts
