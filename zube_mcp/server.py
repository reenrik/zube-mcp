"""Zube.io MCP Server — exposes Zube project management as MCP tools."""

from __future__ import annotations

import os
from typing import Any

from fastmcp import FastMCP

from .auth import load_private_key
from .client import ZubeClient

mcp = FastMCP(
    name="zube",
    instructions=(
        "Zube.io project management tools. Use these to interact with Zube boards, "
        "cards, epics, tickets, sprints, and workspaces. Cards are the primary work "
        "item (like GitHub issues). Tickets are higher-level feature requests / bugs. "
        "Epics group cards. Workspaces are Kanban boards within a project."
    ),
)

_client: ZubeClient | None = None


def _get_client() -> ZubeClient:
    global _client
    if _client is None:
        client_id = os.environ.get("ZUBE_CLIENT_ID", "")
        key_path = os.environ.get("ZUBE_PRIVATE_KEY_PATH", "")
        if not client_id or not key_path:
            raise RuntimeError(
                "ZUBE_CLIENT_ID and ZUBE_PRIVATE_KEY_PATH environment variables are required"
            )
        private_key = load_private_key(key_path)
        _client = ZubeClient(client_id, private_key)
    return _client


def _compact(**kwargs: Any) -> dict[str, Any]:
    """Build a dict from kwargs, dropping any None values."""
    return {k: v for k, v in kwargs.items() if v is not None}


def _build_params(
    page: int = 1,
    per_page: int = 30,
    where: dict[str, Any] | None = None,
    order_by: str | None = None,
    order_direction: str | None = None,
) -> list[tuple[str, Any]]:
    """Build query params as a list of tuples to support repeated keys (array params)."""
    params: list[tuple[str, Any]] = [("page", page), ("per_page", per_page)]
    if where:
        for key, val in where.items():
            if isinstance(val, list):
                for item in val:
                    params.append((f"where[{key}][]", item))
            else:
                params.append((f"where[{key}]", val))
    if order_by:
        params.append(("order[by]", order_by))
    if order_direction:
        params.append(("order[direction]", order_direction))
    return params


# ─── Person ──────────────────────────────────────────────────────────────────


@mcp.tool
async def get_current_person() -> dict:
    """Get the currently authenticated Zube user's profile information."""
    return await _get_client().get("/current_person")


# ─── Accounts ────────────────────────────────────────────────────────────────


@mcp.tool
async def list_accounts(page: int = 1, per_page: int = 30) -> dict:
    """List all Zube organizations (accounts) the current user belongs to."""
    return await _get_client().get("/accounts", _build_params(page, per_page))


@mcp.tool
async def get_account(account_id: int) -> dict:
    """Get details for a specific Zube account (organization)."""
    return await _get_client().get(f"/accounts/{account_id}")


# ─── Projects ────────────────────────────────────────────────────────────────


@mcp.tool
async def list_projects(
    page: int = 1,
    per_page: int = 30,
    account_id: int | None = None,
) -> dict:
    """List all projects. Optionally filter by account_id."""
    where = {"account_id": account_id} if account_id is not None else None
    return await _get_client().get("/projects", _build_params(page, per_page, where))


@mcp.tool
async def get_project(project_id: int) -> dict:
    """Get details for a specific project including its workspaces and sources."""
    return await _get_client().get(f"/projects/{project_id}")


@mcp.tool
async def create_project(account_id: int, name: str, description: str = "") -> dict:
    """Create a new project within an account."""
    data = {"account_id": account_id, "name": name, **_compact(description=description or None)}
    return await _get_client().post("/projects", data)


# ─── Workspaces ──────────────────────────────────────────────────────────────


@mcp.tool
async def list_workspaces(
    page: int = 1,
    per_page: int = 30,
    project_id: int | None = None,
) -> dict:
    """List all workspaces (Kanban boards). Optionally filter by project_id."""
    where = {"project_id": project_id} if project_id is not None else None
    return await _get_client().get("/workspaces", _build_params(page, per_page, where))


@mcp.tool
async def get_workspace(workspace_id: int) -> dict:
    """Get details for a specific workspace."""
    return await _get_client().get(f"/workspaces/{workspace_id}")


