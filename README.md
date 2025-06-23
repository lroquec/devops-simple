# User Management System

## Overview
This project implements a microservices-based user management system with admin and user services using Python Flask and MySQL.

## System Requirements

- Docker and Docker Compose
- Python 3.12+
- MySQL 8.0+

## Project Structure

```
.
├── admin-service/           # Admin microservice
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   ├── static/
│   ├── templates/
│   └── tests/
├── user-service/           # User microservice
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   ├── static/
│   ├── templates/
│   └── tests/
└── shared/
    └── database/
        └── init.sql
```

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/lroquec/devops-simple.git
cd devops-simple
```

2. Create `.env` file:
```bash
SECRET_KEY=your_secret_key_here
MYSQL_HOST=db
MYSQL_USER=root
MYSQL_PASSWORD=example
MYSQL_DB=pythonlogin
```

3. Start services:
```bash
docker compose up -d
```

## Access Services

- Admin Service: http://localhost:5001
- User Service: http://localhost:5002
- Database: localhost:3306

## Default Credentials

Admin Service:
- Username: admin
- Password: myVerysecurepass531.

## Running Tests

Admin Service:
```bash
cd admin-service
python -m pytest --cov=. tests/
```

User Service:
```bash
cd user-service
python -m pytest --cov=. tests/
```

## Features

### Admin Service
- User CRUD operations
- Role-based access control
- User listing and search
- Secure password handling

### User Service
- User registration
- Authentication
- Profile management
- Session handling

## Development Guidelines

### Code Style
```bash
# Run linter
flake8 admin-service user-service
```

### Testing Best Practices
- Write unit tests for new features
- Maintain >80% test coverage
- Run tests before commits

### Security Guidelines
- Use environment variables
- Hash passwords
- Validate all inputs
- Use prepared statements

## Troubleshooting

### Database Issues
```bash
# Check database status
docker compose ps

# View database logs
docker compose logs db
```

### Service Issues
```bash
# View service logs
docker compose logs admin-service
docker compose logs user-service

# Reset environment
docker compose down -v
docker compose up --build -d
```
