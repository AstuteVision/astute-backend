import uuid

import cv2
import uvicorn
from fastapi import Depends, FastAPI, WebSocket

from deps import get_tracker

app = FastAPI()

connected_clients = {}

CONST_cam_ips = "consts.txt"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, tracker=Depends(get_tracker)):
    await websocket.accept()
    client_id = websocket.headers.get("client-id")
    urls = get_urls()
    print(client_id)
    connected_clients[client_id] = websocket
    # fixme destination_zone_id
    destination_coords = 10
    try:
        i = 0
        while True:
            i += 1
            frames = get_frames(urls)
            is_change_direction = tracker.predict(frames, destination_coords=destination_coords)
            if is_change_direction:
                # Detect anomalies and notify clients
                await send_message(client_id, str(i))
    except Exception as e:
        print(e)
        del connected_clients[client_id]


async def send_message(client_id: str, message: str):
    websocket = connected_clients.get(client_id)
    if websocket:
        await websocket.send_text(message)


def get_id():
    return str(uuid.uuid4())


@app.post("/register")
async def register():
    client_id = get_id()
    return {"id": client_id}


async def get_frames(urls: list[str]):
    frames = []
    for url in urls:
        frames.append(read_video_frame(url))
    return frames


async def read_video_frame(url):
    # Create a VideoCapture object with the URL of the video stream
    cap = cv2.VideoCapture(url)
    while True:
        # Read the next frame from the video stream
        ret, frame = cap.read()
        if not ret:
            # Return None if there's no more frames or an error occurred
            return None
        return frame


async def get_urls() -> list[str]:
    with open(CONST_cam_ips) as file:
        streams_addresses = [line.rstrip() for line in file]
    return streams_addresses


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
