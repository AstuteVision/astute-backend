import asyncio
import websockets
import requests


async def receive_data():
    url = "http://localhost:8000/register"
    response = requests.post(url)
    id = response.json().get("id")
    print(id)
    headers = {"client-id": id}
    async with websockets.connect(
        f"ws://localhost:8000/ws", extra_headers=headers
    ) as websocket:
        print("c")
        while True:
            data = await websocket.recv()
            print(f"Получены данные: {data}")


asyncio.get_event_loop().run_until_complete(receive_data())
