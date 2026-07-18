# Connect CommerceCore to Amazon RDS

## Objective

Migrate the existing CommerceCore database from the EC2-hosted MariaDB instance to Amazon RDS MySQL with minimal downtime, then configure Django to use the managed database.

---

## Prerequisites

Before starting, ensure the following are complete:

- Amazon RDS MySQL instance is created
- RDS status is **Available**
- RDS Security Group allows MySQL (3306) from the EC2 Security Group
- EC2 instance can reach the RDS endpoint
- SSH access to the EC2 instance

---

# Architecture

### Before Migration

```text
Browser
    │
Nginx
    │
Gunicorn
    │
Django
    │
MariaDB (EC2)
```

### After Migration

```text
Browser
    │
Nginx
    │
Gunicorn
    │
Django
    │
Amazon RDS MySQL
```

---

# Step 1 — Verify Existing Database

Connect to the local database running on EC2.

```bash
mysql -u root -p
```

Verify the application database exists.

```sql
SHOW DATABASES;
```

Example:

```text
commerceCore_db
information_schema
mysql
performance_schema
sys
```

Exit MySQL.

```sql
exit;
```

---

# Step 2 — Create a Database Backup

Before performing any migration, create a complete SQL backup.

```bash
mysqldump -u root -p commerceCore_db > commercecore_backup.sql
```

Verify that the backup was created successfully.

```bash
ls -lh commercecore_backup.sql
```

Inspect the beginning of the dump file.

```bash
head -20 commercecore_backup.sql
```

---

## Why create a backup?

A database export provides a recovery point in case the migration fails.

```text
EC2 Database
      │
 mysqldump
      ▼
commercecore_backup.sql
      │
      ├── Restore EC2
      └── Import to RDS
```

This follows the standard backup-first strategy used in production environments.

---

# Step 3 — Import Data into Amazon RDS

Import the SQL dump into the RDS database.

```bash
mysql \
-h <RDS_ENDPOINT> \
-u admin \
-p \
commercecore_db < commercecore_backup.sql
```

---

# Step 4 — Verify the Migration

Connect to Amazon RDS.

```bash
mysql \
-h <RDS_ENDPOINT> \
-u admin \
-p
```

Select the application database.

```sql
USE commercecore_db;
```

Verify the imported tables.

```sql
SHOW TABLES;
```

Expected result:

- Django system tables
- Authentication tables
- Application tables
- All custom models

This confirms the migration completed successfully.

```
exit;
```

---

# Step 5 — Configure Django

Update the project environment variables.
run
```
nano ~/CommerceCore/.env
```

```env
DB_NAME=commercecore_db
DB_USER=admin
DB_PASSWORD=<RDS_PASSWORD>
DB_HOST=<RDS_ENDPOINT>
DB_PORT=3306
```
Save:
```
Ctrl + O
Enter
Ctrl + X
```
No code changes are required because Django already reads its database configuration from environment variables.

---

# Step 6 — Restart Gunicorn

Reload the Django application so the updated environment variables take effect.

```bash
sudo systemctl restart gunicorn
```

Verify the service.

```bash
sudo systemctl status gunicorn
```

Expected status:

```text
Active: active (running)
```

---

# Step 7 — Validate the Application

Open the deployed application and verify:

- Homepage loads
- User authentication
- Product listing
- Product details
- Cart functionality
- Order placement

Successful application behavior confirms that Django is now connected to Amazon RDS.

---

# Troubleshooting

## Bad Request (400)

**Cause**

Host missing from `ALLOWED_HOSTS`.

**Solution**

Step 1: Check Gunicorn logs (highest priority)

Run:
```
sudo journalctl -u gunicorn -n 100 --no-pager
```
or watch them live:
```
sudo journalctl -u gunicorn -f
```
Then refresh the webpage and see if any error appears.

Step 2: Check Django application logs

Since we configured logging earlier in CommerceCore, run:

```
tail -f ~/CommerceCore/logs/django.log
```
Refresh the browser again.


Step 3: Update `.env`.

```env
ALLOWED_HOSTS=<Elastic_IP>,<Public_DNS>,localhost,127.0.0.1
```

Step 4: Restart Gunicorn.

```bash
sudo systemctl restart gunicorn
```

---

## Connection Refused

Verify:

- RDS Security Group
- EC2 Security Group
- Port 3306
- Correct RDS endpoint

---

## Access Denied

Verify:

- Database username
- Password
- Database name

---

# Result

After completing this migration:

- EC2 no longer stores application data.
- Django connects to Amazon RDS.
- Database management, backups, and maintenance are handled by AWS.
- CommerceCore now follows a production-ready architecture using a managed relational database service.