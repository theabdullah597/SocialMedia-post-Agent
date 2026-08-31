from google import genai
from config import LLM_API_KEY
def generate_text(prompt):
    client=genai.Client(api_key=LLM_API_KEY)
    chat=client.chats.create(model="gemini-3.6-flash")
    response=chat.send_message(prompt)
    return response.text


if __name__=="__main__":
    result=generate_text("Write a code in pyhton that i can use gemini api key for generating text")
    print(result)