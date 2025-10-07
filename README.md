# Ticket Booking System API

A Django REST Framework (DRF) based ticket booking system with JWT authentication.  
Includes user registration, movie and show management, seat booking/cancellation, and Swagger documentation.

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/tabsheermk/ticket-booking-system.git
cd ticket-booking-system
```

2. **Create a virtual environment**

```bash
python3 -m venv env
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Apply migrations**

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

5. **Run the development server**

```bash
python3 manage.py runserver
```

The server should now be running at:

```
http://127.0.0.1:8000/
```

---

## Generate JWT Tokens

You can obtain JWT tokens using the provided login endpoint.

### 1. Register a new user

**Endpoint:** `POST /api/user/signup/`

**Request Body:**

```json
{
  "username": "tabsheer",
  "password": "your_password"
}
```

**Response:**

```json
{
  "id": 1,
  "username": "tabsheer",
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

### 2. Login (get JWT token)

**Endpoint:** `POST /api/user/login/`

**Request Body:**

```json
{
  "username": "tabsheer",
  "password": "your_password"
}
```

**Response:**

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

### 3. Refresh JWT token

**Endpoint:** `POST /api/token/refresh/`

**Request Body:**

```json
{
  "refresh": "<refresh_token>"
}
```

**Response:**

```json
{
  "access": "<new_access_token>"
}
```

> **Note:** Use the **access token** in the `Authorization` header for all protected endpoints:

```
Authorization: Bearer <access_token>
```

---

## Calling APIs

All endpoints, except signup, login, and refresh are JWT-protected. Examples:

### Movies

- **GET /api/movies/** – List all movies
- **POST /api/movies/** – Create a new movie

### Shows

- **GET /api/movies/{movie_id}/shows/** – List all shows for a movie
- **POST /api/movies/{movie_id}/shows/** – Create a new show

### Booking

- **POST /api/shows/{show_id}/book/** – Book a seat (body: `seat_number`)
- **POST /api/bookings/{booking_id}/cancel/** – Cancel a booking
- **GET /api/my-bookings/** – List all bookings for the logged-in user

---

## Swagger Documentation

Interactive API documentation is available at:

```
http://127.0.0.1:8000/api/swagger/
```

Swagger UI provides request examples, response examples, and authentication support.

---

## Notes

- Database: SQLite (`db.sqlite3`) – included in `.gitignore`
- Migrations are also ignored in `.gitignore` to avoid conflicts
- Authentication is via JWT (`rest_framework_simplejwt`)
