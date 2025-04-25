# Simple Social Board API Reference

## Table of Contents

1. [Authentication](#authentication)
2. [User Profiles](#user-profiles)
3. [Posts](#posts)
4. [Media](#media)
5. [Followers](#followers)
6. [Admin](#admin)
7. [WebSockets](#websockets)
8. [Core](#core)

## Authentication

### Register User

```
POST /api/auth/register
```

Creates a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

**Curl Example:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "username",
    "password": "password123"
  }'
```

**Responses:**

| Status | Description |
|--------|-------------|
| 201 | User account created successfully |
| 400 | Invalid request body or username/email already exists |

**Example Response (201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "username",
  "is_admin": false,
  "created_at": "2023-01-01T12:00:00Z"
}
```

### Login

```
POST /api/auth/token
```

Authenticates a user and returns an access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Curl Example:**
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Authentication successful |
| 401 | Invalid credentials |

**Example Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

## User Profiles

### Get User Profile

```
GET /api/profiles/{user_id}
```

Retrieves a user profile by ID.

**Path Parameters:**
- `user_id`: User ID (UUID)

**Curl Example:**
```bash
curl -X GET "http://localhost:8000/api/profiles/123e4567-e89b-12d3-a456-426614174000"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | User profile found |
| 404 | User profile not found |

**Example Response (200):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "display_name": "User's Display Name",
  "avatar_url": "/static/media/avatars/user123.jpg",
  "background_color": "#f5f5f5",
  "bio": "User's biography text",
  "follower_count": 42,
  "following_count": 123,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Update User Profile

```
PUT /api/profiles/me
```

Updates the current user's profile.

**Authentication:** Bearer token required

**Request Body:**
```json
{
  "display_name": "Updated Name",
  "avatar_url": "/static/media/avatars/user123_new.jpg",
  "background_color": "#e0e0e0",
  "bio": "Updated biography text"
}
```

**Curl Example:**
```bash
curl -X PUT "http://localhost:8000/api/profiles/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Updated Name",
    "avatar_url": "/static/media/avatars/user123_new.jpg",
    "background_color": "#e0e0e0",
    "bio": "Updated biography text"
  }'
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Profile updated successfully |
| 401 | Unauthorized, token missing or invalid |
| 404 | Profile not found |

**Example Response (200):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "display_name": "Updated Name",
  "avatar_url": "/static/media/avatars/user123_new.jpg",
  "background_color": "#e0e0e0",
  "bio": "Updated biography text",
  "follower_count": 42,
  "following_count": 123,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-02T14:30:00Z"
}
```

## Posts

### Get Posts

```
GET /api/posts/feed
```

Retrieves a paginated list of posts.

**Query Parameters:**
- `skip`: Number of posts to skip (default: 0)
- `limit`: Items per page (default: 20)

**Curl Example:**
```bash
curl -X GET "http://localhost:8000/api/posts/feed?skip=0&limit=10"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Posts retrieved successfully |

**Example Response (200):**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "content": "This is a post content",
    "author_id": "123e4567-e89b-12d3-a456-426614174000",
    "author": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "username"
    },
    "created_at": "2023-01-02T15:30:00Z",
    "updated_at": "2023-01-02T15:30:00Z",
    "like_count": 5,
    "repost_count": 2,
    "reply_count": 3,
    "images": [
      {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "image_url": "/static/media/posts/image1.jpg"
      }
    ]
  },
  // More posts...
]
```

### Create Post

```
POST /api/posts
```

Creates a new post.

**Authentication:** Bearer token required

**Request Body:**
```json
{
  "content": "This is my new post!",
  "image_urls": ["/static/media/uploads/image1.jpg"]
}
```

**Curl Example:**
```bash
curl -X POST "http://localhost:8000/api/posts" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is my new post!",
    "image_urls": ["/static/media/uploads/image1.jpg"]
  }'
```

**Responses:**

| Status | Description |
|--------|-------------|
| 201 | Post created successfully |
| 401 | Unauthorized, token missing or invalid |
| 400 | Invalid request body |

**Example Response (201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "This is my new post!",
  "author_id": "123e4567-e89b-12d3-a456-426614174000",
  "author": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "username"
  },
  "created_at": "2023-01-02T15:30:00Z",
  "updated_at": "2023-01-02T15:30:00Z",
  "like_count": 0,
  "repost_count": 0,
  "reply_count": 0,
  "images": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "image_url": "/static/media/uploads/image1.jpg"
    }
  ]
}
```

### Get Post

```
GET /api/posts/{post_id}
```

Retrieves a specific post by ID.

**Path Parameters:**
- `post_id`: Post ID (UUID)

**Curl Example:**
```bash
curl -X GET "http://localhost:8000/api/posts/123e4567-e89b-12d3-a456-426614174000"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Post found |
| 404 | Post not found |

**Example Response (200):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "This is a post content",
  "author_id": "123e4567-e89b-12d3-a456-426614174000",
  "author": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "username"
  },
  "created_at": "2023-01-02T15:30:00Z",
  "updated_at": "2023-01-02T15:30:00Z",
  "like_count": 5,
  "repost_count": 2,
  "reply_count": 3,
  "images": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "image_url": "/static/media/posts/image1.jpg"
    }
  ]
}
```

### Like Post

```
POST /api/posts/{post_id}/like
```

Likes a post.

**Authentication:** Bearer token required

**Path Parameters:**
- `post_id`: Post ID (UUID)

**Curl Example:**
```bash
curl -X POST "http://localhost:8000/api/posts/123e4567-e89b-12d3-a456-426614174000/like" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 201 | Post liked successfully |
| 401 | Unauthorized, token missing or invalid |
| 404 | Post not found |
| 409 | Post already liked by user |

**Example Response (201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "post_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2023-01-02T15:30:00Z"
}
```

### Repost

```
POST /api/posts/{post_id}/repost
```

Reposts a post.

**Authentication:** Bearer token required

**Path Parameters:**
- `post_id`: Post ID (UUID)

**Responses:**

| Status | Description |
|--------|-------------|
| 201 | Post reposted successfully |
| 401 | Unauthorized, token missing or invalid |
| 404 | Post not found |
| 409 | Post already reposted by user |

**Example Response (201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "post_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2023-01-02T15:30:00Z"
}
```

### Unlike Post

```
DELETE /api/posts/{post_id}/like
```

Unlikes a post.

**Authentication:** Bearer token required

**Path Parameters:**
- `post_id`: Post ID (UUID)

**Curl Example:**
```bash
curl -X DELETE "http://localhost:8000/api/posts/123e4567-e89b-12d3-a456-426614174000/like" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Post unliked successfully |
| 401 | Unauthorized, token missing or invalid |
| 404 | Post not found or post not liked by user |

**Example Response (200):**
```json
{
  "detail": "Post unliked successfully"
}
```

### Create Post With Images

```
POST /api/posts/with-images
```

Creates a new post with uploaded images.

**Authentication:** Bearer token required

**Request Body:**
- Form data with:
  - `content`: The text content of the post (string, max 4000 characters)
  - `files`: One or more image files to attach to the post

**Curl Example:**
```bash
curl -X POST "http://localhost:8000/api/posts/with-images" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "content=This is my new post with an image!" \
  -F "files=@/path/to/local/image.jpg"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 201 | Post created successfully with images |
| 401 | Unauthorized, token missing or invalid |
| 400 | Invalid request body or files |
| 413 | Files too large |

**Example Response (201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "This is my new post with images!",
  "author_id": "123e4567-e89b-12d3-a456-426614174000",
  "author": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "username"
  },
  "created_at": "2023-01-02T15:30:00Z",
  "updated_at": "2023-01-02T15:30:00Z",
  "like_count": 0,
  "repost_count": 0,
  "reply_count": 0,
  "images": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "image_url": "/static/media/uploads/image1.jpg"
    }
  ]
}
```

### Create Post Reply

```
POST /api/posts/reply
```

Creates a reply to an existing post.

**Authentication:** Bearer token required

**Request Body:**
```json
{
  "content": "This is my reply to your post!",
  "reply_to_post_id": "123e4567-e89b-12d3-a456-426614174000",
  "image_urls": []
}
```

**Curl Example:**
```bash
curl -X POST "http://localhost:8000/api/posts/reply" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is my reply to your post!",
    "reply_to_post_id": "123e4567-e89b-12d3-a456-426614174000",
    "image_urls": []
  }'
```

**Responses:**

| Status | Description |
|--------|-------------|
| 201 | Reply created successfully |
| 401 | Unauthorized, token missing or invalid |
| 400 | Invalid request body |
| 404 | Post to reply to not found |

**Example Response (201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174001",
  "content": "This is my reply to your post!",
  "author_id": "123e4567-e89b-12d3-a456-426614174002",
  "author": {
    "id": "123e4567-e89b-12d3-a456-426614174002",
    "username": "replier"
  },
  "created_at": "2023-01-02T16:30:00Z",
  "updated_at": "2023-01-02T16:30:00Z",
  "like_count": 0,
  "repost_count": 0,
  "reply_count": 0,
  "reply_to_post_id": "123e4567-e89b-12d3-a456-426614174000",
  "reply_to_post": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "content": "Original post content",
    "author": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "originalauthor"
    },
    "created_at": "2023-01-02T15:30:00Z"
  },
  "images": []
}
```

### Get Post Replies

```
GET /api/posts/{post_id}/replies
```

Retrieves a list of replies to a specific post.

**Path Parameters:**
- `post_id`: Post ID (UUID)

**Query Parameters:**
- `skip`: Number of replies to skip (default: 0)
- `limit`: Items per page (default: 20)

**Curl Example:**
```bash
curl -X GET "http://localhost:8000/api/posts/123e4567-e89b-12d3-a456-426614174000/replies?skip=0&limit=10"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Post replies retrieved successfully |
| 404 | Post not found |

