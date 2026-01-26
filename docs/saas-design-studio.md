# SaaS Design Studio

A multi-agent system for high-fidelity UI/UX engineering with React, Tailwind CSS, and Shadcn/UI.

## Overview

**Pack Name:** `saas-design-studio`  
**Agent Count:** 4  
**Architecture Pattern:** Orchestrator + Specialists with Quality Loop  
**Version:** 2.0

SaaS Design Studio enforces visual consistency through strict separation between Design System Definition and Component Implementation. The system produces polished, production-ready UI components with:

- Zero arbitrary pixel values
- Full design token compliance
- Accessibility checks (WCAG AA)
- Iterative quality refinement
- **Consolidated output** for easy integration
- **HTML preview** for visual verification
- **Deliverables manifest** with integration instructions

## When to Use This Pack

✅ **Good for:**
- Building consistent UI components in React/Tailwind projects
- Enforcing design system compliance
- Teams wanting AI-assisted component generation
- Projects using Shadcn/UI

❌ **Not for:**
- Non-React projects
- Projects not using Tailwind CSS
- One-off prototypes where consistency doesn't matter

## Installation

```bash
npx agent-packs install saas-design-studio
```

Or manually copy the `agent-packs/saas-design-studio/` directory to your project.

## Agents

### 🎨 Design Director (`design-director`)

**Role:** Orchestrator - Project Manager & Visual Strategist

The Design Director is the entry point for all UI requests. It:
- Analyzes user requests and determines the visual "Vibe"
- Establishes feature naming for consolidated output
- Creates structured Design Briefs
- Coordinates the token → component → review → finalization pipeline
- Handles quality loops when components don't meet threshold
- Generates deliverables manifest in Phase 5

**Trigger:** Use `@design-director` for any UI feature request.

**Vibes:**
| Vibe | Characteristics | Use Case |
|------|-----------------|----------|
| Professional | Neutral, trust-building | B2B apps, dashboards |
| Playful | Vibrant, engaging | Consumer products |
| Data-Dense | Compact, scannable | Analytics, admin panels |
| Minimal | Content-first, whitespace | Blogs, documentation |

### 🛠️ Systems Architect (`systems-architect`)

**Role:** Design Token Manager & CSS Specialist

The Systems Architect builds the foundation—the design tokens that all components consume. It:
- Generates `globals.css` with CSS custom properties
- Configures `tailwind.config.ts` theme extensions
- Writes all tokens to `.design-studio/output/{feature}/tokens/`
- Never creates components—only the rules for components

**Key Outputs:**
- `.design-studio/output/{feature}/tokens/globals.css`
- `.design-studio/output/{feature}/tokens/tailwind.config.ts`

### 🔧 Component Foundry (`component-foundry`)

**Role:** React/Tailwind Engineer

The Component Foundry is the builder. It transforms Design Briefs and tokens into working React components. Key responsibilities:

**The Absolute Rule: No Arbitrary Values**
```tsx
// ❌ FORBIDDEN
className="w-[350px]"
style={{ marginTop: 12 }}

// ✅ CORRECT
className="w-full max-w-sm"
className="mt-3"
```

**Key Outputs:**
- `.design-studio/output/{feature}/components/*.tsx`
- `.design-studio/output/{feature}/components/index.ts` (barrel export)
- `.design-studio/output/{feature}/preview.html` (Phase 5)

**Patterns Used:**
- Shadcn/UI components as primitives
- Tailwind utility classes exclusively
- CSS variable references via theme

### 🔍 Visual Linter (`visual-linter`)

**Role:** Senior Product Designer & Accessibility Auditor

The Visual Linter is the quality gate. It reviews every component before it reaches the user, checking:

1. **Token Compliance** (40%) - No arbitrary values
2. **Contrast Ratios** (25%) - WCAG AA compliance
3. **Spacing Consistency** (20%) - Uniform rhythm
4. **Visual Hierarchy** (15%) - Clear importance levels

**Scoring:**
- Score ≥ 9/10: Approved for production
- Score < 9/10: Returns to Foundry with specific fixes

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ USER: "I need a settings page with profile and billing"     │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: BRIEF                                              │
│ → Determine feature name: settings-page                     │
│ → Determine Vibe: Professional                              │
│ → Create Brief: .design-studio/briefs/settings-page.md      │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: TOKENS                                             │
│ → Delegate to Systems Architect                             │
│ → Output: .design-studio/output/settings-page/tokens/       │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: BUILD                                              │
│ → Delegate to Component Foundry                             │
│ → Output: .design-studio/output/settings-page/components/   │
│ → Includes index.ts barrel export                           │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: REVIEW                                             │
│ → Delegate to Visual Linter                                 │
│ → Score: 7/10 → NEEDS_REVISION → Loop to Phase 3            │
│ → Score: 9/10 → APPROVED → Proceed to Phase 5               │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: FINALIZATION  🆕                                   │
│ → Delegate to Foundry for preview.html                      │
│ → Director generates deliverables.md                        │
│ → Return consolidated output to user                        │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

