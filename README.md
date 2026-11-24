# Healthcare Management Backend System 🏥

A robust, production-ready RESTful backend application built using **Django**, **Django REST Framework (DRF)**, and **PostgreSQL**. The system provides secure user authentication via **JWT (JSON Web Tokens)**, full lifecycle management for **Patients** and **Doctors**, and dynamic **Patient-Doctor Mapping**.

---

## 🚀 Features

- **JWT Authentication**: User registration and login with secure JWT token issuing using `djangorestframework-simplejwt`.
- **Custom User Model**: Custom user model using email as the unique authentication identifier.
- **Patient Management**: Full CRUD operations for patients, isolating records to the authenticated user who created them.
- **Doctor Management**: Full CRUD operations for medical practitioners with specialty, experience, and hospital affiliation.
- **Patient-Doctor Mapping**: Dynamic assignment of doctors to patients, preventing duplicate assignments and enabling reverse lookups.
- **Relational Integrity**: Backed by PostgreSQL with foreign key cascades, unique constraints, and database indexes.
- **Error Handling & Validation**: Centralized custom exception handler providing structured, consistent JSON error responses across all endpoints.
- **Interactive API Documentation**: Embedded Swagger UI (`/api/docs/`) and Redoc (`/api/redoc/`) via OpenAPI 3.0 schema generation (`drf-spectacular`).
- **Postman Collection**: Ready-to-import Postman collection with automatic token capture.
- **100% Test Coverage**: Complete automated test suite covering all endpoints, permissions, validations, and edge cases.

---

## 🛠 Tech Stack

- **Backend Framework**: Django 5.2 & Django REST Framework (DRF) 3.18
- **Authentication**: SimpleJWT (`djangorestframework-simplejwt`)
- **Database**: PostgreSQL 18
- **DB Driver**: `psycopg2-binary`
- **Configuration**: `python-dotenv` (12-Factor App design)
- **CORS Handling**: `django-cors-headers`
- **API Documentation**: `drf-spectacular` (Swagger & Redoc)

---

## 📂 Project Structure

```text
healthcare_backend/
├── accounts/                     # User authentication & custom User model
│   ├── models.py                 # Custom User model (email as username)
│   ├── serializers.py            # User registration & login serializers
│   ├── views.py                  # Register, Login, Me views
│   ├── urls.py                   # /api/auth/* routes
│   └── tests.py                  # Auth test cases
├── patients/                     # Patient management app
│   ├── models.py                 # Patient model with user association
│   ├── serializers.py            # Patient serializers with assigned doctors
│   ├── views.py                  # Patient CRUD API views
│   ├── urls.py                   # /api/patients/* routes
│   └── tests.py                  # Patient test cases
├── doctors/                      # Doctor directory app
│   ├── models.py                 # Doctor model
│   ├── serializers.py            # Doctor serializers with assigned patients
│   ├── views.py                  # Doctor CRUD API views
│   ├── urls.py                   # /api/doctors/* routes
│   └── tests.py                  # Doctor test cases
├── mappings/                     # Patient-Doctor assignment app
│   ├── models.py                 # PatientDoctorMapping model
│   ├── serializers.py            # Mapping serializers with validations
│   ├── views.py                  # Assignment & lookup views
│   ├── urls.py                   # /api/mappings/* routes
│   └── tests.py                  # Mapping test cases
├── config/                       # Core project configuration
│   ├── settings.py               # Django settings (DB, JWT, DRF, CORS)
│   ├── urls.py                   # Master routing & API documentation routes
│   ├── exceptions.py             # Custom centralized error handler
│   └── wsgi.py
├── .env                          # Environment variables (secret keys, DB)
├── .env.example                  # Template for environment configuration
├── requirements.txt              # Python dependencies
├── Healthcare_API.postman_collection.json  # Postman collection
├── manage.py
└── README.md
```

---

## ⚙️ Setup and Installation

### 1. Prerequisites
- Python 3.10+ installed
- PostgreSQL 14+ installed and running

### 2. Navigate to the Project Folder
```bash
cd "C:\Users\Admin\Desktop\healthcare_backend"
```

### 3. Activate the Virtual Environment
On Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```
On Windows (Command Prompt):
```cmd
venv\Scripts\activate.bat
```

*(If you ever need to create a new virtual environment from scratch: `python -m venv venv` and `pip install -r requirements.txt`)*

### 4. Database Setup & Environment Variables
Ensure `.env` exists in the root folder with the appropriate PostgreSQL credentials:
```env
SECRET_KEY=django-insecure-healthcare-secret-key-super-secure-production-ready-2026
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=YourNewPassword123
DB_HOST=localhost
DB_PORT=5432

ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7
```

### 5. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser (Optional, for Django Admin)
```bash
python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
python manage.py runserver
```
The server will start at: `http://127.0.0.1:8000/`

---

## 🧪 Running Automated Tests

Run the comprehensive automated test suite (31 tests across all modules):
```bash
python manage.py test --verbosity 2
```

