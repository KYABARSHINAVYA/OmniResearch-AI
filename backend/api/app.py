from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from multimodal.multimodal_router import route_input

from memory.sqlite_memory import save_chat
from memory.semantic_memory import save_memory
from fastapi.responses import PlainTextResponse, StreamingResponse
from graph.workflow import graph
import time

from analytics.token_usage import get_token_usage
from analytics.tool_calls import get_tool_stats
from analytics.memory_hits import get_memory_hits
from auth.auth_routes import router
from fastapi import WebSocket
from api.websocket import websocket_chat
from analytics.agent_status import get_status
from analytics.agent_logs import get_logs
from analytics.latency_monitor import get_latencies
from human_loop.approval import approve
from human_loop.approval import ask_for_approval
from persistence.checkpoints import load_checkpoint
from agents.autonomous_research import generate_report
from agents.browser_agent import browse_url
from config.llm import llm_status
from monitoring.metrics import prometheus_metrics

app = FastAPI()
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*"           # for testing only
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],      # allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)
print("MIDDLEWARE:")
print(app.user_middleware)
print("CORS middleware loaded")
app.include_router(router)


# -----------------------------
# Request Model
# -----------------------------
class Query(BaseModel):
    question: str
    mode: str = "balanced"


class BrowserRequest(BaseModel):
    url: str
    selector: str | None = None


class ResearchRequest(BaseModel):
    topic: str
    urls: list[str] = Field(default_factory=list)


# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "OmniResearch AI Backend Running",
        "features": [
            "multi_llm_routing",
            "evaluator_agent",
            "browser_agent",
            "autonomous_research_reports",
            "prometheus_metrics",
            "vector_graph_memory_architecture",
        ],
    }


# -----------------------------
# CHAT ENDPOINT (UPDATED)
# -----------------------------
@app.post("/chat")
def chat(data: Query):

    # Run LangGraph workflow
    result = graph.invoke(
        {
            "question": data.question,
            "mode": data.mode
        }
    )

    # Save to SQLite Memory
    save_chat(
        data.question,
        str(result["answer"])
    )

    # Save to Semantic Memory
    save_memory(
        data.question,
        str(result["answer"])
    )

    return {
        "plan": result["plan"],
        "answer": result["answer"],
        "evaluation": result.get("evaluation"),
        "timings": result.get("timings"),
        "mode": result.get("mode")
    }
from fastapi import UploadFile, File
import os


@app.post("/multimodal")
async def multimodal_chat(
        file: UploadFile = File(...)
):

    upload_dir = "uploads"

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    file_path = os.path.join(
        upload_dir,
        file.filename
    )

    with open(
            file_path,
            "wb"
    ) as buffer:

        buffer.write(
            await file.read()
        )

    extension = file.filename.split(".")[-1]

    if extension in ["png", "jpg", "jpeg"]:

        extracted_text = route_input(
            "image",
            file_path
        )

    elif extension in ["wav"]:

        extracted_text = route_input(
            "audio",
            file_path
        )

    else:

        extracted_text = "Unsupported file"

    result = graph.invoke(
        {
            "question": extracted_text
        }
    )

    return {
        "extracted_text": extracted_text,
        "answer": result["answer"]
    }
@app.post("/chat-stream")
def chat_stream(data: Query):

    result = graph.invoke({"question": data.question, "mode": data.mode})
    answer = result["answer"]

    def generate():
        for word in answer.split():
            yield word + " "
            time.sleep(0.03)  # typing effect

    return StreamingResponse(generate(), media_type="text/plain")
@app.get("/analytics")
def analytics():

    return {

        "token_usage": get_token_usage(),

        "tool_calls": get_tool_stats(),

        "memory_hits": get_memory_hits()

    }
@app.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket
):

    await websocket_chat(
        websocket
    )
@app.get("/dashboard")
def dashboard():

    return {

        "agent_status": get_status(),

        "latencies": get_latencies(),

        "token_usage": get_token_usage(),

        "tool_calls": get_tool_stats(),

        "memory_hits": get_memory_hits(),

        "logs": get_logs()

    }


@app.get("/llm/status")
def llm_router_status():
    return llm_status()


@app.post("/browser")
def browser(request: BrowserRequest):
    return browse_url(request.url, request.selector)


@app.post("/research/autonomous")
def autonomous_research(request: ResearchRequest):
    return generate_report(request.topic, request.urls)


@app.get("/architecture")
def architecture():
    return {
        "vector": "ChromaDB semantic memory plus FAISS document retrieval",
        "graph": "Neo4j entity relationship retrieval",
        "memory": "SQLite chat history and ChromaDB long-term semantic memory",
        "routing": "GPT, Gemini, DeepSeek, or Ollama selected by task and environment",
        "monitoring": "FastAPI /metrics endpoint for Prometheus and Grafana dashboards",
        "browser": "Playwright browser agent for page extraction when installed",
    }


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return prometheus_metrics()
@app.get("/pause")
def pause_workflow():

    return ask_for_approval()
@app.get("/approve")
def human_approve():

    return approve()
@app.get("/checkpoint")
def checkpoint():

    return load_checkpoint()
