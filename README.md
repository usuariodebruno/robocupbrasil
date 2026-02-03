# RoboCup Brasil - Official Website

Institutional website for RoboCup Brasil, featuring information about OBR, CBR, MNR, news, calendar, regional representatives, and more.

## Requirements

- Python 3.10 or higher (tested on 3.12)
- Git
- (Optional) Virtualenv, Poetry, or Pipenv

## How to Run the Project Locally (Development)

Follow these steps to clone, set up, and run the website on your machine.

### 1. Clone the repository

```bash
git clone https://github.com/lluckymou/robocup-brasil.git
cd robocup-brasil
```

### 2. Create and activate the virtual environment

```bash
# Create the virtual environment (if it doesn't exist)
python3 -m venv venv

# Activate (Linux / macOS)
source venv/bin/activate

# Activate (Windows)
# venv\Scripts\activate
```

You should see `(venv)` at the beginning of your terminal prompt.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing or outdated, install the core packages and regenerate it:
Bash

```bash
pip install django django-ckeditor python-dotenv
pip freeze > requirements.txt
```

### 4. Set up the `.env` file (recommended)

Create a `.env` file in the project root with:

```bash
DJANGO_SECRET_KEY=insert-secure-key
DJANGO_DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,robocup.org.br,*.robocup.org.br
```

Generate a secure key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 5. Apply migrations and set up role-based permissions

```bash
# Apply database migrations
python manage.py migrate

# Create default role groups and assign permissions
python manage.py setup_role_permissions

# Create an admin user (if none exists)
python manage.py createsuperuser
# Suggested: Username: admin
# Email: (optional)
# Password: (your choice)
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open in your browser:

http://127.0.0.1:8000/ → home page
http://127.0.0.1:8000/admin/ → admin panel (login with admin / your password)

Built with care by @llucmou ⚙️