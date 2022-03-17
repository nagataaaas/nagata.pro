from pydantic import BaseModel


class QRCodeRequest(BaseModel):
    text: str
    scheme: str = 'default'

    class Config:
        schema_extra = {
            "example": {
                "text": "https://github.com/nagataaaas",
                "scheme": "default"
            }
        }
