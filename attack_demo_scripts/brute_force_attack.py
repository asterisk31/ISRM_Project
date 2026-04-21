import requests

url = "http://localhost:5000/login"
session = requests.Session()

for pwd in ["1234", "admin", "welcome1", "password123"]:
    r = session.post(url, data={"username": "alice", "password": pwd}, allow_redirects=False)
    print(pwd, r.status_code, r.headers.get("Location"), session.cookies.get_dict())
