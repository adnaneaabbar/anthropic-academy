import os
from dotenv import load_dotenv
import asyncio
from anthropic import AsyncAnthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import RequestContext
from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult,
    TextContent,
    SamplingMessage,
)

load_dotenv()

# Anthropic Config
anthropic_client = AsyncAnthropic()
model = os.getenv("CLAUDE_MODEL", "")

text_to_summarize = """
The increase in global temperatures has led to more frequent and severe weather events, posing a significant threat to ecosystems and human societies. One of the major impacts of climate change is the rise in sea levels, which results from the melting of polar ice caps and glaciers. Coastal areas are particularly vulnerable, as they face higher risks of flooding, storm surges, and erosion. Additionally, the warming atmosphere can hold more moisture, leading to intense and unpredictable precipitation patterns. This variability can cause both severe droughts and devastating floods, affecting agricultural productivity and water resources.
The effects of climate change are widespread, influencing not only the environment but also the socio-economic stability of communities. For example, changing weather patterns can disrupt food supply chains, increase the prevalence of diseases, and force people to migrate from their homes. To mitigate these effects, countries are investing in adaptive infrastructure, developing early warning systems, and implementing policies to reduce greenhouse gas emissions. The collaboration between governments, scientists, and communities is crucial to building resilience against the adverse impacts of climate change. By taking proactive measures, societies can better prepare for the challenges posed by a changing climate and work towards a more sustainable future.
"""

server_params = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
)


async def chat(input_messages: list[SamplingMessage], max_tokens=4000):
    messages = []
    for msg in input_messages:
        if msg.role == "user" and msg.content.type == "text":
            content = (
                msg.content.text
                if hasattr(msg.content, "text")
                else str(msg.content)
            )
            messages.append({"role": "user", "content": content})
        elif msg.role == "assistant" and msg.content.type == "text":
            content = (
                msg.content.text
                if hasattr(msg.content, "text")
                else str(msg.content)
            )
            messages.append({"role": "assistant", "content": content})

    response = await anthropic_client.messages.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )

    text = "".join([p.text for p in response.content if p.type == "text"])
    return text


async def sampling_callback(
    context: RequestContext, params: CreateMessageRequestParams
):
    # Call Claude using the Anthropic SDK
    text = await chat(params.messages)

    return CreateMessageResult(
        role="assistant",
        model=model,
        content=TextContent(type="text", text=text),
    )


async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, sampling_callback=sampling_callback
        ) as session:
            await session.initialize()

            result = await session.call_tool(
                name="summarize",
                arguments={"text_to_summarize": text_to_summarize},
            )
            print(result.content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
