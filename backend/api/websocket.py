from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
from graph.workflow import graph
import traceback
import asyncio


# ---------------- SAFE SEND HELPER ----------------
async def safe_send(websocket: WebSocket, data: dict):
    try:
        await websocket.send_json(data)
    except (WebSocketDisconnect, RuntimeError):
        raise WebSocketDisconnect()


# ---------------- MAIN WEBSOCKET ----------------
async def websocket_chat(websocket: WebSocket):

    await websocket.accept()

    try:
        while True:

            # ---------------- RECEIVE USER INPUT ----------------
            question = await websocket.receive_text()

            # ---------------- AGENT STATUS UPDATES ----------------
            await safe_send(websocket, {"agent": "planner", "status": "running"})
            await safe_send(websocket, {"agent": "research", "status": "running"})
            await safe_send(websocket, {"agent": "rag", "status": "running"})
            await safe_send(websocket, {"agent": "memory", "status": "running"})
            await safe_send(websocket, {"agent": "graph", "status": "running"})

            print("\n========== INVOKING GRAPH ==========\n")

            # ---------------- GRAPH EXECUTION ----------------
            try:
                # non-blocking safe execution (prevents websocket freeze)
                result = await asyncio.to_thread(
                    graph.invoke,
                    {"question": question}
                )

                print("\n========== GRAPH COMPLETED ==========\n")
                print(result)

                # ---------------- SUCCESS STATUS ----------------
                await safe_send(websocket, {"agent": "writer", "status": "completed"})
                await safe_send(websocket, {"agent": "reviewer", "status": "completed"})

                await safe_send(websocket, {
                    "answer": result.get("answer", "No answer returned")
                })

            except Exception as e:

                print("\n========== GRAPH ERROR ==========\n")
                traceback.print_exc()

                # ---------------- FAILURE STATUS ----------------
                try:
                    await safe_send(websocket, {"agent": "writer", "status": "failed"})
                    await safe_send(websocket, {"agent": "reviewer", "status": "failed"})

                    await safe_send(websocket, {
                        "answer": f"Graph error: {str(e)}"
                    })
                except WebSocketDisconnect:
                    break

    # ---------------- CLIENT DISCONNECT HANDLING ----------------
    except WebSocketDisconnect:
        print("Client disconnected cleanly")

    except Exception:
        print("\n========== WEBSOCKET ERROR ==========\n")
        traceback.print_exc()