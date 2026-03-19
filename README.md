# ide.ai

TUI com múltiplas caixinhas de AI chat no terminal — focado em AI developer experience.
Construído com [Textual](https://github.com/Textualize/textual) + [Rich](https://github.com/Textualize/rich).

![alt text](image-2.png)

![alt text](image-1.png)

## Como funciona

Múltiplas sessões de AI chat visíveis ao mesmo tempo, em grade responsiva:

```
╭─ [1] Claude ──────────╮ ╭─ [2] Claude ──────────╮
│                       │ │                       │
│ You: como faço X?     │ │ You: explica Y         │
│ Claude: ...           │ │ Claude: ...            │
├───────────────────────┤ ├───────────────────────┤
│ > Ask AI…             │ │ > Ask AI…             │
╰───────────────────────╯ ╰───────────────────────╯
╭─ [3] Copilot ─────────────────────────────────────╮
│ > Ask AI…                                         │
╰───────────────────────────────────────────────────╯
```

### Responsividade automática

| Largura do terminal | Colunas |
| ------------------- | ------- |
| < 80 chars          | 1       |
| 80 – 159            | 2       |
| 160 – 239           | 3       |
| ≥ 240               | 4       |

## Requisitos

- Python >= 3.10
- [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes recomendado)
- `claude` CLI (opcional) — `npm install -g @anthropic-ai/claude-code`
- `gh` CLI (opcional, para Copilot) — [cli.github.com](https://cli.github.com)

> **Transparência:** funciona melhor em terminais modernos como **kitty**, **WezTerm**, **iTerm2** ou **Ghostty**.

## Como rodar

```bash
# Instalar dependências
uv sync

# Executar
uv run python -m ide_ai
```

## Comandos

### Gerenciar caixinhas

| Tecla          | Ação                        |
| -------------- | --------------------------- |
| `Ctrl+N`       | Criar nova caixinha de chat |
| `Ctrl+W`       | Fechar a caixinha ativa     |
| `Ctrl+]`       | Ir para a próxima caixinha  |
| `Ctrl+[` / `Esc` | Ir para a caixinha anterior |
| `Ctrl+Q`       | Sair                        |

### Dentro de cada caixinha

| Tecla            | Ação                                  |
| ---------------- | ------------------------------------- |
| `Ctrl+Enter`     | Enviar mensagem para a AI             |
| `Ctrl+L`         | Limpar histórico do chat              |
| `Ctrl+Y`         | Alternar provider: Claude ↔ Copilot   |
| `Ctrl+Shift+C`   | Copiar última resposta                |
| `Ctrl+Shift+A`   | Copiar toda a conversa                |

## Estrutura

```
ide.ai/
├── main.py
├── src/
│   └── ide_ai/
│       ├── app.py               # IdeApp — entry point
│       ├── app.tcss             # Estilos (grid, caixinhas, transparência)
│       ├── layout/
│       │   └── panel_grid.py    # Grade responsiva de caixinhas
│       ├── panels/
│       │   └── chat_box.py      # ChatBox — caixinha individual
│       └── ai/
│           ├── base.py          # AIProvider interface
│           ├── claude.py        # ClaudeProvider (subprocess `claude`)
│           └── copilot.py       # CopilotProvider (subprocess `gh copilot`)
├── pyproject.toml
└── uv.lock
```
