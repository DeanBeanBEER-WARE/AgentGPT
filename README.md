# AgentGPT

## Overview
AgentGPT is an autonomous AI agent platform that allows users to create and deploy AI agents in their browser. These agents can perform various tasks using a collection of tools and can be extended with custom capabilities.

## Project Structure

```
AgentGPT/
├── platform/               # Backend (FastAPI)
│   └── reworkd_platform/
│       └── web/
│           └── api/
│               └── agent/
│                   └── tools/      # Tool implementations
├── next/                  # Frontend (Next.js)
│   └── public/
│       └── tools/        # Tool icons
└── cli/                  # CLI tools
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js (>=18)
- OpenAI API key

### Installation
1. Clone the repository:
```bash
git clone https://github.com/reworkd/AgentGPT.git
cd AgentGPT
```

2. Run the setup script:
```bash
# For Mac/Linux
./setup.sh

# For Windows
./setup.bat
```

3. When prompted, enter your OpenAI API key.

4. Access the application at http://localhost:3000

## Tools System

### Understanding Tools
Tools are the core functionality providers for AgentGPT agents. Each tool is a Python class that inherits from the base `Tool` class and provides specific capabilities.

### Tool Structure
Each tool must implement:
```python
class YourTool(Tool):
    description = "Description for the AI"
    public_description = "Description shown to users"
    arg_description = "Description of the expected input"
    image_url = "/tools/your-tool-icon.png"

    async def call(
        self,
        goal: str,
        task: str,
        input_str: str,
        *args: Any,
        **kwargs: Any
    ) -> StreamingResponse:
        # Tool implementation
        pass
```

### Available Tools
1. **Search**: Google search integration using Serper API
2. **Image**: Image generation capabilities
3. **Code**: Code analysis and generation
4. **Calculator**: Mathematical calculations and expressions
5. **Wikipedia**: (Currently disabled) Wikipedia article search
6. **SID**: Custom search implementation

### Adding New Tools

1. Create a new tool file in `platform/reworkd_platform/web/api/agent/tools/`:
```python
from reworkd_platform.web.api.agent.tools.tool import Tool

class NewTool(Tool):
    description = "Tool description"
    public_description = "Public description"
    arg_description = "Input description"
    image_url = "/tools/your-tool-icon.png"

    async def call(self, goal: str, task: str, input_str: str, *args: Any, **kwargs: Any):
        # Implement your tool logic here
        pass
```

2. Add an icon in `next/public/tools/`

3. Register the tool in `tools.py`:
```python
def get_external_tools() -> List[Type[Tool]]:
    return [
        # Existing tools...
        NewTool,  # Add your tool here
    ]
```

4. Rebuild and restart the containers:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Tool Development Tips
1. **Error Handling**: Always implement proper error handling in your tool's `call` method
2. **Async Support**: All tools must be async-compatible
3. **Input Validation**: Validate and sanitize input_str before processing
4. **Response Format**: Use `stream_string()` for simple responses or implement custom streaming
5. **Testing**: Add tests in the `tests` directory

### Example: Calculator Tool
```python
class Calculator(Tool):
    description = "Perform mathematical calculations"
    public_description = "Calculate mathematical expressions"
    arg_description = "A mathematical expression (e.g., '2 + 2')"
    image_url = "/tools/calculator.png"

    async def call(self, goal: str, task: str, input_str: str, *args: Any, **kwargs: Any):
        try:
            result = eval(input_str, {"__builtins__": {}}, safe_dict)
            return stream_string(f"The result of {input_str} is {result}")
        except Exception as e:
            return stream_string(f"Error: {str(e)}")
```

## Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (supports GPT-3.5-turbo and GPT-4)
- `SERP_API_KEY`: (Optional) For Google search functionality
- `REPLICATE_API_KEY`: (Optional) For additional AI models
- `NOTION_API_KEY`: (Optional) For Notion integration

### Using GPT-4
There are two ways to use GPT-4:

1. **Through Environment Variables**:
   Add to your `.env` file:
   ```
   REWORKD_PLATFORM_MODEL=gpt-4
   ```

2. **Through the Web Interface**:
   - Click on the settings icon in the web interface
   - Under "Model", select "GPT-4" from the dropdown
   - Click "Save Changes"

Important Notes:
- Make sure your OpenAI API key has access to GPT-4
- GPT-4 has a max token limit of 8000 (defined in `schemas/agent.py`)
- GPT-4 is more expensive than GPT-3.5-turbo
- You can switch between models at any time

Available Models:
```python
LLM_Model = Literal[
    "gpt-3.5-turbo",      # Default, 4000 tokens
    "gpt-3.5-turbo-16k",  # 16000 tokens
    "gpt-4",              # 8000 tokens
]
```

### SID Integration
The SID tool allows you to access and manage your Notion files and other personal information.

#### To use the SID integration:
1. Ensure you have the SID credentials set up in your application.
2. Use the following format to interact with Notion:
```json
// Search Notion
{"action": "search", "params": {"query": "meeting notes"}}

