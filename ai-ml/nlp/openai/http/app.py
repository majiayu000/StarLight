import json
import os
import secrets
import asyncio
from typing import AsyncGenerator

import httpx
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["OPENAI_API_KEY_"]
# Distinct from OPENAI_API_KEY_: callers must present this token to use the proxy.
PROXY_AUTH_TOKEN = os.environ["PROXY_AUTH_TOKEN"]
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
TIMEOUT = 40

client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)

app = FastAPI()

# auto_error=False so we return a uniform 401 (and never echo credential material).
_bearer_scheme = HTTPBearer(auto_error=False)


def _proxy_tokens_match(provided: str, expected: str) -> bool:
    """Constant-time token compare that never raises on non-ASCII input.

    ``secrets.compare_digest`` on ``str`` only supports ASCII and raises
    ``TypeError`` otherwise, which would turn auth failures into 500s.
    Comparing UTF-8 bytes keeps a uniform False (→ 401) for any credential.
    """
    if not expected:
        return False
    provided_b = provided.encode("utf-8")
    expected_b = expected.encode("utf-8")
    if len(provided_b) != len(expected_b):
        return False
    return secrets.compare_digest(provided_b, expected_b)


async def require_proxy_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> None:
    """Reject unauthenticated callers before any upstream OpenAI usage."""
    if (
        credentials is None
        or credentials.scheme.lower() != "bearer"
        or not _proxy_tokens_match(credentials.credentials, PROXY_AUTH_TOKEN)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )



async def ask_async(message: str | None = None):
    # content = None
    if not message:
        print(f"zero")
        stream =  await client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": "you are a assistant"}],
        stream=True
    )
    else:
        stream =  await client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant",
                },
                {"role": "user", "content": message},
            ],
        stream=True
        )
        
    async for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="")
        yield chunk

class ResponseMessage(BaseModel):
    content: str


class RequestMessage(BaseModel):
    message: str


async def openai_stream(
    data: dict,
) -> AsyncGenerator[str, None]:
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "https://api.gptapi.us/v1/chat/completions",
            timeout=httpx.Timeout(TIMEOUT),
            headers={
                "Authorization": f"Bearer {API_KEY}",
            },
            json=data,
        ) as response:
            print(f"received response status_code={response.status_code}")
            response.raise_for_status()
            async for chunk in response.aiter_text():
                yield chunk


async def _handle_function_call(name: str, arguments: dict) -> str:
    pass


async def response_generator(message: str) -> AsyncGenerator[str, None]:
    func_call = {"arguments": "", "name": None}
    async for response in ask_async(message):
        print(f"response is {response}")
        for block_raw in response.split("\n\n"):
            print(f"block is {block_raw}")
            for line in block_raw.split("\n"):
                if line.startswith("data:"):
                    print(f"line is {line}")
                    json_str = line.replace("data:", "").strip()
                    print(f"json is {json_str}")
                    if json_str == "[DONE]":
                        break
                    else:
                        block = json.loads(json_str)

                        # we assume that we only need to look at the first choice
                        choice = block["choices"][0]
                        delta = choice.get("delta")
                    if "function_call" in delta:
                        name = delta["function_call"].get("name")
                        if name:
                            func_call["name"] = name
                        arguments = delta["function_call"].get("arguments")
                        if arguments:
                            func_call["arguments"] += arguments
                    elif "content" in delta:
                        yield ResponseMessage(
                            content=delta["content"],
                        ).model_dump_json() + "\n"

    # we only handle the function call once all the data has been streamed in
    if func_call.get("name"):
        response_message = await _handle_function_call(
            func_call["name"],
            func_call["arguments"],
        )
        yield ResponseMessage(
            content=response_message,
        ).model_dump_json() + "\n"


async def resp_generator(message: str) -> AsyncGenerator[str, None]:
    func_call = {"arguments": "", "name": None}
    async for response in ask_async(message):
        print(f"response is {response}")
        
        if response.choices[0].finish_reason == "[DONE]":
            break
        else:
            
            delta = response.choices[0].delta
        if response.choices[0].delta.function_call != None:
            name = delta["function_call"].get("name")
            if name:
                func_call["name"] = name
            arguments = delta["function_call"].get("arguments")
            if arguments:
                func_call["arguments"] += arguments
        elif delta.content != None:
            yield ResponseMessage(
                content=delta.content,
            ).model_dump_json() + "\n"

    # we only handle the function call once all the data has been streamed in
    if func_call.get("name"):
        response_message = await _handle_function_call(
            func_call["name"],
            func_call["arguments"],
        )
        yield ResponseMessage(
            content=response_message,
        ).model_dump_json() + "\n"


@app.post("/")
async def message(
    request: RequestMessage,
    _: None = Depends(require_proxy_auth),
):
    return StreamingResponse(
        resp_generator(request.message),
        media_type="application/x-ndjson",
    )


if __name__ == "__main__":
    # asyncio.run(ask_async([{"role": "user", "content": "you are a dog"}]))
    uvicorn.run(app)