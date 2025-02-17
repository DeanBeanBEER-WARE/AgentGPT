from typing import Any
import math
from lanarky.responses import StreamingResponse

from reworkd_platform.web.api.agent.stream_mock import stream_string
from reworkd_platform.web.api.agent.tools.tool import Tool

class Calculator(Tool):
    description = (
        "Perform mathematical calculations. Can handle basic arithmetic, "
        "trigonometry, logarithms, and other mathematical operations. "
        "Input should be a mathematical expression."
    )
    public_description = "Calculate mathematical expressions."
    arg_description = "A mathematical expression (e.g., '2 + 2', 'sin(30)', 'log(100)')"
    image_url = "/tools/calculator.png"  # You'll need to add this image to the public/tools directory

    async def call(
        self, goal: str, task: str, input_str: str, *args: Any, **kwargs: Any
    ) -> StreamingResponse:
        try:
            # Create a safe dictionary of allowed mathematical functions
            safe_dict = {
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'pow': pow,
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'log10': math.log10,
                'pi': math.pi,
                'e': math.e
            }

            # Clean and evaluate the expression
            cleaned_input = input_str.strip().replace('^', '**')
            result = eval(cleaned_input, {"__builtins__": {}}, safe_dict)
            
            # Format the result
            if isinstance(result, (int, float)):
                formatted_result = f"The result of {input_str} is {result}"
            else:
                formatted_result = f"Error: Invalid mathematical expression"

            return stream_string(formatted_result)
        except Exception as e:
            return stream_string(f"Error: Could not evaluate the mathematical expression. Please ensure it's properly formatted. Details: {str(e)}")
