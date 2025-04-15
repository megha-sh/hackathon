from agno.agent import Agent, RunResponse
from agno.models.google import Gemini
from dotenv import load_dotenv
import os
import json

load_dotenv()

os.environ["GOOGLE_API_KEY"] = "AIzaSyBhfyNHJnKWS_teZqpl5qIYAXGp7D_BN5M"  # replace this with your actual key or use .env

def generate_summary(data: str) -> dict:
    agent = Agent(
        model=Gemini(id="gemini-2.0-flash"),
        instructions=[
            "Extract the following fields from the invoice text: "
            "Invoice Number, Invoice Date, Vendor Name, Total Amount. "
            "Return only a valid JSON object with those fields. Do not include explanations or markdown formatting."
        ],
    )

    response = agent.run(data)
    output = response.content.strip()

    # Remove code block markers if present
    if output.startswith("```json"):
        output = output[7:].strip("`").strip()
    elif output.startswith("```"):
        output = output[3:].strip("`").strip()

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse LLM output",
            "raw": response.content
        }
