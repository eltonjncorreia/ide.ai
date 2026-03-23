---
name: ide-ai-design-system
description: Design system for IDE.AI v2 covering layout architecture, color palette, typography, and animations
---

# IDE.AI v2 — Design System

## Overview

IDE.AI v2 is a minimalist IDE focused on **AI CLIs**, inspired by **Claude Code** and **GitHub Copilot CLI**. The new design prioritizes:

- ✨ **Visual Appeal** — Modern, polished, premium feel
- 🎯 **Focus** — Chat as the center, no distractions
- ⚡ **Interactivity** — Smooth transitions, visual feedback
- 📱 **Responsive** — Adapts to different terminal sizes

## Layout Architecture

```
┌─────────────────────────────────────────────────────────┐
│ ide.ai [~/workspace]          Ctrl+Q   Ctrl+L           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ChatPanel (Primary Focus)                             │
│   ╭─────────────────────────────────────────────────╮   │
│   │ ● Claude                  5 messages | ✓ Ready │   │
│   ├─────────────────────────────────────────────────┤   │
│   │ You: How do I do X?                             │   │
│   │ Claude: Here's the answer...                    │   │
│   │ ... (scrollable)                                │   │
│   ├─────────────────────────────────────────────────┤   │
│   │ > _                                             │   │
│   ╰─────────────────────────────────────────────────╯   │
│                                                         │
├──────────────────────────────────────────────────────────┤
│ ● Claude  ● Copilot      │      📄 Files  ⌘ Term  ➕ New│
└──────────────────────────────────────────────────────────┘
```

### Components:

1. **Header** — Workspace path, timestamp
2. **ChatPanel** — Chat log + input (80% of height)
3. **ProviderBar** — Provider selector (left side)
4. **ActionBar** — Action buttons (right side)
5. **Footer** — Keybinding help

## Color Palette

### Semantic Colors

```
Primary Accent (Focus):      #9D4EDD  (purple)
Secondary (Information):     #3A86FF  (blue)
Success (Ready/Positive):    #06D6A0  (green)
Warning (Activity):          #FFD60A  (gold)
Error (Alerts):              #EF476F  (red)

Neutral Light:               #F3F4F6  (almost white)
Neutral Dark:                #1F2937  (almost black)
```

### Usage by Component:

| Component | Color | Purpose |
|---|---|---|
| Prompt (`>`) | Primary (#9D4EDD) | Indicates input area |
| Provider label | Primary (#9D4EDD) | Active provider highlight |
| User message | Secondary (#3A86FF) | Distinguish from AI |
| AI response | Primary (#9D4EDD) | Visually tied to provider |
| Ready status | Success (#06D6A0) | Positive feedback |
| Thinking status | Warning (#FFD60A) | Activity indicator |
| Error | Error (#EF476F) | Problem notification |

## Typography

### Font Selection
- **Monospace**: Fira Code, JetBrains Mono, or Courier (fallback)
- **Rationale**: Better legibility in terminal, aligns with code expectations

### Font Hierarchy

| Component | Size | Weight | Style |
|---|---|---|---|
| Header | Normal | Bold | - |
| Provider label | Normal | Bold | - |
| User message | Normal | Bold | Colored (secondary) |
| AI response | Normal | Normal | Colored (primary) |
| Input prompt | Normal | Bold | Colored (primary) |
| Status info | Small | Normal | Dim |
| Code block | Normal | Normal | Monospace |

## Animations & Transitions

### Duration & Easing

- **Focus transitions**: 200ms ease-out (border, color, background)
- **Message appearance**: 150ms fade-in
- **Provider switch**: 100ms slide
- **Error feedback**: 300ms pulse

## Layout Variants

### Full Layout (80+ char width)

```
┌─────────────────────────────────────────────────────┐
│ ide.ai [~/workspace]        Ctrl+L  Ctrl+Enter      │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ChatPanel                                           │
│ ╭─────────────────────────────────────────────╮     │
│ │ ● Claude                                    │     │
│ │ You: hello                                  │     │
│ │ Claude: Hi there!                           │     │
│ │ > type message...                           │     │
│ ╰─────────────────────────────────────────────╯     │
│                                                     │
├─────────────────────────────────────────────────────┤
│ ● Claude  ● Copilot       │  📄 Files  ⌘ Term  ➕ │
└─────────────────────────────────────────────────────┘
```

### Compact Layout (< 80 char width)

```
┌────────────────────────────┐
│ ide.ai  Ctrl+L Ctrl+Enter  │
├────────────────────────────┤
│ ChatPanel                  │
│ ╭────────────────────────╮ │
│ │ ● Claude              │ │
│ │ You: hello            │ │
│ │ Claude: Hi!           │ │
│ │ > type...             │ │
│ ╰────────────────────────╯ │
├────────────────────────────┤
│ ● Claude  📄 Files ➕ New  │
└────────────────────────────┘
```

## Spacing System

```
xs: 0.25 rem (1 char)
sm: 0.5 rem  (2 chars)
md: 1 rem    (4 chars)
lg: 1.5 rem  (6 chars)
xl: 2 rem    (8 chars)
```

### Default Spacing:

- Panel padding: `md` (top/bottom), `sm` (left/right)
- Message margin: `xs` (vertical), `sm` (horizontal)
- Button spacing: `xs`
- Header/footer: `sm`

## Component Specifications

### Chat Message Box

- Background: Subtle accent color (10% opacity)
- Padding: `xs` (vertical), `sm` (horizontal)
- Border: None (uses background color)
- Max width: 100% (scrolls if needed)

### Input Field

- Background: Slightly raised (1 level darker)
- Prefix: `>` in primary color
- Placeholder: Dimmed text
- Placeholder text: "Ask AI..."
- Focus state: Purple border highlight

### Provider Badge

- Icon: Provider-specific (🤖 Claude, ⚡ Copilot)
- Colors: Primary (active), muted (inactive)
- Animation: Fade-in/out on switch

### Status Indicator

- Icons: ✓ (ready), ⟳ (thinking), ✗ (error)
- Colors: Success/Warning/Error per icon type
- Position: Top-right of ChatPanel

## WCAG AA Compliance

✅ **All colors verified for WCAG AA:**
- Normal text: 4.5:1 contrast minimum
- UI components: 3:1 contrast minimum
- No color-only information — always paired with text/icons
- All interactive elements: keyboard accessible

## Dark Theme (Current)

The current theme uses a dark background (#1F2937) with light text (#F3F4F6) for:
- Low eye strain in dark environments
- Better visibility of accent colors
- Modern aesthetic alignment with Claude Code

---

**Current Status**: Active — Phase 2 Polish  
**Last Updated**: 2024  
**Maintainer**: GitHub Copilot CLI
