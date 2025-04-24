# Simple Social Board

A social media platform with microservices architecture built with FastAPI backend and Nuxt.js frontend.

## Features

- User authentication and profile management with secure UUID identifiers
- Post creation with images (up to 9 per post)
- Social interactions (like, repost)
- Follow/unfollow functionality with follower and following counts
- Real-time updates via WebSocket
- Admin dashboard for moderation
- Responsive UI with daisyUI
- Comprehensive API documentation
- Support for both SQLite (development) and PostgreSQL (production)
- Automatic database migrations

## Backend Architecture

The backend follows a microservices pattern, with the following components:

- **Auth Service**: User registration, login, JWT authentication
- **User Profile Service**: Profile management
- **Post Service**: Post creation, retrieval and search
- **Interaction Service**: Likes, reposts, and following
- **Media Service**: Image upload and storage
- **WebSocket Service**: Real-time updates and notifications
- **Admin Service**: User and content moderation

## Tech Stack

### Backend
- FastAPI
- PostgreSQL with UUID support
- SQLite for development
- SQLAlchemy ORM
- JWT Authentication
- WebSockets for real-time communication
- Docker & Docker Compose

### Frontend (Planned)
- Nuxt.js
- Tailwind CSS
- daisyUI
- Pinia for state management

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.9+ (for local development)

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

### Database Migrations

The application includes automatic database migrations that run during startup. If you're updating from a previous version, please refer to the [Migration Guide](docs/migration-guide.md) for details on the database changes.

### API Documentation

Once the server is running, you can access the interactive Swagger documentation at:

- http://localhost:8000/docs
- http://localhost:8000/redoc

For a comprehensive API reference, see the [API Reference Document](docs/api-reference.md).

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:postgres@db:5432/social_board
```

For SQLite in development:
```
DATABASE_URL=sqlite:///./database.db
```

## Development

To run the backend for development:

```bash
# Using the development script (recommended)
chmod +x run_dev.sh
./run_dev.sh
```

Or manually:

```bash
cd src
pip install -r requirements.txt
export PYTHONPATH=$(pwd)
uvicorn app.main:app --reload
```

## Database Support

The application supports both PostgreSQL and SQLite:

- **PostgreSQL**: Recommended for production with proper UUID support
- **SQLite**: Quick setup for development and testing

Database initialization handles:
- Creating required tables
- Enabling the UUID extension in PostgreSQL
- Custom UUID type for cross-database compatibility

## WebSocket Features

The application provides WebSocket endpoints for real-time features:

- `/api/ws`: General updates (new posts, likes, reposts)
- `/api/ws/notifications`: User-specific notifications

WebSocket authentication is handled through query parameters, allowing for user-specific updates.

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
├── docs/                   # Documentation
│   └── api-reference.md    # Comprehensive API reference
├── static/                 # Static files (media, etc.)
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker configuration
├── requirements.txt        # Python dependencies
└── README.md
```

## Frontend Development

### Getting Started with Frontend

1. Clone the frontend repository (or navigate to the frontend directory)
```bash
cd frontend
npm install
npm run dev
```

2. The development server will start at http://localhost:3000

### Frontend Architecture

The frontend is built with Nuxt.js and follows a modular architecture:

- **Pages**: Main views for different sections
- **Components**: Reusable UI elements
- **Stores**: State management with Pinia
- **Composables**: Shared logic and API integration
- **Middleware**: Authentication and route guards

### API Integration Guide

#### Authentication Flow

1. **Registration**:
```javascript
// Example using fetch API
async function registerUser(userData) {
  const response = await fetch('http://localhost:8000/api/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });
  return response.json();
}
```

2. **Login and Token Handling**:
```javascript
// Example with axios
async function login(email, password) {
  try {
    const response = await axios.post('http://localhost:8000/api/auth/token', 
      new URLSearchParams({
        'username': email, // API expects username field even though it's an email
        'password': password
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );
    
    // Store the token for future requests
    localStorage.setItem('token', response.data.access_token);
    return response.data;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
}
```

3. **Using the Token for Authenticated Requests**:
```javascript
// Example of an authenticated request
async function fetchUserProfile() {
  const token = localStorage.getItem('token');
  
  try {
    const response = await fetch('http://localhost:8000/api/profiles/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.json();
  } catch (error) {
    console.error('Failed to fetch profile:', error);
    throw error;
  }
}
```

#### WebSocket Integration

