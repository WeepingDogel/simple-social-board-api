# Simple Social Board

A social media platform with microservices architecture built with FastAPI backend and Nuxt.js frontend.

## Features

- User authentication and profile management
- Post creation with images (up to 9 per post)
- Social interactions (like, repost)
- Real-time updates via WebSocket
- Admin dashboard for moderation
- Responsive UI with daisyUI

## Backend Architecture

The backend follows a microservices pattern, with the following components:

- **Auth Service**: User registration, login, JWT
- **User Profile Service**: Profile management
- **Post Service**: Post creation and retrieval
- **Interaction Service**: Likes and reposts
- **Media Service**: Image upload and storage
- **Admin Service**: User and content moderation

## Tech Stack

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- JWT Authentication
- WebSockets
- Docker

### Frontend (Planned)
- Nuxt.js
- Tailwind CSS
- daisyUI
- Pinia for state management

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)

### Running the Backend

1. Clone the repository
```bash
git clone <repository-url>
cd simple-social-board
```

2. Start the backend services
```bash
docker-compose up -d
```

The API will be available at http://localhost:8000

### API Documentation

Once the server is running, you can access the Swagger documentation at:

- http://localhost:8000/docs
- http://localhost:8000/redoc

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:postgres@db:5432/social_board
```

## Development

To run the backend for development:

```bash
cd src
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Project Structure

```
simple-social-board-api/
├── src/                    # Source code
│   ├── app/                # Main application
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic services
│   │   └── main.py         # FastAPI application
├── static/                 # Static files (media, etc.)
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker configuration
├── requirements.txt        # Python dependencies
└── README.md
```

## Frontend Development (Coming Soon)

Instructions for setting up and running the Nuxt.js frontend.

## Deployment

The application is containerized and can be deployed to any Docker-compatible environment:

- Docker Swarm
- Kubernetes
- AWS ECS
- Google Cloud Run
- Azure Container Instances

## License

MIT