// Read a page
{"action": "read_page", "params": {"page_id": "page_id_here"}}

// Update a page
{"action": "update_page", "params": {
    "page_id": "page_id_here",
    "updates": {"properties": {"Title": {"title": [{"text": {"content": "New Title"}}]}}}
}}
```
3. The SID tool will handle authentication and access to your Notion files.
4. Make sure to share your Notion pages/databases with the SID integration.

### Notion Integration
To use the Notion integration directly:
1. Create a Notion integration at https://www.notion.so/my-integrations
2. Get your integration token (starts with "secret_")
3. Add to your .env file:
   ```
   REWORKD_PLATFORM_NOTION_API_KEY=your_notion_integration_token
   ```
4. Share your Notion pages/databases with the integration
}}

1. Create a Notion integration at https://www.notion.so/my-integrations
2. Get your integration token (starts with "secret_")
3. Add to your .env file:
   ```
   REWORKD_PLATFORM_NOTION_API_KEY=your_notion_integration_token
   ```
4. Share your Notion pages/databases with the integration

The Notion tool supports:
- Searching pages and databases
- Reading page content
- Updating page content

Example usage:
```json
// Search Notion
{"action": "search", "params": {"query": "meeting notes"}}

// Read a page
{"action": "read_page", "params": {"page_id": "page_id_here"}}

// Update a page
{"action": "update_page", "params": {
    "page_id": "page_id_here",
    "updates": {"properties": {"Title": {"title": [{"text": {"content": "New Title"}}]}}}
}}
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting
1. **Docker Issues**: Ensure Docker Desktop is running
2. **API Key Issues**: Verify your API keys in the .env file
3. **Tool Errors**: Check the Docker logs for detailed error messages
4. **Environment Updates**: Changes to environment variables in `.env` files are automatically integrated into the running Docker containers - no restart required

## LangChain Configuration

### Version Management
The project uses LangChain for AI model integration. The version is specified in `platform/pyproject.toml`:

```toml
[tool.poetry.dependencies]
langchain = "^0.1.0"  # Specify version here
```

### Common Issues and Solutions

1. **Module Not Found Errors**
   - Error: `ModuleNotFoundError: No module named 'langchain.globals'`
   - Solution: Update LangChain version to ^0.1.0 or later in pyproject.toml
   - After updating, rebuild containers:
     ```bash
     docker-compose down
     docker-compose build --no-cache
     docker-compose up
     ```

2. **LangChain Model Configuration**
   - Location: `platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py`
   - Modify model parameters:
     ```python
     chat = ChatOpenAI(
         temperature=0.9,
         model_name="gpt-3.5-turbo",
         streaming=True,
     )
     ```

3. **Custom LangChain Tools Integration**
   - Extend the base Tool class
   - Implement LangChain-specific functionality:
     ```python
     from langchain.tools import BaseTool
     from reworkd_platform.web.api.agent.tools.tool import Tool

     class CustomLangChainTool(Tool):
         def to_langchain_tool(self) -> BaseTool:
             # Convert your tool to LangChain format
             pass
     ```

4. **Environment Variables**
   - `LANGCHAIN_TRACING`: Enable/disable LangChain tracing
   - `LANGCHAIN_API_KEY`: If using LangChain API
   - Add to .env file:
     ```
     LANGCHAIN_TRACING=true
     LANGCHAIN_API_KEY=your_key_here
     ```

### LangChain Customization

1. **Custom Prompts**
   - Location: `platform/reworkd_platform/web/api/agent/prompts.py`
   - Modify existing prompts or add new ones:
     ```python
     from langchain.prompts import PromptTemplate

     CUSTOM_PROMPT = PromptTemplate(
         input_variables=["input"],
         template="Your custom prompt here: {input}"
     )
     ```

2. **Chain Modification**
   - Create custom chains in `agent_service` directory
   - Example:
     ```python
     from langchain.chains import LLMChain

     custom_chain = LLMChain(
         llm=chat,
         prompt=CUSTOM_PROMPT,
         verbose=True
     )
     ```

3. **Memory Integration**
   - Add conversation memory:
     ```python
     from langchain.memory import ConversationBufferMemory

     memory = ConversationBufferMemory(
         memory_key="chat_history",
         return_messages=True
     )
     ```

## Additional Resources
- [Official Documentation](https://docs.reworkd.ai/)
- [API Reference](https://docs.reworkd.ai/api-reference)
- [Contributing Guide](https://docs.reworkd.ai/contributing)
- [LangChain Documentation](https://python.langchain.com/docs/)
