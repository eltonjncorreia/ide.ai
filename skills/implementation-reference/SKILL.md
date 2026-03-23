---
name: ide-ai-implementation-reference
description: Implementation guide for IDE.AI v2 component architecture, color palette system, and coding patterns
---

# IDE.AI Implementation Reference

## Architecture Overview (v2)

### File Structure

```
src/ide_ai/
├── app_new.py                  # Main app (v2)
├── app_new.tcss                # Main stylesheet
│
├── panels/
│   ├── chat_panel.py           # ChatPanel (central focus)
│   ├── provider_bar.py         # Provider selector
│   ├── action_bar.py           # Quick action buttons
│   ├── chat_box.py             # ChatBox (legacy)
│   ├── file_tree.py            # File tree (legacy)
│   └── terminal.py             # Terminal (legacy)
│
├── style/
│   ├── colors.tcss             # Color system
│   ├── typography.tcss         # Font hierarchy
│   ├── spacing.tcss            # Layout rhythm
│   └── animations.tcss         # Transitions
│
├── ai/
│   ├── base.py                 # AIProvider interface
│   ├── claude.py               # Claude CLI provider
│   └── copilot.py              # Copilot provider
│
└── ...
```

## Core Components

### ChatPanel

**Responsibility**: Central chat interface with message rendering

**Key features:**
- Chat log with rich rendering
- Input area with prompts
- Message bubbles (You/AI)
- Status indicators
- Syntax highlighting

**Structure:**
```python
class ChatPanel(Static):
    """Main chat interface."""
    
    def __init__(self, provider: AIProvider):
        super().__init__()
        self.provider = provider
        self.messages: list[ChatMessage] = []
    
    def post_message(self, sender: str, content: str):
        """Add message to chat."""
        msg = ChatMessage(sender=sender, content=content)
        self.messages.append(msg)
        self.refresh()
    
    async def send_to_ai(self, text: str):
        """Send message to AI and stream response."""
        self.post_message("You", text)
        async for chunk in self.provider.send(text, context=[]):
            self.stream_response(chunk)
```

### ProviderBar

**Responsibility**: Display and switch between AI providers

**Features:**
- Visual indication of active provider
- Switch with Ctrl+Tab
- Provider icons and labels

### ActionBar

**Responsibility**: Quick-access action buttons

**Features:**
- New chat button
- Clear chat button
- Files toggle
- Terminal toggle

## Color System Architecture

### Core Theme Variables (Automatic)

These are provided by Textual and adapt to the active theme:

| Variable | Purpose | Example (Dracula) |
|----------|---------|-------------------|
| `$accent` | Highlight & focus color | #FF79C6 (pink) |
| `$primary` | Theme primary color | #BD93F9 (purple) |
| `$secondary` | Theme secondary color | #6272A4 (indigo) |
| `$foreground` | High-contrast text | #F8F8F2 (off-white) |
| `$background` | Terminal background | #282A36 (dark) |
| `$panel` | Base panel background | #313442 (dark) |
| `$surface` | Elevated background | #2B2E3B (dark) |
| `$warning` | Warning/attention | #FFB86C (amber) |
| `$error` | Error state | #FF5555 (red) |
| `$success` | Success/positive | #50FA7B (green) |

### Derived Colors (Automatic Tonal Scales)

Textual automatically derives these from `$panel`:

| Variable | Usage |
|----------|-------|
| `$panel-lighten-1` | Borders & fine lines |
| `$panel-lighten-2` | Inactive headers |
| `$panel-lighten-3` | Inactive panel backgrounds |

### Semantic Color Decisions

#### Inactive Panels
```tcss
background: $panel-lighten-3 5%;
border: solid $panel-lighten-1;
color: $text-muted;
```

#### Active/Focused Panels
```tcss
background: $panel;
border: solid $primary;
color: $text;
```

#### Error States
```tcss
color: $error;
background: $error 20%;  /* 20% opacity */
border: solid $error;
```

#### Success States
```tcss
color: $success;
background: $success 20%;
border: solid $success;
```

## Coding Patterns

### AIProvider Interface

All AI providers implement this pattern:

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator

class AIProvider(ABC):
    """Base class for AI providers."""
    
    @abstractmethod
    async def send(self, message: str, context: list[str]) -> AsyncIterator[str]:
        """Send message and stream response."""
        ...
    
    @abstractmethod
    async def clear_session(self) -> None:
        """Clear conversation history."""
        ...
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        ...
```

### Claude Provider Implementation

```python
class ClaudeProvider(AIProvider):
    """Claude CLI provider."""
    
    async def send(self, message: str, context: list[str]) -> AsyncIterator[str]:
        """Send to Claude and stream response."""
        process = await asyncio.create_subprocess_exec(
            "claude", "--chat",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdin_data = "\n".join(context) + "\n" + message
        
        try:
            stdout, _ = await process.communicate(stdin_data.encode())
            response = stdout.decode()
            
            for chunk in response.split():
                yield chunk + " "
        finally:
            await process.wait()
    
    @property
    def name(self) -> str:
        return "Claude"
```

### Message Rendering

```python
class ChatMessage:
    """Represents a chat message."""
    
    sender: str          # "You", "Claude", "Copilot"
    content: str         # Message text
    timestamp: datetime
    is_streaming: bool
    has_code: bool       # Auto-detected
    
    def render(self) -> str:
        """Render message with styling."""
        if self.sender == "You":
            label = f"[secondary]You:[/]"
            body = f"[secondary bold]{self.content}[/]"
        else:
            icon = "🤖" if self.sender == "Claude" else "⚡"
            label = f"[primary]{icon} {self.sender}:[/]"
            body = self.content  # Rich handles code blocks
        
        return f"{label}\n{body}\n"
```

### Chat Panel Update Pattern

```python
class ChatPanel(Static):
    """Chat interface."""
    
    async def _handle_message(self, text: str):
        """Send message to AI and render response."""
        # Add user message
        self.post_message("You", text)
        
        # Get AI response (streaming)
        response_text = ""
        self.post_message(self.provider.name, "")
        
        async for chunk in self.provider.send(text, context=[]):
            response_text += chunk
            self.update_last_message(response_text)
            
            # Yield to event loop for responsiveness
            await asyncio.sleep(0)
```

## Key Patterns

### 1. Async Message Handling

Always use `async/await` for AI interactions:

```python
async def on_input_submitted(self, message: Input.Submitted) -> None:
    """Handle input submission."""
    text = message.value
    message.clear()
    
    # Non-blocking AI call
    await self._handle_message(text)
```

### 2. Streaming Responses

Yield control back to event loop during streaming:

```python
async for chunk in provider.send(text, context):
    self.update_ui(chunk)
    await asyncio.sleep(0)  # Yield to event loop
```

### 3. Rich Text Rendering

Use Rich for markdown and syntax highlighting:

```python
from rich.console import Console
from rich.markdown import Markdown

content = Markdown("**Bold** and `code block`")
self.update(content)  # Renders with highlighting
```

### 4. Component Composition

Build complex UIs by composing simpler components:

```python
class IdeApp(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield ChatPanel()
        with Container():
            yield ProviderBar()
            yield ActionBar()
        yield Footer()
```

## Best Practices

### 1. Separate Concerns

- **AIProvider**: Handles AI communication only
- **ChatPanel**: Handles UI rendering only
- **IdeApp**: Coordinates between them

### 2. Use Type Hints

```python
async def send(self, message: str, context: list[str]) -> AsyncIterator[str]:
    """Clear type hints for better IDE support."""
    ...
```

### 3. Handle Errors Gracefully

```python
try:
    async for chunk in provider.send(text, context):
        self.update_ui(chunk)
except asyncio.CancelledError:
    self.post_message("System", "Request cancelled")
except Exception as e:
    self.post_message("System", f"Error: {e}")
```

### 4. Test AI Providers

```python
class MockProvider(AIProvider):
    """Mock provider for testing."""
    
    async def send(self, message: str, context: list[str]) -> AsyncIterator[str]:
        yield "Mock response"
    
    async def clear_session(self) -> None:
        pass
    
    @property
    def name(self) -> str:
        return "Mock"
```

## Testing Implementation

### Unit Test Example

```python
def test_chat_message_render():
    """Test message rendering."""
    msg = ChatMessage(
        sender="You",
        content="Hello",
        timestamp=datetime.now(),
    )
    rendered = msg.render()
    assert "[secondary]You:[/]" in rendered
    assert "Hello" in rendered
```

### Integration Test Example

```python
async def test_send_message_to_ai():
    """Test sending message to Claude."""
    provider = ClaudeProvider()
    response = ""
    
    async for chunk in provider.send("hello", context=[]):
        response += chunk
    
    assert len(response) > 0
    assert "Claude" not in response  # Response shouldn't mention provider name
```

## Performance Considerations

### 1. Lazy Loading

Load components only when needed:

```python
def on_show(self) -> None:
    """Load data when panel becomes visible."""
    if not self._loaded:
        self._load_data()
        self._loaded = True
```

### 2. Efficient Rendering

Update only changed portions:

```python
def update_last_message(self, new_content: str):
    """Update only the last message, not whole chat."""
    self.messages[-1].content = new_content
    self.refresh_last_message()  # Partial refresh
```

### 3. Memory Management

Limit chat history in memory:

```python
MAX_MESSAGES = 100

def post_message(self, sender: str, content: str):
    """Add message, dropping oldest if needed."""
    self.messages.append(ChatMessage(sender, content, datetime.now()))
    
    if len(self.messages) > MAX_MESSAGES:
        self.messages.pop(0)  # Remove oldest
```

---

**Current Status**: Active — Phase 2 Implementation  
**Last Updated**: 2024  
**Maintainer**: GitHub Copilot CLI