All 31 test cases verify:
- User registration (valid data, duplicate email rejection, password validation)
- User login (JWT token return, credential validation)
- Authentication permissions on protected endpoints
- Patient creation, listing (only created by authenticated user), retrieval, update, deletion
- Doctor creation, listing, retrieval, update, deletion, unique email enforcement
- Patient-doctor assignment, duplicate mapping prevention, retrieval by patient, deletion of mapping

---

## 📖 API Documentation & Endpoints

Interactive Swagger UI and Redoc documentation are available out of the box:
- **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
- **Redoc**: `http://127.0.0.1:8000/api/redoc/`
- **OpenAPI Schema**: `http://127.0.0.1:8000/api/schema/`

### 1. Authentication APIs
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register a new user with `name`, `email`, `password` | No |
| `POST` | `/api/auth/login/` | Log in with `email` and `password`, returns JWT | No |
| `GET` | `/api/auth/me/` | Get current authenticated user details | Yes (Bearer) |

#### Register Request Body:
```json
{
    "name": "Dr. Sarah Connor",
    "email": "sarah@healthcare.com",
    "password": "SecurePassword123"
}
```

#### Login Response:
```json
{
    "success": true,
    "message": "Login successful.",
    "user": {
        "id": 1,
        "name": "Dr. Sarah Connor",
        "email": "sarah@healthcare.com"
    },
    "access": "eyJhbGciOiJIUzI1NiIsIn...",
    "refresh": "eyJhbGciOiJIUzI1NiIsIn...",
    "tokens": {
        "access": "eyJhbGciOiJIUzI1NiIsIn...",
        "refresh": "eyJhbGciOiJIUzI1NiIsIn..."
    }
}
```

---

### 2. Patient Management APIs
*All patient endpoints require `Authorization: Bearer <access_token>`*

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/patients/` | Add a new patient (auto-assigned to requesting user) |
| `GET` | `/api/patients/` | Retrieve all patients created by the authenticated user |
| `GET` | `/api/patients/<id>/` | Get details of a specific patient (including assigned doctors) |
| `PUT` | `/api/patients/<id>/` | Update patient details |
| `DELETE` | `/api/patients/<id>/` | Delete a patient record |

#### Create Patient Request Body:
```json
{
    "name": "John Doe",
    "date_of_birth": "1990-04-15",
    "age": 36,
    "gender": "male",
    "contact_number": "+1-555-0199",
    "email": "johndoe@example.com",
    "address": "123 Main Street, New York, NY",
    "medical_history": "Mild allergies to penicillin."
}
```

---

### 3. Doctor Management APIs
*All doctor endpoints require `Authorization: Bearer <access_token>`*

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/doctors/` | Add a new doctor |
| `GET` | `/api/doctors/` | Retrieve all registered doctors |
| `GET` | `/api/doctors/<id>/` | Get details of a specific doctor (including assigned patients) |
| `PUT` | `/api/doctors/<id>/` | Update doctor details |
| `DELETE` | `/api/doctors/<id>/` | Delete a doctor record |

#### Create Doctor Request Body:
```json
{
    "name": "Gregory House",
    "specialization": "Diagnostic Medicine",
    "contact_number": "+1-555-0300",
    "email": "drhouse@hospital.org",
    "years_of_experience": 20,
    "hospital_affiliation": "Princeton-Plainsboro"
}
```

---

### 4. Patient-Doctor Mapping APIs
*All mapping endpoints require `Authorization: Bearer <access_token>`*

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/mappings/` | Assign a doctor to a patient |
| `GET` | `/api/mappings/` | Retrieve all patient-doctor mappings |
| `GET` | `/api/mappings/<patient_id>/` | Get all doctors assigned to a specific patient |
| `DELETE` | `/api/mappings/<id>/` | Remove a doctor from a patient (delete mapping by mapping ID) |

#### Assign Doctor Request Body:
```json
{
    "patient_id": 1,
    "doctor_id": 1,
    "notes": "Assigned for annual comprehensive physical exam."
}
```

#### Get Doctors Assigned to Patient Response:
```json
{
    "success": true,
    "patient": {
        "id": 1,
        "name": "John Doe",
        "gender": "male",
        "contact_number": "+1-555-0199",
        "email": "johndoe@example.com"
    },
    "assigned_doctors_count": 1,
    "doctors": [
        {
            "mapping_id": 1,
            "assigned_at": "2026-11-24T12:00:00Z",
            "notes": "Assigned for annual comprehensive physical exam.",
            "doctor": {
                "id": 1,
                "name": "Gregory House",
                "specialization": "Diagnostic Medicine",
                "contact_number": "+1-555-0300",
                "email": "drhouse@hospital.org",
                "years_of_experience": 20,
                "hospital_affiliation": "Princeton-Plainsboro"
            }
        }
    ]
}
```

---

## 📮 Postman Collection Instructions

1. Open **Postman**.
2. Click **Import** (top left).
3. Select the file: `C:\Users\Admin\Desktop\healthcare_backend\Healthcare_API.postman_collection.json`.
4. Open the imported collection:
   - Send the **Login User** request under `1. Authentication`.
   - The test script will **automatically extract and store the JWT access token** into the collection variable `{{access_token}}`.
   - All subsequent requests (Patients, Doctors, Mappings) will automatically inherit this token and authenticate seamlessly!
