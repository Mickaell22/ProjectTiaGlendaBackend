# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is "Centro Tía Glenda" - a healthcare management system built with Flask (Python) that manages medical center operations including patients, staff, specialties, therapy sessions, and user authentication. The system uses PostgreSQL as the database and provides a REST API with Swagger documentation.

## Development Commands

### Running the Application
```bash
python app.py
```
The Flask app runs on port 5000 by default, configurable via PORT environment variable.

### Testing
```bash
# Run all tests using the advanced test runner
python tests/test_api_complete_master.py

# Run specific module tests
python tests/test_autenticacion_api.py
python tests/test_pacientes_api.py
python tests/test_personal_api.py
python tests/test_especialidades_api.py
python tests/test_usuarios_api.py
python tests/test_tutores_api.py
python tests/test_personas_api.py
python tests/test_roles_api.py
python tests/test_sesiones_terapia_api.py
python tests/test_sesiones_pedagogicas_api.py

# Unit tests
python tests/test_units.py
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Activate virtual environment (if using venv)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

## Architecture

### Directory Structure
- `src/api/`: Core API implementation
  - `Components/`: Data access layer (database interactions)
  - `Service/`: Business logic layer
  - `routes/`: Route definitions and HTTP handling
- `src/utils/`: Utility modules
  - `database/`: Database connection and operations
  - `general/`: Configuration, logging, authentication, security
- `tests/`: Comprehensive test suite with advanced test runner
- `static/swagger.json`: API documentation
- `docs/`: Documentation directory (currently empty)

### API Architecture Pattern
The project follows a 3-layer architecture:
1. **Routes** (`api_routes.py`): HTTP request handling and routing
2. **Services** (`*Service.py`): Business logic and validation
3. **Components** (`*Component.py`): Data access and database operations

### Key Modules
- **Authentication**: JWT-based with role-based access control (@token_required, @admin_required)
- **Database**: PostgreSQL with custom connection handling (DataBaseHandle class)
- **Logging**: Comprehensive logging system with daily log files in src/utils/general/LOGS/
- **Security**: Password hashing, JWT tokens, input validation
- **Testing**: Advanced test runner with progress bars, colored output, and detailed statistics

## Configuration

### Database Configuration
Database settings are managed through:
1. Environment variables (highest priority)
2. `src/utils/general/config.cfg` file
3. Default values in `src/utils/general/config.py`

Key environment variables:
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `JWT_SECRET`
- `AMBIENTE` (DEVELOPMENT/PRODUCTION)

### API Endpoints Structure
- `/api/test`: API health check
- `/api/test-db`: Database connectivity test
- `/api/login`, `/api/logout`, `/api/verify-token`, `/api/me`: Authentication
- `/api/personas`: Person management
- `/api/usuarios`: User management (admin-only)
- `/api/personal`: Staff management
- `/api/especialidades`: Medical specialties
- `/api/pacientes`: Patient management
- `/api/tutores`: Guardian/tutor management
- `/api/roles`: Role management
- `/api/sesiones-terapia`: Therapy session management with cronograma generation
- `/api/sesiones-pedagogicas`: Pedagogical session management with class scheduling
- `/docs/`: Swagger UI documentation
- `/health`: Application health endpoint

## Development Practices

### Testing Philosophy
The project uses a sophisticated testing framework (`tests/utils/advanced_test_runner.py`) that provides:
- Color-coded progress bars
- Detailed timing statistics
- ETA calculations
- Retry mechanisms for failed tests
- Export capabilities for test results

### Security Implementation
- JWT tokens for stateless authentication
- Role-based authorization (regular users vs admin)
- Password hashing with bcrypt
- Input validation and sanitization
- CORS configuration for frontend integration

### Logging Strategy
- Separate error and info logs by date
- Location: `src/utils/general/LOGS/`
- Automatic rotation by day
- Integration throughout the application

### Database Patterns
- Custom DataBaseHandle class for connection management with specific methods:
  - `getRecords()`: For SELECT queries (returns dict/list)
  - `getRecordsWithStatus()`: For SELECT with detailed error handling and status info
  - `ExecuteNonQuery()`: For INSERT/UPDATE/DELETE without return values
  - `ExecuteInsert()`: For INSERT with ID return (limited use)
- **Important**: Never use `getRecords()` with INSERT RETURNING - use ExecuteNonQuery + separate SELECT
- **Important**: No `updateRecords()` method exists - use `ExecuteNonQuery()` for updates
- **Important**: Use `getRecordsWithStatus()` for operations where you need to distinguish between "no data" vs "query error"
- PostgreSQL time objects require conversion to strings for JSON serialization
- Support for parameterized queries and proper connection cleanup

## Dependencies

Main dependencies include:
- Flask: Web framework
- flask-swagger-ui: Swagger UI integration
- psycopg2: PostgreSQL driver
- PyJWT: JWT token handling
- bcrypt: Password hashing
- flask-cors: CORS support
- configparser: Configuration management
- validators: Input validation
- python-dotenv: Environment variable loading
- gunicorn: Production WSGI server
- openpyxl, pillow, reportlab: Document/report generation
- requests: HTTP client for testing

## API Documentation

The system includes comprehensive Swagger documentation available at `/docs/` when the application is running. The Swagger JSON specification is located at `/static/swagger.json`.

## Common Development Workflow

1. Check database connectivity: `GET /api/test-db`
2. Authenticate: `POST /api/login`
3. Use the returned JWT token in Authorization header for protected routes
4. Run tests to verify changes: `python tests/test_api_complete_master.py`
5. Check logs in `src/utils/general/LOGS/` for debugging

## Critical Development Notes

### JSON Serialization Issues
When working with database responses, always convert PostgreSQL-specific types to JSON-serializable formats:
- `time` objects: Use `str(time_obj)` 
- `date` objects: Use `date_obj.isoformat()`
- `datetime` objects: Use `datetime_obj.isoformat()`

### Test Runner Compatibility
The advanced test runner (`tests/utils/advanced_test_runner.py`) is Windows-compatible with ASCII-only characters in progress bars. Unicode characters have been replaced with ASCII equivalents to prevent encoding errors.

### Debug Utilities
The project includes specialized debugging tools for development:
- `debug_cronograma.py`: Debug therapy session scheduling/cronograma generation
- `debug_endpoint.py`: Direct endpoint testing with authentication
- `debug_test_flow.py`: Test workflow debugging
These can be run directly with `python <script_name>.py` for targeted debugging.

### Therapy Sessions Module
The therapy sessions (`/api/sesiones-terapia`) module includes:
- Automatic cronograma (schedule) generation when creating sessions
- Complex relationships between sessions, patients, therapists, and schedules
- Custom business logic for session date calculations based on weekdays
- Four main tables: `sesion_terapia`, `sesion_paciente`, `cronograma_sesiones`, `asistencia_sesiones`

### Pedagogical Sessions Module
The pedagogical sessions (`/api/sesiones-pedagogicas`) module includes:
- Academic/educational session management for group classes
- Automatic class schedule generation when creating sessions
- Student enrollment and management within sessions
- Complex relationships between sessions, students, educators, and class schedules
- Four main tables: `sesion_pedagogica`, `sesion_estudiante`, `cronograma_clases`, `asistencia_clases`
- Academic grading and attendance tracking capabilities

### Database Schema Notes
- All tables include audit fields: `fecha_creacion`, `fecha_modificacion`, `usuario_creacion`, `usuario_modificacion`
- Foreign key relationships are strictly enforced
- Triggers automatically update `fecha_modificacion` on record updates
- Session codes are auto-generated with format "ST-YYYY-NNN" via database triggers
- Database initialization scripts are located in `src/utils/database/`:
  - `01_estructura_tablas.sql`: Complete database schema
  - `02_datos_iniciales.sql`: Initial/seed data