**Example Response (200):**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174001",
    "content": "This is a reply to the post",
    "author_id": "123e4567-e89b-12d3-a456-426614174002",
    "author": {
      "id": "123e4567-e89b-12d3-a456-426614174002",
      "username": "replier"
    },
    "created_at": "2023-01-02T16:30:00Z",
    "updated_at": "2023-01-02T16:30:00Z",
    "like_count": 1,
    "repost_count": 0,
    "reply_count": 0,
    "reply_to_post_id": "123e4567-e89b-12d3-a456-426614174000",
    "images": []
  },
  // More replies...
]
```

### Get Posts by User

```
GET /api/posts/user/{user_id}
```

Retrieves posts created by a specific user.

**Path Parameters:**
- `user_id`: User ID (UUID)

**Query Parameters:**
- `skip`: Number of posts to skip (default: 0)
- `limit`: Items per page (default: 20)

**Curl Example:**
```bash
curl -X GET "http://localhost:8000/api/posts/user/123e4567-e89b-12d3-a456-426614174000?skip=0&limit=10"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Posts retrieved successfully |
| 404 | User not found |

## Media

### Upload Media

```
POST /api/media/upload
```

Uploads a media file.

**Authentication:** Bearer token required

**Request Body:**
- Form data with file field "file"

**Responses:**

