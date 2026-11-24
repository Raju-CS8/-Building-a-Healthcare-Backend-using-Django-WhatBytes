# Django Assignment: Building a Healthcare Backend 🏥 - CareSync

A production-ready, full-stack healthcare application with a robust **Django & Django REST Framework (DRF)** backend, **PostgreSQL** relational database, **SimpleJWT** token authentication, and a modern **interactive frontend portal**.

---

## 🌟 What Makes This Project Stand Out

1. **Full-Stack Experience**: In addition to complete, verified RESTful APIs, the project includes an interactive **CareSync Portal** at `http://127.0.0.1:8000/`, built with Django templates, Tailwind CSS, Lucide icons, and an asynchronous JavaScript client consuming the JWT-secured backend in real-time.
2. **Strict Security & Privacy**:
   - **Object-Level Permissions (`IsOwnerOrAdmin`)**: Strict HIPAA-style data isolation ensuring only the creator or authorized admin can access, update, or delete a patient's medical record.
   - **Rate Limiting / Throttling**: Protected against brute-force attacks on login/registration via DRF `ScopedRateThrottle`.
   - **HTTP Security Headers**: `SECURE_BROWSER_XSS_FILTER`, `SECURE_CONTENT_TYPE_NOSNIFF`, and `X_FRAME_OPTIONS = 'DENY'`.
3. **Database Integrity**: Backed by PostgreSQL with relational cascades, unique index constraints (preventing duplicate doctor-patient assignments), and optimized joins (`select_related`).
4. **Interactive Documentation**: Auto-generated OpenAPI 3.0 documentation with Swagger UI (`/api/docs/`) and Redoc (`/api/redoc/`).
5. **100% Automated Test Coverage**: **40 out of 40 automated test cases** passing against PostgreSQL.
6. **Pre-configured Postman Collection**: Importable collection with automated token extraction script.
7. **One-Click Demo Seeding**: `python manage.py seed_data` pre-populates verified doctors, patients, and assignments.

---

## 🛠 Tech Stack

- **Backend**: Django 5.2 & Django REST Framework (DRF) 3.18
- **Authentication**: JWT via `djangorestframework-simplejwt`
- **Database**: PostgreSQL 18 with `psycopg2-binary`
- **Frontend Portal**: Django Templates + Tailwind CSS + Lucide Icons + Fetch API
- **API Documentation**: `drf-spectacular` (OpenAPI 3.0, Swagger UI, Redoc)
- **Configuration**: `python-dotenv` (12-Factor App methodology)
- **CORS Support**: `django-cors-headers`

---

## 📂 Project Structure

```text
healthcare_backend/
├── accounts/                     # JWT Authentication & Custom User model
│   ├── models.py                 # Custom User (email as username)
│   ├── serializers.py            # User registration & login serializers
│   ├── views.py                  # Register, Login, Me views
│   ├── urls.py                   # /api/auth/* routes
│   └── tests.py                  # Auth & health check tests
├── patients/                     # Patient management app
│   ├── models.py                 # Patient model with user association
│   ├── permissions.py            # Object-level permission (IsOwnerOrAdmin)
│   ├── serializers.py            # Deep validations (phone regex, DOB future check, auto age)
│   ├── views.py                  # Patient CRUD API views
│   ├── urls.py                   # /api/patients/* routes
│   └── tests.py                  # Patient tests (permissions, validations, CRUD)
├── doctors/                      # Doctor directory app
│   ├── models.py                 # Doctor model
│   ├── serializers.py            # Doctor validation (phone, email, experience)
│   ├── views.py                  # Doctor CRUD API views
│   ├── urls.py                   # /api/doctors/* routes
│   └── tests.py                  # Doctor tests
├── mappings/                     # Patient-Doctor assignment app
│   ├── models.py                 # PatientDoctorMapping with unique constraints
│   ├── serializers.py            # Validation & nested representation
│   ├── views.py                  # Assignment & lookup views
│   ├── urls.py                   # /api/mappings/* routes
│   └── tests.py                  # Mapping tests
├── config/                       # Core configuration
│   ├── settings.py               # PostgreSQL, SimpleJWT, DRF, CORS, Throttling
│   ├── urls.py                   # Master routing & documentation routes
│   ├── exceptions.py             # Centralized JSON error handler
│   └── wsgi.py
├── templates/
│   └── index.html                # Interactive CareSync Frontend Portal
├── .env                          # Environment variables (DB credentials)
├── .env.example                  # Template environment file
├── requirements.txt              # Python dependencies
├── Healthcare_API.postman_collection.json  # Postman collection
├── manage.py
└── README.md
```

---

## ⚙️ Quick Setup

### 1. Activate Virtual Environment
```powershell
cd "C:\Users\Admin\Desktop\healthcare_backend"
.\venv\Scripts\Activate.ps1
```

### 2. Configure Environment Variables
Ensure `.env` exists in the root folder with your PostgreSQL credentials:
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

### 3. Apply Migrations & Seed Sample Data
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
```

### 4. Run the Server
```bash
python manage.py runserver
```

---

## 🌐 Access Points

| Service | URL | Description |
|---|---|---|
| **CareSync Portal** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | Full-featured web portal with metrics, CRUD, and assignments |
| **Swagger UI** | [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/) | Interactive OpenAPI documentation & API explorer |
| **Redoc** | [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/) | Detailed API reference specifications |
| **Health Check** | [http://127.0.0.1:8000/api/health/](http://127.0.0.1:8000/api/health/) | Live PostgreSQL and API uptime probe |
| **Django Admin** | [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) | Visual administration panel for all models |

---

## 🧪 Running Automated Tests

Run the full suite of **40 test cases**:
```bash
python manage.py test --verbosity 2
```

---

## 📖 API Endpoints Reference

### 1. Authentication APIs
- `POST /api/auth/register/` - Register new user (`name`, `email`, `password`)
- `POST /api/auth/login/` - Authenticate user, return JWT tokens (`access` & `refresh`)
- `GET /api/auth/me/` - Retrieve current user profile (Requires Bearer token)

### 2. Patient Management APIs *(Authenticated)*
- `POST /api/patients/` - Add new patient (automatically assigned to `request.user`)
- `GET /api/patients/` - Retrieve all patients created by the authenticated user
- `GET /api/patients/<id>/` - Retrieve details of a specific patient (including assigned doctors)
- `PUT /api/patients/<id>/` - Update patient details (owner/admin only)
- `DELETE /api/patients/<id>/` - Delete a patient record (owner/admin only)

### 3. Doctor Management APIs *(Authenticated)*
- `POST /api/doctors/` - Add new doctor
- `GET /api/doctors/` - Retrieve all doctors
- `GET /api/doctors/<id>/` - Retrieve details of a specific doctor (including assigned patients)
- `PUT /api/doctors/<id>/` - Update doctor details
- `DELETE /api/doctors/<id>/` - Delete a doctor record

### 4. Patient-Doctor Mapping APIs *(Authenticated)*
- `POST /api/mappings/` - Assign doctor to patient (prevents duplicate assignments)
- `GET /api/mappings/` - Retrieve all patient-doctor mappings
- `GET /api/mappings/<patient_id>/` - Get all doctors assigned to a specific patient
- `DELETE /api/mappings/<id>/` - Remove doctor from patient (deletes mapping by ID)

---

## 📮 Postman Collection
Import `Healthcare_API.postman_collection.json` directly into Postman. When you execute **Login User**, the response test script automatically captures the JWT token and sets the collection-level `{{access_token}}` variable.
