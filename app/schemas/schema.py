from pydantic import BaseModel



class TextInput(BaseModel):
    text: str

class TextResponse(BaseModel):
    response: str 