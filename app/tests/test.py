import requests

thread_data = {
  "user_id": "abc123"
}

message_data = {
    "thread_id": "your-thread-id-from-previous-call",
    "content": "Hi, can you help me make a plan to Manchester?"
}

response = requests.post("http://127.0.0.1:8000/api/thread", json=thread_data)
print(response.json())