import React from 'react';

function App() {
    return (
        <div style={{ padding: 24 }}>
            <h2>EduTrack</h2>
            <p>Use the links below to open the static pages:</p>
            <ul>
                <li><a href="/login.html">Login</a></li>
                <li><a href="/teacher.html">Teacher Dashboard</a></li>
                <li><a href="/manage-students.html">Manage Students</a></li>
                <li><a href="/attendance.html">Attendance</a></li>
                <li><a href="/reports.html">Reports</a></li>
            </ul>
        </div>
    );
}

export default App;