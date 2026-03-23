---
name: ide-ai-skills-index
description: Index and guide to all IDE.AI Claude Skills for efficient development and contribution
---

# IDE.AI Skills Index

A comprehensive collection of Claude Skills that document the IDE.AI project architecture, design system, implementation patterns, and development workflows.

## Quick Navigation

### 1. **Project Overview** 📋
   - **File**: `project-overview/SKILL.md`
   - **Purpose**: Understand the overall IDE.AI vision, architecture, and implementation phases
   - **Best for**: New contributors, understanding project scope, design decisions
   - **Contents**:
     - Project vision and architecture
     - Technology stack
     - Project structure
     - Panel layout
     - AI provider interface
     - Implementation phases (0-3)
     - Core conventions
     - Getting started guide

### 2. **Style Guide** 🎨
   - **File**: `style-guide/SKILL.md`
   - **Purpose**: UI/UX consistency guidelines for IDE.AI v2
   - **Best for**: UI component development, maintaining visual consistency
   - **Contents**:
     - Icon scheme (provider icons, action indicators, fallbacks)
     - Color palette (semantic colors, WCAG AA compliance)
     - Component patterns (chat, buttons, status, input)
     - Keybindings and conventions
     - Responsive design breakpoints
     - Accessibility standards
     - Contribution checklist

### 3. **Design System** 🏗️
   - **File**: `design-system/SKILL.md`
   - **Purpose**: Complete design specifications for IDE.AI v2 UI
   - **Best for**: Understanding visual design, layout architecture, spacing
   - **Contents**:
     - Layout architecture with component specs
     - Color palette and usage guidelines
     - Typography and font hierarchy
     - Animations and transitions
     - Layout variants (full, compact)
     - Spacing system
     - Component specifications
     - Dark theme implementation

### 4. **Responsive Layout Guide** 📱
   - **File**: `architecture-guide/SKILL.md`
   - **Purpose**: Terminal size handling and responsive layout implementation
   - **Best for**: Responsive design implementation, handling different terminal sizes
   - **Contents**:
     - Breakpoints (small, medium, large, XL)
     - CSS Grid configuration
     - Terminal size handling strategies
     - Layout integrity verification
     - Edge case handling
     - Dynamic resizing behavior
     - Responsive component patterns
     - Performance considerations

### 5. **Testing Methodology** 🧪
   - **File**: `development-workflow/SKILL.md`
   - **Purpose**: Comprehensive testing approach for IDE.AI
   - **Best for**: Writing tests, validating responsive design, CI/CD setup
   - **Contents**:
     - Testing strategy (computational simulation)
     - Mathematical validation approach
     - 7 test categories (40+ individual tests)
     - Edge case handling
     - Real-world scenario testing
     - Test coverage matrix
     - Running tests
     - CI/CD integration

### 6. **Implementation Reference** 💻
   - **File**: `implementation-reference/SKILL.md`
   - **Purpose**: Code patterns, architecture details, and implementation best practices
   - **Best for**: Coding new features, understanding architecture, maintaining code quality
   - **Contents**:
     - v2 architecture and file structure
     - Core components (ChatPanel, ProviderBar, ActionBar)
     - Color system architecture
     - Coding patterns (AIProvider, Claude provider, etc.)
     - Key patterns (async, streaming, Rich rendering)
     - Best practices
     - Testing examples
     - Performance considerations

## Usage Scenarios

### Scenario 1: I'm new to IDE.AI

**Start with**:
1. **Project Overview** — Understand the vision and architecture
2. **Design System** — See how it looks and feels
3. **Architecture Guide** — Understand responsive layout
4. **Implementation Reference** — Start reading code patterns

### Scenario 2: I'm adding a new UI component

**Use**:
1. **Style Guide** — Icon scheme, colors, keybindings
2. **Design System** — Component specifications, spacing
3. **Implementation Reference** — Code patterns and examples

### Scenario 3: I'm fixing a responsive layout bug

**Use**:
1. **Responsive Layout Guide** — Breakpoint definitions
2. **Testing Methodology** — How to test responsive design
3. **Implementation Reference** — Performance considerations

### Scenario 4: I'm implementing a new AI provider

**Use**:
1. **Project Overview** — AIProvider interface definition
2. **Implementation Reference** — Provider implementation patterns
3. **Testing Methodology** — How to test the provider

