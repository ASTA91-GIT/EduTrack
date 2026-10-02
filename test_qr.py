import requests
import json
import time

base_url = "http://127.0.0.1:8000/api/v1"

# 1. Login as Faculty
fac_payload = {"email": "faculty@edutrack.local", "password": "faculty123"}
res_fac = requests.post(f"{base_url}/auth/login/json", json=fac_payload)
if res_fac.status_code != 200:
    print("Faculty login failed:", res_fac.text)
    exit(1)
fac_token = res_fac.json()["access_token"]
fac_headers = {"Authorization": f"Bearer {fac_token}"}

# 2. Login as Student
stu_payload = {"email": "student1@edutrack.local", "password": "student123"}
res_stu = requests.post(f"{base_url}/auth/login/json", json=stu_payload)
stu_token = res_stu.json()["access_token"]
stu_headers = {"Authorization": f"Bearer {stu_token}"}

# 3. Faculty Creates QR Session
sess_payload = {
    "subject": "Security",
    "class_name": "CS-A",
    "duration_minutes": 10
}
res_sess = requests.post(f"{base_url}/attendance_sessions/session", json=sess_payload, headers=fac_headers)
print("Create Session:", res_sess.status_code)
session_token = res_sess.json()["session_token"]
print("Token:", session_token)

# 4. Student Scans QR successfully
scan_payload = {"session_token": session_token}
res_scan1 = requests.post(f"{base_url}/attendance_sessions/session/scan", json=scan_payload, headers=stu_headers)
print("Scan 1 (Valid):", res_scan1.status_code, res_scan1.json())

# 5. Student Scans again (Duplicate)
res_scan2 = requests.post(f"{base_url}/attendance_sessions/session/scan", json=scan_payload, headers=stu_headers)
print("Scan 2 (Duplicate):", res_scan2.status_code, res_scan2.json())

# 6. Faculty closes session
res_close = requests.post(f"{base_url}/attendance_sessions/session/{session_token}/close", headers=fac_headers)
print("Close Session:", res_close.status_code)

# 7. Another student tries to scan closed session
res_stu2 = requests.post(f"{base_url}/auth/login/json", json={"email": "student2@edutrack.local", "password": "student123"})
stu2_token = res_stu2.json()["access_token"]
res_scan3 = requests.post(f"{base_url}/attendance_sessions/session/scan", json=scan_payload, headers={"Authorization": f"Bearer {stu2_token}"})
print("Scan 3 (Closed Session):", res_scan3.status_code, res_scan3.json())

