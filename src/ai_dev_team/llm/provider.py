import ollama
from threading import Event, Thread
from time import perf_counter


class LLMProvider:
    #def __init__(self, model: str = "qwen2.5-coder:7b"):
    #def __init__(self, model: str = "llama3.1:latest"):
    def __init__(self, model: str = "qwen3:14b", timeout: float = 600):       
        self.model = model
        self.client = ollama.Client(timeout=timeout)

    def chat(self, messages: list, tools: list) -> ollama.Message:
        """Return an assistant message including tool calls for an agent loop."""
        response = self._request(messages=messages, tools=tools, think=False)
        return response.message
    

    def _request(self, **kwargs):
        """Report waiting time without changing the model request or response."""
        started = perf_counter()
        stopped = Event()

        def report_wait():
            while not stopped.wait(300):
                elapsed = perf_counter() - started
                print(f'[Ollama] Waiting for {self.model}: {elapsed:.0f}s elapsed '
                      '(response not received yet).', flush=True)

        print(f'[Ollama] Request started: {self.model}', flush=True)
        reporter = Thread(target=report_wait, daemon=True)
        reporter.start()
        try:
            response = self.client.chat(model=self.model, **kwargs)
            print(f'[Ollama] Response received in {perf_counter() - started:.2f}s', flush=True)
            return response
        except BaseException as exc:
            print(f'[Ollama] Request interrupted or failed: {type(exc).__name__}', flush=True)
            raise
        finally:
            stopped.set()
            reporter.join()

    def generate(self, prompt: str) -> str:
        response = self._request(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            think=False,
        )

        return response["message"]["content"]
