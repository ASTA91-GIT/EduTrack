import requests

base_url = "http://127.0.0.1:8000/api/v1"

# 1. Login as student
login_payload = {
    "email": "normal_student@edutrack.local",
    "password": "password123"
}
res = requests.post(f"{base_url}/auth/login/json", json=login_payload)
token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Try to access admin dashboard
res_admin = requests.get(f"{base_url}/dashboard/admin", headers=headers)
print("Student accessing admin dashboard:", res_admin.status_code)

# 3. Try to access teacher ping
res_teacher = requests.get(f"{base_url}/auth/teacher/ping", headers=headers)
print("Student accessing teacher ping:", res_teacher.status_code)

# 4. Try student ping
res_student = requests.get(f"{base_url}/auth/student/ping", headers=headers)
print("Student accessing student ping:", res_student.status_code)
