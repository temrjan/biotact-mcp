# biotact-mcp

MCP сервер для доступа к базе знаний Biotact из Claude Code и Claude Desktop.

## Инструменты

| Tool | Описание |
|------|----------|
| `biotact_search` | Поиск по базе знаний (продукты, Dr. Berg, нутрициология, медицина) |
| `biotact_stats` | Статистика коллекций (количество векторов) |
| `biotact_get_transcript` | Полный транскрипт видео Dr. Berg по YouTube ID |

## Требования

- Python 3.10+
- Доступ к `core.biotact.uz` (API ключ)

## Установка

```bash
git clone git@github.com:temrjan/biotact-mcp.git C:/Claude/biotact-mcp
cd C:/Claude/biotact-mcp
pip install mcp httpx
```

## Подключение

### Claude Code CLI

```bash
claude mcp add biotact -s user -- python C:/Claude/biotact-mcp/server.py
```

Затем добавить API ключ в `~/.claude.json`:

```json
"mcpServers": {
  "biotact": {
    "type": "stdio",
    "command": "python",
    "args": ["C:/Claude/biotact-mcp/server.py"],
    "env": {
      "BIOTACT_API_KEY": "your_key_here"
    }
  }
}
```

### Claude Desktop App

Добавить в `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "biotact": {
      "command": "python",
      "args": ["C:/Claude/biotact-mcp/server.py"],
      "env": {
        "BIOTACT_API_KEY": "your_key_here"
      }
    }
  }
}
```

Перезапустить Claude Desktop после изменения конфига.

## Использование `biotact_search`

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `query` | str | — | Поисковый запрос (RU/EN) |
| `source` | str | "" (все) | `biotact` / `dr_berg` / `nutrition` / `medical` / `files` |
| `limit` | int | 5 | Количество результатов (1–50) |
| `threshold` | float | 0.0 | Минимальный score схожести (0.0–1.0) |

## Коллекции базы знаний

| Источник | Что содержит |
|----------|--------------|
| `biotact` | Карточки 11 продуктов Biotact (RU + UZ) |
| `dr_berg` | Транскрипты YouTube Dr. Berg (500+ видео) |
| `nutrition` | Общая нутрициология (WHO, OER, US Gov) |
| `medical` | Peer-reviewed статьи PubMed по специальностям |
| `files` | Файлы пользователей |
