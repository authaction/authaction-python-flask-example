# authaction-python-flask-example

A Python Flask application demonstrating API authorization using [AuthAction](https://app.authaction.com/) with the `authaction-python-sdk`.

## Overview

This application shows how to configure and handle authorization using AuthAction's access tokens in a Flask API. It validates JSON Web Tokens (JWT) by using the `authaction` SDK, which handles JWKS fetching and RS256 validation automatically.

## Prerequisites

- **Python 3.11+**
- **AuthAction credentials**: `tenantDomain` and `apiIdentifier` from your AuthAction account.

## Installation

1. **Clone the repository**:

   ```bash
   git clone git@github.com:authaction/authaction-python-flask-example.git
   cd authaction-python-flask-example
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your AuthAction credentials**:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and replace the placeholders:

   ```env
   AUTHACTION_DOMAIN=your-authaction-tenant-domain
   AUTHACTION_AUDIENCE=your-authaction-api-identifier
   ```

## Usage

1. **Start the development server**:

   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:5000`.

2. **Obtain an access token** via client credentials:

   ```bash
   curl --request POST \
     --url https://your-authaction-tenant-domain/oauth2/m2m/token \
     --header 'content-type: application/json' \
     --data '{
       "client_id": "your-authaction-app-clientid",
       "client_secret": "your-authaction-app-client-secret",
       "audience": "your-authaction-api-identifier",
       "grant_type": "client_credentials"
     }'
   ```

3. **Call the public endpoint** (no token required):

   ```bash
   curl http://localhost:5000/public
   ```

   ```json
   { "message": "This is a public message!" }
   ```

4. **Call the protected endpoint** with the access token:

   ```bash
   curl --request GET \
     --url http://localhost:5000/protected \
     --header 'Authorization: Bearer YOUR_ACCESS_TOKEN'
   ```

   ```json
   { "message": "This is a protected message!", "sub": "client-id@clients" }
   ```

## Project Structure

```
authaction-python-flask-example/
├── auth/
│   ├── __init__.py
│   └── jwt_validator.py    # AuthAction SDK setup and require_auth decorator
├── app.py                  # Flask app and route definitions
├── .env.example
├── requirements.txt
└── README.md
```

## Code Explanation

### `auth/jwt_validator.py` — Auth Decorator Setup

Creates an `AuthAction` client from `authaction` with `AUTHACTION_DOMAIN` and `AUTHACTION_AUDIENCE`, then calls `make_require_auth(aa)` from `authaction.flask` to produce a `require_auth` route decorator. The SDK handles JWKS fetching, caching, and RS256 JWT validation internally.

### `app.py` — Routes

- **`GET /public`** — No decorator, accessible without authentication.
- **`GET /protected`** — `@require_auth` guards the route. The verified payload
  is available via `g.current_user`.

## Common Issues

**Invalid token errors** — Verify that `AUTHACTION_DOMAIN` and
`AUTHACTION_AUDIENCE` match the values in your AuthAction dashboard exactly.

**Public key fetching errors** — Check that your application can reach
`https://{AUTHACTION_DOMAIN}/.well-known/jwks.json`.

**Unauthorized access** — Ensure the `Authorization: Bearer <token>` header is
present and the token was issued for the correct audience.

## Contributing

Feel free to submit issues or pull requests if you encounter bugs or have suggestions for improvement!
