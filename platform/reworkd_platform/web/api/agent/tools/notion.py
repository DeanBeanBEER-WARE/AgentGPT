from typing import Any, Optional, Dict, List
from notion_client import Client
from lanarky.responses import StreamingResponse
from reworkd_platform.settings import settings
from reworkd_platform.web.api.agent.stream_mock import stream_string
from reworkd_platform.web.api.agent.tools.tool import Tool
from reworkd_platform.db.crud.oauth import OAuthCrud
from reworkd_platform.schemas.user import UserBase
import json

class Notion(Tool):
    description = (
        "Access and manage Notion pages and databases. Can search, read, update, and create "
        "content in Notion. Use this for managing notes, documents, and databases."
    )
    public_description = "Interact with Notion pages and databases"
    arg_description = (
        "A JSON string with 'action' and 'params' keys. "
        "Actions: 'search', 'read_page', 'update_page', 'create_page', 'list_databases'. "
        "Example: {'action': 'search', 'params': {'query': 'meeting notes'}}"
    )
    image_url = "/tools/notion.svg"

    def __init__(self):
        self.notion = None
        if settings.notion_api_key:
            self.notion = Client(auth=settings.notion_api_key)

    @staticmethod
    def available() -> bool:
        return bool(settings.notion_api_key)

    @staticmethod
    async def dynamic_available(user: UserBase, oauth_crud: OAuthCrud) -> bool:
        return bool(settings.notion_api_key)

    async def _search(self, query: str) -> str:
        """Search Notion content"""
        if not query:
            return "Error: Search query is required"
        
        results = self.notion.search(query=query).get('results', [])
        formatted_results = []
        for result in results[:5]:
            title = self._get_title_from_result(result)
            page_id = result.get('id', '')
            object_type = result.get('object', 'unknown')
            formatted_results.append(f"- {title} (Type: {object_type}, ID: {page_id})")
        
        return "\n".join(formatted_results) if formatted_results else "No results found"

    async def _read_page(self, page_id: str) -> str:
        """Read a Notion page"""
        if not page_id:
            return "Error: Page ID is required"
        
        try:
            page = self.notion.pages.retrieve(page_id)
            blocks = self.notion.blocks.children.list(page_id).get('results', [])
            
            # Get page title
            title = self._get_title_from_result(page)
            content = [f"Title: {title}"]
            
            # Extract block content
            for block in blocks:
                block_content = self._extract_block_content(block)
                if block_content:
                    content.append(block_content)
            
            return "\n".join(content)
        except Exception as e:
            return f"Error reading page: {str(e)}"

    async def _create_page(self, parent_id: str, title: str, content: str) -> str:
        """Create a new Notion page"""
        try:
            # Create the page
            new_page = self.notion.pages.create(
                parent={"page_id": parent_id},
                properties={
                    "title": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    }
                }
            )
            
            # Add content as blocks
            self.notion.blocks.children.append(
                new_page["id"],
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": content}}]
                        }
                    }
                ]
            )
            
            return f"Page created successfully with ID: {new_page['id']}"
        except Exception as e:
            return f"Error creating page: {str(e)}"

    async def _list_databases(self) -> str:
        """List available Notion databases"""
        try:
            results = self.notion.search(
                filter={"property": "object", "value": "database"}
            ).get('results', [])
            
            if not results:
                return "No databases found"
            
            formatted_results = []
            for db in results:
                title = self._get_title_from_result(db)
                db_id = db.get('id', '')
                formatted_results.append(f"- {title} (ID: {db_id})")
            
            return "\n".join(formatted_results)
        except Exception as e:
            return f"Error listing databases: {str(e)}"

    def _get_title_from_result(self, result: Dict) -> str:
        """Extract title from a Notion result object"""
        if 'properties' in result:
            title_prop = result.get('properties', {}).get('title', [])
            if title_prop and isinstance(title_prop, list):
                return title_prop[0].get('text', {}).get('content', 'Untitled')
            elif title_prop and isinstance(title_prop, dict):
                return title_prop.get('title', [{}])[0].get('text', {}).get('content', 'Untitled')
        return 'Untitled'

    def _extract_block_content(self, block: Dict) -> Optional[str]:
        """Extract content from a Notion block"""
        block_type = block.get('type', '')
        if not block_type:
            return None
            
        block_data = block.get(block_type, {})
        if 'rich_text' in block_data:
            text_content = []
            for text in block_data['rich_text']:
                text_content.append(text.get('text', {}).get('content', ''))
            return ' '.join(text_content)
        return None

    async def call(
        self,
        goal: str,
        task: str,
        input_str: str,
        user: UserBase,
        oauth_crud: OAuthCrud,
    ) -> StreamingResponse:
        if not self.notion:
            return stream_string("Error: Notion API key not configured")

        try:
            input_data = json.loads(input_str)
            action = input_data.get('action', '')
            params = input_data.get('params', {})

            result = "Invalid action"
            
            if action == 'search':
                result = await self._search(params.get('query', ''))
            elif action == 'read_page':
                result = await self._read_page(params.get('page_id', ''))
            elif action == 'create_page':
                result = await self._create_page(
                    params.get('parent_id', ''),
                    params.get('title', ''),
                    params.get('content', '')
                )
            elif action == 'list_databases':
                result = await self._list_databases()
            elif action == 'update_page':
                try:
                    page_id = params.get('page_id', '')
                    updates = params.get('updates', {})
                    if not page_id or not updates:
                        result = "Error: Page ID and updates are required"
                    else:
                        self.notion.pages.update(page_id, **updates)
                        result = "Page updated successfully"
                except Exception as e:
                    result = f"Error updating page: {str(e)}"
            else:
                result = (
                    "Invalid action. Supported actions are: "
                    "'search', 'read_page', 'update_page', 'create_page', 'list_databases'"
                )

            return stream_string(result)

        except json.JSONDecodeError:
            return stream_string("Error: Input must be a valid JSON string with 'action' and 'params' keys")
        except Exception as e:
            return stream_string(f"Error accessing Notion: {str(e)}")
