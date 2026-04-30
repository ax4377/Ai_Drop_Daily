from google import genai
import json
import logging
import time
from config import GEMINI_API_KEY
from database import is_duplicate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

def validate_tools_list(tools):
    """
    Validate tools list by filtering out invalid entries.
    Removes tools with empty name, link, or summary, or links not starting with http.
    """
    if not tools:
        return []
    
    original_count = len(tools)
    valid_tools = []
    
    for tool in tools:
        # Check if tool is a dictionary
        if not isinstance(tool, dict):
            continue
            
        name = tool.get('name')
        link = tool.get('link')
        summary = tool.get('summary')
        price_type = tool.get('price_type')
        category = tool.get('category')
        
        # Validate required fields
        if not name or not isinstance(name, str) or name.strip() == '':
            continue
        if not link or not isinstance(link, str) or link.strip() == '':
            continue
        if not link.strip().startswith('http'):
            continue
        if not summary or not isinstance(summary, str) or summary.strip() == '':
            continue
            
        # All checks passed
        valid_tools.append(tool)
    
    removed_count = original_count - len(valid_tools)
    if removed_count > 0:
        logger.info(f"Removed {removed_count} invalid tools during validation")
    
    return valid_tools

async def fetch_all_tools():
    """
    Fetch 15 recently launched or trending AI tools from Gemini API.
    Returns list of new tools not yet posted to database.
    """
    try:
        logger.info("Fetching AI tools from Gemini gemini-3-flash-preview...")
        
        prompt = """You are an AI tools researcher with up to date knowledge of April 2026. Give me a list of 15 recently launched or currently trending AI tools in 2025-2026. For each tool provide accurate real information. Return ONLY a valid JSON array with no markdown, no code blocks, no extra text. Each object in array must have exactly these keys: name (string, tool name), link (string, actual working website URL of the tool), summary (string, 2-3 lines what this tool does), price_type (string, exactly one of: Free, Freemium, Paid), category (string, like Image Generation, Writing, Coding, Video, Audio, Productivity, Research). Return exactly 15 tools in the array."""
        
        # Generate content with Gemini
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        
        # Wait for 1 second to avoid rate limiting
        time.sleep(1)
        
        # Parse the JSON response
        response_text = response.text.strip()
        
        # Find JSON array in the response (in case there's extra text)
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            tools = json.loads(json_str)
            
            # Validate we got a list
            if not isinstance(tools, list):
                logger.error(f"Gemini response is not a list: {type(tools)}")
                tools = []
        else:
            logger.warning(f"No JSON array found in Gemini response: {response_text}")
            tools = []
        
        logger.info(f"Gemini returned {len(tools)} tools")
        
        # Validate tools list
        tools = validate_tools_list(tools)
        
        # Filter out duplicates
        new_tools = []
        for tool in tools:
            if not is_duplicate(tool['link']):
                new_tools.append(tool)
            else:
                logger.debug(f"Skipping duplicate tool: {tool['name']}")
        
        logger.info(f"{len(new_tools)} new tools after duplicate filter")
        
        # Warn if fewer than 5 tools but still return what we have
        if len(new_tools) < 5:
            logger.warning(f"Fewer than 5 tools returned ({len(new_tools)}), but continuing with available tools")
        
        return new_tools
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        logger.error(f"Response text: {response.text if 'response' in locals() else 'No response'}")
        return []
    except Exception as e:
        logger.error(f"Error fetching AI tools from Gemini: {e}")
        return []

async def fetch_best_tool():
    """
    Fetch the single most impressive AI tool from Gemini API.
    Returns a dictionary with tool information.
    """
    try:
        logger.info("Fetching best AI tool from Gemini gemini-3-flash-preview...")
        
        prompt = """You are an AI tools researcher with up to date knowledge of April 2026. What is the single most impressive and useful AI tool launched or updated in 2025-2026? Give me real accurate information. Return ONLY a valid JSON object with no markdown, no code blocks, no extra text. The object must have exactly these keys: name (string), link (string, actual working website URL), summary (string, 3-4 lines about what makes this tool special), price_type (string, exactly one of: Free, Freemium, Paid), category (string), why_best (string, 1-2 lines explaining why this tool stands out)."""
        
        # Generate content with Gemini
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        
        # Wait for 1 second to avoid rate limiting
        time.sleep(1)
        
        # Parse the JSON response
        response_text = response.text.strip()
        
        # Find JSON object in the response (in case there's extra text)
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            tool = json.loads(json_str)
            
            # Validate we got a dictionary
            if not isinstance(tool, dict):
                logger.error(f"Gemini response is not a dict: {type(tool)}")
                raise ValueError("Response is not a dictionary")
        else:
            logger.warning(f"No JSON object found in Gemini response: {response_text}")
            raise ValueError("No JSON object found in response")
        
        # Validate required fields
        required_fields = ['name', 'link', 'summary', 'price_type', 'category', 'why_best']
        for field in required_fields:
            if field not in tool:
                logger.error(f"Missing required field '{field}' in Gemini response")
                raise ValueError(f"Missing required field: {field}")
        
        # Check if duplicate
        if is_duplicate(tool['link']):
            logger.info("Best tool is duplicate, fetching all tools and returning first")
            all_tools = await fetch_all_tools()
            if all_tools:
                return all_tools[0]
            else:
                # Fallback if no tools available
                return {
                    "name": "TheresAnAIForThat",
                    "link": "https://theresanaiforthat.com",
                    "summary": "Best directory for latest AI tools",
                    "price_type": "Free",
                    "category": "Directory",
                    "why_best": "Largest AI tools collection updated daily"
                }
        
        return tool
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in fetch_best_tool: {e}")
        logger.error(f"Response text: {response.text if 'response' in locals() else 'No response'}")
        # Fallback response
        return {
            "name": "TheresAnAIForThat",
            "link": "https://theresanaiforthat.com",
            "summary": "Best directory for latest AI tools",
            "price_type": "Free",
            "category": "Directory",
            "why_best": "Largest AI tools collection updated daily"
        }
    except Exception as e:
        logger.error(f"Error fetching best AI tool from Gemini: {e}")
        # Fallback response
        return {
            "name": "TheresAnAIForThat",
            "link": "https://theresanaiforthat.com",
            "summary": "Best directory for latest AI tools",
            "price_type": "Free",
            "category": "Directory",
            "why_best": "Largest AI tools collection updated daily"
        }