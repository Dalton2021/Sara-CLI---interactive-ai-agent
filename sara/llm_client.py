"""LM Studio client with streaming support"""
import requests
import json
from typing import Iterator, Optional


class LMStudioClient:
    def __init__(self, base_url: str = "http://127.0.0.1:1234"):
        self.base_url = base_url
        self.api_url = f"{base_url}/v1/chat/completions"

    def stream_chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Iterator[str]:
        """Stream responses from LM Studio"""
        payload = {
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                stream=True,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.RequestException as e:
            yield f"\n\nError connecting to LM Studio: {str(e)}\n"
            yield "Make sure LM Studio is running and the server is started.\n"

    def check_connection(self) -> bool:
        """Check if LM Studio is accessible"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
