from typing import Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from rag.config import Settings


def stream_completion(messages: list[dict], settings: "Settings") -> Generator[str, None, None]:
    backend = settings.llm_backend.lower()

    if backend == "groq":
        yield from _stream_groq(messages, settings)
    elif backend == "azure":
        yield from _stream_azure(messages, settings)
    elif backend == "claude":
        yield from _stream_claude(messages, settings)
    elif backend == "ollama":
        yield from _stream_ollama(messages, settings)
    else:
        raise ValueError(f"Unknown llm_backend: '{backend}'")


def _stream_groq(messages: list[dict], settings: "Settings") -> Generator[str, None, None]:
    from groq import Groq
    client = Groq(api_key=settings.groq_api_key)
    stream = client.chat.completions.create(
        model=settings.groq_model,
        messages=messages,
        stream=True,
        temperature=0.2,
        max_tokens=1024,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content


def _stream_azure(messages: list[dict], settings: "Settings") -> Generator[str, None, None]:
    from openai import AzureOpenAI
    client = AzureOpenAI(
        api_key=settings.azure_api_key,
        azure_endpoint=settings.azure_endpoint,
        api_version=settings.azure_api_version,
    )
    stream = client.chat.completions.create(
        model=settings.azure_deployment,
        messages=messages,
        stream=True,
        temperature=0.2,
        max_tokens=1024,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def _stream_claude(messages: list[dict], settings: "Settings") -> Generator[str, None, None]:
    import anthropic
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    system_prompt = ""
    filtered_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_prompt = msg["content"]
        else:
            filtered_messages.append(msg)

    with client.messages.stream(
        model=settings.claude_model,
        system=system_prompt,
        messages=filtered_messages,
        max_tokens=1024,
        temperature=0.2,
    ) as stream:
        for text in stream.text_stream:
            yield text


def _stream_ollama(messages: list[dict], settings: "Settings") -> Generator[str, None, None]:
    import requests
    import json
    url = f"{settings.ollama_base_url}/api/chat"
    response = requests.post(
        url,
        json={
            "model": settings.ollama_model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": 0.2},
        },
        stream=True,
        timeout=120,
    )
    response.raise_for_status()

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            content = data.get("message", {}).get("content", "")
            if content:
                yield content
            if data.get("done", False):
                break
