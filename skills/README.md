# IDE.AI Claude Skills

This directory contains a comprehensive set of **Claude Skills** that document the IDE.AI project architecture, design system, implementation patterns, and development workflows.

## What are Skills?

Skills are structured knowledge documents that Claude can load to provide expert assistance on specific tasks. Unlike scattered markdown files, skills follow a standardized format that makes them easy for Claude to understand and apply.

**Learn more**: [What are skills? - Claude Help Center](https://support.claude.com/en/articles/12512176-what-are-skills)

## Skills in This Directory

### 📋 **Project Overview**
- **File**: `project-overview/SKILL.md`
- Comprehensive overview of IDE.AI's vision, architecture, technology stack, and implementation phases
- Best for: Understanding the big picture, getting started

### 🎨 **Style Guide**
- **File**: `style-guide/SKILL.md`
- UI/UX consistency guidelines, icon schemes, color palette, keybindings, accessibility standards
- Best for: UI component development, maintaining visual consistency

### 🏗️ **Design System**
- **File**: `design-system/SKILL.md`
- Complete design specifications including layout architecture, typography, spacing, animations, and component patterns
- Best for: Understanding visual design and component specifications

### 📱 **Responsive Layout Guide**
- **File**: `architecture-guide/SKILL.md`
- Terminal size handling, responsive breakpoints, CSS Grid configuration, edge case handling
- Best for: Implementing responsive designs, handling different terminal sizes

### 🧪 **Testing Methodology**
- **File**: `development-workflow/SKILL.md`
- Comprehensive testing approach with 40+ test categories, coverage matrix, and CI/CD integration
- Best for: Writing tests, validating responsive design

### 💻 **Implementation Reference**
- **File**: `implementation-reference/SKILL.md`
- Code patterns, architecture details, component implementations, best practices, and performance considerations
- Best for: Coding new features, understanding architecture

## How to Use These Skills

### Option 1: Claude.ai (Recommended)

1. Go to [claude.ai](https://claude.ai)
2. Create a new conversation
3. Click the **paperclip icon** to upload files
4. Select any `.SKILL.md` files from this directory
5. Ask Claude questions related to the skill

Example: "Using the style-guide skill, what colors should I use for error messages?"

### Option 2: Claude Code

1. Run the IDE.AI project
2. In Claude Code, upload the skills directory
3. Reference skills by name in your prompts

### Option 3: Claude API

```python
from anthropic import Anthropic

client = Anthropic()

# Load a skill
with open("skills/style-guide/SKILL.md", "r") as f:
    skill_content = f.read()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user", 
            "content": skill_content + "\n\nUsing the style guide, what icon should I use for a success message?"
        }
    ]
)

print(response.content[0].text)
```

## Navigation Guide

**New to IDE.AI?**
1. Start with **Project Overview** to understand the vision
2. Read **Design System** to see how it looks
3. Check **Architecture Guide** for responsive layout
4. Review **Implementation Reference** for code patterns

**Need to add a UI component?**
1. Check **Style Guide** for icons, colors, keybindings
2. Use **Design System** for component specifications
3. Follow patterns in **Implementation Reference**

**Fixing a responsive layout issue?**
1. Review **Responsive Layout Guide** for breakpoints
2. Check **Testing Methodology** for testing approach
3. Use **Implementation Reference** for performance tips

**Writing tests?**
1. Read **Testing Methodology** for strategy
2. Check test categories and examples
3. Use **Implementation Reference** for patterns

## Skills Structure

Each skill follows this format:

```markdown
---
name: ide-ai-<skill-name>
description: Brief description of the skill
---

# Skill Title

## Sections

Content organized by topic...
```

## Key Features of These Skills

✅ **Comprehensive** — Covers architecture, design, implementation, and testing  
✅ **Interconnected** — Cross-references between skills show relationships  
✅ **Practical** — Includes code examples, patterns, and best practices  
✅ **Accessible** — Organized for easy navigation and understanding  
✅ **Updated** — All documentation synced from project source files  

## How Skills Replace Scattered Markdown

### Before (Scattered Markdown)
```
- CLAUDE.md (architectural overview)
- STYLE_GUIDE.md (UI guidelines)
- DESIGN_SYSTEM_V2.md (design specs)
- RESPONSIVE_QUICK_REFERENCE.md (layout guide)
- TESTING_METHODOLOGY.md (testing approach)
- V2_IMPLEMENTATION.md (implementation details)
- README.md (getting started)
```

### After (Organized Skills)
```
skills/
├── project-overview/SKILL.md        (replaces CLAUDE.md, README.md)
├── style-guide/SKILL.md             (replaces STYLE_GUIDE.md)
├── design-system/SKILL.md           (replaces DESIGN_SYSTEM_V2.md)
├── architecture-guide/SKILL.md      (replaces RESPONSIVE_QUICK_REFERENCE.md)
├── development-workflow/SKILL.md    (replaces TESTING_METHODOLOGY.md)
├── implementation-reference/SKILL.md (replaces V2_IMPLEMENTATION.md)
└── INDEX.md                         (navigation guide)
```

## What Happened to the Original Files?

The original `.md` files in the project root can now be **archived or removed** since:
- All content is preserved in skills format
- Skills provide better structure for Claude
- Skills are easier to maintain and update
- No loss of information

You can safely clean up by:
```bash
# Back up originals (optional)
mkdir -p docs-backup
mv *.md docs-backup/

# Keep skills directory as primary documentation
# Reference skills in README instead
```

## Contributing to Skills

### Updating an Existing Skill

1. Edit the relevant `SKILL.md` file
2. Update the frontmatter if needed
3. Commit changes to git

### Adding a New Skill

1. Create a new directory: `skills/my-skill-name/`
2. Create `SKILL.md` with proper frontmatter
3. Add entry to `INDEX.md`
4. Commit to git

### Skill Template

```markdown
---
name: ide-ai-my-skill-name
description: Brief, clear description of what this skill teaches
---

# My Skill Title

## Overview

Introduction and context...

## Section 1

Content with examples...

## Section 2

More content...

---

**Current Status**: Active — Phase X  
**Last Updated**: YYYY  
**Maintainer**: GitHub Copilot CLI
```

## Quick Start

### For Claude Users
1. Download the `skills/` directory
2. Upload to Claude.ai or Claude Code
3. Ask questions using the skills as context

### For Developers
1. Use skills as reference while coding
2. Upload to Claude when asking for help
3. Example: "Using the implementation-reference skill, how should I implement a new AIProvider?"

### For Project Maintainers
1. Update skills when project architecture changes
2. Keep skills in sync with actual code
3. Reference skills in main README and contributing guides

## Support

- **Documentation**: See individual skills for detailed information
- **Questions**: Upload skills to Claude and ask specific questions
- **Updates**: Keep skills synchronized with the actual codebase
- **Issues**: Report skill content problems in the IDE.AI repository

## Links

- [IDE.AI Repository](https://github.com/eltonjncorreia/ide.ai)
- [Claude Skills Documentation](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Main README](../README.md)
- [Skills Index](./INDEX.md)

---

**Last Updated**: 2024  
**Skill Format Version**: 1.0  
**Compatible with**: Claude 3.5+
