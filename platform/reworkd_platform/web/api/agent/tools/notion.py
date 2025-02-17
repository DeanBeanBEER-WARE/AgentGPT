from typing import Any, Optional
from notion_client import Client
from lanarky.responses import StreamingResponse
from reworkd_platform.settings import settings
from reworkd_platform.web.api.agent.stream_mock import stream_string
from reworkd_platform.web.api.agent.tools.tool import Tool
from reworkd_platform.db.crud.oauth import OAuthCrud
from reworkd_platform.schemas.user import UserBase

class Notion(Tool):
    description = (
        "Access and manage Notion pages and databases. Can search, read, and update "
        "Notion content. Use this for managing notes, documents, and databases in Notion."
    )
    public_description = "Interact with Notion pages and databases"
    arg_description = (
        "A JSON string with 'action' and 'params' keys. "
        "Actions: 'search', 'read_page', 'update_page'. "
        "Example: {'action': 'search', 'params': {'query': 'meeting notes'}}"
    )
    image_url = "/tools/notion.png"

    @staticmethod
    def available() -> bool:
        return bool(settings.notion_api_key)

    @staticmethod
    async def dynamic_available(user: UserBase, oauth_crud: OAuthCrud) -> bool:
        return bool(settings.notion_api_key)

    async def call(
        self,
        goal: str,
        task: str,
        input_str: str,
        user: UserBase,
        oauth_crud: OAuthCrud,
    ) -> StreamingResponse:
        try:
            # Initialize Notion client
            notion = Client(auth=settings.notion_api_key)
            
            # Parse input as action and parameters
            import json
            try:
                input_data = json.loads(input_str)
                action = input_data.get('action', '')
                params = input_data.get('params', {})
            except json.JSONDecodeError:
                return stream_string("Error: Input must be a valid JSON string with 'action' and 'params' keys")

            # Handle different actions
            if action == 'search':
                query = params.get('query', '')
                if not query:
                    return stream_string("Error: Search query is required")
                
                results = notion.search(query=query).get('results', [])
                formatted_results = []
                for result in results[:5]:  # Limit to 5 results
                    title = result.get('properties', {}).get('title', [{}])[0].get('text', {}).get('content', 'Untitled')
                    page_id = result.get('id', '')
                    formatted_results.append(f"- {title} (ID: {page_id})")
                
                return stream_string("\n".join(formatted_results) if formatted_results else "No results found")

            elif action == 'read_page':
                page_id = params.get('page_id', '')
                if not page_id:
                    return stream_string("Error: Page ID is required")
                
                try:
                    page = notion.pages.retrieve(page_id)
                    # Extract and format page content
                    title = page.get('properties', {}).get('title', [{}])[0].get('text', {}).get('content', 'Untitled')
                    content = f"Title: {title}\n"
                    # Add more page content formatting as needed
                    return stream_string(content)
                except Exception as e:
                    return stream_string(f"Error reading page: {str(e)}")

            elif action == 'update_page':
                page_id = params.get('page_id', '')
                updates = params.get('updates', {})
                if not page_id or not updates:
                    return stream_string("Error: Page ID and updates are required")
                
                try:
                    notion.pages.update(page_id, **updates)
                    return stream_string("Page updated successfully")
                except Exception as e:
                    return stream_string(f"Error updating page: {str(e)}")

            else:
                return stream_string(
                    "Invalid action. Supported actions are: 'search', 'read_page', 'update_page'"
                )

        except Exception as e:
            return stream_string(f"Error accessing Notion: {str(e)}")
