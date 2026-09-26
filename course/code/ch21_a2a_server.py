"""Chapter 21: the Chapter 8 SQL analyst published as an A2A (Agent2Agent) agent.

Section 13.6 published this agent as an MCP *tool*. Here it becomes an A2A *agent*: it
describes itself in an agent card, accepts tasks, reports progress while it works and
returns its answer as an artifact. Any A2A client, in any framework, can use it.

Run it:    ./course.sh serve-a2a
           (its card: http://localhost:9999/.well-known/agent-card.json)
Try it:    ./course.sh python ch21_a2a_client.py   (starts its own copy if needed)
Secure it: set A2A_TOKEN in .env; callers then send "Authorization: Bearer <token>"."""
import asyncio
import hmac
import logging
import os
import sys

from a2a.helpers import (get_message_text, new_task_from_user_message,
                         new_text_message, new_text_part)
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import (AgentCapabilities, AgentCard, AgentInterface, AgentSkill,
                       HTTPAuthSecurityScheme, SecurityScheme, TaskState)
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from ch04_agent import run_agent
import ch08_sql_tools as sql

log = logging.getLogger("a2a-agent")
PORT = int(os.environ.get("A2A_PORT", "9999"))
PUBLIC_URL = os.environ.get("A2A_PUBLIC_URL", f"http://localhost:{PORT}")
TOKEN = os.environ.get("A2A_TOKEN", "")
MAX_STEPS = 8                # the inner agent's own budget; callers can't raise it

# ------------------------------------------------------------ 1. the agent card
# What other agents read to decide whether, and how, to call this one.
BEARER = {"bearer": SecurityScheme(
    http_auth_security_scheme=HTTPAuthSecurityScheme(scheme="bearer"))}
CARD = AgentCard(
    name="Shop data analyst",
    description="Answers questions about the shop's customers, products, orders "
                "and revenue by writing and running read-only SQL.",
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(streaming=True),
    supported_interfaces=[AgentInterface(protocol_binding="JSONRPC", url=PUBLIC_URL,
                                         protocol_version="1.0")],
    skills=[AgentSkill(
        id="shop_data_questions",
        name="Shop data questions",
        description="One self-contained question about sales data, answered in "
                    "plain English with the numbers found.",
        tags=["sql", "sales", "analytics"],
        examples=["How many orders were cancelled?",
                  "Which city has the most customers?"],
    )],
    security_schemes=BEARER if TOKEN else {},
)

# ------------------------------------------------------------ 2. the executor
class AgentLoopExecutor(AgentExecutor):
    """Runs one A2A task as one run of the Chapter 4 agent loop."""

    def __init__(self, tools, run_tool, system, working="Working on it..."):
        self.tools, self.run_tool = tools, run_tool
        self.system, self.working = system, working

    async def execute(self, context: RequestContext, queue: EventQueue) -> None:
        task = context.current_task or new_task_from_user_message(context.message)
        if not context.current_task:
            await queue.enqueue_event(task)       # the caller gets a task id at once
        updater = TaskUpdater(event_queue=queue, task_id=task.id,
                              context_id=task.context_id)
        question = get_message_text(context.message)
        log.info("task %s: %s", task.id, question[:200])
        await updater.update_status(state=TaskState.TASK_STATE_WORKING,
                                    message=new_text_message(self.working))
        # run_agent is blocking code: run it in a thread so the server stays responsive
        answer, _, stats = await asyncio.to_thread(
            run_agent, question, self.tools, self.run_tool, system=self.system,
            max_iterations=MAX_STEPS, verbose=False)
        if stats["stop_reason"] not in ("end_turn", "stop_sequence"):
            await updater.update_status(
                state=TaskState.TASK_STATE_FAILED,
                message=new_text_message(f"The agent didn't finish: {answer}"))
            return
        await updater.add_artifact(
            parts=[new_text_part(text=answer, media_type="text/plain")], name="answer")
        await updater.update_status(state=TaskState.TASK_STATE_COMPLETED)
        log.info("task %s done in %d steps", task.id, stats["steps"])

    async def cancel(self, context: RequestContext, queue: EventQueue) -> None:
        raise NotImplementedError("Tasks here are short; cancelling isn't supported.")

# ------------------------------------------------------------ 3. the server
class RequireToken:
    """ASGI middleware. The card stays public (it's how callers find you); every
    other request needs "Authorization: Bearer <A2A_TOKEN>" when a token is set."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        public = scope.get("path", "").startswith("/.well-known/")
        if TOKEN and scope["type"] == "http" and not public:
            auth = dict(scope.get("headers") or []).get(b"authorization", b"").decode()
            if not hmac.compare_digest(auth.removeprefix("Bearer ").strip(), TOKEN):
                refuse = JSONResponse({"error": "wrong token"}, status_code=401)
                return await refuse(scope, receive, send)
        await self.app(scope, receive, send)

def build_app(card=CARD, executor=None):
    """An ASGI app that serves `card` and runs tasks (default: the SQL analyst)."""
    executor = executor or AgentLoopExecutor(sql.TOOLS, sql.run_tool, sql.SYSTEM,
                                             working="Querying the shop database...")
    handler = DefaultRequestHandler(agent_executor=executor, agent_card=card,
                                    task_store=InMemoryTaskStore())
    routes = [*create_agent_card_routes(card), *create_jsonrpc_routes(handler, "/")]
    return RequireToken(Starlette(routes=routes))

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    log.info("A2A agent card at %s/.well-known/agent-card.json", PUBLIC_URL)
    uvicorn.run(build_app(), host=os.environ.get("A2A_HOST", "0.0.0.0"), port=PORT,
                log_level="warning")
