from huggingface_hub import InferenceClient
import os

class LLMService:
    def __init__(self):
        self.client = InferenceClient(
            model="deepseek-ai/deepseek-llm-7b",
            token=os.getenv("HF_TOKEN")  # Get your free token at huggingface.co/settings/tokens
        )

    def generate(self, prompt: str) -> str:
        try:
            return self.client.text_generation(
                prompt,
                max_new_tokens=1000,
                temperature=0.7
            )
        except Exception as e:
            raise Exception(f"HuggingFace error: {str(e)}")