Deployment Process
1. Install the Packages from the Ubuntu Repositories
sudo apt update
sudo apt install python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl

2. Creating the PostgreSQL Database and User
sudo -u postgres psql
CREATE DATABASE clinic_system;
CREATE USER clinic_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE clinic_system TO clinic_user;


3. Create a Python Virtual Environment for Project
python3 -m venv env
source env/bin/activate

4. Create and Configure New Django Project
Clone django project from git
sudo apt install git
git clone project-repo-link
Install requirements
pip install -r requirements.txt
Update settings
allowed host
static root setting
run migrations
collect static
try to run on 0.0.0.0:8000

5. Try to Serve project via gunicorn
Install gunicorn - pip install gunicorn
gunicorn --bind 0.0.0.0:8000 main.wsgi


6.  Creating Gunicorn systemd Socket and Service Files
sudo vim /etc/systemd/system/gunicorn.socket

[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target

sudo vim /etc/systemd/system/gunicorn.service

[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/django_projects/Clinic_management_system_in_django_bootstrap_postgresql/main
ExecStart=/p/root/django_projects/env/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          main.wsgi:application

[Install]
WantedBy=multi-user.target

sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl status gunicorn
sudo systemctl daemon-reload (if you do any change)
sudo systemctl restart gunicorn

7. Configure Nginx to Proxy Pass to Gunicorn
sudo vim /etc/nginx/sites-available/clinic_system

server {
    listen 80;
    server_name 108.170.31.73;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /root/django_projects/Clinic_management_system_in_django_bootstrap_postgresql/main;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}

sudo ln -s /etc/nginx/sites-available/clinic_system /etc/nginx/sites-enabled
sudo nginx -t (test nginx settings)
sudo systemctl status nginx