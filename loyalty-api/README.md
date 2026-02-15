# Loyalty API - Backend

Python FastAPI backend for the Fidelity Points Loyalty System.

## Features

✅ **REST API Framework** - FastAPI with automatic OpenAPI documentation  
✅ **Authentication** - API key-based authentication for terminals  
✅ **Authorization** - Role-based access control  
✅ **Idempotency** - Duplicate transaction prevention with idempotency keys  
✅ **Rate Limiting** - Per-terminal request rate limiting  
✅ **Request Logging** - Structured JSON logging with correlation IDs  
✅ **Error Handling** - Standardized error responses  
✅ **Security Headers** - CORS, CSP, HSTS, and other security headers  
✅ **Health Check** - Database connectivity and service health monitoring  
✅ **Database Migrations** - Alembic for schema versioning  
✅ **Integration Tests** - Comprehensive test suite

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Python**: 3.11+
- **Database**: PostgreSQL 14+ (async with asyncpg)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Testing**: Pytest with async support
- **Server**: Uvicorn with auto-reload

## Quick Start

### 1. Prerequisites

- Python 3.11 or higher
- PostgreSQL 14 or higher
- pip and virtualenv

### 2. Installation

```bash
# Clone the repository (if not already done)
cd loyalty-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# At minimum, set DATABASE_URL
nano .env
```

### 4. Database Setup

```bash
# Start PostgreSQL (using docker-compose from parent directory)
cd ..
docker-compose -f docker-compose.loyalty.yml up -d loyalty-postgres
cd loyalty-api

# Run migrations
alembic upgrade head
```

### 5. Run Development Server

```bash
# Start the API server
python -m app.server

# Or use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

The API will be available at:
- API: http://localhost:3000
- Documentation: http://localhost:3000/api-docs
- Health Check: http://localhost:3000/health

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run only integration tests
pytest tests/integration/

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/integration/test_auth.py
```

### Code Quality

