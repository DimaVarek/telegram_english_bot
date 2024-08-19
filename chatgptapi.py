import time

from openai import AsyncOpenAI
from Types import EnglishLevel
from tokens import CHATGPT_API_KEY


class ChatGPTClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=CHATGPT_API_KEY)

    async def generate_list(self, word: str, level: str):
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": f"I learn english. You must come up with 10 sentences using the word given to you. "
                                    f"And write them without any additional information. Level {level}."
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": word
                        }
                    ]
                }
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "text"
            }
        )
        return response.choices[0].message.content

