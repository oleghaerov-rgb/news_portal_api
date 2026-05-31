# News Portal API

Base URL for local development:

```text
http://127.0.0.1:8000
```

## Authentication

The API supports token authentication and Django session authentication.

Get a token:

```http
POST /api/token/
Content-Type: application/json

{
  "username": "api_user",
  "password": "StrongPass123!"
}
```

Use the token:

```http
Authorization: Token <token>
```

## Users

`GET /api/users/`

Returns a paginated list of users.

`POST /api/users/`

Creates a user.

```json
{
  "username": "api_user",
  "first_name": "API",
  "last_name": "User",
  "email": "api_user@example.com",
  "password": "StrongPass123!"
}
```

`GET /api/users/<id>/`

Returns one user.

`PUT/PATCH /api/users/<id>/`

Updates a user. Only the same user or an administrator can update the profile.

`DELETE /api/users/<id>/`

Deletes a user. Only the same user or an administrator can delete the account.

## News

`GET /api/news/`

Returns a paginated list of news. Default page size is 10.

Filtering:

```text
GET /api/news/?author=5
```

Search:

```text
GET /api/news/?search=django
```

Ordering:

```text
GET /api/news/?ordering=-date_created
```

`POST /api/news/`

Creates a news item. Authentication is required. The author is set from the current user.

```json
{
  "title": "API news example",
  "summary": "Short summary for API news",
  "content": "This is a long enough text for the API news example. It has more than fifty symbols."
}
```

`GET /api/news/<id>/`

Returns one news item.

`PUT/PATCH /api/news/<id>/`

Updates a news item. Only the author can update it.

`DELETE /api/news/<id>/`

Deletes a news item. Only the author can delete it.

## Validation Errors

Errors are returned as JSON:

```json
{
  "title": ["Минимум 5 символов."],
  "content": ["Минимум 50 символов."]
}
```

## Environment Variables

For production:

```text
SECRET_KEY=<secure secret key>
DEBUG=False
ALLOWED_HOSTS=news-portal-api-y7hi.onrender.com
DATABASE_URL=<optional PostgreSQL URL>
```

On Render, the application also reads `RENDER_EXTERNAL_HOSTNAME`, which Render sets automatically for web services. If `DisallowedHost` still appears, set `ALLOWED_HOSTS` manually to your service host without `https://`.

## Render Deployment

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn news_portal.wsgi:application --log-file -
```

Alternative start script:

```bash
bin/start.sh
```
