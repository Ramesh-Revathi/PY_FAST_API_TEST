# PY_FAST_API_TEST

Clean FastAPI sample using a modular monolith structure.

## Features

- User registration
- OTP generation for login
- OTP based login with JWT token
- Protected `me` endpoint
- Admin UI for SQLite database browsing
- SQLite for local development

## Project structure

```text
app/
	core/
		config.py
		database.py
		security.py
	modules/
		auth/
			application/
				services.py
			domain/
				schemas.py
			infrastructure/
				models.py
				repositories.py
			presentation/
				routes.py
	main.py
requirements.txt
```

## Admin access for app.db

Open the admin panel at:

`/admin`

Default credentials:

- Username: `admin`
- Password: `admin123`

Change them with environment variables:

- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_SECRET_KEY`

## Run locally

1. Create a virtual environment
2. Install dependencies
3. Start the API server

Example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API flow

### 1. Register

`POST /api/v1/auth/register`

```json
{
	"full_name": "Ramesh",
	"email": "ramesh@example.com",
	"phone": "+919999999999",
	"password": "StrongPass@123"
}
```

### 2. Request OTP

`POST /api/v1/auth/request-otp`

```json
{
	"identifier": "ramesh@example.com"
}
```

For this sample project, the OTP is returned in the response as `demo_otp`.

### 3. Login with OTP

`POST /api/v1/auth/login`

```json
{
	"identifier": "ramesh@example.com",
	"otp": "123456"
}
```

### 4. Access protected endpoint

`GET /api/v1/auth/me`

Use the bearer token returned by the login endpoint.

## Notes

- Default database: SQLite (`app.db`)
- OTP is exposed only for sample/demo usage
- Replace the OTP delivery logic with SMS or email provider for production