@mcp.tool
async def create_workspace(
    project_id: int, name: str, description: str = ""
) -> dict:
    """Create a new workspace (Kanban board) within a project."""
    data = {"project_id": project_id, "name": name, **_compact(description=description or None)}
    return await _get_client().post("/workspaces", data)


# ─── Cards ───────────────────────────────────────────────────────────────────


@mcp.tool
async def list_cards(
    page: int = 1,
    per_page: int = 30,
    project_id: int | None = None,
    workspace_id: int | None = None,
    sprint_id: int | None = None,
    epic_id: int | None = None,
    number: int | None = None,
    state: str | None = None,
    category_name: str | None = None,
    search_key: str | None = None,
    order_by: str | None = None,
    order_direction: str | None = None,
) -> dict:
    """List cards (issues/PRs) with optional filters.

    Filters: project_id, workspace_id, sprint_id, epic_id, number (visible card number),
    state (open/closed), category_name (column name), search_key (text search).
    Order by any card field; direction is 'asc' or 'desc'.
    """
    where: dict[str, Any] = {}
    if project_id is not None:
        where["project_id"] = project_id
    if workspace_id is not None:
        where["workspace_id"] = workspace_id
    if sprint_id is not None:
        where["sprint_id"] = sprint_id
    if epic_id is not None:
        where["epic_id"] = epic_id
    if number is not None:
        where["number"] = number
    if state:
        where["state"] = state
    if category_name:
        where["category_name"] = category_name
    if search_key:
        where["search_key"] = search_key
    return await _get_client().get(
        "/cards",
        _build_params(page, per_page, where or None, order_by, order_direction),
    )


@mcp.tool
async def get_card(card_id: int) -> dict:
    """Get full details for a specific card by its internal ID."""
    return await _get_client().get(f"/cards/{card_id}")


@mcp.tool
async def get_card_by_number(number: int, project_id: int | None = None) -> dict:
    """Look up a card by its visible card number (e.g. #15293).

    Optionally scope to a project_id. Returns full card details including
    assignees and labels. Returns an error dict if no card is found.
    """
    where: dict[str, Any] = {"number": number}
    if project_id is not None:
        where["project_id"] = project_id
    result = await _get_client().get(
        "/cards", _build_params(page=1, per_page=1, where=where)
    )
    cards = result.get("data", [])
    if not cards:
        return {"error": f"No card found with number {number}"}
    return cards[0]


@mcp.tool
async def create_card(
    project_id: int,
    title: str,
    body: str = "",
    workspace_id: int | None = None,
    assignee_ids: list[int] | None = None,
    label_ids: list[int] | None = None,
    epic_id: int | None = None,
    sprint_id: int | None = None,
    priority: int | None = None,
    points: float | None = None,
    category_name: str | None = None,
) -> dict:
    """Create a new card (issue) in a project.

    priority: 1-5 (1=highest). category_name: column name on the workspace board.
    """
    data = {
        "project_id": project_id,
        "title": title,
        **_compact(
            body=body or None,
            workspace_id=workspace_id,
            assignee_ids=assignee_ids,
            label_ids=label_ids,
            epic_id=epic_id,
            sprint_id=sprint_id,
            priority=priority,
            points=points,
            category_name=category_name,
        ),
    }
    return await _get_client().post("/cards", data)


@mcp.tool
async def update_card(
    card_id: int,
    title: str | None = None,
    body: str | None = None,
    project_id: int | None = None,
    workspace_id: int | None = None,
    assignee_ids: list[int] | None = None,
    label_ids: list[int] | None = None,
    epic_id: int | None = None,
    sprint_id: int | None = None,
    priority: int | None = None,
    points: float | None = None,
    state: str | None = None,
) -> dict:
    """Update an existing card. Only provided fields are changed.

    state: 'open' or 'closed'. priority: 1-5 or null.
    """
    data = _compact(
        title=title,
        body=body,
        project_id=project_id,
        workspace_id=workspace_id,
        assignee_ids=assignee_ids,
        label_ids=label_ids,
        epic_id=epic_id,
        sprint_id=sprint_id,
        priority=priority,
        points=points,
        state=state,
    )
    # Preserve context fields when not in payload so partial updates (e.g. epic-only) don't clear them.
    # Zube PUT treats omitted fields as "clear" rather than "leave unchanged".
    if data:
        current = await _get_client().get(f"/cards/{card_id}")
        for key in ("project_id", "workspace_id", "epic_id"):
            if key not in data and current.get(key) is not None:
                data[key] = current[key]
        # Always preserve sprint_id when not explicitly being changed (e.g. epic-only updates must not clear sprint).
        if "sprint_id" not in data:
            sid = current.get("sprint_id")
            if sid is None and current.get("sprint"):
                sid = current["sprint"].get("id")
            if sid is not None:
                data["sprint_id"] = sid
    return await _get_client().put(f"/cards/{card_id}", data)


