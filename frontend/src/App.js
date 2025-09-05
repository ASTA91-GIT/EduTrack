import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLogin from './components/login/MainLogin';
import Teacher from './components/teacher/Teacher';
import Student from './components/student/Student';
// ...other imports

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<MainLogin />} />
                <Route path="/teacher" element={<Teacher />} />
                <Route path="/student" element={<Student />} />
                {/* ...other routes */}
            </Routes>
        </BrowserRouter>
    );
}

export default App; 