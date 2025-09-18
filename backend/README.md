# EduTrack Backend

This is the backend service for the EduTrack application, a student attendance tracking system with facial recognition capabilities.

## Features

- JWT-based authentication with refresh tokens
- Role-based access control
- Facial recognition for attendance tracking
- Optimized database connections with connection pooling
- Comprehensive error handling and logging
- Secure CORS configuration

## Tech Stack

- FastAPI: Modern, fast web framework for building APIs
- SQLAlchemy: SQL toolkit and ORM
- PostgreSQL: Relational database
- JWT: JSON Web Tokens for authentication
- Face Recognition: For biometric attendance verification

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Virtual environment (recommended)

### Installation

1. Clone the repository
2. Navigate to the backend directory
3. Create and activate a virtual environment (optional but recommended)

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

4. Install dependencies

```bash
pip install -r requirements.txt
```

5. Set up environment variables by copying `.env.example` to `.env` and updating the values

```bash
cp .env.example .env
# Edit .env with your configuration
```

6. Run the application

```bash
uvicorn app.main:app --reload
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `JWT_REFRESH_SECRET_KEY`: Secret key for refresh token generation
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration time in minutes
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration time in days
- `CORS_ORIGINS`: Comma-separated list of allowed origins for CORS
- `DEBUG`: Enable debug mode (True/False)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `APP_NAME`, `APP_VERSION`, `APP_DESCRIPTION`: Application metadata
- `LOG_FILE`, `LOG_FORMAT`: Logging configuration

## API Documentation

When the server is running, you can access the API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Main Endpoints

### Authentication

- `POST /api/auth/register`: Register a new user
- `POST /api/auth/login`: Login and get access token
- `POST /api/auth/refresh`: Refresh access token
- `GET /api/auth/me`: Get current user information

### Attendance

- `POST /api/attendance/record`: Record attendance
- `GET /api/attendance/history`: Get attendance history
- `GET /api/attendance/stats`: Get attendance statistics

## Docker Support

You can also run the application using Docker:

```bash
docker build -t edutrack-backend .
docker run -p 8000:8000 --env-file .env edutrack-backend
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.