@mcp.tool
async def move_card(
    card_id: int,
    position: int,
    destination_type: str = "category",
    workspace_id: int | None = None,
    category_name: str | None = None,
) -> dict:
    """Move a card to a column on a workspace board or to project triage.

    destination_type: 'category' (move to a board column) or 'project' (move to triage).
    For 'category', workspace_id and category_name are required.
    """
    dest: dict[str, Any] = {"position": position, "type": destination_type}
    if destination_type == "category":
        if workspace_id is not None:
            dest["workspace_id"] = workspace_id
        if category_name is not None:
            dest["name"] = category_name
    return await _get_client().put(f"/cards/{card_id}/move", {"destination": dest})


@mcp.tool
async def archive_card(card_id: int) -> dict:
    """Archive a card."""
    return await _get_client().put(f"/cards/{card_id}/archive")


# ─── Card Comments ───────────────────────────────────────────────────────────


@mcp.tool
async def list_card_comments(card_id: int, page: int = 1, per_page: int = 30) -> dict:
    """List comments on a card."""
    return await _get_client().get(
        f"/cards/{card_id}/comments", _build_params(page, per_page)
    )


@mcp.tool
async def create_card_comment(card_id: int, body: str) -> dict:
    """Add a comment to a card."""
    return await _get_client().post(f"/cards/{card_id}/comments", {"body": body})


@mcp.tool
async def update_card_comment(card_id: int, comment_id: int, body: str) -> dict:
    """Update an existing comment on a card."""
    return await _get_client().put(
        f"/cards/{card_id}/comments/{comment_id}", {"body": body}
    )


@mcp.tool
async def delete_card_comment(card_id: int, comment_id: int) -> dict | str:
    """Delete a comment from a card."""
    return await _get_client().delete(f"/cards/{card_id}/comments/{comment_id}")


@mcp.tool
async def create_card_relation(card_id: int, linked_card_id: int) -> dict:
    """Create a Related Card link between two cards (Zube "Related cards" feature).

    card_id: the card that will show the link; linked_card_id: the card it is linked to.
    """
    data = {"card_id": card_id, "linked_card_id": linked_card_id}
    return await _get_client().post("/card_relations", data)


# ─── Labels ──────────────────────────────────────────────────────────────────


@mcp.tool
async def list_labels(
    project_id: int, page: int = 1, per_page: int = 30
) -> dict:
    """List all labels for a project."""
    return await _get_client().get(
        f"/projects/{project_id}/labels", _build_params(page, per_page)
    )


@mcp.tool
async def create_label(project_id: int, name: str, color: str) -> dict:
    """Create a label in a project. color: hex code without '#' (e.g. 'FF5733')."""
    return await _get_client().post(
        f"/projects/{project_id}/labels", {"name": name, "color": color}
    )


# ─── Epics ───────────────────────────────────────────────────────────────────


@mcp.tool
async def list_epics(
    project_id: int,
    page: int = 1,
    per_page: int = 30,
    state: str | None = None,
    status: str | None = None,
) -> dict:
    """List epics for a project. state: open/closed. status: new/queued/in_progress/completed/closed/archived."""
    where: dict[str, Any] = {}
    if state:
        where["state"] = state
    if status:
        where["status"] = status
    return await _get_client().get(
        f"/projects/{project_id}/epics",
        _build_params(page, per_page, where or None),
    )


@mcp.tool
async def get_epic(project_id: int, epic_id: int) -> dict:
    """Get details for a specific epic."""
    return await _get_client().get(f"/projects/{project_id}/epics/{epic_id}")


