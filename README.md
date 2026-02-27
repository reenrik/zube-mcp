# zube-mcp

MCP server for the [Zube.io](https://zube.io) project management API. Exposes Zube boards, cards, epics, tickets, sprints, and workspaces as tools that AI assistants can call.

## Setup

### 1. Get your Zube API credentials

1. Go to **Zube.io → Account Settings → API Keys**
2. Create a new API key — this gives you a **Client ID** and a **private key** file (PEM)
3. Save the private key somewhere safe (e.g. `~/.zube/private-key.pem`)

### 2. Install

```bash
cd /path/to/zube-mcp
pip install -e .
```

Or run directly with `uvx`:

```bash
uvx --from /path/to/zube-mcp zube-mcp
```

### 3. Configure in Cursor

Add to your `.cursor/mcp.json` (project-level or global):

```json
{
  "mcpServers": {
    "zube": {
      "command": "uvx",
      "args": ["--from", "/Users/enoch/_CODE/zube-mcp", "zube-mcp"],
      "env": {
        "ZUBE_CLIENT_ID": "your-client-id-here",
        "ZUBE_PRIVATE_KEY_PATH": "/Users/enoch/.zube/private-key.pem"
      }
    }
  }
}
```

## Development

### Making changes

After editing the source code, you **must bump the version** in `pyproject.toml` for Cursor to pick up changes. This is because `uvx` caches the built package by version — if the version hasn't changed, it serves the stale cached copy.

```bash
# 1. Edit code in zube_mcp/
# 2. Bump version in pyproject.toml (e.g. 0.2.0 → 0.3.0)
# 3. In Cursor: Settings → MCP → toggle zube off, then on
```

To verify your changes locally before restarting Cursor:

```bash
uvx --from /Users/enoch/_CODE/zube-mcp python3 -c "
from zube_mcp.server import mcp
import inspect
# check a specific function's signature
from zube_mcp.server import list_cards
print(inspect.signature(list_cards))
"
```

### Zube API reference

Full API docs: https://zube.io/docs/api

Key concepts for adding new filters:
- List endpoints support `where[field]=value` query params for filtering
- The `_build_params()` helper in `server.py` converts a `where` dict into these query params automatically
- Array filters (e.g. `assignee_ids`) use `where[field][]=value` (handled by `_build_params` when the value is a list)
- Card numbers (the `#12345` visible in the UI) are distinct from internal card IDs — use `where[number]` to filter by the visible number

### Known Zube API quirks

- `get_card` requires the **internal card ID**, not the visible card number. Use `get_card_by_number` to look up by the human-visible `#number`.
- `search_key` on list endpoints is a full-text search and can be unreliable for finding cards by number.
- List responses return items in `data` array with a `pagination` object.
- Rate limit: 1 request/second. Short bursts are tolerated but sustained higher rates will be rejected.

## Available Tools

### Person & Accounts
| Tool | Description |
|------|-------------|
| `get_current_person` | Get the authenticated user's profile |
| `list_accounts` | List organizations the user belongs to |
| `get_account` | Get details for a specific account |

### Projects
| Tool | Description |
|------|-------------|
| `list_projects` | List projects (optionally by account) |
| `get_project` | Get project details |
| `create_project` | Create a new project |

### Workspaces (Kanban Boards)
| Tool | Description |
|------|-------------|
| `list_workspaces` | List workspaces (optionally by project) |
| `get_workspace` | Get workspace details |
| `create_workspace` | Create a new workspace |

### Cards (Issues / PRs)
| Tool | Description |
|------|-------------|
| `list_cards` | List cards with filters (project, workspace, sprint, epic, number, state, search) |
| `list_project_cards` | List cards scoped to a project (also supports number filter) |
| `list_triage_cards` | List cards in a project's triage |
| `get_card` | Get full card details by internal ID |
| `get_card_by_number` | Look up a card by its visible `#number` (e.g. 15293) |
| `create_card` | Create a card |
| `update_card` | Update a card |
| `move_card` | Move a card to a column or triage |
| `archive_card` | Archive a card |

### Card Comments
| Tool | Description |
|------|-------------|
| `list_card_comments` | List comments on a card |
| `create_card_comment` | Add a comment |
| `update_card_comment` | Edit a comment |
| `delete_card_comment` | Delete a comment |

### Epics
| Tool | Description |
|------|-------------|
| `list_epics` | List epics for a project |
| `get_epic` | Get epic details |
| `create_epic` | Create an epic |
| `update_epic` | Update an epic |
| `list_epic_cards` | List cards in an epic |

### Sprints
| Tool | Description |
|------|-------------|
| `list_sprints` | List sprints for a workspace |
| `get_sprint` | Get sprint details |
| `create_sprint` | Create a sprint |
| `update_sprint` | Update a sprint |

### Tickets
| Tool | Description |
|------|-------------|
| `list_tickets` | List tickets for a project |
| `get_ticket` | Get ticket details |
| `create_ticket` | Create a ticket |
| `update_ticket` | Update a ticket |

### Labels & Members
| Tool | Description |
|------|-------------|
| `list_labels` | List project labels |
| `create_label` | Create a label |
| `list_sources` | List connected GitHub repos |
| `list_project_members` | List project members |
| `list_account_members` | List account members |

## Architecture

```
zube_mcp/
  auth.py      # RS256 JWT creation for Zube's refresh token flow
  client.py    # Async HTTP client with automatic token management
  server.py    # FastMCP tool definitions (40 tools)
```

The auth flow:
1. Sign a 60-second JWT with your private key
2. Exchange it at `POST /api/users/tokens` for a 24-hour access token
3. The client auto-refreshes when the token is near expiry