### Pack Files
```
agent-packs/saas-design-studio/
├── .roomodes                           # Agent definitions
├── README.md                           # Quick start
└── .roo/
    ├── rules-design-director/
    │   └── rules.md                    # Orchestrator protocol
    ├── rules-systems-architect/
    │   └── rules.md                    # Token generation rules
    ├── rules-component-foundry/
    │   └── rules.md                    # Component building rules
    └── rules-visual-linter/
        └── rules.md                    # Critique protocol
```

### Target Project Files (Created During Use)
```
your-project/
├── .design-studio/
│   ├── briefs/                         # Design briefs
│   │   └── {feature-name}.md
│   ├── state/
│   │   └── current-workflow.md         # Active workflow
│   └── output/                         # ✨ ALL USER DELIVERABLES
│       └── {feature-name}/
│           ├── components/             # React components
│           │   ├── ProfileCard.tsx
│           │   ├── BillingSection.tsx
│           │   └── index.ts            # Barrel export
│           ├── tokens/                 # Design tokens
│           │   ├── globals.css         # CSS custom properties
│           │   └── tailwind.config.ts  # Tailwind theme
│           ├── preview.html            # Browser preview
│           └── deliverables.md         # Integration instructions
```

## New Capabilities (v2.0)

### Consolidated Output

All deliverables for a feature are now generated to a single directory:
```
.design-studio/output/{feature-name}/
```

This enables:
- Easy copying to your project
- Self-contained feature packages
- Clear separation between features

### Deliverables Manifest

Every completed feature includes a `deliverables.md` with:
- Complete file inventory
- Per-file integration instructions
- Copy-paste code examples
- Quick start guide

### HTML Preview

Every completed feature includes a `preview.html` that:
- Works in any browser (no React setup needed)
- Uses Tailwind CDN
- Inlines all design tokens
- Shows static representations of all components

**Limitations:**
- Interactive behavior not demonstrated
- React state shown with static mock data
- Represents visual appearance only

### Barrel Exports

Components are exported via `index.ts`:
```tsx
// Clean imports
import { ProfileCard, BillingSection } from './components';

// Instead of individual imports
import { ProfileCard } from './components/ProfileCard';
import { BillingSection } from './components/BillingSection';
```

## Design Brief Format

```markdown
# Design Brief: Settings Page

## Metadata
- Created: 2026-01-26T20:00:00Z
- Feature: settings-page
- Vibe: Professional
- Status: approved

## User Persona
SaaS power user, 25-45, manages team settings daily

## Emotional Goal
Confident and in control—settings should feel safe to change

## Views Required
1. Profile Section - Avatar, name, email editing
2. Billing Section - Current plan, usage, upgrade CTA

## Key Interactions
- Inline editing for profile fields
- Plan comparison modal for upgrades

## Visual Hierarchy
- Primary: Save buttons, current plan badge
- Secondary: Form labels, usage stats
- Tertiary: Help text, timestamps
```

## Token System

### CSS Custom Properties

```css
:root {
  /* Core Colors */
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96.1%;
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --accent: 210 40% 96.1%;
  --destructive: 0 84.2% 60.2%;
  --border: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;
  
  /* Typography */
  --font-sans: ui-sans-serif, system-ui, sans-serif;
  --font-mono: ui-monospace, monospace;
  
  /* Spacing */
  --radius: 0.5rem;
}
```

### Tailwind Configuration

```typescript
theme: {
  extend: {
    colors: {
      background: "hsl(var(--background))",
      foreground: "hsl(var(--foreground))",
      primary: {
        DEFAULT: "hsl(var(--primary))",
        foreground: "hsl(var(--primary-foreground))",
      },
      // ... etc
    },
    borderRadius: {
      lg: "var(--radius)",
      md: "calc(var(--radius) - 2px)",
      sm: "calc(var(--radius) - 4px)",
    },
  },
}
```

## Quality Criteria

### Token Compliance
Every value must come from:
- Tailwind's default scale (`p-4`, `text-lg`)
- CSS custom properties (`bg-primary`, `text-muted-foreground`)
- Responsive/state modifiers (`hover:bg-accent`, `md:flex`)

### Contrast Ratios (WCAG AA)
| Content Type | Minimum Ratio |
|--------------|---------------|
| Normal text (<18px) | 4.5:1 |
| Large text (≥18px or 14px bold) | 3:1 |
| UI components | 3:1 |