```bash
# Format code with Black
black app/ tests/

# Sort imports
isort app/ tests/

# Run linter
flake8 app/ tests/

# Type checking
mypy app/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

## Project Structure

```
loyalty-api/
├── app/
│   ├── api/              # API route handlers
│   │   └── health.py     # Health check endpoint
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings and configuration
│   │   ├── database.py   # Database connection
│   │   ├── logging.py    # Logging setup
│   │   └── security.py   # Security utilities
│   ├── middleware/       # Custom middleware
│   │   ├── auth.py       # Authentication middleware
│   │   ├── idempotency.py # Idempotency middleware
│   │   ├── logging.py    # Request logging
│   │   └── rate_limit.py # Rate limiting
│   ├── models/           # Database models
│   │   └── auth.py       # Auth-related models
│   ├── main.py           # FastAPI application
│   └── server.py         # Server entry point
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py            # Alembic environment
├── tests/                # Test suite
│   ├── integration/      # Integration tests
│   └── conftest.py       # Test configuration
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── pyproject.toml        # Python project config
├── alembic.ini           # Alembic configuration
└── README.md             # This file
```

## API Documentation

### Authentication

All API endpoints (except /health and /) require authentication:

```http
Authorization: Bearer loyalty_<env>_<terminal_id>_<random>
X-Terminal-ID: <terminal_id>
```

### Idempotency

State-changing endpoints require an idempotency key:

```http
X-Idempotency-Key: <operation>_<entity>_<timestamp>_<terminal_id>
```

### Rate Limiting

- 100 requests per minute per terminal (default)
- Rate limit headers included in responses
- 429 status code when limit exceeded

### Error Responses

All errors follow this format:

```json
{
  "error_code": "ERROR_CODE",
  "error_message": "Human-readable message",
  "details": {}
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `PORT` | API server port | 3000 |
| `ENVIRONMENT` | Environment (development/production) | development |
| `DEBUG` | Enable debug mode | false |
| `LOG_LEVEL` | Logging level | INFO |
| `LOG_FORMAT` | Log format (json/text) | json |
| `API_KEY_SALT` | Salt for API key hashing | Required |
| `JWT_SECRET` | JWT token secret | Required |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | true |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | Rate limit | 100 |
| `CORS_ORIGINS` | Allowed CORS origins | localhost |

## Deployment

### Using Docker

```bash
# Build image
docker build -t loyalty-api:latest .

# Run container
docker run -d \
  --name loyalty-api \
  -p 3000:3000 \
  --env-file .env \
  loyalty-api:latest
```

### Manual Deployment

```bash
# Install production dependencies only
pip install -r requirements.txt

# Run with gunicorn (production server)
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:3000
```

## Security

- **API Key Authentication**: SHA-256 hashed API keys
- **Rate Limiting**: Per-terminal rate limits
- **Security Headers**: HSTS, CSP, X-Frame-Options, etc.
- **CORS**: Configured with whitelist
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection**: Protected by SQLAlchemy ORM
- **Sensitive Data**: No API keys or secrets in logs

## Monitoring

- **Health Check**: `/health` endpoint for monitoring
- **Structured Logging**: JSON logs for easy parsing
- **Correlation IDs**: Track requests across services
- **Database Health**: Automatic connectivity checks

## Troubleshooting

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
psql -h localhost -p 5433 -U loyalty_user -d loyalty_system
```

### Migration Errors

```bash
# Reset database (WARNING: destroys data)
alembic downgrade base
alembic upgrade head
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements-dev.txt
```

## Documentation

For complete documentation, see:
- [Points System/02_architecture/CLOUD_BACKEND.md](../Points%20System/02_architecture/CLOUD_BACKEND.md) - Architecture
- [Points System/06_security/AUTHENTICATION.md](../Points%20System/06_security/AUTHENTICATION.md) - Authentication
- [Points System/06_security/IDEMPOTENCY.md](../Points%20System/06_security/IDEMPOTENCY.md) - Idempotency

## License

Proprietary - PrestaShop Entre

## Support

For issues or questions, contact the development team.

## Customer and Card Management API

### Customer Endpoints

#### Create Customer
- **POST** `/api/v1/customers`
- Creates a new customer with optional card assignment
- Requires `X-Idempotency-Key` header
- Records GDPR consent
- Request body:
```json
{
  "name": "string",
  "email": "string (required, validated)",
  "phone": "string (optional, E.164 format)",
  "prestashop_customer_id": "integer (optional)",
  "consent_loyalty": "boolean (required, must be true)",
  "consent_marketing": "boolean (optional)",
  "language": "string (es|ca|en, default: es)",
  "card_uid": "string (optional, 14 hex chars)"
}
```

#### Get Customer
- **GET** `/api/v1/customers/{customer_id}`
- Retrieves customer details including cards and balance
- No authentication required (API key in headers)

#### Update Customer
- **PATCH** `/api/v1/customers/{customer_id}`
- Updates customer contact information
- Requires `X-Idempotency-Key` header
- Tracks consent changes
- Request body (all fields optional):
```json
{
  "name": "string",
  "email": "string (validated)",
  "phone": "string (E.164 format)",
  "consent_marketing": "boolean",
  "language": "string (es|ca|en)"
}
```

### Card Endpoints

#### Register Card
- **POST** `/api/v1/cards`
- Registers a new NFC card (inactive status)
- Requires `X-Idempotency-Key` header
- Request body:
```json
{
  "card_uid": "string (required, 14 hex chars)",
  "card_number": "string (required, e.g. LC-00000001)"
}
```

#### Assign Card
- **POST** `/api/v1/cards/{card_uid}/assign`
- Assigns an inactive card to a customer
- Requires `X-Idempotency-Key` header
- Prevents reassignment to different customer
- Request body:
```json
{
  "customer_id": "uuid"
}
```

#### Lookup Customer by Card
- **GET** `/api/v1/cards/{card_uid}/customer`
- Retrieves customer information for a card
- Used by POS terminals for card tap identification
- Returns 404 if card not assigned or inactive

### Validation Rules

- **Email**: Must match standard email format (regex validated)
- **Phone**: Must be E.164 format (e.g., +34612345678)
- **Card UID**: Must be 14 hexadecimal characters (case-insensitive)
- **Card Numbers**: Must be unique across all cards
- **Customer Email**: Must be unique across all customers

### Consent Tracking

All customer creation and consent changes are logged in `consent_records` table with:
- Consent type (loyalty_program, marketing_email, etc.)
- Timestamp
- Method (pos_enrollment, account_settings, etc.)
- IP address (when available)
- Consent text version

