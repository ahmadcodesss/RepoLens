import contextlib
import logging
import os
import random

import anyio
from dotenv import load_dotenv
from groq import APIConnectionError, APIStatusError, AsyncGroq

from agent.error import (
    ModelMisbehaviorError,
    PermanentError,
    ResourceLimitError,
    TransientError,
)

load_dotenv()

log = logging.getLogger("repolens.llm")

MODEL_NAME = "openai/gpt-oss-120b"
REQUEST_TIMEOUT = 30.0
MAX_TRANSIENT_ATTEMPTS = 4
MAX_MISBEHAVIOR_ATTEMPTS = 3
BASE_DELAY = 1.0
MAX_DELAY = 30.0
MAX_WAIT = 60.0


@contextlib.asynccontextmanager
async def open_client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise PermanentError("GROQ_API_KEY is not set. Add it to your .env file.")
    async with AsyncGroq(api_key=key, timeout=REQUEST_TIMEOUT, max_retries=0) as client:
        yield client


def convert_mcp_tools_to_openai_format(mcp_tools: list) -> list:
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
            },
        }
        for tool in mcp_tools
    ]


def _retry_after(e: APIStatusError):
    value = e.response.headers.get("retry-after")
    try:
        return float(value) if value else None
    except ValueError:
        return None


def _error_info(e: APIStatusError):
    body = e.body if isinstance(e.body, dict) else {}
    inner = body.get("error", body)
    if not isinstance(inner, dict):
        return None, str(inner)
    return inner.get("code"), str(inner.get("message", ""))


def classify(e: Exception):
    if isinstance(e, APIConnectionError):
        return TransientError("Could not reach the model service.")

    status = e.status_code
    code, message = _error_info(e)

    if status == 400 and code == "tool_use_failed":
        return ModelMisbehaviorError("The model produced an invalid tool call.")
    if status == 413 or (status == 400 and "reduce the length" in message.lower()):
        return ResourceLimitError(
            "The conversation became too large for the model. "
            "Try a more specific question or a smaller repository."
        )
    if status == 429:
        return TransientError(
            "The model service is rate limiting requests.", retry_after=_retry_after(e)
        )
    if status >= 500 or status == 408:
        return TransientError(
            "The model service had a temporary error.", retry_after=_retry_after(e)
        )
    if status in (401, 403):
        return PermanentError("The Groq API key was rejected. Check GROQ_API_KEY.")
    if status == 404:
        return PermanentError(f"Model '{MODEL_NAME}' is not available for this key.")
    return PermanentError(f"The model service rejected the request (status {status}).")


def _delay(attempt: int, retry_after) -> float:
    backoff = min(MAX_DELAY, BASE_DELAY * 2 ** (attempt - 1))
    base = retry_after if retry_after is not None else backoff
    return base + random.uniform(0, 1)


async def call_llm(client, messages: list, tools: list, tool_choice="auto", on_wait=None):
    transient = 0
    misbehaved = 0

    while True:
        try:
            return await client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
            )
        except (APIStatusError, APIConnectionError) as e:
            err = classify(e)
            log.warning("LLM call failed: %s | %s", type(e).__name__, e)

            if isinstance(err, TransientError):
                transient += 1
                if transient >= MAX_TRANSIENT_ATTEMPTS:
                    raise err from e
                delay = _delay(transient, err.retry_after)
                if delay > MAX_WAIT:
                    raise PermanentError(
                        f"Rate limit reached. The service asks to wait about "
                        f"{int(delay)}s. Try again later."
                    ) from e
                log.info("Retrying in %.1fs (attempt %d)", delay, transient)
                if on_wait:
                    on_wait(delay)
                await anyio.sleep(delay)

            elif isinstance(err, ModelMisbehaviorError):
                misbehaved += 1
                if misbehaved >= MAX_MISBEHAVIOR_ATTEMPTS:
                    raise err from e

            else:
                raise err from e