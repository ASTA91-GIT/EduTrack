import requests

base_url = "http://127.0.0.1:8000/api/v1"

# 1. Login as Student
stu_payload = {"email": "student1@edutrack.local", "password": "student123"}
res_stu = requests.post(f"{base_url}/auth/login/json", json=stu_payload)
stu_token = res_stu.json()["access_token"]
stu_headers = {"Authorization": f"Bearer {stu_token}"}

# 2. Login as Faculty
fac_payload = {"email": "faculty@edutrack.local", "password": "faculty123"}
res_fac = requests.post(f"{base_url}/auth/login/json", json=fac_payload)
fac_token = res_fac.json()["access_token"]
fac_headers = {"Authorization": f"Bearer {fac_token}"}

# Test Timetable
r1 = requests.get(f"{base_url}/academic/timetable", headers=stu_headers)
print("Timetable GET:", r1.status_code, "Items:", len(r1.json()))

# Test Lectures
r2 = requests.get(f"{base_url}/academic/lectures", headers=stu_headers)
print("Lectures GET:", r2.status_code, "Items:", len(r2.json()))

# Test Resources
r3 = requests.get(f"{base_url}/resources/", headers=stu_headers)
print("Resources GET:", r3.status_code, "Items:", len(r3.json()) if r3.status_code == 200 else r3.text)

# Test Admin / Faculty Add Resource
import io
files = {'file': ('test.txt', io.BytesIO(b"Hello from test"), 'text/plain')}
data = {'title': 'Test Book', 'description': 'Test Desc', 'resource_type': 'document', 'subject': 'CS'}
r4 = requests.post(f"{base_url}/resources/", data=data, files=files, headers=fac_headers)
print("Resource POST (Faculty):", r4.status_code)
if r4.status_code == 200:
    res_id = r4.json()["id"]
    r5 = requests.get(f"{base_url}/resources/{res_id}/download", headers=stu_headers)
    print("Resource Download (Student):", r5.status_code, r5.content)
