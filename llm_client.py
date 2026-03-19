"""
LLM Client - Handles all Anthropic Claude interactions.
Provides sync and async methods with token tracking.
"""
import asyncio
import tiktoken
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from config import (
    ANTHROPIC_API_KEY,
    PLANNER_MODEL,
    GENERATOR_MODEL,
    DEFAULT_MAX_OUTPUT_TOKENS,
    MAX_OUTPUT_TOKENS_PER_CALL,
)


def get_llm(temperature: float = 0.7, max_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS, model: str = None) -> ChatAnthropic:
    """Create and return a ChatAnthropic instance."""
    return ChatAnthropic(
        api_key=ANTHROPIC_API_KEY,
        model=model or GENERATOR_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count the number of tokens in a text string."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    model: str = None,
) -> dict:
    """
    Make a single LLM call and return result with token counts.

    Returns:
        dict with keys: content, input_tokens, output_tokens
    """
    llm = get_llm(temperature=temperature, max_tokens=max_tokens, model=model)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    input_tokens = count_tokens(system_prompt + user_prompt)
    response = llm.invoke(messages)
    output_tokens = count_tokens(response.content)

    return {
        "content": response.content,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


async def call_llm_async(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    model: str = None,
) -> dict:
    """
    Make an async LLM call and return result with token counts.

    Returns:
        dict with keys: content, input_tokens, output_tokens
    """
    llm = get_llm(temperature=temperature, max_tokens=max_tokens, model=model)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    input_tokens = count_tokens(system_prompt + user_prompt)
    response = await llm.ainvoke(messages)
    output_tokens = count_tokens(response.content)

    return {
        "content": response.content,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


async def batch_call_llm(
    calls: list[dict],
    concurrency: int = 5,
) -> list[dict]:
    """
    Run multiple LLM calls in parallel batches.

    Each call dict supports keys: system_prompt, user_prompt, temperature (optional),
    max_tokens (optional), model (optional — defaults to GENERATOR_MODEL).

    Returns:
        List of result dicts with keys: content, input_tokens, output_tokens
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def limited_call(call_params):
        async with semaphore:
            return await call_llm_async(
                system_prompt=call_params["system_prompt"],
                user_prompt=call_params["user_prompt"],
                temperature=call_params.get("temperature", 0.7),
                max_tokens=call_params.get("max_tokens", DEFAULT_MAX_OUTPUT_TOKENS),
                model=call_params.get("model", None),
            )

    tasks = [limited_call(c) for c in calls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    processed = []
    for result in results:
        if isinstance(result, Exception):
            processed.append(
                {
                    "content": f"ERROR: {str(result)}",
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "error": str(result),
                }
            )
        else:
            processed.append(result)

    return processed
