from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from pathlib import Path
from dotenv import load_dotenv

# ==========================================
# 1. PUT YOUR NEW GROQ KEY HERE
# ==========================================
MY_API_KEY = os.getenv("GROQ_API_KEY", "gsk_YOUR_API_KEY_HERE")
print(f"DEBUG: The key in the code is: {MY_API_KEY}")

# ==========================================
# 2. AUTOMATIC .ENV CREATOR
# ==========================================
# This forces Windows to create the .env file perfectly
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    with open(env_path, "w") as f:
        f.write(f"GROQ_API_KEY={MY_API_KEY}\n")

# Load the file we just created
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GROQ_API_KEY")

# ==========================================
# 3. INITIALIZE FASTAPI & GROQ
# ==========================================
app = FastAPI(title="Peybrands AI Bot")
client = OpenAI(
    api_key=MY_API_KEY, 
    base_url="https://api.groq.com/openai/v1"
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

# ==========================================
# 4. THE ROUTES
# ==========================================
@app.get("/")
def read_root():
    return {"status": "Chatbot is online!"}

@app.post("/chat", response_model=ChatResponse)
def chat_with_ai(request: ChatRequest):
    user_message = request.message.strip()
    
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b", # The active Groq model
            messages=[
                {"role": "system", "content": "You are a helpful assistant for Peybrands Solar Installations. You help clients with questions about solar panels, inverters, batteries, and installations. Keep your answers clear and concise."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        
        reply = response.choices[0].message.content
        
        # CLEAN THE TEXT: This fixes the weird symbols (Ă°ÂŻ) on Windows
        reply = reply.encode("ascii", "ignore").decode("ascii") # pyright: ignore[reportOptionalMemberAccess]
        
        return ChatResponse(reply=reply)
        
    except Exception as e:
        print(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)