from app.providers.openai_compatible import OpenAICompatibleProvider

class LMStudioProvider(OpenAICompatibleProvider):
    name: str = "lm_studio"

    def __init__(self, base_url: str = "http://127.0.0.1:1234/v1"):
        super().__init__(base_url, name="lm_studio")

