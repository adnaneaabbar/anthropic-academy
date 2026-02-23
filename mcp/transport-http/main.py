import asyncio

import uvicorn
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response
from mcp.server.fastmcp import FastMCP, Context


mcp = FastMCP(
    "mcp-server",
    # stateless_http=True,
    # json_response=True,
)


@mcp.tool()
async def add(a: int, b: int, ctx: Context) -> int:
    await ctx.info("Preparing to add...")
    await asyncio.sleep(2)
    await ctx.report_progress(80, 100)

    return a + b


# Load the demo HTML page
@mcp.custom_route("/", methods=["GET"])
async def get(request: Request) -> Response:
    with open("index.html", "r") as f:
        html_content = f.read()
    return Response(content=html_content, media_type="text/html")


if __name__ == "__main__":
    app = mcp.streamable_http_app()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    uvicorn.run(
        app,
        host=mcp.settings.host,
        port=mcp.settings.port,
        log_level=mcp.settings.log_level.lower(),
    )