### Linear-Style Checklist
- [ ] Borders are visible and high-contrast
- [ ] Backgrounds use subtle layering
- [ ] No decorative shadows (max `shadow-sm`)
- [ ] Typography has clear weight hierarchy
- [ ] Spacing is generous but not excessive
- [ ] Interactions are subtle

## Example Usage

### Request
```
@design-director I need a user profile card that shows avatar, 
name, email, and role badge. Include an edit button.
```

### Output Structure
```
.design-studio/output/user-profile/
├── components/
│   ├── ProfileCard.tsx
│   └── index.ts
├── tokens/
│   ├── globals.css
│   └── tailwind.config.ts
├── preview.html
└── deliverables.md
```

### Example Component
```tsx
// .design-studio/output/user-profile/components/ProfileCard.tsx
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Pencil } from "lucide-react"

interface ProfileCardProps {
  user: {
    name: string
    email: string
    role: string
    avatarUrl?: string
  }
  onEdit?: () => void
}

export function ProfileCard({ user, onEdit }: ProfileCardProps) {
  return (
    <Card className="w-full max-w-sm border border-border">
      <CardHeader className="flex flex-row items-center gap-4 pb-2">
        <Avatar className="h-12 w-12">
          <AvatarImage src={user.avatarUrl} alt={user.name} />
          <AvatarFallback className="bg-muted text-muted-foreground">
            {user.name.slice(0, 2).toUpperCase()}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1 space-y-1">
          <h3 className="text-lg font-semibold text-foreground">
            {user.name}
          </h3>
          <p className="text-sm text-muted-foreground">{user.email}</p>
        </div>
        <Button variant="ghost" size="icon" onClick={onEdit}>
          <Pencil className="h-4 w-4" />
          <span className="sr-only">Edit profile</span>
        </Button>
      </CardHeader>
      <CardContent>
        <Badge variant="secondary">{user.role}</Badge>
      </CardContent>
    </Card>
  )
}
```

## Integration Guide

After generation completes:

### 1. Preview the Output
Open `preview.html` in your browser to verify the design.

### 2. Read the Manifest
Check `deliverables.md` for detailed integration instructions.

### 3. Copy to Your Project
```bash
cp -r .design-studio/output/settings-page/ ./src/features/settings/
```

### 4. Add CSS Tokens
```css
/* In your root CSS file */
@import './features/settings/tokens/globals.css';
```

### 5. Merge Tailwind Config
```typescript
// tailwind.config.ts
import settingsTokens from './src/features/settings/tokens/tailwind.config';

export default {
  // ... your config
  theme: {
    extend: {
      ...settingsTokens.theme.extend,
      // Your other extensions
    }
  }
}
```

### 6. Import Components
```tsx
import { ProfileCard, BillingSection } from './features/settings/components';
```

## Troubleshooting

### "Arbitrary value detected"
The Linter found something like `w-[350px]`. Fix by using:
- `max-w-sm` (384px) or `max-w-xs` (320px)
- Standard Tailwind spacing scale

### "Contrast ratio too low"
Text color doesn't have enough contrast with background. Fix by:
- Using `text-foreground` instead of `text-muted-foreground` on dark backgrounds
- Checking token pairs are designed for sufficient contrast

### "Loop cap reached"
After 3 iterations, components still don't meet quality threshold. This usually means:
- Design Brief is too ambitious for current tokens
- Need manual review of requirements

### "Preview doesn't match React"
The HTML preview is a static representation. For accurate behavior:
- Build and run your React project
- Preview is for visual design verification only

## Limitations

1. **React Only** - No Vue, Angular, or other framework support
2. **Tailwind Required** - Cannot generate plain CSS or styled-components
3. **Shadcn Patterns** - Assumes Shadcn/UI is installed
4. **English Only** - Design Briefs and communication in English
5. **Static Preview** - HTML preview doesn't show React interactivity

## Migration from v1.0

If you used the previous version:

| v1.0 Location | v2.0 Location |
|---------------|---------------|
| `src/globals.css` | `.design-studio/output/{feature}/tokens/globals.css` |
| `tailwind.config.ts` | `.design-studio/output/{feature}/tokens/tailwind.config.ts` |
| `src/components/{feature}/` | `.design-studio/output/{feature}/components/` |

**Note:** Previous files remain in place. New features use the consolidated output structure.

## Support

For issues with this pack, check:
1. Agent rules in `.roo/rules-{agent}/rules.md`
2. Design Brief format in `.design-studio/briefs/`
3. Token configuration in `.design-studio/output/{feature}/tokens/`
4. Generated manifest in `.design-studio/output/{feature}/deliverables.md`
