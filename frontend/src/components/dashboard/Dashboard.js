import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Table, Badge } from 'react-bootstrap';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalStudents: 0,
    totalClasses: 0,
    todayAttendance: 0,
    averageAttendance: 0
  });
  const [recentAttendance, setRecentAttendance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch students
      const studentsResponse = await fetch('http://localhost:5000/api/students');
      const students = await studentsResponse.json();
      
      // Fetch attendance summary
      const attendanceResponse = await fetch('http://localhost:5000/api/analytics/attendance-summary');
      const attendanceData = await attendanceResponse.json();
      
      setStats({
        totalStudents: students.length,
        totalClasses: 4, // Hardcoded for demo
        todayAttendance: attendanceData.filter(s => s.attendance_percentage > 75).length,
        averageAttendance: attendanceData.length > 0 
          ? (attendanceData.reduce((sum, s) => sum + s.attendance_percentage, 0) / attendanceData.length).toFixed(1)
          : 0
      });
      
      setRecentAttendance(attendanceData.slice(0, 5));
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const pieChartData = {
    labels: ['Present', 'Absent', 'Late'],
    datasets: [
      {
        data: [75, 15, 10],
        backgroundColor: ['#28a745', '#dc3545', '#ffc107'],
        borderWidth: 2,
      },
    ],
  };

  const barChartData = {
    labels: ['CS101', 'CS102', 'ME101', 'EE101'],
    datasets: [
      {
        label: 'Attendance %',
        data: [85, 92, 78, 88],
        backgroundColor: 'rgba(54, 162, 235, 0.8)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

  if (loading) {
    return <div className="text-center mt-5">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <h2 className="mb-4">📊 EduTrack Dashboard</h2>
      
      {/* Stats Cards */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <Card.Title>👥 Total Students</Card.Title>
              <Card.Text className="h2 text-primary">{stats.totalStudents}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <Card.Title>📚 Total Classes</Card.Title>
              <Card.Text className="h2 text-success">{stats.totalClasses}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <Card.Title>✅ Today's Attendance</Card.Title>
              <Card.Text className="h2 text-info">{stats.todayAttendance}</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <Card.Title>📈 Average Attendance</Card.Title>
              <Card.Text className="h2 text-warning">{stats.averageAttendance}%</Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>Attendance Distribution</Card.Header>
            <Card.Body>
              <Pie data={pieChartData} />
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header>Class-wise Attendance</Card.Header>
            <Card.Body>
              <Bar 
                data={barChartData} 
                options={{
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 100
                    }
                  }
                }}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Recent Attendance */}
      <Card>
        <Card.Header>Recent Attendance Records</Card.Header>
        <Card.Body>
          <Table striped bordered hover>
            <thead>
              <tr>
                <th>Student Name</th>
                <th>Roll Number</th>
                <th>Department</th>
                <th>Attendance %</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {recentAttendance.map((student, index) => (
                <tr key={index}>
                  <td>{student.name}</td>
                  <td>{student.roll_number}</td>
                  <td>{student.department}</td>
                  <td>{student.attendance_percentage}%</td>
                  <td>
                    <Badge 
                      bg={student.attendance_percentage >= 75 ? 'success' : 
                          student.attendance_percentage >= 60 ? 'warning' : 'danger'}
                    >
                      {student.attendance_percentage >= 75 ? 'Good' : 
                       student.attendance_percentage >= 60 ? 'Warning' : 'Critical'}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </div>
  );
};

export default Dashboard;
