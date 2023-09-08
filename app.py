import uuid

import cv2
import uvicorn
from fastapi import FastAPI, WebSocket
from tracker.dummy import DummyTracker
from recommendator.dummy import DummyRecommendator
from graph import Graph
import json
import asyncio


app = FastAPI()

connected_clients = {}

CONST_cam_ips = "consts.txt"


#NEAR_REAL content: Полное сообщение товара "рядом с вами сыр"
#NEAR_RECOMMENDED content: Полное сообщение товара "вы дошли до сыр"
#DIRECTION: число от 1 до 360
#json: {type: str, content: str}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = websocket.headers.get("client-id")
    urls = get_urls()
    print(client_id)
    connected_clients[client_id] = websocket
    # fixme destination_zone_id
    tracker = DummyTracker()
    recommendator = DummyRecommendator()
    graph = Graph()
    real_goods = [12, 8]
    recommendations = recommendator.predict(real_goods)
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
            if (man_coordinate==graph.coords[destination]):
                if destination in real_goods:
                    await send_message(client_id, json.dumps({"type": "NEAR_REAL", "content": "вы дошли до сыр"}))
                if destination in recommendations:
                    await send_message(client_id, json.dumps({"type": "NEAR_RECOMMENDED", "content": "рядом с вами сыр"}))
                destination_index+=1
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
