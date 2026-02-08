from openai import OpenAI
import os


class AIBackend:
    def __init__(self):
        self.key = os.getenv("OPENAI_API_KEY")

        if self.key is None:
            raise EnvironmentError("OpenAI API key not set")

        self.client = OpenAI(
            api_key=self.key,
            base_url="https://api.gapgpt.app/v1",
        )

    def send_message(self, message: str, model='gpt-4o'):
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': message
                }
            ]
        )
        return response.choices[0].message.content

