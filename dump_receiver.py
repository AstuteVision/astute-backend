import asyncio

import requests
import websockets


async def receive_data():
    url = "http://localhost:8000/register"
    response = requests.post(url, timeout=60)
    client_id = response.json().get("id")
    print(client_id)
    headers = {"client-id": client_id}
    async with websockets.connect("ws://localhost:8000/ws", extra_headers=headers) as websocket:
        print("c")
        while True:
            data = await websocket.recv()
            print(f"Пoлyчeны дaнныe: {data}")


asyncio.get_event_loop().run_until_complete(receive_data())
