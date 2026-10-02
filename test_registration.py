import requests

url = "http://127.0.0.1:8000/api/v1/auth/register"

def test_registration(email, role):
    payload = {
        "name": f"Test User {role}",
        "email": email,
        "password": "password123",
        "role": role
    }
    response = requests.post(url, json=payload)
    print(f"[{role.upper()}] Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"[{role.upper()}] Resulting Role: {data.get('user', {}).get('role')}")
    else:
        print(f"[{role.upper()}] Error: {response.text}")

print("Testing Registration with malicious roles...")
test_registration("malicious_admin@edutrack.local", "admin")
test_registration("malicious_faculty@edutrack.local", "faculty")
test_registration("normal_student@edutrack.local", "student")
