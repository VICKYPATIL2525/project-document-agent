"""
LLM Client - Handles all Azure OpenAI interactions.
Provides sync and async methods with token tracking.
"""
import asyncio
import tiktoken
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_VERSION,
    AZURE_DEPLOYMENT_NAME,
    MAX_OUTPUT_TOKENS_PER_CALL,
)


def get_llm(temperature: float = 0.7, max_tokens: int = MAX_OUTPUT_TOKENS_PER_CALL) -> AzureChatOpenAI:
    """Create and return an AzureChatOpenAI instance."""
    return AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_VERSION,
        azure_deployment=AZURE_DEPLOYMENT_NAME,
        deployment_name=AZURE_DEPLOYMENT_NAME,
        model_name=AZURE_DEPLOYMENT_NAME,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def count_tokens(text: str, model: str = "gpt-4.1-mini") -> int:
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
    max_tokens: int = MAX_OUTPUT_TOKENS_PER_CALL,
) -> dict:
    """
    Make a single LLM call and return result with token counts.

    Returns:
        dict with keys: content, input_tokens, output_tokens
    """
    llm = get_llm(temperature=temperature, max_tokens=max_tokens)
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
    max_tokens: int = MAX_OUTPUT_TOKENS_PER_CALL,
) -> dict:
    """
    Make an async LLM call and return result with token counts.

    Returns:
        dict with keys: content, input_tokens, output_tokens
    """
    llm = get_llm(temperature=temperature, max_tokens=max_tokens)
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

    Args:
        calls: List of dicts with keys: system_prompt, user_prompt, temperature (optional), max_tokens (optional)
        concurrency: Max number of concurrent calls

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
                max_tokens=call_params.get("max_tokens", MAX_OUTPUT_TOKENS_PER_CALL),
            )

    tasks = [limited_call(c) for c in calls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    processed = []
    for i, result in enumerate(results):
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