@mcp.tool
async def create_epic(
    project_id: int,
    title: str,
    description: str = "",
    assignee_id: int | None = None,
    color: str | None = None,
    due_on: str | None = None,
    label_ids: list[int] | None = None,
    track_cards: bool | None = None,
) -> dict:
    """Create an epic in a project. color: hex without '#'. due_on: ISO timestamp."""
    data = {
        "title": title,
        **_compact(
            description=description or None,
            assignee_id=assignee_id,
            color=color,
            due_on=due_on,
            label_ids=label_ids,
            track_cards=track_cards,
        ),
    }
    return await _get_client().post(f"/projects/{project_id}/epics", data)


@mcp.tool
async def update_epic(
    project_id: int,
    epic_id: int,
    title: str | None = None,
    description: str | None = None,
    assignee_id: int | None = None,
    state: str | None = None,
    status: str | None = None,
    color: str | None = None,
    due_on: str | None = None,
    label_ids: list[int] | None = None,
    track_cards: bool | None = None,
) -> dict:
    """Update an epic. state: open/closed. status: new/queued/in_progress/completed/closed/archived."""
    data = _compact(
        title=title,
        description=description,
        assignee_id=assignee_id,
        state=state,
        status=status,
        color=color,
        due_on=due_on,
        label_ids=label_ids,
        track_cards=track_cards,
    )
    return await _get_client().put(f"/projects/{project_id}/epics/{epic_id}", data)


@mcp.tool
async def list_epic_cards(
    epic_id: int, page: int = 1, per_page: int = 30
) -> dict:
    """List all cards belonging to an epic."""
    return await _get_client().get(
        f"/epics/{epic_id}/cards", _build_params(page, per_page)
    )


# ─── Sprints ─────────────────────────────────────────────────────────────────


@mcp.tool
async def list_sprints(
    workspace_id: int,
    page: int = 1,
    per_page: int = 30,
    state: str | None = None,
) -> dict:
    """List sprints for a workspace. state: open/closed."""
    where = {"state": state} if state else None
    return await _get_client().get(
        f"/workspaces/{workspace_id}/sprints",
        _build_params(page, per_page, where),
    )


@mcp.tool
async def get_sprint(workspace_id: int, sprint_id: int) -> dict:
    """Get details for a specific sprint."""
    return await _get_client().get(
        f"/workspaces/{workspace_id}/sprints/{sprint_id}"
    )


@mcp.tool
async def create_sprint(
    workspace_id: int,
    title: str,
    start_date: str,
    end_date: str,
    description: str = "",
) -> dict:
    """Create a sprint. Dates are ISO timestamps (e.g. '2026-03-01T00:00:00Z')."""
    data = {
        "title": title,
        "start_date": start_date,
        "end_date": end_date,
        **_compact(description=description or None),
    }
    return await _get_client().post(f"/workspaces/{workspace_id}/sprints", data)


@mcp.tool
async def update_sprint(
    workspace_id: int,
    sprint_id: int,
    title: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    description: str | None = None,
    state: str | None = None,
) -> dict:
    """Update a sprint. state: 'open' or 'closed'."""
    data = _compact(
        title=title,
        start_date=start_date,
        end_date=end_date,
        description=description,
        state=state,
    )
    return await _get_client().put(
        f"/workspaces/{workspace_id}/sprints/{sprint_id}", data
    )


# ─── Tickets ─────────────────────────────────────────────────────────────────


@mcp.tool
async def list_tickets(
    project_id: int,
    page: int = 1,
    per_page: int = 30,
    state: str | None = None,
    status: str | None = None,
    assignee_id: int | None = None,
    priority: int | None = None,
) -> dict:
    """List tickets for a project. state: open/closed. status: new/queued/in_progress/completed/closed/archived. priority: 1-4."""
    where: dict[str, Any] = {}
    if state:
        where["state"] = state
    if status:
        where["status"] = status
    if assignee_id is not None:
        where["assignee_id"] = assignee_id
    if priority is not None:
        where["priority"] = priority
    return await _get_client().get(
        f"/projects/{project_id}/tickets",
        _build_params(page, per_page, where or None),
    )


@mcp.tool
async def get_ticket(project_id: int, ticket_id: int) -> dict:
    """Get details for a specific ticket."""
    return await _get_client().get(f"/projects/{project_id}/tickets/{ticket_id}")


