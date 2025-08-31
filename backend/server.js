const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const mysql = require('mysql2/promise');

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Database connection
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'edutrack_db'
};

// Create database connection pool
const pool = mysql.createPool(dbConfig);

// Test database connection
pool.getConnection()
  .then(connection => {
    console.log('✅ Database connected successfully');
    connection.release();
  })
  .catch(err => {
    console.error('❌ Database connection failed:', err);
  });

// Routes
app.get('/', (req, res) => {
  res.json({ 
    message: 'EduTrack API is running!',
    version: '1.0.0',
    status: 'active'
  });
});

// Student routes
app.get('/api/students', async (req, res) => {
  try {
    const [rows] = await pool.execute('SELECT * FROM students');
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/students', async (req, res) => {
  try {
    const { name, roll_number, email, department } = req.body;
    const [result] = await pool.execute(
      'INSERT INTO students (name, roll_number, email, department) VALUES (?, ?, ?, ?)',
      [name, roll_number, email, department]
    );
    res.status(201).json({ id: result.insertId, message: 'Student added successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Attendance routes
app.post('/api/attendance', async (req, res) => {
  try {
    const { student_id, class_id, status, timestamp } = req.body;
    const [result] = await pool.execute(
      'INSERT INTO attendance (student_id, class_id, status, timestamp) VALUES (?, ?, ?, ?)',
      [student_id, class_id, status, timestamp || new Date()]
    );
    res.status(201).json({ id: result.insertId, message: 'Attendance marked successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/attendance/:student_id', async (req, res) => {
  try {
    const { student_id } = req.params;
    const [rows] = await pool.execute(
      'SELECT * FROM attendance WHERE student_id = ? ORDER BY timestamp DESC',
      [student_id]
    );
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Analytics routes
app.get('/api/analytics/attendance-summary', async (req, res) => {
  try {
    const [rows] = await pool.execute(`
      SELECT 
        s.name,
        s.roll_number,
        COUNT(a.id) as total_classes,
        SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present_count,
        ROUND((SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) / COUNT(a.id)) * 100, 2) as attendance_percentage
      FROM students s
      LEFT JOIN attendance a ON s.id = a.student_id
      GROUP BY s.id, s.name, s.roll_number
      ORDER BY attendance_percentage ASC
    `);
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 EduTrack API server running on port ${PORT}`);
  console.log(`📊 Dashboard: http://localhost:${PORT}`);
});
