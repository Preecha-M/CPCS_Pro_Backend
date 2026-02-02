from google import genai
from google.genai import types
from datetime import datetime, timedelta
import asyncio
from ..core import config
from .. import state

# Initial setup
client = None
if config.GEMINI_API_KEY:
    client = genai.Client(api_key=config.GEMINI_API_KEY)

# System Instruction / Persona
RICE_EXPERT_INSTRUCTION = """
คุณคือ "พี่ข้าวหอม" ผู้ช่วยอัจฉริยะด้านการปลูกข้าวและการเกษตร
คุณมีความเชี่ยวชาญเรื่องโรคข้าว แมลงศัตรูพืช การใส่ปุ๋ย และการดูแลรักษาแปลงนา
- ตอบคำถามด้วยภาษาไทยที่สุภาพ เป็นกันเอง เข้าใจง่าย เหมาะสำหรับเกษตรกร
- เน้นให้ข้อมูลที่ปฏิบัติได้จริง (Actionable advice)
- หากได้รับคำถามที่ไม่เกี่ยวกับข้าวหรือการเกษตร ให้ตอบกลับอย่างสุภาพว่าขอให้ถามเรื่องที่เกี่ยวข้อง
- พยายามกระชับคำตอบ ไม่ยืดเยื้อเกินความจำเป็น
"""

class GeminiService:
    @staticmethod
    async def generate_reply(user_message: str) -> str:
        """
        Generates a reply using the current Gemini model.
        Handles 429 Resource Exhausted by switching to fallback.
        Checks if it's time to switch back to primary.
        """
        if not client:
             return "ระบบยังไม่ได้เชื่อมต่อกับ Gemini API (Missing API Key)"

        # Check if we should switch back to primary
        if state.CURRENT_GEMINI_MODEL != config.GEMINI_MODEL_PRIMARY:
            if state.GEMINI_QUOTA_RESET_TIME and datetime.now() > state.GEMINI_QUOTA_RESET_TIME:
                state.CURRENT_GEMINI_MODEL = config.GEMINI_MODEL_PRIMARY
                state.GEMINI_QUOTA_RESET_TIME = None
                print(f"🔄 Quota reset! Switching back to Primary Model: {state.CURRENT_GEMINI_MODEL}")

        try:
            return await GeminiService._call_gemini(state.CURRENT_GEMINI_MODEL, user_message)
        except Exception as e:
            # Check for 429 Resource Exhausted (The new SDK might raise different error types, catching broad Exception for now)
            # Typically looks for "429" or "RESOURCE_EXHAUSTED"
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "exhausted" in error_str.lower():
                print(f"⚠️ Quota exceeded on {state.CURRENT_GEMINI_MODEL}. Switching to fallback...")
                
                # Switch to fallback if we haven't already
                if state.CURRENT_GEMINI_MODEL == config.GEMINI_MODEL_PRIMARY:
                    state.CURRENT_GEMINI_MODEL = config.GEMINI_MODEL_FALLBACK
                    # Set a conservative reset time
                    state.GEMINI_QUOTA_RESET_TIME = datetime.now() + timedelta(minutes=10)
                    
                    # Retry immediately with fallback
                    try:
                        return await GeminiService._call_gemini(state.CURRENT_GEMINI_MODEL, user_message)
                    except Exception as fallback_error:
                         return f"❌ ขออภัย ระบบ AI ไม่สามารถตอบกลับได้ในขณะนี้ (Fallback Failed: {fallback_error})"
            
            return f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อกับ AI: {e}"

    @staticmethod
    async def _call_gemini(model_name: str, text: str) -> str:
        # Run synchronous generation in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        try:
            def sync_call():
                # Define config with system instruction
                generate_config = types.GenerateContentConfig(
                    system_instruction=RICE_EXPERT_INSTRUCTION
                )
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=text,
                    config=generate_config
                )
                # Check structure of response object in new SDK
                # Usually response.text is available if it's a simple text response
                return response.text

            return await loop.run_in_executor(None, sync_call)
        except Exception as e:
            raise e
