# 🚀 EduTrack Setup Guide

## Prerequisites

- Node.js (v16 or higher)
- MySQL (v8.0 or higher)
- Git

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/edutrack.git
cd edutrack
```

### 2. Install Dependencies
```bash
npm run install-all
```

### 3. Database Setup
1. Create a MySQL database named `edutrack_db`
2. Import the schema:
```bash
mysql -u root -p edutrack_db < database/schema.sql
```

### 4. Environment Configuration
Create `.env` files in the backend directory:

**backend/.env**
```env
PORT=5000
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=edutrack_db
JWT_SECRET=your_jwt_secret_key
```

### 5. Start the Application
```bash
npm start
```

This will start both the backend server (port 5000) and frontend development server (port 3000).

## Access Points

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api

## Features

- ✅ Student Management
- ✅ Attendance Tracking (QR Code, Face Recognition, Manual)
- ✅ Real-time Analytics Dashboard
- ✅ Faculty Panel
- ✅ Student Panel
- ✅ Notifications & Alerts

## Tech Stack

- **Frontend**: React.js, Bootstrap, Chart.js
- **Backend**: Node.js, Express.js
- **Database**: MySQL
- **Additional**: QR Code generation, Face Recognition (OpenCV)

## Development

```bash
# Development mode with auto-reload
npm run dev

# Build for production
npm run build
```

## Troubleshooting

1. **Database Connection Issues**: Check MySQL service and credentials
2. **Port Conflicts**: Change ports in .env files
3. **Dependencies**: Run `npm run install-all` again

## Support

For issues and questions, please create an issue on GitHub.
