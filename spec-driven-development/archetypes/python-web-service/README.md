# Python Web Service Archetype

Use this archetype for a Python web service shaped as a FastAPI-first Python HTTP service.

Choose it when the first useful slice is an endpoint, route contract, or persistence-backed web workflow rather than a different project shape.

After bootstrapping, review all six constitution files and replace remaining host-specific placeholders.

---

## Example concrete file-map (reference only)

This is an illustrative file-map from a real web-service host (the framework's origin project).
Use it as a shape reference when populating your own host's architecture map; replace every
entry with your project's actual modules.

| File | Purpose | Stability |
|------|---------|-----------|
| `agent/engine.py` | Lazy singleton orchestrator | Stable -- modify with extreme care |
| `agent/api.py` | Web app, pages, board, chat, uploads, WebSocket | Active -- routes being extracted |
| `agent/routes/__init__.py` | Shared route utilities (get_engine, esc, safe_path) | Stable |
| `agent/llm.py` | Dual-endpoint LLM client | Stable |
| `agent/config.py` | Frozen dataclass settings | Stable |
| `agent/world_state.py` | Data aggregation for prompts | Stable |
| `agent/models.py` | ORM table definitions | Growing (additive changes) |
| `agent/database.py` | SQLite session management | Stable |