| Status | Description |
|--------|-------------|
| 201 | File uploaded successfully |
| 401 | Unauthorized, token missing or invalid |
| 400 | Invalid file or file type not supported |
| 413 | File too large |

**Example Response (201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "image1.jpg",
  "file_url": "/static/media/uploads/image1.jpg"
}
```

## Followers

### Follow User

```
POST /api/follow
```

Follow a user by providing their user ID.

**Authentication:** Bearer token required

**Request Body:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Curl Example:**
```bash
curl -X POST "http://localhost:8000/api/follow" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

**Responses:**

| Status | Description |
|--------|-------------|
| 201 | Successfully followed user |
| 400 | Bad request (e.g., trying to follow yourself) |
| 401 | Unauthorized, token missing or invalid |
| 404 | User not found |
| 409 | Already following this user |

**Example Response (201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "follower_id": "123e4567-e89b-12d3-a456-426614174000",
  "following_id": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2023-01-02T15:30:00Z"
}
```

### Unfollow User

```
DELETE /api/follow/{user_id}
```

Unfollow a user by their user ID.

**Authentication:** Bearer token required

**Path Parameters:**
- `user_id`: User ID to unfollow (UUID)

**Curl Example:**
```bash
curl -X DELETE "http://localhost:8000/api/follow/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 204 | Successfully unfollowed user |
| 401 | Unauthorized, token missing or invalid |
| 404 | User not found or not following this user |

### Get User Followers

```
GET /api/users/{user_id}/followers
```

Get a list of users who follow the specified user.

**Path Parameters:**
- `user_id`: User ID (UUID)

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10, max: 100)

**Curl Example:**
```bash
curl -X GET "http://localhost:8000/api/users/123e4567-e89b-12d3-a456-426614174000/followers?page=1&limit=10"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | List of followers retrieved successfully |
| 404 | User not found |

**Example Response (200):**
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "username": "johndoe",
      "display_name": "John Doe",
      "avatar_url": "/static/media/avatars/user1.jpg",
      "created_at": "2023-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

### Get Users Followed by User

```
GET /api/users/{user_id}/following
```

Get a list of users followed by the specified user.

**Path Parameters:**
- `user_id`: User ID (UUID)

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10, max: 100)

**Curl Example:**
```bash
curl -X GET "http://localhost:8000/api/users/123e4567-e89b-12d3-a456-426614174000/following?page=1&limit=10"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | List of followed users retrieved successfully |
| 404 | User not found |

