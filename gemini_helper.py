from google import genai
import json
import logging
import time
from config import GEMINI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

def analyze_tool(tool_name, tool_summary, tool_link):
    """
    Analyze an AI tool using Gemini API and return a dictionary with analysis.
    """
    # Default response in case of failure
    default_response = {
        "short_description": "AI tool for various tasks",
        "use_case": "Anyone looking for AI solutions",
        "price_type": "Free",
        "score": 5,
        "emoji": "🤖"
    }
    
    try:
        # Prepare the prompt for Gemini
        prompt = f"""
        Analyze this AI tool and return a JSON object with the following keys:
        - short_description: max 2 lines explaining what the tool does in English only
        - use_case: one line who should use this (in English)
        - price_type: exactly one of: Free, Paid. If the tool has a free tier use Free, if it requires payment use Paid. Never use Freemium.
        - score: integer from 1 to 10 based on how useful and innovative the tool is
        - emoji: one relevant emoji for the tool
        - category: string like Image Generation, Writing, Coding, Video, Audio, Productivity, Research

        Tool Name: {tool_name}
        Tool Summary: {tool_summary}
        Tool Link: {tool_link}

        Respond only in English. Do not use Hindi or Hinglish in any field.
        Return ONLY the JSON object, no extra text or markdown.
        """
        
        # Generate content with Gemini
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        
        # Wait for 2 seconds to avoid rate limiting
        time.sleep(2)
        
        # Parse the JSON response
        response_text = response.text.strip()
        
        # Find JSON object in the response (in case there's extra text)
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Validate the result has all required keys
            required_keys = ["short_description", "use_case", "price_type", "score", "emoji", "category"]
            if all(key in result for key in required_keys):
                # Ensure price_type is one of the allowed values
                    if result["price_type"] not in ["Free", "Paid"]:
                        result["price_type"] = "Free"
                # Ensure score is between 1 and 10
                result["score"] = max(1, min(10, int(result["score"])))
                # Ensure category is provided, default to "Other" if missing or empty
                if not result["category"] or not isinstance(result["category"], str):
                    result["category"] = "Other"
                return result
            else:
                logger.warning(f"Gemini response missing required keys: {result}")
                return default_response
        else:
            logger.warning(f"No JSON found in Gemini response: {response_text}")
            return default_response
            
    except Exception as e:
        logger.error(f"Error in Gemini analysis for {tool_name}: {e}")
        return default_response