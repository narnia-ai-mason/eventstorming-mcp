#!/usr/bin/env python3
"""
Event Storming MCP Server

A comprehensive MCP server for conducting Domain-Driven Design Event Storming workshops
in a text-based environment. Supports all core Event Storming elements with structured
JSON storage, bounded context management, and analysis tools.

Features:
- Workshop session management
- Core DDD elements: Events, Commands, Actors, Aggregates, Policies, Read Models
- Bounded Context definition and grouping
- Timeline and flow visualization
- Search, statistics, and analysis
- Import/Export capabilities
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# CONSTANTS
# ============================================================================

CHARACTER_LIMIT = 25000
STORAGE_DIR = Path.home() / ".eventstorming_workshops"
STORAGE_DIR.mkdir(exist_ok=True)

# ============================================================================
# ENUMS
# ============================================================================


class ElementType(str, Enum):
    """Types of Event Storming elements."""

    EVENT = "event"
    COMMAND = "command"
    ACTOR = "actor"
    AGGREGATE = "aggregate"
    POLICY = "policy"
    READ_MODEL = "read_model"
    EXTERNAL_SYSTEM = "external_system"
    HOTSPOT = "hotspot"


class ResponseFormat(str, Enum):
    """Output format for tool responses."""

    MARKDOWN = "markdown"
    JSON = "json"


class DetailLevel(str, Enum):
    """Detail level for element responses."""

    SUMMARY = "summary"  # Essential fields only (id, type, name, position)
    FULL = "full"  # All fields including notes, relationships, etc.


# Traditional Event Storming color scheme
ELEMENT_COLORS = {
    ElementType.EVENT: "orange",
    ElementType.COMMAND: "blue",
    ElementType.ACTOR: "yellow",
    ElementType.AGGREGATE: "pale_yellow",
    ElementType.POLICY: "lilac",
    ElementType.READ_MODEL: "green",
    ElementType.EXTERNAL_SYSTEM: "pink",
    ElementType.HOTSPOT: "red",
}

# ============================================================================
# DATA MODELS
# ============================================================================


class WorkshopMetadata(BaseModel):
    """Metadata for an Event Storming workshop."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    id: str = Field(..., description="Unique workshop identifier")
    name: str = Field(..., description="Workshop name", min_length=1, max_length=200)
    description: Optional[str] = Field(default="", description="Workshop description")
    domain: Optional[str] = Field(default="", description="Domain/project name")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    updated_at: str = Field(..., description="Last update timestamp (ISO format)")
    facilitators: List[str] = Field(
        default_factory=list, description="Workshop facilitators"
    )
    schema_version: str = Field(
        default="2.0", description="Data schema version for migration tracking"
    )


class BoundedContext(BaseModel):
    """A bounded context in DDD."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    id: str = Field(..., description="Unique context identifier")
    name: str = Field(..., description="Context name", min_length=1, max_length=100)
    description: Optional[str] = Field(default="", description="Context description")
    element_ids: List[str] = Field(
        default_factory=list, description="IDs of elements in this context"
    )
    color: Optional[str] = Field(default=None, description="Visual color code")


class EventStormingElement(BaseModel):
    """Base model for all Event Storming elements."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    id: str = Field(..., description="Unique element identifier")
    type: ElementType = Field(..., description="Element type")
    name: str = Field(..., description="Element name", min_length=1, max_length=200)
    position: int = Field(default=0, description="Position in timeline (0-based)")
    notes: Optional[str] = Field(
        default="", description="Notes and detailed description"
    )
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    created_by: Optional[str] = Field(default="", description="Creator name")

    # Relationships
    triggers: List[str] = Field(
        default_factory=list, description="IDs of elements this triggers"
    )
    triggered_by: List[str] = Field(
        default_factory=list, description="IDs of elements that trigger this"
    )

    # Context assignment
    bounded_context_id: Optional[str] = Field(
        default=None, description="Assigned bounded context ID"
    )


class Workshop(BaseModel):
    """Complete Event Storming workshop data."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    metadata: WorkshopMetadata
    elements: List[EventStormingElement] = Field(default_factory=list)
    bounded_contexts: List[BoundedContext] = Field(default_factory=list)


class PaginationInfo(BaseModel):
    """Pagination metadata for paginated responses."""

    model_config = ConfigDict(str_strip_whitespace=True)

    page: int = Field(..., description="Current page number (1-indexed)", ge=1)
    page_size: int = Field(..., description="Number of items per page", ge=1)
    total_items: int = Field(..., description="Total number of items", ge=0)
    total_pages: int = Field(..., description="Total number of pages", ge=0)
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


# ============================================================================
# INPUT MODELS
# ============================================================================


class CreateWorkshopInput(BaseModel):
    """Input for creating a new workshop."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    name: str = Field(
        ...,
        description="Workshop name (e.g., 'E-commerce Order Management', 'Healthcare Patient Journey')",
        min_length=1,
        max_length=200,
    )
    description: Optional[str] = Field(
        default="", description="Workshop description and goals", max_length=1000
    )
    domain: Optional[str] = Field(
        default="",
        description="Domain or project name (e.g., 'E-commerce', 'Healthcare')",
        max_length=100,
    )
    facilitators: List[str] = Field(
        default_factory=list, description="Names of workshop facilitators", max_items=10
    )


class LoadWorkshopInput(BaseModel):
    """Input for loading a workshop."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    workshop_id: str = Field(
        ..., description="Workshop ID to load (from list_workshops)", min_length=1
    )
    detail_level: DetailLevel = Field(
        default=DetailLevel.SUMMARY,
        description="Detail level: summary (stats + essential fields) or full (all data)",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format"
    )


class AddElementInput(BaseModel):
    """Input for adding an Event Storming element."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    workshop_id: str = Field(..., description="Workshop ID", min_length=1)
    type: ElementType = Field(..., description="Element type")
    name: str = Field(
        ...,
        description="Element name (e.g., 'Order Placed', 'Place Order', 'Customer')",
        min_length=1,
        max_length=200,
    )
    position: Optional[int] = Field(
        default=None,
        description="Position in timeline (auto-assigned if not provided)",
        ge=0,
    )
    notes: Optional[str] = Field(
        default="",
        description="Notes and detailed description",
        max_length=2000,
    )
    created_by: Optional[str] = Field(
        default="", description="Creator name", max_length=100
    )
    triggers: List[str] = Field(
        default_factory=list, description="Element IDs this triggers", max_items=20
    )
    triggered_by: List[str] = Field(
        default_factory=list, description="Element IDs that trigger this", max_items=20
    )
    bounded_context_id: Optional[str] = Field(
        default=None, description="Bounded context to assign to"
    )


