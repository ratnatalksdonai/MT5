# Web dashboard for monitoring real-time trade data
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json
import os
from threading import Thread
from typing import Any, Dict

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Trade Copy Dashboard</title>
</head>
<body>
    <h1>Trade Copy Monitoring</h1>
    <div id="trade_data">Waiting for trade data...</div>
    <script>
        const ws = new WebSocket('ws://' + window.location.host + '/ws');

        ws.onmessage = function(event) {
            document.getElementById('trade_data').innerText = event.data;
        };
    </script>
</body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    with open("logs/trade_copier.log") as log_file:
        for line in log_file:
            await websocket.send_text(line.strip())
    await websocket.close()


def run_app():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    dashboard_thread = Thread(target=run_app)
    dashboard_thread.start()
