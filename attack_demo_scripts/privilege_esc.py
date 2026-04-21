import requests

base_url = "http://localhost:5000"
session = requests.Session()
session.post(
    f"{base_url}/login",
    data={"username": "alice", "password": "password123"},
)

req = session.post(f"{base_url}/api/change_role", data={"username": "alice", "role": "admin"})
print(req.status_code)