@mcp.tool
async def create_ticket(
    project_id: int,
    title: str,
    description: str = "",
    assignee_id: int | None = None,
    priority: int | None = None,
    ticket_type: str | None = None,
    due_on: str | None = None,
    start_date: str | None = None,
    customer_id: int | None = None,
    track_cards: bool | None = None,
) -> dict:
    """Create a ticket. type: task/bug/feature/question. priority: 1-4 (1=highest)."""
    data = {
        "title": title,
        **_compact(
            description=description or None,
            assignee_id=assignee_id,
            priority=priority,
            type=ticket_type,
            due_on=due_on,
            start_date=start_date,
            customer_id=customer_id,
            track_cards=track_cards,
        ),
    }
    return await _get_client().post(f"/projects/{project_id}/tickets", data)


@mcp.tool
async def update_ticket(
    project_id: int,
    ticket_id: int,
    title: str | None = None,
    description: str | None = None,
    assignee_id: int | None = None,
    priority: int | None = None,
    ticket_type: str | None = None,
    state: str | None = None,
    status: str | None = None,
    due_on: str | None = None,
    start_date: str | None = None,
    customer_id: int | None = None,
    track_cards: bool | None = None,
) -> dict:
    """Update a ticket. state: open/closed. status: new/queued/in_progress/completed/closed/archived."""
    data = _compact(
        title=title,
        description=description,
        assignee_id=assignee_id,
        priority=priority,
        type=ticket_type,
        state=state,
        status=status,
        due_on=due_on,
        start_date=start_date,
        customer_id=customer_id,
        track_cards=track_cards,
    )
    return await _get_client().put(
        f"/projects/{project_id}/tickets/{ticket_id}", data
    )


# ─── Sources ─────────────────────────────────────────────────────────────────


@mcp.tool
async def list_sources(page: int = 1, per_page: int = 30) -> dict:
    """List all connected GitHub repositories (sources)."""
    return await _get_client().get("/sources", _build_params(page, per_page))


# ─── Project Cards (scoped) ─────────────────────────────────────────────────


@mcp.tool
async def list_project_cards(
    project_id: int,
    page: int = 1,
    per_page: int = 30,
    number: int | None = None,
    state: str | None = None,
    category_name: str | None = None,
    workspace_id: int | None = None,
    assignee_ids: list[int] | None = None,
    label_names: list[str] | None = None,
    search_key: str | None = None,
    order_by: str | None = None,
    order_direction: str | None = None,
) -> dict:
    """List cards scoped to a specific project with filtering and ordering.

    number: filter by visible card number (e.g. 15293).
    assignee_ids: filter to cards assigned to these person IDs.
    label_names: filter to cards with these label names.
    """
    where: dict[str, Any] = {}
    if number is not None:
        where["number"] = number
    if state:
        where["state"] = state
    if category_name:
        where["category_name"] = category_name
    if workspace_id is not None:
        where["workspace_id"] = workspace_id
    if assignee_ids:
        where["assignee_ids"] = assignee_ids
    if label_names:
        where["labels"] = label_names
    if search_key:
        where["search_key"] = search_key
    return await _get_client().get(
        f"/projects/{project_id}/cards",
        _build_params(page, per_page, where or None, order_by, order_direction),
    )


@mcp.tool
async def list_triage_cards(project_id: int) -> dict:
    """List cards in a project's triage (unassigned to any workspace column)."""
    return await _get_client().get(f"/projects/{project_id}/triage_cards")


# ─── Members ─────────────────────────────────────────────────────────────────


@mcp.tool
async def list_project_members(
    project_id: int, page: int = 1, per_page: int = 30
) -> dict:
    """List all members of a project."""
    return await _get_client().get(
        f"/projects/{project_id}/members", _build_params(page, per_page)
    )


@mcp.tool
async def list_account_members(
    account_id: int, page: int = 1, per_page: int = 30
) -> dict:
    """List all members of an account (organization)."""
    return await _get_client().get(
        f"/accounts/{account_id}/members", _build_params(page, per_page)
    )


# ─── Entrypoint ──────────────────────────────────────────────────────────────


def main():
    mcp.run()


if __name__ == "__main__":
    main()
