from google import genai
from dotenv import load_dotenv
import os
load_dotenv() 
 


class GenAI():
    def __init__(self):
        API_KEY =  os.getenv("API_KEY")
        self.client = genai.Client(api_key=API_KEY)

    def gen_text(self, text):

        response = self.client.models.generate_content(
        model="gemini-2.0-flash", contents=text
        )
        return {"response": response.text} 
