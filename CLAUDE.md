# ide.ai — TUI IDE para AI CLIs

Uma IDE no terminal estilo **tmux**, construída com **Python + Textual**, focada em trabalhar com
**Claude CLI** e **GitHub Copilot CLI** de forma ultra-rápida.

---

## Visão Geral

- Layout em painéis redimensionáveis (File Tree | Editor | AI Chat | Terminal)
- Keybindings estilo VS Code
- Integração com Claude CLI e GitHub Copilot CLI via subprocess async com streaming
- Sem dependência de LSP/editor real no v1 (editor é visualizador com syntax highlight)

---

## Stack

| Camada | Tecnologia | Motivo |
|---|---|---|
| TUI Framework | `textual` | CSS-like layout, widgets ricos, async nativo |
| Rich text | `rich` | Markdown, syntax highlight nos chats |
| Syntax highlight | `pygments` | Highlight do código enviado/recebido |
| Subprocess AI | `asyncio.subprocess` | Async stdin/stdout para Claude e Copilot |
| File watching | `watchfiles` | Detectar mudanças nos arquivos do workspace |
| Config | `tomllib` / `tomli-w` | Config em TOML |
| Package manager | `uv` | Ultra-rápido, moderno |

---

## Estrutura do Projeto

```
ide.ai/
├── src/
│   └── ide_ai/
│       ├── __main__.py          # Entrypoint: python -m ide_ai
│       ├── app.py               # IdeApp (Textual App principal)
│       ├── layout/
│       │   ├── workspace.py     # WorkspaceLayout — gerencia painéis
│       │   └── panel.py         # Panel base class (redimensionável)
│       ├── panels/
│       │   ├── file_tree.py     # FileTreePanel — navegação de arquivos
│       │   ├── ai_chat.py       # AIChatPanel — chat com AI
│       │   ├── terminal.py      # TerminalPanel — terminal embutido
│       │   └── editor.py        # EditorPanel — visualizador de código (read-only v1)
│       ├── ai/
│       │   ├── base.py          # AIProvider interface (ABC)
│       │   ├── claude.py        # ClaudeProvider (subprocess `claude`)
│       │   └── copilot.py       # CopilotProvider (subprocess `gh copilot`)
│       ├── keybindings.py       # Mapa de atalhos estilo VS Code
│       ├── context.py           # ContextManager — envia arquivos como contexto
│       └── config.py            # Leitura de ~/.ide_ai/config.toml
├── tests/
├── pyproject.toml
└── CLAUDE.md
```

---

## Layout dos Painéis

```
┌─────────────────────────────────────────────────────────────┐
│  ide.ai  [workspace: ~/projeto]           Ctrl+P  Ctrl+Shift+P│
├──────────┬──────────────────────────┬────────────────────────┤
│          │                          │                        │
│  File    │   Editor / Preview       │   AI Chat              │
│  Tree    │   (código com highlight) │   (Claude / Copilot)   │
│          │                          │                        │
│  F1      │                          │   Ctrl+L clear         │
│          │                          │   Ctrl+Enter send      │
├──────────┴──────────────────────────┴────────────────────────┤
│  Terminal (Ctrl+`)                                           │
└─────────────────────────────────────────────────────────────┘
```

Painéis redimensionáveis com `Alt+←/→/↑/↓`, fecháveis com `Ctrl+W`.

---

## Keybindings

| Atalho | Ação |
|---|---|
| `Ctrl+P` | Quick Open (buscar arquivo) |
| `Ctrl+Shift+P` | Command Palette |
| `Ctrl+\` | Split painel vertical |
| `Ctrl+W` | Fechar painel ativo |
| `Ctrl+`` ` | Toggle terminal |
| `Ctrl+1/2/3` | Focar painel 1/2/3 |
| `Ctrl+L` | Limpar chat AI |
| `Ctrl+Enter` | Enviar mensagem para AI |
| `Ctrl+Shift+C` | Copiar arquivo atual como contexto para AI |
| `Ctrl+Shift+A` | Alternar entre Claude / Copilot |
| `F1` | Focar file tree |
| `Escape` | Voltar para painel anterior |

---

## Interface AIProvider

Todos os providers de AI implementam essa interface:

```python
class AIProvider(ABC):
    async def send(self, message: str, context: list[str]) -> AsyncIterator[str]: ...
    async def clear_session(self) -> None: ...

    @property
    def name(self) -> str: ...
```

### Claude CLI
```python
# Inicia sessão interativa: `claude --chat`
# Injeta contexto via stdin
# Faz stream do stdout para o painel
```

### GitHub Copilot CLI
```python
# Usa: `gh copilot suggest` ou `gh copilot explain`
# Passa contexto de arquivo via stdin / flag --target
```

---

## Comandos de Desenvolvimento

```bash
# Setup do projeto
uv sync

# Rodar a IDE
uv run python -m ide_ai

# Rodar testes
uv run pytest

# Lint
uv run ruff check src/
uv run ruff format src/
```

---

## Fases de Implementação

### Passo 0 — Setup base
- Setup do projeto com `uv` + `pyproject.toml`
- `IdeApp` com tela inicial (sem background sólido/transparente)
- Layout vazio mas funcional, `q` para sair

### Fase 1 — MVP (esqueleto funcional)
- `IdeApp` básico com layout de 3 painéis
- `FileTreePanel` navegável com setas
- `AIChatPanel` com input e área de resposta (texto simples)
- `ClaudeProvider` via subprocess async com streaming
- Keybindings básicos (`Ctrl+Enter`, `Ctrl+1/2/3`, `F1`)

### Fase 2 — Integração Copilot + UX
- `CopilotProvider` (`gh copilot suggest/explain`)
- Switch Claude ↔ Copilot (`Ctrl+Shift+A`)
- Syntax highlight nas respostas com código (via `rich`)
- `ContextManager`: enviar arquivo aberto como contexto
- `TerminalPanel` embutido

### Fase 3 — Power features
- Command Palette (`Ctrl+Shift+P`)
- Quick Open de arquivos (`Ctrl+P`)
- Histórico de conversas persistido
- Config `~/.ide_ai/config.toml` (provider padrão, tema, keybindings)
- Redimensionamento de painéis com teclado
- Modo sessão: retomar conversa anterior

---

## Convenções

- **Async everywhere**: Textual é async-native; todos os providers de AI usam `asyncio.subprocess` com streaming para não travar a UI.
- **Sem editor real no v1**: o painel Editor é visualizador com highlight apenas. Edição real pode vir depois.
- **Testabilidade**: providers de AI têm interface clara (`AIProvider`); fácil de mockar em testes.
- **Cross-platform**: Textual roda em Linux, macOS e Windows Terminal.
- **Config em TOML**: preferir `~/.ide_ai/config.toml` sobre flags de linha de comando para configurações persistentes.
- **Package manager**: usar sempre `uv` (não `pip` diretamente).
