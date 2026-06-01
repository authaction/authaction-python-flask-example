# authaction-python-flask-example

A Python Flask application demonstrating API authorization using [AuthAction](https://app.authaction.com/) with JWKS-based JWT validation.

## Overview

This application shows how to configure and handle authorization using AuthAction's access tokens in a Flask API. It validates JSON Web Tokens (JWT) signed with RS256 by fetching public keys dynamically from AuthAction's JWKS endpoint.

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
│   └── jwt_validator.py    # JWKS fetching, caching, JWT validation, require_auth decorator
├── app.py                  # Flask app and route definitions
├── .env.example
├── requirements.txt
└── README.md
```

## Code Explanation

### `auth/jwt_validator.py` — JWT Validation

- **`_get_jwks()`** — Fetches and in-memory caches the public keys from
  `https://{AUTHACTION_DOMAIN}/.well-known/jwks.json`. On a cache miss caused
  by key rotation, it busts the cache and retries once.

- **`_find_rsa_key(token)`** — Extracts the `kid` from the unverified token
  header and finds the matching RSA key in the JWKS response.

- **`verify_token(token)`** — Decodes and validates the JWT using:
  - Algorithm: `RS256`
  - Issuer: `https://{AUTHACTION_DOMAIN}`
  - Audience: `{AUTHACTION_AUDIENCE}`

- **`require_auth`** — A route decorator that extracts the `Bearer` token from
  the `Authorization` header, calls `verify_token`, and stores the decoded
  payload on `request.current_payload`. Returns 401 on any validation failure.

### `app.py` — Routes

- **`GET /public`** — No decorator, accessible without authentication.
- **`GET /protected`** — `@require_auth` guards the route. The verified payload
  is available via `request.current_payload`.

## Common Issues

**Invalid token errors** — Verify that `AUTHACTION_DOMAIN` and
`AUTHACTION_AUDIENCE` match the values in your AuthAction dashboard exactly.

**Public key fetching errors** — Check that your application can reach
`https://{AUTHACTION_DOMAIN}/.well-known/jwks.json`.

**Unauthorized access** — Ensure the `Authorization: Bearer <token>` header is
present and the token was issued for the correct audience.

## Contributing

Feel free to submit issues or pull requests if you encounter bugs or have suggestions for improvement!