class UpdateElementInput(BaseModel):
    """Input for updating an element."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    workshop_id: str = Field(..., description="Workshop ID", min_length=1)
    element_id: str = Field(..., description="Element ID to update", min_length=1)
    name: Optional[str] = Field(
        default=None, description="New name", min_length=1, max_length=200
    )
    position: Optional[int] = Field(default=None, description="New position", ge=0)
    notes: Optional[str] = Field(
        default=None, description="New notes and description", max_length=2000
    )
    triggers: Optional[List[str]] = Field(
        default=None, description="New triggers list", max_items=20
    )
    triggered_by: Optional[List[str]] = Field(
        default=None, description="New triggered_by list", max_items=20
    )
    bounded_context_id: Optional[str] = Field(
        default=None, description="New bounded context (use 'null' to remove)"
    )


class DeleteElementInput(BaseModel):
    """Input for deleting an element."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    workshop_id: str = Field(..., description="Workshop ID", min_length=1)
    element_id: str = Field(..., description="Element ID to delete", min_length=1)


class CreateBoundedContextInput(BaseModel):
    """Input for creating a bounded context."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    workshop_id: str = Field(..., description="Workshop ID", min_length=1)
    name: str = Field(
        ...,
        description="Context name (e.g., 'Order Management', 'Payment Processing')",
        min_length=1,
        max_length=100,
    )
    description: Optional[str] = Field(
        default="",
        description="Context description and responsibilities",
        max_length=1000,
    )
    color: Optional[str] = Field(
        default=None, description="Visual color code (e.g., '#FF5733')", max_length=20
    )


class AssignToContextInput(BaseModel):
    """Input for assigning elements to a bounded context."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    workshop_id: str = Field(..., description="Workshop ID", min_length=1)
    context_id: str = Field(..., description="Bounded context ID", min_length=1)
    element_ids: List[str] = Field(
        ..., description="Element IDs to assign", min_items=1, max_items=100
    )


class SearchElementsInput(BaseModel):
    """Input for searching elements."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    workshop_id: str = Field(..., description="Workshop ID", min_length=1)
    query: str = Field(
        ...,
        description="Search query (searches in name and notes)",
        min_length=1,
        max_length=200,
    )
    element_type: Optional[ElementType] = Field(
        default=None, description="Filter by element type"
    )
    bounded_context_id: Optional[str] = Field(
        default=None, description="Filter by bounded context"
    )
    page: int = Field(default=1, description="Page number (1-indexed)", ge=1)
    page_size: int = Field(
        default=50, description="Items per page", ge=1, le=200
    )
    detail_level: DetailLevel = Field(
        default=DetailLevel.SUMMARY,
        description="Detail level: summary (essential fields) or full (all fields)",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format"
    )


class GetTimelineInput(BaseModel):
    """Input for viewing timeline."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    workshop_id: str = Field(..., description="Workshop ID", min_length=1)
    element_type: Optional[ElementType] = Field(
        default=None, description="Filter by element type"
    )
    bounded_context_id: Optional[str] = Field(
        default=None, description="Filter by bounded context"
    )
    page: int = Field(default=1, description="Page number (1-indexed)", ge=1)
    page_size: int = Field(
        default=50, description="Items per page", ge=1, le=200
    )
    detail_level: DetailLevel = Field(
        default=DetailLevel.SUMMARY,
        description="Detail level: summary (essential fields) or full (all fields)",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format"
    )


class GetContextOverviewInput(BaseModel):
    """Input for bounded context overview."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    workshop_id: str = Field(..., description="Workshop ID", min_length=1)
    context_id: Optional[str] = Field(
        default=None, description="Specific context ID (shows all if not provided)"
    )
    page: int = Field(default=1, description="Page number for elements (1-indexed)", ge=1)
    page_size: int = Field(
        default=50, description="Items per page for elements", ge=1, le=200
    )
    detail_level: DetailLevel = Field(
        default=DetailLevel.SUMMARY,
        description="Detail level: summary (essential fields) or full (all fields)",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format"
    )


class GetStatisticsInput(BaseModel):
    """Input for workshop statistics."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    workshop_id: str = Field(..., description="Workshop ID", min_length=1)
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format"
    )


class ExportWorkshopInput(BaseModel):
    """Input for exporting workshop."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    workshop_id: str = Field(..., description="Workshop ID", min_length=1)
    include_metadata: bool = Field(
        default=True, description="Include workshop metadata"
    )


class ImportWorkshopInput(BaseModel):
    """Input for importing workshop."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    workshop_data: str = Field(
        ..., description="JSON workshop data (from export)", min_length=1
    )
    new_name: Optional[str] = Field(
        default=None,
        description="Optional new name for imported workshop",
        max_length=200,
    )


