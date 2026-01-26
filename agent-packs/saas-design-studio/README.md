# SaaS Design Studio

A 4-agent multi-agent system for high-fidelity UI/UX engineering with React, Tailwind CSS, and Shadcn/UI.

## Overview

SaaS Design Studio enforces visual consistency through strict separation between Design System Definition and Component Implementation. It produces polished, production-ready UI components with zero arbitrary pixel values.

**v2.0 Features:**
- 🎯 **Consolidated Output** - All deliverables in `.design-studio/output/{feature}/`
- 📋 **Deliverables Manifest** - Clear instructions for integration
- 👁️ **HTML Preview** - View components without React setup
- 📦 **Barrel Exports** - Clean component imports

## Agents

| Agent | Slug | Role |
|-------|------|------|
| 🎨 Design Director | `design-director` | Orchestrator - manages workflow, creates briefs |
| 🛠️ Systems Architect | `systems-architect` | Token Manager - generates CSS variables, Tailwind config |
| 🔧 Component Foundry | `component-foundry` | Builder - creates React/TSX components |
| 🔍 Visual Linter | `visual-linter` | Critic - audits UI quality, provides fixes |

## Quick Start

1. **Install the pack** using the agent-packs CLI or copy files manually
2. **Switch to Design Director** mode (`@design-director`)
3. **Describe your UI feature** - e.g., "I need a settings page with profile editing and billing info"
4. **Let the pipeline run** - Director coordinates tokens → components → review → finalization

## Technical Stack

- **Framework:** React (TypeScript)
- **Styling:** Tailwind CSS
- **Components:** Shadcn/UI
- **Icons:** Lucide React
- **Aesthetic:** Linear-style minimalism

## Prerequisites

Before using generated components in your project:

### Required Dependencies

```bash
# Tailwind CSS (if not already installed)
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Shadcn/UI initialization
npx shadcn-ui@latest init

# Required Shadcn/UI components (install as needed)
npx shadcn-ui@latest add button card input label dialog badge avatar tabs

# Icons
npm install lucide-react
```

### Shadcn/UI Components Used

The generated components may use these primitives:
- `Button` - Action triggers
- `Card`, `CardHeader`, `CardContent`, `CardFooter` - Container layouts
- `Input`, `Label`, `Textarea` - Form elements
- `Dialog`, `Sheet` - Overlays
- `Badge`, `Avatar` - Display elements
- `Tabs`, `Accordion`, `Separator` - Navigation/organization

### Project Structure Assumptions

Components expect this import path structure:
```tsx
import { Button } from "@/components/ui/button"
```

If your project uses a different path, update imports after copying components.

## Workflow

```
User Request → Director → Architect → Foundry → Linter → [Loop or Finalize]
```

1. **Director** analyzes request, determines "Vibe", creates Design Brief
2. **Architect** generates design tokens → `.design-studio/output/{feature}/tokens/`
3. **Foundry** builds React components → `.design-studio/output/{feature}/components/`
4. **Linter** reviews and scores (1-10 scale)
5. If score < 9/10, loop back to Foundry with fixes
6. **Phase 5 - Finalization**: Generate `preview.html` and `deliverables.md`
7. Return consolidated output to user

## Output Structure

All deliverables are generated to a single location per feature:

```
.design-studio/
├── briefs/                          # Design briefs (reference)
│   └── {feature-name}.md
├── state/                           # Workflow tracking
│   └── current-workflow.md
└── output/                          # ✨ ALL USER DELIVERABLES
    └── {feature-name}/
        ├── components/              # React components
        │   ├── ComponentA.tsx
        │   ├── ComponentB.tsx
        │   └── index.ts             # Barrel export
        ├── tokens/                  # Design tokens
        │   ├── globals.css          # CSS custom properties
        │   └── tailwind.config.ts   # Tailwind theme extension
        ├── preview.html             # Browser-viewable preview
        └── deliverables.md          # Integration instructions
```

## Key Principles

### Token-First Design
All styling comes from design tokens. No arbitrary values like `w-[350px]` or `text-[#hex]`.

### Quality Gate
Every component must score 9/10 or higher on:
- Token compliance
- Contrast ratios (WCAG AA)
- Spacing consistency
- Visual hierarchy

### Boomerang Pattern
Sub-agents always return to Director. No direct user interaction from Architect, Foundry, or Linter.

### Consolidated Output
All generated files go to `.design-studio/output/{feature}/` for easy copying and integration.

## Using the Output

After generation completes:

1. **Preview**: Open `preview.html` in your browser to see components
2. **Read**: Check `deliverables.md` for integration instructions
3. **Copy**: Move the entire `{feature-name}/` folder to your project
4. **Import**:
   ```tsx
   import { ProfileCard, BillingSection } from './components';
   ```
5. **Add tokens**:
   ```css
   @import './tokens/globals.css';
   ```

## Documentation

See [docs/saas-design-studio.md](../../docs/saas-design-studio.md) for complete documentation.
