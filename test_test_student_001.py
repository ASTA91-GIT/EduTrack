"""
Comprehensive Test Suite for EduTrack using ONE Central Test Student (TEST_STUDENT_001)
Validates all requirements:
- Real authentication, real database inserts
- 30-meter GPS Geofencing (Haversine formula on backend)
- Accuracy boundary (>60m rejection)
- Duplicate attendance prevention (409 Conflict)
- Dynamic QR expiration and closed session rejection
- WebSocket real-time live attendance broadcasting
- Safe development test data reset
"""

import sys
import os
import requests
import asyncio
import websockets
import json

from backend.app.test_config import (
    ENVIRONMENT,
    TEST_STUDENT_ID,
    TEST_STUDENT_EMAIL,
    TEST_STUDENT_PASSWORD,
    TEST_FACULTY_EMAIL,
    TEST_FACULTY_PASSWORD,
)

BASE = "http://localhost:8000/api/v1"
WS_BASE = "ws://localhost:8000/api/v1"

def print_result(item_num, description, passed, detail=""):
    mark = "PASS" if passed else "FAIL"
    status_str = f"[{mark}]"
    print(f"{status_str:<6} Check {item_num:02d}: {description} {detail}")
    if not passed:
        raise AssertionError(f"Check {item_num} failed: {description}")

