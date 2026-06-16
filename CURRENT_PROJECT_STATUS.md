AWS EC2                    ✅
MariaDB                    ✅
Django                     ✅
Gunicorn                   ✅
Systemd Service            ✅
Nginx                      ✅
Static Files               ✅
Media Files                ✅
GitHub Repository          ✅
GitHub Actions             ✅
CI/CD                      ✅
Auto Deployment            ✅
Security Group Cleanup     ✅

Current Architecture
Internet
    ↓
Nginx (Port 80)
    ├── /static/ → staticfiles
    ├── /media/  → media
    └── Django Requests
              ↓
          Gunicorn
              ↓
          Django
              ↓
          MariaDB