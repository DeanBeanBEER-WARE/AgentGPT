from notion_client import Client

# Initialize the client
notion = Client(auth="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")

# Try to list all databases
try:
    response = notion.search(
        filter={"property": "object", "value": "database"}
    )
    print("Connection successful!")
    print("\nAvailable databases:")
    for result in response.get('results', []):
        if 'title' in result.get('properties', {}):
            title = result['properties']['title'].get('title', [{}])[0].get('text', {}).get('content', 'Untitled')
            print(f"- {title} (ID: {result['id']})")
except Exception as e:
    print(f"Error connecting to Notion: {str(e)}")
