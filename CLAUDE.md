# Zube MCP Server

MCP server exposing the Zube.io project management API as tools for AI assistants.

## Stack

- Python 3.10+, FastMCP, httpx, PyJWT
- Auth: RS256 JWT → access token exchange (auto-refreshed by `client.py`)
- Runs via `uvx --from /path/to/zube-mcp zube-mcp` in Cursor

## Project Layout

| File | Purpose |
|------|---------|
| `zube_mcp/server.py` | All tool definitions (`@mcp.tool` decorators) and `_build_params()` helper |
| `zube_mcp/client.py` | `ZubeClient` async HTTP client with token management |
| `zube_mcp/auth.py` | RS256 JWT signing for Zube's refresh flow |
| `pyproject.toml` | Package metadata, dependencies, entry point |

## After Making Changes — Version Bump Required

Cursor runs this server via `uvx`, which **caches the built package by version**.
If you edit code but don't bump the version in `pyproject.toml`, Cursor will keep running the old cached copy.

**Every code change requires:**
1. Bump `version` in `pyproject.toml` (e.g. `0.2.0` → `0.3.0`)
2. Commit and push to GitHub
3. Toggle the zube MCP server off/on in Cursor Settings → MCP

To verify changes locally before restarting:
```bash
uvx --from . python3 -c "from zube_mcp.server import <function_name>; import inspect; print(inspect.signature(<function_name>))"
```

## Adding New Filters to List Endpoints

The Zube API supports `where[field]=value` query params on list endpoints.
The `_build_params()` helper in `server.py` converts a Python dict to these params:

```python
where = {"number": 15293, "state": "open"}
# → where[number]=15293&where[state]=open
```

For array values (e.g. `assignee_ids`), pass a list — `_build_params` emits `where[field][]=val` for each item.

To add a new filter:
1. Add the parameter to the tool function signature (e.g. `number: int | None = None`)
2. Add `if param is not None: where["param"] = param` in the function body
3. Update the docstring
4. Bump the version

## Zube API Quirks

- **Card number ≠ card ID**: The `#12345` visible in the Zube UI is the `number` field. The `id` field is an internal integer. Use `get_card_by_number` to look up by visible number, `get_card` for internal ID.
- **`search_key`** is full-text search and unreliable for exact lookups by number.
- **Rate limit**: 1 req/sec sustained. Short bursts OK.
- **List responses**: `{"pagination": {...}, "data": [...]}` — items are in the `data` array.
- **Full API docs**: https://zube.io/docs/api
