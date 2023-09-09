import asyncio
import json
import uuid

import cv2
import uvicorn
from fastapi import FastAPI, WebSocket
from tracker.dummy import DummyTracker
from tracker.yolo import YoloTracker
from recommender.dummy import DummyRecommender
from graph import Graph
import json
import asyncio

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
    tracker = YoloTracker()
    recommendator = DummyRecommender()
    graph = Graph()
    goods = parse_goods()
    real_goods = [3, 5]
    recommendations = recommendator.predict(real_goods)
    way = graph.dijkstra(real_goods, recommendations)
    print(way)
    destination_index = 0
    destination = way[0]
    destination_coords = graph.coords[way[0]]
    old_direction = 0
    url = urls[0]
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    try:
        while True:
            await asyncio.sleep(0.2)
            sucess_flag, frame = cap.read()
            if not sucess_flag:
                break
            direction, man_coordinate = tracker.predict(frame, destination_coords=destination_coords)
            cv2.imshow("frames", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            print(man_coordinate)
            if (man_coordinate==graph.coords[destination]):
                if destination in real_goods:
                    print(f"NEAR_REAL {goods[str(destination)]}")
                    await send_message(client_id, json.dumps({"type": "NEAR_REAL", "content": f"Вы дошли до {goods[str(destination)]}"}))
                if destination in recommendations:
                    print(f"NEAR_RECOMMENDED {goods[str(destination)]}")
                    await send_message(client_id, json.dumps({"type": "NEAR_RECOMMENDED", "content": f"Рядом с Вами {goods[str(destination)]}"}))
                destination_index+=1
                destination = way[destination_index]
                destination_coords = graph.coords[destination]
            if direction-old_direction:
                # Detect anomalies and notify clients
                old_direction = direction
                await send_message(client_id, json.dumps({"type": "DIRECTION", "content": str(direction)}))
    except Exception as e:
        print(e)
        del connected_clients[client_id]


async def send_message(client_id: str, message: str):
    websocket = connected_clients.get(client_id)
    if websocket:
        await websocket.send_text(message)

def parse_goods():
    goods = {}
    with open("goods.txt", encoding="utf-8") as f:
        for line in f:
            s = line.split()
            goods[s[0]] = s[1]
    print(goods)
    return goods


def get_id():
    return str(uuid.uuid4())


@app.post("/register")
def register():
    client_id = get_id()
    return {"id": client_id}

@app.get("/goodList")
def register():
    goods = []
    with open("goods.txt", encoding="utf-8") as f:
        for line in f:
            s = line.split()
            goods.append(s[1])
    goods.pop(0)
    print(goods)
    return goods

def get_urls() -> list[str]:
    with open(CONST_cam_ips) as file:
        streams_addresses = [line.rstrip() for line in file]
    return streams_addresses


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