1. **Connecting to the Main WebSocket**:
```javascript
function connectToUpdates() {
  const token = localStorage.getItem('token');
  const ws = new WebSocket(`ws://localhost:8000/api/ws?token=${token}`);
  
  ws.onopen = () => {
    console.log('Connected to updates websocket');
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // Handle different event types
    switch(data.type) {
      case 'new_post':
        // Handle new post
        break;
      case 'new_like':
        // Handle new like
        break;
      case 'new_repost':
        // Handle new repost
        break;
      case 'heartbeat':
        // Respond to heartbeat
        break;
    }
  };
  
  ws.onclose = () => {
    // Reconnect logic
    setTimeout(() => connectToUpdates(), 1000);
  };
  
  return ws;
}
```

2. **Connecting to User Notifications**:
```javascript
function connectToNotifications() {
  const token = localStorage.getItem('token');
  
  // This endpoint requires authentication
  const ws = new WebSocket(`ws://localhost:8000/api/ws/notifications?token=${token}`);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'notification') {
      // Display notification to user
      showNotification(data.data);
    }
  };
  
  return ws;
}
```

#### Handling Posts and Media

1. **Creating a Post with Images**:
```javascript
async function createPost(content, imageFiles) {
  const token = localStorage.getItem('token');
  
  // First upload images
  const imageUrls = [];
  for (const file of imageFiles) {
    const formData = new FormData();
    formData.append('file', file);
    
    const uploadResponse = await fetch('http://localhost:8000/api/media/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    const uploadResult = await uploadResponse.json();
    imageUrls.push(uploadResult.file_url);
  }
  
  // Then create post with image URLs
  const postResponse = await fetch('http://localhost:8000/api/posts', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      content: content,
      image_urls: imageUrls
    })
  });
  
  return postResponse.json();
}
```

2. **Fetching and Displaying Posts**:
```javascript
async function fetchPosts(page = 1, limit = 10) {
  try {
    const response = await fetch(`http://localhost:8000/api/posts?page=${page}&limit=${limit}`);
    return response.json();
  } catch (error) {
    console.error('Failed to fetch posts:', error);
    throw error;
  }
}
```

### Working with UUID Fields

The API uses UUID fields for all IDs. When sending or receiving data:

```javascript
// Example of creating a post with a reply to another post
async function createReply(content, replyToPostId) {
  const token = localStorage.getItem('token');
  
  // UUID must be a string in the correct format
  const response = await fetch('http://localhost:8000/api/posts', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      content: content,
      reply_to_post_id: replyToPostId // UUID as string
    })
  });
  
  return response.json();
}
```

### Error Handling

The API returns consistent error responses. Handle them with:

```javascript
async function makeApiCall(url, options) {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const errorData = await response.json();
      
      // Handle specific error cases
      if (response.status === 401) {
        // Unauthorized - redirect to login
        router.push('/login');
      } else if (response.status === 403) {
        // Forbidden - user doesn't have permission
        showError('You do not have permission to perform this action');
      } else if (response.status === 404) {
        // Not found
        showError('The requested resource was not found');
      } else {
        // General error
        showError(errorData.detail || 'An error occurred');
      }
      
      throw new Error(errorData.detail || 'API request failed');
    }
    
    return response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}
```

### Recommended Packages

For frontend development with this API, we recommend:

- **axios**: For HTTP requests with easy interceptors for auth
- **pinia**: State management
- **vue-query** or **swrv**: Data fetching and caching
- **vue-use**: Composable utilities including WebSocket helpers
- **vee-validate**: Form validation
- **date-fns**: Date formatting and manipulation

## Deployment

The application is containerized and can be deployed to any Docker-compatible environment:

- Docker Swarm
- Kubernetes
- AWS ECS
- Google Cloud Run
- Azure Container Instances

## Testing

Run tests with pytest:

```bash
cd src
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT

#### Following Users

1. **Follow a User**:
```javascript
async function followUser(userId) {
  const token = localStorage.getItem('token');
  
  try {
    const response = await fetch(`http://localhost:8000/api/followers/follow/${userId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  } catch (error) {
    console.error('Failed to follow user:', error);
    throw error;
  }
}
```

2. **Unfollow a User**:
```javascript
async function unfollowUser(userId) {
  const token = localStorage.getItem('token');
  
  try {
    const response = await fetch(`http://localhost:8000/api/followers/unfollow/${userId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  } catch (error) {
    console.error('Failed to unfollow user:', error);
    throw error;
  }
}
```

3. **Get User's Followers**:
```javascript
async function getUserFollowers(userId, page = 1, limit = 20) {
  try {
    const response = await fetch(`http://localhost:8000/api/followers/${userId}/followers?page=${page}&limit=${limit}`);
    return response.json();
  } catch (error) {
    console.error('Failed to fetch followers:', error);
    throw error;
  }
}
```

4. **Get Users Followed by User**:
```javascript
async function getUserFollowing(userId, page = 1, limit = 20) {
  try {
    const response = await fetch(`http://localhost:8000/api/followers/${userId}/following?page=${page}&limit=${limit}`);
    return response.json();
  } catch (error) {
    console.error('Failed to fetch following users:', error);
    throw error;
  }
}
```