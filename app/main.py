import openai
from fastapi import FastAPI
from app.config import Config

app = FastAPI()
config = Config()

openai.api_key = Config.OPEN_API_KEY
messages = []


@app.post("/openai")
async def openai_endpoint(request_data: dict):
    if "content" not in request_data:
        return {"error": "Invalid request data"}

    content = request_data["content"]
    messages.append({"role": "user", "content": content})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        print(response)
        response_content = response["choices"][0]["message"]["content"]
        print(response_content)
        messages.append({"role": "assistant", "content": response_content})
        return {"response": response_content}
    except Exception as e:
        return {"error": str(e)}
