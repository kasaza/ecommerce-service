# E-Commerce API with Django and Auth0

[![Django](https://img.shields.io/badge/Django-3.2-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.12-blue.svg)](https://www.django-rest-framework.org/)
[![Auth0](https://img.shields.io/badge/Auth0-OIDC-orange.svg)](https://auth0.com/)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)](https://github.com/yourusername/ecommerce-api)

A complete e-commerce API with OpenID Connect authentication, hierarchical product categories, and order processing with SMS/email notifications.

---

## Features

- **Authentication & Authorization**
  - OpenID Connect via Auth0
  - Role-based access control
  - JWT token validation

- **Product Management**
  - Hierarchical categories (unlimited depth)
  - CSV bulk upload
  - Category statistics (average price, product count)

- **Order Processing**
  - Complete order lifecycle
  - SMS notifications (Africa's Talking)
  - Email alerts for admins

- **Infrastructure**
  - Docker-ready
  - Kubernetes deployment
  - CI/CD pipeline

---

## API Documentation

### Base URL: `http://localhost:8000/`

### Core Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `api/categories/` | GET | List all categories | Yes |
| `api/categories/` | POST | Create categories | Admin |
| `api/categories/stats/?category_id=<id>` | GET | Get category statistics | Admin |
| `api/products/` | GET | List all products | Yes |
| `api/products/` | POST | Create products | Admin |
| `api/products/upload/` | POST | Bulk upload (CSV) | Admin |
| `api/orders/` | POST | Create new order | Yes |

---

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- [Auth0](https://auth0.com/) account
- [Africa's Talking](https://africastalking.com/) account (for SMS)

### Installation
```bash
git clone https://github.com/kasaza/ecommerce-service.git
cd ecommerce-service
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python manage.py migrate
python manage.py createsuperuser
```

### Running Locally
```bash
python manage.py runserver
```

---

## Deployment

### Docker
```bash
docker-compose up --build
```

```bash
 docker-compose up
```

### Kubernetes
1. Build and push Docker image
2. Apply Kubernetes configurations in `k8s/` directory

```bash
kubectl apply -f k8s/
```

---

## Configuration

### Required Environment Variables (.env)
```ini
# Auth0
OIDC_CLIENT_ID=your_client_id
OIDC_CLIENT_SECRET=your_client_secret
OIDC_DOMAIN=your-domain.us.auth0.com

# Database
DATABASE_URL=postgres://user:password@localhost:5432/ecommerce

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=you@mail.com
EMAIL_HOST_PASSWORD=password
ADMIN_EMAIL=admin@gmail.com

# Notifications
AFRICASTALKING_API_KEY=your_api_key
EMAIL_HOST=smtp.example.com
```

---

## API Examples

## Categories Endpoints

### 1. List All Categories

**URL**: `api/categories/`
**Method**: `GET`
**Permissions**: Authenticated users
**Response**:

```json
[
    {
        "id": 1,
        "name": "Bakery",
        "description": "bakery products category main",
        "parent": null,
        "children": [
            {
                "id": 2,
                "name": "Bread",
                "description": "bakery products bread category main",
                "parent": 1,
                "children": []
            }
        ]
    }
]
```

### 2. Get Category Statistics

**URL**: `api/categories/stats/?category_id=<id>`
**Method**: `GET`
**Permissions**: Authenticated users
**Parameters**:

* `category_id` (required): ID of the category to analyze

**Success Response**:

```json
{
    "category": 1,
    "average_price": 32.50,
    "product_count": 3
}
```

**Error Responses**:

* `400 Bad Request`: Missing category\_id parameter

```json
{"error": "category_id parameter is required"}
```

* `404 Not Found`: Category not found

```json
{"error": "Category not found"}
```

---

## Products Endpoints

### 1. List All Products

**URL**: `/products/`
**Method**: `GET`
**Permissions**: Authenticated users
**Response**:

```json
[
    {
        "id": 1,
        "name": "Premium Headphones",
        "description": "Noise-cancelling wireless headphones",
        "price": 199.99,
        "categories": [1],
        "stock_quantity": 15
    }
]
```

### 2. Upload Products (CSV)

**URL**: `/products/upload/`
**Method**: `POST`
**Permissions**: Admin only
**Request Format**: `multipart/form-data`
**Parameters**:

* `file` (required): CSV file containing product data

**CSV Format**:

```csv
name,description,price,stock_quantity,categories
Product 1,Description 1,19.99,100,1
Product 2,Description 2,29.99,50,1;2
```

**Success Response**:

```json
{"status": "5 products created"}
```

---

## Orders Endpoints

### 1. Create Order

**URL**: `api/orders/`
**Method**: `POST`
**Permissions**: Authenticated users
**Request**:

```json
{
    "items": [
        {
            "product": 1,
            "quantity": 2
        }
    ]
}
```

**Success Response**:

```json
{
    "id": 1,
    "customer": 1,
    "status": "P",
    "items": [
        {
            "product": 1,
            "quantity": 2,
            "price": 199.99
        }
    ],
    "total_price": 399.98
}
```

---

## Authentication Endpoints

### 1. Login

**URL**: `/oidc/login/`
**Method**: `GET`
**Flow**: Redirects to Auth0 login page

### 2. Logout

**URL**: `/oidc/logout/`
**Method**: `GET`
**Effect**: Terminates both Django and Auth0 sessions

### 3. Callback

**URL**: `/oidc/callback/`
**Method**: `GET`
**Note**: Used internally by Auth0

---

## Error Responses

### Common Errors

| Code | Description                             |
| ---- | --------------------------------------- |
| 400  | Bad Request - Invalid input data        |
| 401  | Unauthorized - Missing or invalid token |
| 403  | Forbidden - Insufficient permissions    |
| 404  | Not Found - Resource doesn't exist      |
| 500  | Server Error - Internal server issue    |

---

## Sample Requests

### Get Category Stats

```bash
curl "http://localhost:8000/api/categories/stats/?category_id=1" \
  -H "Authorization: Bearer <your_token>"
```

### Create Order

```bash
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"product": 1, "quantity": 2}]}'
```

### Upload Products

```bash
curl -X POST "http://localhost:8000/api/products/upload/" \
  -H "Authorization: Bearer <admin_token>" \
  -F "file=@products.csv"
```

---

## Rate Limits

* 100 requests/minute per authenticated user
* 10 requests/minute for anonymous users

---

## Testing
```bash
pytest --cov=. --cov-report=html
```

## Project Structure
```
ecommerce/
├── ecommerce/        # Django settings
├── products/         # Categories & products
├── orders/           # Order processing
├── accounts/         # Auth (OIDC)
├── tests/            # Unit & integration tests
├── k8s/              # Kubernetes manifests
├── templates/  
├── pytest.ini
├── manage.py
├── docker-compose.yml          
└── Dockerfile       
```

---

## Support

For issues or feature requests, please [open an issue](https://github.com/kasaza/ecommerce-service/issues).

## License
MIT © 2025 Sylvester Kasaza | kasazax@gmail.com

---