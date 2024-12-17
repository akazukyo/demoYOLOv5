import google.generativeai as genai
from config import GENERATION_CONFIG, SAFETY_SETTINGS, GENAI_API_KEY
import markdown2

genai.configure(api_key=GENAI_API_KEY)

modelGemini = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=GENERATION_CONFIG,
    safety_settings=SAFETY_SETTINGS
)

def promptAll():
    text = " Format the information below, identify the section headings, and format them in a clear and readable way. The section headings should be highlighted, and the detailed content of each section should be presented clearly. Remove any index numbers or navigation numbers, while preserving the content and order of the sections."
    return text

def format_with_gemini(text):
    try:
        prompt = f"""
            {promptAll()}
            \n\n{text}
        """
        chat_session = modelGemini.start_chat(history=[])
        response = chat_session.send_message(prompt)
        markdown_text = response.text
        print(response.usage_metadata)
        html_text = markdown2.markdown(markdown_text, extras=["tables"])
        return html_text
    except Exception as e:
        print(f"Error processing with Gemini: {e}")
        return text