import asyncio
import json
import uuid

import cv2
import uvicorn
from fastapi import FastAPI, WebSocket

from graph import Graph
from recommender.dummy import DummyRecommender
from tracker.dummy import DummyTracker

app = FastAPI()

connected_clients = {}

CONST_cam_ips = "consts.txt"


# NEAR_REAL content: Пoлнoe coo6щeниe тoвapa "pядoм c вaми cыp"
# NEAR_RECOMMENDED content: Пoлнoe coo6щeниe тoвapa "вы дoшли дo cыp"
# DIRECTION: чиcлo oт 1 дo 360
# json: {type: str, content: str}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = websocket.headers.get("client-id")
    urls = get_urls()
    print(client_id)
    connected_clients[client_id] = websocket
    # fixme destination_zone_id
    tracker = DummyTracker()
    recommender = DummyRecommender()
    graph = Graph()
    real_goods = [12, 8]
    recommendations = recommender.predict(real_goods)
    way = graph.dijkstra(real_goods, recommendations)
    print(way)
    destination_index = 0
    destination = way[0]
    destination_coords = graph.coords[way[0]]
    try:
        i = 0
        while True:
            await asyncio.sleep(1)
            i += 1
            frames = get_frames(urls)
            direction, man_coordinate = tracker.predict(frames, destination_coords=destination_coords)
            print(direction, man_coordinate, graph.coords[destination])
            if man_coordinate == graph.coords[destination]:
                if destination in real_goods:
                    await send_message(client_id, json.dumps({"type": "NEAR_REAL", "content": "вы дoшли дo cыp"}))
                if destination in recommendations:
                    await send_message(
                        client_id, json.dumps({"type": "NEAR_RECOMMENDED", "content": "pядoм c вaми cыp"})
                    )
                destination_index += 1
                destination = way[destination_index]
            if direction:
                # Detect anomalies and notify clients
                await send_message(client_id, json.dumps({"type": "DIRECTION", "content": str(direction)}))
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
def register():
    client_id = get_id()
    return {"id": client_id}


async def get_frames(urls: list[str]):
    frames = []
    for url in urls:
        frames.append(read_video_frame(url))
    return frames


def read_video_frame(url):
    # Create a VideoCapture object with the URL of the video stream
    cap = cv2.VideoCapture(url)
    while True:
        # Read the next frame from the video stream
        ret, frame = cap.read()
        if not ret:
            # Return None if there's no more frames or an error occurred
            return None
        return frame


def get_urls() -> list[str]:
    with open(CONST_cam_ips) as file:
        streams_addresses = [line.rstrip() for line in file]
    return streams_addresses


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
