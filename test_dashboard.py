import requests

base_url = "http://127.0.0.1:8000/api/v1"

# 1. Login as student 1 (from seed)
login_payload = {
    "email": "student1@edutrack.local",
    "password": "student123"
}
res = requests.post(f"{base_url}/auth/login/json", json=login_payload)
token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. What-If Simulation
res_whatif = requests.get(f"{base_url}/dashboard/student/whatif?attend_next=5", headers=headers)
print("WhatIf Response Code:", res_whatif.status_code)
if res_whatif.status_code == 200:
    print(res_whatif.json())
else:
    print(res_whatif.text)

# 3. Overall Dashboard
res_dash = requests.get(f"{base_url}/dashboard/student", headers=headers)
print("Dashboard Response Code:", res_dash.status_code)