async def run_all_tests():
    print("=" * 65)
    print(f"RUNNING EDUTRACK SUITE WITH DEDICATED STUDENT: {TEST_STUDENT_ID}")
    print("=" * 65)

    # 1. Reset any previous test records for TEST_STUDENT_001 safely
    res_reset = requests.post(f"{BASE}/attendance_sessions/dev/reset-test-data")
    print_result(1, "Test Data Cleaned for TEST_STUDENT_001", res_reset.status_code == 200, f"(cleared: {res_reset.json().get('deleted', 0)})")

    # 2. Teacher Login
    res_teach_login = requests.post(f"{BASE}/auth/login/json", json={
        "email": TEST_FACULTY_EMAIL,
        "password": TEST_FACULTY_PASSWORD,
        "role": "teacher"
    })
    teacher_ok = res_teach_login.status_code == 200 and "access_token" in res_teach_login.json()
    print_result(2, "Teacher Authentication Successful", teacher_ok)
    teacher_token = res_teach_login.json()["access_token"]
    headers_teacher = {"Authorization": f"Bearer {teacher_token}"}

    # 3. Student Login with TEST_STUDENT_001
    res_stu_login = requests.post(f"{BASE}/auth/login/json", json={
        "email": TEST_STUDENT_EMAIL,
        "password": TEST_STUDENT_PASSWORD,
        "role": "student"
    })
    student_ok = res_stu_login.status_code == 200 and "access_token" in res_stu_login.json()
    print_result(3, f"TEST_STUDENT_001 Authentication Successful ({TEST_STUDENT_EMAIL})", student_ok)
    student_token = res_stu_login.json()["access_token"]
    headers_student = {"Authorization": f"Bearer {student_token}"}

    # 4. Student Dashboard Loads Real Metrics
    res_dash = requests.get(f"{BASE}/dashboard/student", headers=headers_student)
    print_result(4, "Student Dashboard Data-Driven Response", res_dash.status_code == 200 and "overall_percentage" in res_dash.json())

    # 5. Teacher Creates Live Attendance Session 1 (Room 101 - CS Lab: 19.0760, 72.8777)
    res_session = requests.post(
        f"{BASE}/attendance_sessions/session",
        json={
            "subject": "Distributed Systems",
            "class_name": "CS-A",
            "classroom_name": "Room 101 - CS Lab",
            "duration_minutes": 10,
            "geofence_radius": 30.0
        },
        headers=headers_teacher
    )
    session_data = res_session.json()
    session_ok = res_session.status_code == 200 and "session_token" in session_data and "qr_token" in session_data
    print_result(5, "Teacher Starts Attendance Session with 30m Geofence", session_ok)
    session_token = session_data["session_token"]
    qr_token = session_data["qr_token"]

    # 6. QR Code Generation
    res_qr = requests.get(f"{BASE}/attendance_sessions/session/{session_token}/qr")
    print_result(6, "Dynamic QR Image Generated", res_qr.status_code == 200 and res_qr.headers.get("content-type") == "image/png")

    # 7. QR Dynamic Token Rotation Check
    res_rot = requests.get(f"{BASE}/attendance_sessions/session/{session_token}/refresh-qr", headers=headers_teacher)
    rot_data = res_rot.json()
    rot_ok = res_rot.status_code == 200 and "qr_token" in rot_data
    print_result(7, "QR Dynamic Token Rotation Support (15-20s)", rot_ok)
    latest_qr_token = rot_data["qr_token"]

    # 8 & 9. Connect WebSocket & Trigger Live Verification with TEST_STUDENT_001
    ws_url = f"{WS_BASE}/attendance_sessions/ws/{session_token}"
    async with websockets.connect(ws_url) as ws:
        # Student marks presence inside geofence (Room 101: 19.0760, 72.8777 -> ~8.8m)
        res_inside = requests.post(
            f"{BASE}/attendance_sessions/session/verify-gps",
            json={
                "session_token": session_token,
                "qr_token": latest_qr_token,
                "latitude": 19.07608,
                "longitude": 72.8777,
                "accuracy": 8.5
            },
            headers=headers_student
        )
        inside_data = res_inside.json()
        inside_ok = res_inside.status_code == 200 and inside_data.get("success") is True and inside_data.get("distance") <= 30.0
        print_result(8, f"GPS Inside Geofence (<=30m): Verified", inside_ok, f"(distance: {inside_data.get('distance')}m)")

        # Receive real-time WebSocket push on teacher's connection
        ws_msg = await asyncio.wait_for(ws.recv(), timeout=3.0)
        ws_data = json.loads(ws_msg)
        ws_event_ok = ws_data.get("type") == "STUDENT_VERIFIED" and ws_data["student"]["id"] == TEST_STUDENT_ID
        print_result(9, "WebSocket Broadcast to Teacher Dashboard (Real-Time)", ws_event_ok,
                     f"(Student: {ws_data['student']['name']}, Present Count: {ws_data['present_count']}, Distance: {ws_data['student']['distance']}m)")

    # 10. Test: Duplicate Attendance with SAME TEST_STUDENT_001 in Same Session
    res_dup = requests.post(
        f"{BASE}/attendance_sessions/session/verify-gps",
        json={
            "session_token": session_token,
            "qr_token": latest_qr_token,
            "latitude": 19.07608,
            "longitude": 72.8777,
            "accuracy": 8.5
        },
        headers=headers_student
    )
    dup_ok = res_dup.status_code == 409
    print_result(10, "Duplicate Protection Check (Same Student + Same Session -> 409)", dup_ok, f"({res_dup.json().get('detail')})")

    # 11. Create Session 2 for Negative Geofence Tests (never create another student!)
    res_session2 = requests.post(
        f"{BASE}/attendance_sessions/session",
        json={
            "subject": "Algorithm Analysis",
            "class_name": "CS-A",
            "classroom_name": "Room 101 - CS Lab",
            "duration_minutes": 10,
            "geofence_radius": 30.0
        },
        headers=headers_teacher
    )
    session2_data = res_session2.json()
    session2_token = session2_data["session_token"]
    session2_qr = session2_data["qr_token"]

    # 12. Test: Outside Geofence (> 30m: 19.0800, 72.8777 -> ~445m away)
    res_outside = requests.post(
        f"{BASE}/attendance_sessions/session/verify-gps",
        json={
            "session_token": session2_token,
            "qr_token": session2_qr,
            "latitude": 19.0800,
            "longitude": 72.8777,
            "accuracy": 8.0
        },
        headers=headers_student
    )
    outside_ok = res_outside.status_code == 400 and "Outside classroom" in res_outside.json().get("detail", "")
    print_result(11, "GPS Outside Geofence Check (>30m -> Rejection 400)", outside_ok, f"({res_outside.json().get('detail')})")

    # 13. Test: Poor GPS Accuracy (> 60m: accuracy=85.0)
    res_accuracy = requests.post(
        f"{BASE}/attendance_sessions/session/verify-gps",
        json={
            "session_token": session2_token,
            "qr_token": session2_qr,
            "latitude": 19.07605,
            "longitude": 72.8777,
            "accuracy": 85.0
        },
        headers=headers_student
    )
    acc_ok = res_accuracy.status_code == 400 and "accuracy" in res_accuracy.json().get("detail", "").lower()
    print_result(12, "GPS Accuracy Check (>60m -> Rejection 400)", acc_ok, f"({res_accuracy.json().get('detail')})")

    # 14. Test: Expired / Forged QR Token
    res_expired = requests.post(
        f"{BASE}/attendance_sessions/session/verify-gps",
        json={
            "session_token": session2_token,
            "qr_token": f"{session2_token}_1600000000_fake_signature",
            "latitude": 19.07605,
            "longitude": 72.8777,
            "accuracy": 10.0
        },
        headers=headers_student
    )
    exp_ok = res_expired.status_code == 400
    print_result(13, "Expired / Forged Dynamic QR Token Check (Rejection 400)", exp_ok, f"({res_expired.json().get('detail')})")

    # 15. Test: Closed Session Rejection
    requests.post(f"{BASE}/attendance_sessions/session/{session2_token}/close", headers=headers_teacher)
    res_closed = requests.post(
        f"{BASE}/attendance_sessions/session/verify-gps",
        json={
            "session_token": session2_token,
            "qr_token": session2_qr,
            "latitude": 19.07605,
            "longitude": 72.8777,
            "accuracy": 10.0
        },
        headers=headers_student
    )
    closed_ok = res_closed.status_code == 400 and "Session has ended" in res_closed.json().get("detail", "")
    print_result(14, "Closed Session Check (Rejection 400)", closed_ok, f"({res_closed.json().get('detail')})")

    # 16. Final Cleanup of TEST_STUDENT_001 records
    res_final_clean = requests.post(f"{BASE}/attendance_sessions/dev/reset-test-data")
    print_result(15, "Final Test Student Record Cleanup", res_final_clean.status_code == 200, f"(cleared: {res_final_clean.json().get('deleted', 0)})")

    print("=" * 65)
    print("ALL 15 CORE CRITERIA VERIFIED WITH TEST_STUDENT_001!")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
