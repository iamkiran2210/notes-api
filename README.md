# Notes API

A lightweight REST API for managing personal notes, built with **FastAPI, SQLite, SQLAlchemy, and Pydantic**.

The API provides user authentication, note management, tagging, search, filtering, and pagination. Each user can securely manage their notes through JWT-protected endpoints.

## Features

- **User Authentication:** Register and log in using username, email, and password.
- **JWT Authentication:** Secure protected endpoints using access and refresh tokens.
- **Notes CRUD:** Create, retrieve, update, and delete notes.
- **Search Notes:** Search notes using a search query.
- **Tag Filtering:** Organize and retrieve notes based on tags.
- **Pagination:** Retrieve notes efficiently with configurable page sizes.
- **Archive Notes:** Mark notes as archived or active.
- **Health Checks:** Monitor application and database availability.
- **Data Validation:** Validate incoming requests using Pydantic.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | REST API framework |
| SQLite | Relational database |
| SQLAlchemy | ORM and database operations |
| Pydantic | Data validation and serialization |
| JWT | Authentication and authorization |

## Getting Started

### Prerequisites

- Python 3.10+
- pip
- Git

### Installation

**1. Clone the repository**

```bash
git clone <your-repository-url>
cd <repository-name>
```

**2. Create a virtual environment**

```bash
python -m venv .venv
```

Activate it:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root and configure the environment variables required by your application.

```env
# Example configuration
SECRET_KEY=your-secret-key
ALGORITHM=HS256
```

Configure additional settings according to your application implementation.

**5. Run the application**

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

*Adjust the Uvicorn import path to match your project structure.*

---

## API Documentation

### Authentication

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | Not required |
| POST | `/auth/login` | Authenticate a user | Not required |
| GET | `/auth/me` | Get current user details | Required |

### Notes Management

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/notes/` | Create a note | Required |
| GET | `/notes/` | Retrieve notes with filtering and pagination | Required |
| GET | `/notes/{id}` | Retrieve a specific note | Required |
| PATCH | `/notes/{id}` | Partially update a note | Required |
| DELETE | `/notes/{id}` | Delete a note | Required |

### Health Checks

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health/` | Application health check |
| GET | `/health/db` | Database readiness check |

---

## Authentication

The API uses OAuth2 Password Bearer authentication with JWT tokens.

### 1. Register

Create a new account.

**Request**

```http
POST /auth/register
Content-Type: application/json
```

```json
{
  "username": "kiran",
  "email": "kiran@example.com",
  "password": "your_password"
}
```

**Response — 200 OK**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "kiran"
}
```

### 2. Login

Authenticate using OAuth2 form data.

**Request**

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

```text
username=kiran
password=your_password
```

**Response — 200 OK**

```json
{
  "access_token": "<access_token>",
  "refresh_token": "<refresh_token>",
  "token_type": "bearer"
}
```

### 3. Get Current User

Retrieve the authenticated user's details.

**Request**

```http
GET /auth/me
Authorization: Bearer <access_token>
```

---

## Notes API

### 1. Create a Note

Create a new note for the authenticated user.

**Request**

```http
POST /notes/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "title": "Learning FastAPI",
  "content": "Understanding dependency injection and SQLAlchemy.",
  "is_archived": false,
  "tags": [
    "python",
    "backend",
    "learning"
  ]
}
```

**Response — 201 Created**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Learning FastAPI",
  "content": "Understanding dependency injection and SQLAlchemy.",
  "is_archived": false,
  "tags": [
    "python",
    "backend",
    "learning"
  ]
}
```

### 2. Get Notes

Retrieve notes with optional filtering, searching, and pagination.

**Request**

```http
GET /notes/?page=1&size=10
Authorization: Bearer <access_token>
```

**Available Query Parameters**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| id | UUID | No | None | Retrieve a note by ID |
| search | string | No | None | Search notes (2–30 characters) |
| tag | string | No | None | Filter by tag (2–50 characters) |
| page | integer | No | 1 | Page number |
| size | integer | No | 50 | Number of records per page (maximum 100) |

**Example: Search notes**

```http
GET /notes/?search=FastAPI
```

**Example: Filter by tag**

```http
GET /notes/?tag=python
```

**Example: Pagination**

```http
GET /notes/?page=2&size=10
```

**Response — 200 OK**

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Learning FastAPI",
      "content": "Understanding dependency injection.",
      "is_archived": false,
      "tags": [
        "python",
        "backend"
      ]
    }
  ],
  "total": 25,
  "page": 1,
  "size": 10,
  "pages": 3
}
```

### 3. Get Note by ID

Retrieve an individual note using its UUID.

**Request**

```http
GET /notes/{id}
Authorization: Bearer <access_token>
```

### 4. Update a Note

Update one or more fields of an existing note.

**Request**

```http
PATCH /notes/{id}
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "title": "Advanced FastAPI",
  "is_archived": true
}
```

The update schema supports:

- `title`
- `content`
- `is_archived`
- `tags`

All update fields are optional.

### 5. Delete a Note

Permanently delete a note using its UUID.

**Request**

```http
DELETE /notes/{id}
Authorization: Bearer <access_token>
```

**Response — 204 No Content**

The note is deleted successfully. No response body is returned.

---

## Pagination

The notes endpoint supports pagination to avoid returning the entire dataset in a single request.

The paginated response contains:

| Field | Description |
|---|---|
| items | Notes returned for the current page |
| total | Total number of matching notes |
| page | Current page number |
| size | Number of records per page |
| pages | Total number of pages |

Example:

```text
GET /notes/?page=2&size=10
```

If there are 25 matching notes, the API returns:

```text
Total records: 25
Page size:     10
Total pages:   3
Current page:  2
```

## Health Checks

Monitor application availability and database readiness.

**Application health**

```http
GET /health/
```

**Database readiness**

```http
GET /health/db
```

These endpoints can be used by monitoring systems and deployment health checks.

## Error Handling

The API uses standard HTTP status codes.

| Status Code | Meaning |
|---|---|
| 200 | Request successful |
| 201 | Resource created |
| 204 | Resource deleted successfully |
| 401 | Authentication required or invalid token |
| 403 | Access forbidden |
| 404 | Resource not found |
| 422 | Request validation error |
| 500 | Internal server error |

Validation errors follow FastAPI's standard validation response format.

## Interactive API Documentation

FastAPI automatically generates interactive API documentation.

After starting the application, visit:

| Documentation | URL |
|---|---|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI JSON | http://localhost:8000/openapi.json |

## Project Structure

```text
project/
│
├── app/
│   ├── main.py
│   ├── ...
│
├── .env
├── requirements.txt
└── README.md
```

---

**Built with FastAPI, SQLAlchemy, SQLite, and Pydantic.**
