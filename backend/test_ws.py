import asyncio
import websockets

async def test():
    uri = "ws://127.0.0.1:8000/ws"

    async with websockets.connect(uri) as ws:
        await ws.send("What is AI?")

        # 🔥 Read FULL STREAM
        while True:
            try:
                msg = await ws.recv()
                print(msg)

                if "final_answer" in msg:
                    break

            except Exception:
                break

asyncio.run(test())