**Example Response (200):**
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174002",
      "username": "janedoe",
      "display_name": "Jane Doe",
      "avatar_url": "/static/media/avatars/user2.jpg",
      "created_at": "2023-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

### Check Following Status

```
GET /api/users/{user_id}/is-following/{target_id}
```

Check if a user is following another user.

**Path Parameters:**
- `user_id`: User ID to check (UUID)
- `target_id`: Target user ID (UUID)

**Curl Example:**
```bash
curl -X GET "http://localhost:8000/api/users/123e4567-e89b-12d3-a456-426614174000/is-following/123e4567-e89b-12d3-a456-426614174001"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Following status retrieved successfully |
| 404 | User not found |

**Example Response (200):**
```json
{
  "is_following": true
}
```

## Admin

### List Users

```
GET /api/admin/users
```

Lists all users (admin only).

**Authentication:** Bearer token required (admin)

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)

**Curl Example:**
```bash
curl -X GET "http://localhost:8000/api/admin/users?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN"
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Users retrieved successfully |
| 401 | Unauthorized, token missing or invalid |
| 403 | Forbidden, user is not an admin |

**Example Response (200):**
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "username": "username",
      "is_admin": false,
      "is_active": true,
      "created_at": "2023-01-01T12:00:00Z"
    },
    // More users...
  ],
  "total": 100,
  "page": 1,
  "limit": 10,
  "pages": 10
}
```

### Moderate Content

```
POST /api/admin/moderate
```

Takes moderation action on content or users.

**Authentication:** Bearer token required (admin)

**Request Body:**
```json
{
  "action_type": "DELETE_POST",
  "target_post_id": "123e4567-e89b-12d3-a456-426614174000",
  "reason": "Violation of community guidelines"
}
```

**Curl Example:**
```bash
curl -X POST "http://localhost:8000/api/admin/moderate" \
  -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "DELETE_POST",
    "target_post_id": "123e4567-e89b-12d3-a456-426614174000",
    "reason": "Violation of community guidelines"
  }'
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Moderation action performed successfully |
| 401 | Unauthorized, token missing or invalid |
| 403 | Forbidden, user is not an admin |
| 404 | Target post or user not found |

**Example Response (200):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "admin_id": "123e4567-e89b-12d3-a456-426614174000",
  "action_type": "DELETE_POST",
  "target_post_id": "123e4567-e89b-12d3-a456-426614174000",
  "target_user_id": null,
  "reason": "Violation of community guidelines",
  "created_at": "2023-01-03T10:15:00Z"
}
```

## WebSockets

### Real-time Updates

```
WebSocket /api/ws
```

WebSocket connection for real-time updates.

**Query Parameters:**
- `token`: Optional authentication token

**Events Sent to Client:**
- `new_post`: When a new post is created
- `new_like`: When a post is liked
- `new_repost`: When a post is reposted
- `heartbeat`: Periodic heartbeat to keep connection alive

**Example Event:**
```json
{
  "type": "new_post",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "content": "This is a new post",
    "author_id": "123e4567-e89b-12d3-a456-426614174000",
    "author": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "username"
    },
    "created_at": "2023-01-02T15:30:00Z"
  }
}
```

### User Notifications

```
WebSocket /api/ws/notifications
```

WebSocket connection for user-specific notifications.

**Query Parameters:**
- `token`: Authentication token (required)

**Events Sent to Client:**
- `connected`: When connection is established
- `notification`: For user-specific notifications like mentions, replies, etc.

**Example Event:**
```json
{
  "type": "notification",
  "data": {
    "type": "mention",
    "post_id": "123e4567-e89b-12d3-a456-426614174000",
    "from_user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "username"
    },
    "created_at": "2023-01-02T15:30:00Z"
  }
}
```

## Core

### Root Endpoint

```
GET /
```

Returns basic information about the API.

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | API information retrieved successfully |
| 500 | Internal server error |

**Example Response (200):**
```json
{
  "title": "Simple Social Board API Backend",
  "description": "A social media platform built with FastAPI",
  "version": "1.0.0"
}
```

### Health Check

```
GET /health
```

Returns the health status of the application.

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Health status retrieved successfully |
| 500 | Internal server error |

**Example Response (200):**
```json
{
  "status": "healthy",
  "cpu_usage": "23.5%",
  "memory_usage": "43.2%",
  "disk_usage": "67.8%",
  "total_memory": "16.00 GB",
  "available_memory": "9.12 GB"
}
```

### Static Files

```
GET /static/{file_path}
```

Serves static files.

**Path Parameters:**
- `file_path`: Path to the file

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | File retrieved successfully |
| 404 | File not found |
| 500 | Internal server error |