### Scenario 5: I'm improving accessibility

**Use**:
1. **Style Guide** — WCAG AA requirements
2. **Design System** — Color contrast guidelines
3. **Implementation Reference** — Best practices

## Skills Structure

```
skills/
├── project-overview/
│   └── SKILL.md                 # Overview, architecture, phases
├── style-guide/
│   └── SKILL.md                 # Icons, colors, keybindings, accessibility
├── design-system/
│   └── SKILL.md                 # Layout, typography, animations, components
├── architecture-guide/
│   └── SKILL.md                 # Responsive layout, breakpoints, CSS Grid
├── development-workflow/
│   └── SKILL.md                 # Testing strategy, test categories, coverage
├── implementation-reference/
│   └── SKILL.md                 # Patterns, components, best practices
└── INDEX.md                     # This file
```

## Key Concepts

### 1. Async-First Architecture
All AI interactions use `async/await` to prevent UI blocking. See **Implementation Reference** for examples.

### 2. Responsive by Default
Layout adapts from 60 to 600+ character terminal widths using CSS Grid and Textual's media queries. See **Responsive Layout Guide**.

### 3. Component-Based
UI is built from reusable components (ChatPanel, ProviderBar, etc.) following clear patterns. See **Implementation Reference**.

### 4. Theme-Agnostic Colors
Color system uses semantic variables that automatically adapt to any Textual theme. See **Design System**.

### 5. AI Provider Interface
All AI providers (Claude, Copilot, etc.) implement a consistent interface for easy swapping. See **Project Overview**.

## Development Workflow

1. **Understand the project** → Read **Project Overview**
2. **Check style guidelines** → Review **Style Guide**
3. **Design your component** → Use **Design System** and **Responsive Layout Guide**
4. **Write the code** → Follow patterns in **Implementation Reference**
5. **Test it** → Use approach in **Testing Methodology**
6. **Verify accessibility** → Check **Style Guide** WCAG AA section

## Quick References

### Keybindings
See **Style Guide** > Keybindings section

### Color Palette
See **Design System** > Color Palette section

### Breakpoints
See **Responsive Layout Guide** > Breakpoints section

### Test Coverage
See **Testing Methodology** > Test Coverage Matrix

### Component Patterns
See **Implementation Reference** > Coding Patterns

## Contributing

When contributing to IDE.AI:

1. **Read the relevant skill(s)** — Choose from the scenarios above
2. **Follow the patterns** — Code structure, colors, keybindings
3. **Test thoroughly** — Use testing methodology
4. **Update documentation** — If adding new patterns or behaviors, update the relevant skill
5. **Check accessibility** — Ensure WCAG AA compliance (see Style Guide)

## Skill Metadata

Each skill is a Markdown file with YAML frontmatter:

```yaml
---
name: ide-ai-<skill-name>
description: Brief description of what this skill teaches
---

# Title
Content...
```

### Using Skills in Claude

1. Upload this `skills/` directory to Claude
2. Ask Claude to reference specific skills by name
3. Example: "Using the style-guide skill, what colors should I use for..."

### Loading Skills via Claude API

```python
# Skills can be loaded and used via the Claude API
# See https://docs.claude.com/en/api/skills-guide
```

## Related Files

While these skills capture the essential documentation, other files in the project include:

- `README.md` — Quick start guide
- `pyproject.toml` — Project dependencies
- `src/ide_ai/` — Source code
- `tests/` — Test suite
- `CLAUDE.md` — Core architectural notes
- `IMPLEMENTATION_CHECKLIST.md` — Task tracking

## Version Information

| Skill | Version | Status |
|---|---|---|
| Project Overview | 2.0 | Active |
| Style Guide | 2.0 | Active |
| Design System | 2.0 | Active |
| Responsive Layout | 2.0 | Stable |
| Testing Methodology | 2.0 | Stable |
| Implementation Reference | 2.0 | Active |

**Last Updated**: 2024  
**Current Phase**: Phase 2 (Copilot Integration + UX Polish)  
**Maintainer**: GitHub Copilot CLI

---

## Next Steps

1. **Clone or fork** the repository
2. **Read** the relevant skill(s) for your task
3. **Set up** development environment: `uv sync`
4. **Run** IDE.AI: `uv run python -m ide_ai`
5. **Contribute** following the patterns you learned!

For detailed getting-started guide, see **Project Overview** > Development Commands section.
