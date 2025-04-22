# An Order Management System

This is a web service app for managing customers and orders with real-time SMS notifications built with Django.

##  Live Demo

The application is deployed and available at: [https://sms.socialsynch.top](https://sms.socialsynch.top)

##  Features

- **Customer Management**
- **Order Processing**
- **Real-time Notifications**: Automatic SMS alerts to customers when orders are placed via Africa's Talking API
- **Secure Authentication**: OpenID Connect implementation with Auth0 for secure user authentication
- **RESTful API**: Use of Redoc documentation to diplay the correct requests and response to the app
- **Comprehensive Testing**: 91% code coverage
- **CI/CD Pipeline**: Automated testing and deployment via GitHub Actions

##  Technology Stack

- **Backend**: Django/Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: Auth0 OpenID Connect
- **SMS Gateway**: Africa's Talking API
- **Deployment**: DigitalOcean
- **Web Server**: Nginx + Gunicorn
- **CI/CD**: GitHub Actions
- **DNS Management**: Cloudflare

##  Installation & Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Nginx
- Git

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/weeserious/sms-service.git
   cd sms-service
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

##  API Documentation

The API is documented using Redoc and is available on the homepage when the server is running.

### Authentication

All API endpoints require authentication using JWT tokens obtained through OpenID Connect with Auth0.

### Endpoints

#### Customers

- `GET /api/customers/` - List all customers
- `POST /api/customers/` - Create a new customer
- `GET /api/customers/{id}/` - Retrieve a specific customer
- `PUT /api/customers/{id}/` - Update a customer
- `DELETE /api/customers/{id}/` - Delete a customer

#### Orders

- `GET /api/orders/` - List all orders
- `POST /api/orders/` - Create a new order
- `GET /api/orders/{id}/` - Retrieve a specific order
- `PUT /api/orders/{id}/` - Update an order
- `DELETE /api/orders/{id}/` - Delete an order

#### Authentication

- `POST /api/generate-token/` - Generate an access token for API usage

##  Authentication Flow

This project implements Auth0 OpenID Connect for secure authentication and authorization. The authentication flow is as follows:

1. Users generate an access token
2. The token is used for subsequent API requests

The middleware automatically handles token refresh when tokens are about to expire.

##  SMS Notifications

The system uses Africa's Talking SMS gateway to send notifications to customers when orders are placed. This was done using sandbox environment for testing.

Example notification format:
```
Hello [Customer Name], order for [Item] has been received. Total: Ksh [Amount]. Thank you!
```

##  Testing

The project includes 21 unit tests with a 91% code coverage.

Run tests with:
```bash
python manage.py test
```

Generate coverage report:
```bash
coverage run --source='.' manage.py test
coverage report
```

##  Deployment

### Deployment Process

The application is deployed on DigitalOcean using a custom CI/CD pipeline with GitHub Actions:

1. Push changes to the main branch
2. GitHub Actions runs tests and build the application
3. If tests pass, the application is automatically deployed to DigitalOcean
4. Nginx serves the application with Gunicorn as the WSGI server

### Server Configuration

The application runs as a systemd service for reliability:

```bash
sudo systemctl status sms_service  # Check service status
sudo systemctl restart sms_service  # Restart the service
```