class VisualizeFlowInput(BaseModel):
    """Input for visualizing event flow."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    workshop_id: str = Field(..., description="Workshop ID", min_length=1)
    start_element_id: Optional[str] = Field(
        default=None,
        description="Start from specific element (shows all flows if not provided)",
    )
    max_depth: int = Field(
        default=5, description="Maximum depth to traverse", ge=1, le=20
    )
    max_elements: int = Field(
        default=100,
        description="Maximum number of elements to display in flow",
        ge=1,
        le=500,
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """Get current ISO timestamp."""
    return datetime.utcnow().isoformat() + "Z"


def get_workshop_path(workshop_id: str) -> Path:
    """Get file path for a workshop."""
    return STORAGE_DIR / f"{workshop_id}.json"


def save_workshop(workshop: Workshop) -> None:
    """Save workshop to disk."""
    workshop.metadata.updated_at = get_timestamp()
    path = get_workshop_path(workshop.metadata.id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(workshop.model_dump(), f, indent=2, ensure_ascii=False)


def migrate_workshop_data(data: dict) -> dict:
    """Migrate old workshop data to current schema (v2.0).

    Changes in v2.0:
    - Removed EventStormingElement.description field
    - Merged description content into notes field
    - Added WorkshopMetadata.schema_version field

    Args:
        data: Raw workshop data dictionary

    Returns:
        Migrated data dictionary compatible with v2.0 schema
    """
    # Check schema version
    schema_version = data.get("metadata", {}).get("schema_version", "1.0")

    if schema_version == "2.0":
        # Already migrated
        return data

    # Migrate elements: description → notes
    for element in data.get("elements", []):
        if "description" in element:
            description = element.get("description", "").strip()
            notes = element.get("notes", "").strip()

            # Merge description into notes (description comes first)
            if description and notes:
                element["notes"] = f"{description}\n\n{notes}"
            elif description:
                element["notes"] = description
            elif not notes:
                element["notes"] = ""

            # Remove description field
            del element["description"]

        # Ensure notes field exists
        if "notes" not in element:
            element["notes"] = ""

    # Add schema_version to metadata
    if "metadata" in data:
        data["metadata"]["schema_version"] = "2.0"

    return data


def load_workshop(workshop_id: str) -> Workshop:
    """Load workshop from disk with automatic schema migration."""
    path = get_workshop_path(workshop_id)
    if not path.exists():
        raise FileNotFoundError(f"Workshop not found: {workshop_id}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Automatic migration
    data = migrate_workshop_data(data)

    return Workshop(**data)


def format_element_markdown(element: EventStormingElement) -> str:
    """Format a single element as markdown."""
    color = ELEMENT_COLORS.get(element.type, "gray")
    lines = [
        f"**[{element.type.value.upper()}]** {element.name} `{element.id}` ({color})",
        f"  Position: {element.position}",
    ]

    if element.notes:
        lines.append(f"  Notes: {element.notes}")

    if element.bounded_context_id:
        lines.append(f"  Context: {element.bounded_context_id}")

    if element.triggered_by:
        lines.append(f"  Triggered by: {', '.join(element.triggered_by)}")

    if element.triggers:
        lines.append(f"  Triggers: {', '.join(element.triggers)}")

    return "\n".join(lines)


def paginate_list(
    items: List, page: int = 1, page_size: int = 50
) -> tuple[List, PaginationInfo]:
    """Paginate a list and return items with pagination metadata.

    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (paginated_items, pagination_info)
    """
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0

    # Clamp page to valid range
    page = max(1, min(page, total_pages if total_pages > 0 else 1))

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_items = items[start_idx:end_idx]

    pagination_info = PaginationInfo(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    return paginated_items, pagination_info


def format_element_summary(element: EventStormingElement) -> dict:
    """Format element with summary-level detail (essential fields only).

    Args:
        element: Element to format

    Returns:
        Dictionary with essential fields only
    """
    return {
        "id": element.id,
        "type": element.type.value,
        "name": element.name,
        "position": element.position,
        "bounded_context_id": element.bounded_context_id,
    }


def format_pagination_markdown(pagination: PaginationInfo) -> str:
    """Format pagination info as markdown.

    Args:
        pagination: Pagination metadata

    Returns:
        Markdown string with pagination info
    """
    lines = [
        f"**Page {pagination.page} of {pagination.total_pages}** "
        f"(showing {len(range((pagination.page - 1) * pagination.page_size, min(pagination.page * pagination.page_size, pagination.total_items)))} "
        f"of {pagination.total_items} items)"
    ]

    hints = []
    if pagination.has_next:
        hints.append(f"Use `page={pagination.page + 1}` for next page")
    if pagination.has_prev:
        hints.append(f"Use `page={pagination.page - 1}` for previous page")

    if hints:
        lines.append("💡 " + " | ".join(hints))

    return "\n".join(lines)


def truncate_response(content: str, data_count: int, suggestion: str = "") -> str:
    """Truncate response if needed."""
    if len(content) <= CHARACTER_LIMIT:
        return content

    truncated = content[:CHARACTER_LIMIT]
    message = f"\n\n⚠️ Response truncated (showing ~{len(truncated)}/{len(content)} characters)"
    if suggestion:
        message += f"\n💡 {suggestion}"

    return truncated + message


# ============================================================================
# MCP SERVER INITIALIZATION
# ============================================================================

mcp = FastMCP("eventstorming_mcp")

# ============================================================================
# WORKSHOP MANAGEMENT TOOLS
# ============================================================================


@mcp.tool(
    name="eventstorming_create_workshop",
    annotations={
        "title": "Create Event Storming Workshop",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def create_workshop(params: CreateWorkshopInput) -> str:
    """Create a new Event Storming workshop session.

    This creates a new workshop with the specified metadata and returns the workshop ID
    that can be used for all subsequent operations. The workshop is saved to disk and
    can be loaded later.

    Args:
        params (CreateWorkshopInput): Workshop creation parameters containing:
            - name (str): Workshop name
            - description (Optional[str]): Workshop description
            - domain (Optional[str]): Domain/project name
            - facilitators (List[str]): Facilitator names

    Returns:
        str: JSON response with workshop ID and confirmation
    """
    workshop_id = generate_id()
    timestamp = get_timestamp()

    metadata = WorkshopMetadata(
        id=workshop_id,
        name=params.name,
        description=params.description or "",
        domain=params.domain or "",
        created_at=timestamp,
        updated_at=timestamp,
        facilitators=params.facilitators,
    )

    workshop = Workshop(metadata=metadata)
    save_workshop(workshop)

    response = {
        "success": True,
        "workshop_id": workshop_id,
        "name": params.name,
        "message": f"Workshop '{params.name}' created successfully",
        "storage_path": str(get_workshop_path(workshop_id)),
    }

    return json.dumps(response, indent=2)


@mcp.tool(
    name="eventstorming_list_workshops",
    annotations={
        "title": "List Event Storming Workshops",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def list_workshops() -> str:
    """List all available Event Storming workshops.

    Returns a list of all workshops stored on disk with their basic metadata.
    Use the workshop_id from this list to load a specific workshop.

    Returns:
        str: JSON array of workshops with id, name, domain, created_at, updated_at
    """
    workshops = []

    for path in STORAGE_DIR.glob("*.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            workshops.append(
                {
                    "id": data["metadata"]["id"],
                    "name": data["metadata"]["name"],
                    "domain": data["metadata"].get("domain", ""),
                    "created_at": data["metadata"]["created_at"],
                    "updated_at": data["metadata"]["updated_at"],
                    "element_count": len(data.get("elements", [])),
                    "context_count": len(data.get("bounded_contexts", [])),
                }
            )
        except Exception:
            continue

    workshops.sort(key=lambda x: x["updated_at"], reverse=True)

    return json.dumps({"workshops": workshops, "total": len(workshops)}, indent=2)


@mcp.tool(
    name="eventstorming_load_workshop",
    annotations={
        "title": "Load Event Storming Workshop",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def load_workshop_tool(params: LoadWorkshopInput) -> str:
    """Load an existing Event Storming workshop with all its data.

    Loads the complete workshop including all elements, bounded contexts, and metadata.
    Use this to continue working on a previously created workshop.

    Args:
        params (LoadWorkshopInput): Parameters containing:
            - workshop_id (str): Workshop ID from list_workshops
            - detail_level (DetailLevel): summary (stats only) or full (all data)
            - response_format (ResponseFormat): Output format (markdown or json)

    Returns:
        str: Workshop data in specified format
    """
    try:
        workshop = load_workshop(params.workshop_id)
    except FileNotFoundError as e:
        return json.dumps(
            {
                "error": str(e),
                "suggestion": "Use eventstorming_list_workshops to see available workshops",
            },
            indent=2,
        )

    if params.response_format == ResponseFormat.JSON:
        if params.detail_level == DetailLevel.SUMMARY:
            # Return summary with element list (essential fields only)
            return json.dumps(
                {
                    "metadata": workshop.metadata.model_dump(),
                    "elements": [
                        format_element_summary(e) for e in workshop.elements
                    ],
                    "bounded_contexts": [
                        {
                            "id": ctx.id,
                            "name": ctx.name,
                            "element_count": len(ctx.element_ids),
                        }
                        for ctx in workshop.bounded_contexts
                    ],
                    "statistics": {
                        "total_elements": len(workshop.elements),
                        "total_contexts": len(workshop.bounded_contexts),
                    },
                },
                indent=2,
            )
        else:
            # FULL: Return all data
            return json.dumps(workshop.model_dump(), indent=2)

    # Markdown format
    lines = [
        f"# Workshop: {workshop.metadata.name}",
        f"**ID**: `{workshop.metadata.id}`",
        f"**Domain**: {workshop.metadata.domain or 'Not specified'}",
        f"**Created**: {workshop.metadata.created_at}",
        f"**Updated**: {workshop.metadata.updated_at}",
        "",
    ]

    if workshop.metadata.description:
        lines.extend([f"**Description**: {workshop.metadata.description}", ""])

    if workshop.metadata.facilitators:
        lines.extend(
            [f"**Facilitators**: {', '.join(workshop.metadata.facilitators)}", ""]
        )

    lines.extend(
        [
            "## Statistics",
            f"- Total Elements: {len(workshop.elements)}",
            f"- Bounded Contexts: {len(workshop.bounded_contexts)}",
            "",
        ]
    )

    # Count by type
    type_counts = {}
    for element in workshop.elements:
        type_counts[element.type] = type_counts.get(element.type, 0) + 1

    if type_counts:
        lines.append("### Elements by Type")
        for elem_type, count in sorted(type_counts.items()):
            lines.append(f"- {elem_type.value}: {count}")
        lines.append("")

    if workshop.bounded_contexts:
        lines.append("## Bounded Contexts")
        for ctx in workshop.bounded_contexts:
            lines.append(
                f"- **{ctx.name}** (`{ctx.id}`): {len(ctx.element_ids)} elements"
            )
        lines.append("")

    # Add element list if SUMMARY level
    if params.detail_level == DetailLevel.SUMMARY and workshop.elements:
        lines.append("## Elements (Summary)")
        for element in sorted(workshop.elements, key=lambda e: (e.type.value, e.position)):
            lines.append(
                f"- [{element.type.value}] **{element.name}** "
                f"(pos: {element.position}, id: `{element.id}`)"
            )
        lines.append("")
        lines.append("💡 Use `detail_level=full` to see all element details")

    content = "\n".join(lines)
    return truncate_response(
        content,
        len(workshop.elements),
        "Use specific queries to explore elements and contexts",
    )


# ============================================================================
# ELEMENT MANAGEMENT TOOLS
# ============================================================================


@mcp.tool(
    name="eventstorming_add_element",
    annotations={
        "title": "Add Event Storming Element",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def add_element(params: AddElementInput) -> str:
    """Add a new element to the Event Storming workshop.

    Creates a new element (Event, Command, Actor, Aggregate, Policy, Read Model,
    External System, or Hotspot) and adds it to the workshop. Elements can be
    linked to show relationships and assigned to bounded contexts.

    Args:
        params (AddElementInput): Element parameters containing:
            - workshop_id (str): Workshop ID
            - type (ElementType): Element type
            - name (str): Element name
            - position (Optional[int]): Timeline position
            - notes (Optional[str]): Notes and detailed description
            - created_by (Optional[str]): Creator name
            - triggers (List[str]): Element IDs this triggers
            - triggered_by (List[str]): Element IDs that trigger this
            - bounded_context_id (Optional[str]): Context to assign to

    Returns:
        str: JSON response with element ID and confirmation
    """
    try:
        workshop = load_workshop(params.workshop_id)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)}, indent=2)

    element_id = generate_id()
    timestamp = get_timestamp()

    # Auto-assign position if not provided
    position = params.position
    if position is None:
        position = len([e for e in workshop.elements if e.type == params.type])

    element = EventStormingElement(
        id=element_id,
        type=params.type,
        name=params.name,
        position=position,
        notes=params.notes or "",
        created_at=timestamp,
        updated_at=timestamp,
        created_by=params.created_by or "",
        triggers=params.triggers,
        triggered_by=params.triggered_by,
        bounded_context_id=params.bounded_context_id,
    )

    workshop.elements.append(element)

    # Update bounded context if assigned
    if params.bounded_context_id:
        for ctx in workshop.bounded_contexts:
            if ctx.id == params.bounded_context_id:
                if element_id not in ctx.element_ids:
                    ctx.element_ids.append(element_id)
                break

    save_workshop(workshop)

    return json.dumps(
        {
            "success": True,
            "element_id": element_id,
            "type": params.type.value,
            "name": params.name,
            "position": position,
            "message": f"{params.type.value.title()} '{params.name}' added successfully",
        },
        indent=2,
    )


@mcp.tool(
    name="eventstorming_update_element",
    annotations={
        "title": "Update Event Storming Element",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def update_element(params: UpdateElementInput) -> str:
    """Update an existing Event Storming element.

    Modifies the properties of an existing element. Only provided fields will be updated.
    Use this to refine elements as the workshop progresses.

    Args:
        params (UpdateElementInput): Update parameters containing:
            - workshop_id (str): Workshop ID
            - element_id (str): Element ID to update
            - name (Optional[str]): New name
            - position (Optional[int]): New position
            - notes (Optional[str]): New notes and description
            - triggers (Optional[List[str]]): New triggers
            - triggered_by (Optional[List[str]]): New triggered_by
            - bounded_context_id (Optional[str]): New context

    Returns:
        str: JSON response with confirmation
    """
    try:
        workshop = load_workshop(params.workshop_id)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)}, indent=2)

    element = next((e for e in workshop.elements if e.id == params.element_id), None)
    if not element:
        return json.dumps(
            {"error": f"Element not found: {params.element_id}"}, indent=2
        )

    # Update fields
    updated_fields = []
    if params.name is not None:
        element.name = params.name
        updated_fields.append("name")
    if params.position is not None:
        element.position = params.position
        updated_fields.append("position")
    if params.notes is not None:
        element.notes = params.notes
        updated_fields.append("notes")
    if params.triggers is not None:
        element.triggers = params.triggers
        updated_fields.append("triggers")
    if params.triggered_by is not None:
        element.triggered_by = params.triggered_by
        updated_fields.append("triggered_by")

    # Handle context change
    old_context = element.bounded_context_id
    if params.bounded_context_id is not None:
        new_context = (
            params.bounded_context_id if params.bounded_context_id != "null" else None
        )
        element.bounded_context_id = new_context
        updated_fields.append("bounded_context_id")

        # Update context element lists
        for ctx in workshop.bounded_contexts:
            if ctx.id == old_context and element.id in ctx.element_ids:
                ctx.element_ids.remove(element.id)
            if ctx.id == new_context and element.id not in ctx.element_ids:
                ctx.element_ids.append(element.id)

    element.updated_at = get_timestamp()
    save_workshop(workshop)

    return json.dumps(
        {
            "success": True,
            "element_id": params.element_id,
            "updated_fields": updated_fields,
            "message": "Element updated successfully",
        },
        indent=2,
    )


@mcp.tool(
    name="eventstorming_delete_element",
    annotations={
        "title": "Delete Event Storming Element",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def delete_element(params: DeleteElementInput) -> str:
    """Delete an Event Storming element from the workshop.

    Permanently removes an element and cleans up all references to it in
    triggers, triggered_by relationships, and bounded context assignments.

    Args:
        params (DeleteElementInput): Parameters containing:
            - workshop_id (str): Workshop ID
            - element_id (str): Element ID to delete

    Returns:
        str: JSON response with confirmation
    """
    try:
        workshop = load_workshop(params.workshop_id)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)}, indent=2)

    element = next((e for e in workshop.elements if e.id == params.element_id), None)
    if not element:
        return json.dumps(
            {"error": f"Element not found: {params.element_id}"}, indent=2
        )

    element_name = element.name
    element_type = element.type.value

    # Remove element
    workshop.elements = [e for e in workshop.elements if e.id != params.element_id]

    # Clean up references in other elements
    for e in workshop.elements:
        e.triggers = [t for t in e.triggers if t != params.element_id]
        e.triggered_by = [t for t in e.triggered_by if t != params.element_id]

    # Clean up bounded context references
    for ctx in workshop.bounded_contexts:
        ctx.element_ids = [eid for eid in ctx.element_ids if eid != params.element_id]

    save_workshop(workshop)

    return json.dumps(
        {
            "success": True,
            "deleted_element": {
                "id": params.element_id,
                "name": element_name,
                "type": element_type,
            },
            "message": f"{element_type.title()} '{element_name}' deleted successfully",
        },
        indent=2,
    )


# ============================================================================
# BOUNDED CONTEXT TOOLS
# ============================================================================


@mcp.tool(
    name="eventstorming_create_bounded_context",
    annotations={
        "title": "Create Bounded Context",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def create_bounded_context(params: CreateBoundedContextInput) -> str:
    """Create a new bounded context in the workshop.

    Bounded contexts are a key DDD concept that group related elements together
    to define clear boundaries in the domain model. Elements can be assigned
    to contexts to show their organizational structure.

    Args:
        params (CreateBoundedContextInput): Parameters containing:
            - workshop_id (str): Workshop ID
            - name (str): Context name
            - description (Optional[str]): Context description
            - color (Optional[str]): Visual color code

    Returns:
        str: JSON response with context ID and confirmation
    """
    try:
        workshop = load_workshop(params.workshop_id)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)}, indent=2)

    context_id = generate_id()

    context = BoundedContext(
        id=context_id,
        name=params.name,
        description=params.description or "",
        color=params.color,
    )

    workshop.bounded_contexts.append(context)
    save_workshop(workshop)

    return json.dumps(
        {
            "success": True,
            "context_id": context_id,
            "name": params.name,
            "message": f"Bounded context '{params.name}' created successfully",
        },
        indent=2,
    )


@mcp.tool(
    name="eventstorming_assign_to_context",
    annotations={
        "title": "Assign Elements to Bounded Context",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def assign_to_context(params: AssignToContextInput) -> str:
    """Assign multiple elements to a bounded context.

    Groups elements together by assigning them to the same bounded context.
    This helps organize the domain model into cohesive boundaries.

    Args:
        params (AssignToContextInput): Parameters containing:
            - workshop_id (str): Workshop ID
            - context_id (str): Bounded context ID
            - element_ids (List[str]): Element IDs to assign

    Returns:
        str: JSON response with assignment confirmation
    """
    try:
        workshop = load_workshop(params.workshop_id)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)}, indent=2)

    context = next(
        (c for c in workshop.bounded_contexts if c.id == params.context_id), None
    )
    if not context:
        return json.dumps(
            {"error": f"Bounded context not found: {params.context_id}"}, indent=2
        )

    assigned = []
    not_found = []

    for element_id in params.element_ids:
        element = next((e for e in workshop.elements if e.id == element_id), None)
        if element:
            element.bounded_context_id = params.context_id
            if element_id not in context.element_ids:
                context.element_ids.append(element_id)
            assigned.append(element_id)
        else:
            not_found.append(element_id)

    save_workshop(workshop)

    response = {
        "success": True,
        "context_name": context.name,
        "assigned_count": len(assigned),
        "assigned_elements": assigned,
    }

    if not_found:
        response["warnings"] = f"Elements not found: {', '.join(not_found)}"

    return json.dumps(response, indent=2)


# ============================================================================
# QUERY AND ANALYSIS TOOLS
# ============================================================================


@mcp.tool(
    name="eventstorming_search_elements",
    annotations={
        "title": "Search Event Storming Elements",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def search_elements(params: SearchElementsInput) -> str:
    """Search for elements in the workshop by keyword.

    Searches through element names and notes to find matching elements.
    Results can be filtered by type and bounded context. Supports pagination.

    Args:
        params (SearchElementsInput): Parameters containing:
            - workshop_id (str): Workshop ID
            - query (str): Search query
            - element_type (Optional[ElementType]): Filter by type
            - bounded_context_id (Optional[str]): Filter by context
            - page (int): Page number (default: 1)
            - page_size (int): Items per page (default: 50)
            - detail_level (DetailLevel): summary or full (default: summary)
            - response_format (ResponseFormat): Output format

    Returns:
        str: Matching elements in specified format with pagination
    """
    try:
        workshop = load_workshop(params.workshop_id)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)}, indent=2)

    query_lower = params.query.lower()
    matches = []

    for element in workshop.elements:
        # Type filter
        if params.element_type and element.type != params.element_type:
            continue

        # Context filter
        if (
            params.bounded_context_id
            and element.bounded_context_id != params.bounded_context_id
        ):
            continue

        # Search in name and notes
        if query_lower in element.name.lower() or query_lower in element.notes.lower():
            matches.append(element)

    # Apply pagination
    paginated_matches, pagination = paginate_list(
        matches, params.page, params.page_size
    )

    if params.response_format == ResponseFormat.JSON:
        if params.detail_level == DetailLevel.SUMMARY:
            elements_data = [format_element_summary(e) for e in paginated_matches]
        else:
            elements_data = [e.model_dump() for e in paginated_matches]

        return json.dumps(
            {
                "query": params.query,
                "matches": elements_data,
                "pagination": pagination.model_dump(),
            },
            indent=2,
        )

    # Markdown format
    lines = [
        f"# Search Results: '{params.query}'",
        f"Found {pagination.total_items} matching element(s)",
        "",
        format_pagination_markdown(pagination),
        "",
    ]

    if paginated_matches:
        for element in paginated_matches:
            if params.detail_level == DetailLevel.SUMMARY:
                lines.append(
                    f"- [{element.type.value}] **{element.name}** "
                    f"(pos: {element.position}, id: `{element.id}`)"
                )
            else:
                lines.append(format_element_markdown(element))
                lines.append("")
    else:
        lines.append("No matching elements found on this page.")

    content = "\n".join(lines)
    return content


@mcp.tool(
    name="eventstorming_get_timeline",
    annotations={
        "title": "Get Event Timeline",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_timeline(params: GetTimelineInput) -> str:
    """View elements in timeline order.

    Shows elements arranged by their position in the timeline, which represents
    the chronological flow of events in the domain. Can be filtered by type
    or bounded context. Supports pagination.

    Args:
        params (GetTimelineInput): Parameters containing:
            - workshop_id (str): Workshop ID
            - element_type (Optional[ElementType]): Filter by type
            - bounded_context_id (Optional[str]): Filter by context
            - page (int): Page number (default: 1)
            - page_size (int): Items per page (default: 50)
            - detail_level (DetailLevel): summary or full (default: summary)
            - response_format (ResponseFormat): Output format

    Returns:
        str: Timeline view in specified format with pagination
    """
    try:
        workshop = load_workshop(params.workshop_id)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)}, indent=2)

    # Filter elements
    elements = workshop.elements
    if params.element_type:
        elements = [e for e in elements if e.type == params.element_type]
    if params.bounded_context_id:
        elements = [
            e for e in elements if e.bounded_context_id == params.bounded_context_id
        ]

    # Sort by position
    elements = sorted(elements, key=lambda e: (e.position, e.created_at))

    # Apply pagination
    paginated_elements, pagination = paginate_list(
        elements, params.page, params.page_size
    )

    if params.response_format == ResponseFormat.JSON:
        if params.detail_level == DetailLevel.SUMMARY:
            elements_data = [format_element_summary(e) for e in paginated_elements]
        else:
            elements_data = [e.model_dump() for e in paginated_elements]

        return json.dumps(
            {"timeline": elements_data, "pagination": pagination.model_dump()},
            indent=2,
        )

    # Markdown format
    lines = [f"# Timeline: {workshop.metadata.name}", ""]

    if params.element_type:
        lines.append(f"Filter: {params.element_type.value}")
    if params.bounded_context_id:
        ctx = next(
            (c for c in workshop.bounded_contexts if c.id == params.bounded_context_id),
            None,
        )
        if ctx:
            lines.append(f"Context: {ctx.name}")

    lines.extend(["", format_pagination_markdown(pagination), ""])

    if paginated_elements:
        current_position = None
        for element in paginated_elements:
            if params.detail_level == DetailLevel.FULL:
                if element.position != current_position:
                    current_position = element.position
                    lines.append(f"\n## Position {current_position}")
                lines.append(format_element_markdown(element))
                lines.append("")
            else:
                lines.append(
                    f"- [{element.type.value}] **{element.name}** "
                    f"(pos: {element.position}, id: `{element.id}`)"
                )
    else:
        lines.append("No elements found on this page.")

    content = "\n".join(lines)
    return content


@mcp.tool(
    name="eventstorming_get_context_overview",
    annotations={
        "title": "Get Bounded Context Overview",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_context_overview(params: GetContextOverviewInput) -> str:
    """View bounded context details and their elements.

    Shows information about bounded contexts including their assigned elements,
    relationships, and statistics. Provides a high-level view of domain organization.
    Supports pagination for elements within contexts.

    Args:
        params (GetContextOverviewInput): Parameters containing:
            - workshop_id (str): Workshop ID
            - context_id (Optional[str]): Specific context (all if not provided)
            - page (int): Page number for elements (default: 1)
            - page_size (int): Items per page for elements (default: 50)
            - detail_level (DetailLevel): summary or full (default: summary)
            - response_format (ResponseFormat): Output format

    Returns:
        str: Context overview in specified format with pagination
    """
    try:
        workshop = load_workshop(params.workshop_id)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)}, indent=2)

    contexts = workshop.bounded_contexts
    if params.context_id:
        contexts = [c for c in contexts if c.id == params.context_id]

    if params.response_format == ResponseFormat.JSON:
        result = []
        for ctx in contexts:
            elements = [e for e in workshop.elements if e.id in ctx.element_ids]
            paginated_elements, pagination = paginate_list(
                elements, params.page, params.page_size
            )

            if params.detail_level == DetailLevel.SUMMARY:
                elements_data = [format_element_summary(e) for e in paginated_elements]
            else:
                elements_data = [e.model_dump() for e in paginated_elements]

            result.append(
                {
                    "context": ctx.model_dump(),
                    "elements": elements_data,
                    "pagination": pagination.model_dump(),
                    "type_breakdown": {
                        etype.value: len([e for e in elements if e.type == etype])
                        for etype in ElementType
                    },
                }
            )
        return json.dumps(result, indent=2)

    # Markdown format
    lines = [f"# Bounded Contexts: {workshop.metadata.name}", ""]

    if not contexts:
        lines.append("No bounded contexts defined.")
        return "\n".join(lines)

    for ctx in contexts:
        lines.extend([f"## {ctx.name}", f"**ID**: `{ctx.id}`"])

        if ctx.description:
            lines.append(f"**Description**: {ctx.description}")
        if ctx.color:
            lines.append(f"**Color**: {ctx.color}")

        elements = [e for e in workshop.elements if e.id in ctx.element_ids]
        paginated_elements, pagination = paginate_list(
            elements, params.page, params.page_size
        )

        lines.append(f"**Total Elements**: {len(elements)}")

        if elements:
            # Type breakdown
            type_counts = {}
            for e in elements:
                type_counts[e.type] = type_counts.get(e.type, 0) + 1

            lines.append("\n### Element Breakdown")
            for etype, count in sorted(type_counts.items()):
                if count > 0:
                    lines.append(f"- {etype.value}: {count}")

            lines.extend(["", "### Elements", format_pagination_markdown(pagination), ""])

            for element in sorted(
                paginated_elements, key=lambda e: (e.type.value, e.position)
            ):
                if params.detail_level == DetailLevel.SUMMARY:
                    lines.append(
                        f"- [{element.type.value}] **{element.name}** "
                        f"(pos: {element.position}, id: `{element.id}`)"
                    )
                else:
                    lines.append(format_element_markdown(element))
                    lines.append("")

        lines.append("")

    content = "\n".join(lines)
    return content


@mcp.tool(
    name="eventstorming_get_statistics",
    annotations={
        "title": "Get Workshop Statistics",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_statistics(params: GetStatisticsInput) -> str:
    """Get comprehensive statistics about the workshop.

    Provides detailed statistics including element counts by type, bounded context
    distribution, relationship metrics, and other useful analytics.

    Args:
        params (GetStatisticsInput): Parameters containing:
            - workshop_id (str): Workshop ID
            - response_format (ResponseFormat): Output format

    Returns:
        str: Statistics in specified format
    """
    try:
        workshop = load_workshop(params.workshop_id)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)}, indent=2)

    stats = {
        "workshop": {
            "name": workshop.metadata.name,
            "domain": workshop.metadata.domain,
            "created_at": workshop.metadata.created_at,
            "updated_at": workshop.metadata.updated_at,
        },
        "totals": {
            "elements": len(workshop.elements),
            "bounded_contexts": len(workshop.bounded_contexts),
        },
        "by_type": {},
        "by_context": {},
        "relationships": {
            "elements_with_triggers": 0,
            "elements_with_triggered_by": 0,
            "total_trigger_links": 0,
        },
        "coverage": {"elements_in_contexts": 0, "elements_without_context": 0},
    }

    # Count by type
    for etype in ElementType:
        count = len([e for e in workshop.elements if e.type == etype])
        stats["by_type"][etype.value] = count

    # Count by context
    for ctx in workshop.bounded_contexts:
        stats["by_context"][ctx.name] = len(ctx.element_ids)

    # Relationship stats
    for element in workshop.elements:
        if element.triggers:
            stats["relationships"]["elements_with_triggers"] += 1
            stats["relationships"]["total_trigger_links"] += len(element.triggers)
        if element.triggered_by:
            stats["relationships"]["elements_with_triggered_by"] += 1

    # Coverage stats
    for element in workshop.elements:
        if element.bounded_context_id:
            stats["coverage"]["elements_in_contexts"] += 1
        else:
            stats["coverage"]["elements_without_context"] += 1

    if params.response_format == ResponseFormat.JSON:
        return json.dumps(stats, indent=2)

    # Markdown format
    lines = [
        f"# Workshop Statistics: {workshop.metadata.name}",
        "",
        "## Overview",
        f"- **Domain**: {workshop.metadata.domain or 'Not specified'}",
        f"- **Created**: {workshop.metadata.created_at}",
        f"- **Last Updated**: {workshop.metadata.updated_at}",
        f"- **Total Elements**: {stats['totals']['elements']}",
        f"- **Bounded Contexts**: {stats['totals']['bounded_contexts']}",
        "",
        "## Elements by Type",
    ]

    for etype, count in sorted(stats["by_type"].items()):
        if count > 0:
            lines.append(f"- **{etype}**: {count}")

    if stats["by_context"]:
        lines.extend(["", "## Elements by Bounded Context"])
        for ctx_name, count in sorted(stats["by_context"].items()):
            lines.append(f"- **{ctx_name}**: {count}")

    lines.extend(
        [
            "",
            "## Relationships",
            f"- Elements with outgoing triggers: {stats['relationships']['elements_with_triggers']}",
            f"- Elements with incoming triggers: {stats['relationships']['elements_with_triggered_by']}",
            f"- Total trigger links: {stats['relationships']['total_trigger_links']}",
            "",
            "## Context Coverage",
            f"- Elements assigned to contexts: {stats['coverage']['elements_in_contexts']}",
            f"- Elements without context: {stats['coverage']['elements_without_context']}",
        ]
    )

    if stats["coverage"]["elements_without_context"] > 0:
        percentage = (
            stats["coverage"]["elements_without_context"] / stats["totals"]["elements"]
        ) * 100
        lines.append(
            f"- **Coverage**: {100 - percentage:.1f}% of elements are contextualized"
        )

    return "\n".join(lines)


@mcp.tool(
    name="eventstorming_visualize_flow",
    annotations={
        "title": "Visualize Event Flow",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def visualize_flow(params: VisualizeFlowInput) -> str:
    """Visualize the flow of events and their relationships.

    Traces the flow of cause and effect through the domain by following
    trigger relationships between elements. Shows how events cascade through
    the system.

    Args:
        params (VisualizeFlowInput): Parameters containing:
            - workshop_id (str): Workshop ID
            - start_element_id (Optional[str]): Start element (shows all if not provided)
            - max_depth (int): Maximum depth to traverse (default: 5)
            - max_elements (int): Maximum number of elements to display (default: 100)

    Returns:
        str: Markdown visualization of event flows
    """
    try:
        workshop = load_workshop(params.workshop_id)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)}, indent=2)

    element_count = [0]  # Use list to make it mutable in nested function

    def trace_flow(
        element_id: str, depth: int, visited: set, indent: int = 0
    ) -> List[str]:
        """Recursively trace flow from an element."""
        if depth >= params.max_depth or element_id in visited:
            return []

        # Check max_elements limit
        if element_count[0] >= params.max_elements:
            return [f"{'  ' * indent}... (max elements limit reached)"]

        visited.add(element_id)
        element_count[0] += 1

        element = next((e for e in workshop.elements if e.id == element_id), None)
        if not element:
            return []

        prefix = "  " * indent
        lines = [f"{prefix}→ [{element.type.value}] **{element.name}** `{element.id}`"]

        if element.notes and len(element.notes) < 100:  # Show short notes only
            lines.append(f"{prefix}  _{element.notes}_")

        # Follow triggers
        for trigger_id in element.triggers:
            if element_count[0] >= params.max_elements:
                lines.append(f"{prefix}  ... (max elements limit reached)")
                break
            lines.extend(trace_flow(trigger_id, depth + 1, visited, indent + 1))

        return lines

    lines = [f"# Event Flow Visualization: {workshop.metadata.name}", ""]

    if params.start_element_id:
        # Trace from specific element
        start = next(
            (e for e in workshop.elements if e.id == params.start_element_id), None
        )
        if not start:
            return json.dumps(
                {"error": f"Start element not found: {params.start_element_id}"},
                indent=2,
            )

        lines.append(f"## Flow from: {start.name}")
        lines.append("")
        lines.extend(trace_flow(params.start_element_id, 0, set()))
    else:
        # Find all root elements (not triggered by anything)
        roots = [e for e in workshop.elements if not e.triggered_by]

        if not roots:
            lines.append(
                "No root elements found (all elements are triggered by something)."
            )
            lines.append(
                "This might indicate circular dependencies or incomplete modeling."
            )
        else:
            lines.append(f"Found {len(roots)} root element(s)")
            lines.append("")

            for root in roots:
                if element_count[0] >= params.max_elements:
                    lines.append("... (max elements limit reached)")
                    break
                lines.append(f"## Flow from: {root.name}")
                lines.extend(trace_flow(root.id, 0, set()))
                lines.append("")

    if element_count[0] >= params.max_elements:
        lines.append("")
        lines.append(
            f"⚠️ Display limit reached ({params.max_elements} elements). "
            f"Use start_element_id to focus on specific flows."
        )

    content = "\n".join(lines)
    return content


# ============================================================================
# IMPORT/EXPORT TOOLS
# ============================================================================


@mcp.tool(
    name="eventstorming_export_workshop",
    annotations={
        "title": "Export Event Storming Workshop",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def export_workshop(params: ExportWorkshopInput) -> str:
    """Export workshop data as JSON for sharing or backup.

    Creates a complete JSON export of the workshop that can be shared with
    others or imported into another system. The export includes all elements,
    contexts, and metadata.

    Args:
        params (ExportWorkshopInput): Parameters containing:
            - workshop_id (str): Workshop ID
            - include_metadata (bool): Include workshop metadata

    Returns:
        str: JSON export of workshop data
    """
    try:
        workshop = load_workshop(params.workshop_id)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e)}, indent=2)

    export_data = workshop.model_dump()

    if not params.include_metadata:
        # Remove metadata fields
        export_data["metadata"] = {
            "name": workshop.metadata.name,
            "domain": workshop.metadata.domain,
            "description": workshop.metadata.description,
        }

    export_data["export_info"] = {
        "exported_at": get_timestamp(),
        "version": "1.0",
        "tool": "eventstorming_mcp",
    }

    return json.dumps(export_data, indent=2)


@mcp.tool(
    name="eventstorming_import_workshop",
    annotations={
        "title": "Import Event Storming Workshop",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def import_workshop(params: ImportWorkshopInput) -> str:
    """Import a workshop from JSON data.

    Creates a new workshop from exported JSON data. The imported workshop
    gets a new ID and can optionally be given a new name.

    Args:
        params (ImportWorkshopInput): Parameters containing:
            - workshop_data (str): JSON workshop data
            - new_name (Optional[str]): New name for imported workshop

    Returns:
        str: JSON response with new workshop ID
    """
    try:
        data = json.loads(params.workshop_data)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON data: {str(e)}"}, indent=2)

    # Create new workshop with new ID
    new_id = generate_id()
    timestamp = get_timestamp()

    # Update metadata
    if "metadata" in data:
        data["metadata"]["id"] = new_id
        data["metadata"]["created_at"] = timestamp
        data["metadata"]["updated_at"] = timestamp
        if params.new_name:
            data["metadata"]["name"] = params.new_name

    try:
        workshop = Workshop(**data)
        save_workshop(workshop)
    except Exception as e:
        return json.dumps({"error": f"Failed to import workshop: {str(e)}"}, indent=2)

    return json.dumps(
        {
            "success": True,
            "workshop_id": new_id,
            "name": workshop.metadata.name,
            "message": "Workshop imported successfully",
            "statistics": {
                "elements": len(workshop.elements),
                "bounded_contexts": len(workshop.bounded_contexts),
            },
        },
        indent=2,
    )


# ============================================================================
# SERVER EXECUTION
# ============================================================================

if __name__ == "__main__":
    mcp.run()
