import cv2, base64
import uvicorn
from fastapi import FastAPI, WebSocket
import uuid
from ml_model import DummyTracker

app = FastAPI()

connected_clients = {}

CONST_cam_ips = "consts.txt"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = websocket.headers.get("client-id")
    urls = get_urls()
    print(client_id)
    connected_clients[client_id] = websocket
    tracker = DummyTracker()
    try:
        i = 0
        while True:
            i += 1
            frames = get_frames(urls)
            is_change_direction = tracker.predict(frames)
            if is_change_direction:
                # Detect anomalies and notify clients
                await send_message(client_id, str(i))
    except Exception as e:
        del connected_clients[client_id]


async def send_message(client_id: str, message: str):
    websocket = connected_clients.get(client_id)
    if websocket:
        await websocket.send_text(message)


def get_id():
    return str(uuid.uuid4())


@app.post("/register")
async def register():
    id = get_id()
    return {"id": id}


async def get_frames(urls):
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

        # Convert the frame to bytes
        _, img_encoded = cv2.imencode(".jpg", frame)

        # Convert the bytes to base64 string
        img_base64 = base64.b64encode(img_encoded).decode("utf-8")

        # Return the base64 string of the frame
        return img_base64


async def get_urls():
    with open(CONST_cam_ips) as file:
        streams_addresses = [line.rstrip() for line in file]
    return streams_addresses


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
