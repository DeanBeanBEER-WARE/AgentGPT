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
        "Direct integration with Notion databases - NO BROWSER NEEDED. "
        "This tool can directly access Notion content using database IDs (found in URLs). "
        "When given a Notion URL like 'notion.so/.../your-database-id?v=...', "
        "extract the database ID (part before '?') and use it with this tool.\n\n"
        "Example: From URL 'notion.so/1234...?v=5678', use '1234...' as database_id.\n\n"
        "Available actions:\n"
        "1. List all databases\n"
        "2. Read entries from a database\n"
        "3. Create new entries"
    )
    public_description = "Direct access to Notion databases - no browser needed"
    arg_description = (
        "To read a Notion database from a URL like 'notion.so/abc123?v=xyz', use:\n"
        "1. First list databases: {'action': 'list_databases'}\n"
        "2. Then read database: {'action': 'read_database', 'params': {'database_id': 'abc123'}}\n"
        "3. Or create entry: {'action': 'create_entry', 'params': {'database_id': 'abc123', 'title': 'New Entry'}}"
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

    def _get_title_property(self, database_id: str) -> str:
        """Get the name of the title property in a database"""
        db_info = self.notion.databases.retrieve(database_id)
        for prop_name, prop_info in db_info.get('properties', {}).items():
            if prop_info.get('type') == 'title':
                return prop_name
        raise ValueError("No title property found in database")

    async def _read_database(self, database_id: str) -> str:
        """Read entries from a Notion database"""
        try:
            # Clean the database ID (remove any URL parts)
            database_id = database_id.split('?')[0].strip()
            
            # Get database structure
            db_info = self.notion.databases.retrieve(database_id)
            title_prop = self._get_title_property(database_id)
            
            # Query entries
            query_result = self.notion.databases.query(
                database_id=database_id,
                page_size=10
            )
            
            if not query_result['results']:
                return "No entries found in database"
            
            # Format output
            output = [f"Database: {db_info['title'][0]['text']['content']}\n"]
            output.append("Entries:")
            for page in query_result['results']:
                title = page['properties'][title_prop]['title']
                if title:
                    output.append(f"- {title[0]['text']['content']}")
            
            return "\n".join(output)
            
        except Exception as e:
            return (
                f"Error reading database: {str(e)}.\n"
                "If you provided a full URL, make sure to use only the database ID part (before the '?')."
            )

    async def _create_entry(self, database_id: str, title: str) -> str:
        """Create a new entry in a Notion database"""
        try:
            # Clean the database ID (remove any URL parts)
            database_id = database_id.split('?')[0].strip()
            
            # Get the title property name
            title_prop = self._get_title_property(database_id)
            
            # Create the entry
            new_page = self.notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    title_prop: {
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
            
            return f"Successfully created new entry '{title}' in the database"
        except Exception as e:
            return (
                f"Error creating entry: {str(e)}.\n"
                "If you provided a full URL, make sure to use only the database ID part (before the '?')."
            )

    async def _list_databases(self) -> str:
        """List available Notion databases"""
        try:
            results = self.notion.search(
                filter={"property": "object", "value": "database"}
            ).get('results', [])
            
            if not results:
                return "No databases found. Make sure you've shared your databases with the integration."
            
            output = ["Available Notion databases:"]
            for db in results:
                title = db['title'][0]['text']['content'] if db.get('title') else 'Untitled'
                output.append(f"- {title}")
                output.append(f"  ID: {db['id']}")
                output.append("")  # Empty line for better readability
            
            return "\n".join(output)
        except Exception as e:
            return f"Error listing databases: {str(e)}"

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
            # If input looks like a URL, extract the database ID
            if "notion.so" in input_str and "?" in input_str:
                database_id = input_str.split("?")[0].split("/")[-1]
                return await self._read_database(database_id)

            # Otherwise, try to parse as JSON command
            try:
                input_data = json.loads(input_str)
            except json.JSONDecodeError:
                # If not JSON and not URL, assume it's a direct database ID
                if input_str.strip():
                    return await self._read_database(input_str.strip())
                return stream_string(
                    "Please provide either:\n"
                    "1. A Notion URL\n"
                    "2. A database ID\n"
                    "3. A JSON command like {'action': 'list_databases'}"
                )

            action = input_data.get('action', '')
            params = input_data.get('params', {})

            if action == 'list_databases':
                result = await self._list_databases()
            elif action == 'read_database':
                database_id = params.get('database_id')
                if not database_id:
                    return stream_string("Error: database_id is required for read_database action")
                result = await self._read_database(database_id)
            elif action == 'create_entry':
                database_id = params.get('database_id')
                title = params.get('title', 'New Entry')
                if not database_id:
                    return stream_string("Error: database_id is required for create_entry action")
                result = await self._create_entry(database_id, title)
            else:
                result = (
                    "Invalid action. You can:\n"
                    "1. Provide a Notion URL or database ID directly\n"
                    "2. Use {'action': 'list_databases'} to see available databases\n"
                    "3. Use {'action': 'read_database', 'params': {'database_id': 'your-id'}}\n"
                    "4. Use {'action': 'create_entry', 'params': {'database_id': 'your-id', 'title': 'New Entry'}}"
                )

            return stream_string(result)

        except Exception as e:
            return stream_string(f"Error accessing Notion: {str(e)}")
