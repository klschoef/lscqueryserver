import json
import argparse
import asyncio
import websockets
import time

parser = argparse.ArgumentParser(description='Process and send log file entries to the lsc query server and save responses.')
parser.add_argument('log_file', type=str, help='Path to the log file containing queries to send.')
parser.add_argument('--server_url', type=str, default='ws://localhost:8080', help='WebSocket server URL (default: ws://localhost:8080).')
parser.add_argument('--response_log_file', type=str, default=f'response.{int(time.time())}.log', help='File to save the responses from the server (default: response.[timestamp].log).')

args = parser.parse_args()

async def send_and_receive_message():
    print(f"Trying to connect to server {args.server_url} ...")
    async with websockets.connect(args.server_url) as websocket:
        print(f"Connected to server {args.server_url} ...")
        with open(args.log_file, 'r') as file:
            log_file_lines = file.readlines()
            total_lines = len(log_file_lines)

        with open(args.response_log_file, 'w') as response_file:
            for index, line in enumerate(log_file_lines):
                current_line = index + 1
                if not line.strip():
                    continue
                parts = line.split(':', 1)
                if len(parts) < 2:
                    print("Invalid log entry format. Skipping...")
                    continue
                json_content = parts[1].strip()

                print(f"Sending query ({current_line}/{total_lines}) to the server... {json_content}")
                try:
                    await websocket.send(json_content)
                    error = False
                    while True:
                        response = await websocket.recv()
                        response = json.loads(response)
                        if "results" in response:
                            print("Received results from the server.")
                            response_file.write(f"{parts[0]}: {json.dumps([r.get('filepath') for r in response['results'] if r and r.get('filepath')])}\n")
                            break
                        elif response.get("type", "") == "progress":
                            print(f"Progress: {response.get('message', '')}")
                        if response.get("type", "") == "error":
                            print(f"Error: {response.get('message', '')}")
                            error = True
                            break

                    if error:
                        continue

                except Exception as e:
                    print(f"Error: {e}")

        print("Done processing all entries.")

asyncio.get_event_loop().run_until_complete(send_and_receive_message())
