# RoboCup Brasil CMS

Institutional Content Management System (CMS) and website for RoboCup Brasil using Django and SQLite, featuring information about OBR, CBR, MNR, news, calendar, regional representatives, and more.

## Requirements

- Python 3.10 or higher (tested on 3.12)
- Git
- (Optional) Virtualenv, Poetry, or Pipenv

## How to Run the Project Locally (Development)

Follow these steps to clone, set up, and run the website on your machine.

### 1. Clone the repository

```bash
git clone https://github.com/lluckymou/robocupbrasil.git
cd robocupbrasil
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

Note: for PDF thumbnail generation the project uses `pdf2image`, which requires the `poppler` system package. On Debian/Ubuntu (and derivatives like Zorin/PopOS) servers install:

```bash
sudo apt update
sudo apt install poppler-utils
```

After installing `poppler-utils`, re-run:

```bash
pip install -r requirements.txt
```

<!-- If `requirements.txt` is missing or outdated, install the core packages and regenerate it:
Bash

```bash
pip install django django-ckeditor python-dotenv django-compressor django-resized
pip freeze > requirements.txt
``` -->

### 4. Set up the `.env` file (recommended)

Generate a secure key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Create a `.env` file in the project root with:

```bash
DJANGO_SECRET_KEY=insert-secure-key
DJANGO_DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost,robocup.org.br,*.robocup.org.br
```

### 5. Apply migrations and set up permissions and basic structure

```bash
# Apply database migrations
python manage.py migrate

# Create default role groups and assign permissions
python manage.py setup_role_permissions

# Create default tags and basic site structure
python manage.py setup_default_tags

# Compile Translations
python manage.py compilemessages

# Create an admin user
python manage.py createsuperuser
# Suggested: Username: admin
```

### 6. Caching

To enhance performance, this project utilizes Django's file-based caching system. When a page is visited for the first time, its rendered HTML is stored in a file. Subsequent visits will be served directly from this file, significantly speeding up response times and reducing server load.

- The cache files are stored in the `django_cache/` directory, which is created automatically in the project root.
- Cache is automatically cleared whenever content is created, updated, or deleted in the admin panel.
- This directory is intentionally not tracked by Git (and is listed in `.gitignore`).

### 7. Production

```bash
# Collectsatatic for production
python manage.py collectstatic --noinput && python manage.py compress --force
```

**Nginx configuration:**

```nginx
location /media/ {
    alias /PATH/TO/robocupbrasil/media/;
}

location /static/ {
    alias /PATH/TO/robocupbrasil/staticfiles/;
}
```

### 7. Run the server

```bash
python manage.py runserver
```

Open in your browser:

http://127.0.0.1:8000/ → home page
http://127.0.0.1:8000/admin/ → admin panel (login with admin / your password)

Built with care by @llucmou 🌲