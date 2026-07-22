# Phase 11 — Amazon RDS Integration for CommerceCore

> **Objective**
>
> Replace the local MariaDB database running on the EC2 instance with a fully managed Amazon RDS MySQL database, while understanding how RDS works, how it connects to Django, and how backup and disaster recovery are handled in production.

---

# Learning Outcomes

After completing this phase, you should be able to:

- Explain why Amazon RDS is used in production.
- Create and configure an RDS MySQL instance.
- Configure networking between EC2 and RDS.
- Migrate an existing MySQL database to Amazon RDS.
- Connect a Django application to RDS.
- Configure backups and snapshots.
- Explain Point-in-Time Recovery (PITR).
- Describe production backup strategies.
- Answer Amazon RDS interview questions confidently.

---

# Why Amazon RDS?

Initially, CommerceCore stored data inside the EC2 instance.

```
                Internet
                     │
              Elastic IP
                     │
                 Nginx
                     │
                Gunicorn
                     │
                Django App
                     │
             Local MariaDB
             (Inside EC2)
```

Although this works, it has several drawbacks.

### Problems

- Database is tied to one EC2 instance.
- Hardware failures can affect both the application and database.
- Manual backups are required.
- Database upgrades must be managed manually.
- Scaling becomes difficult.
- Disaster recovery is limited.

---

# Amazon RDS Architecture

Instead of storing data inside EC2, the database is moved to a managed AWS service.

```
                 Internet
                      │
               Elastic IP
                      │
                 Nginx
                      │
                 Gunicorn
                      │
                 Django App
                      │
              Private VPC Network
                      │
                 Port 3306
                      │
             Amazon RDS MySQL
```

Now,

- EC2 hosts the application.
- RDS hosts the database.

Both remain inside the same VPC.

---

# Benefits of Amazon RDS

- Managed MySQL service
- Automated backups
- Point-in-Time Recovery
- Snapshots
- Monitoring
- Automatic patching
- High availability (Multi-AZ)
- Easier scaling
- Better security
- Reduced operational effort

---

# CommerceCore Architecture

## Before Migration

```
Browser
   │
Elastic IP
   │
Nginx
   │
Gunicorn
   │
Django
   │
MariaDB (localhost)
```

---

## After Migration

```
Browser
   │
Elastic IP
   │
Nginx
   │
Gunicorn
   │
Django
   │
Private VPC
   │
Amazon RDS MySQL
```

---

# Phase Implementation

---

# Part 1 — Introduction

Topics Covered

- What is Amazon RDS
- Why managed databases are preferred
- RDS vs EC2 MySQL
- Supported database engines
- Production architecture

---

# Part 2 — Create RDS Instance

Created:

- MySQL Engine
- db.t4g.micro instance
- Single-AZ deployment
- 20 GB storage
- Private database
- Automated backup enabled

Topics Learned

- Engine
- Engine Version
- Templates
- Availability
- Storage
- Compute
- Authentication
- Monitoring
- Maintenance
- Backup

---

# Part 3 — Security Groups

Created

### EC2 Security Group

Allows

- HTTP (80)
- SSH (22)

---

### RDS Security Group

Allows only

```
MySQL
Port 3306
Source:
EC2 Security Group
```

Meaning

```
Internet
     │
     ▼
EC2
     │
     ▼
RDS
```

Direct internet access to the database is **blocked**.

---

# Networking

```
VPC
│
├── EC2
│
└── Amazon RDS
```

Communication occurs entirely inside the private AWS network.

---

# Part 4 — Connect CommerceCore to RDS

## Step 1

Verify local database.

```
SHOW DATABASES;
```

---

## Step 2

Create backup.

```
mysqldump -u root -p commerceCore_db > commercecore_backup.sql
```

Purpose:

Always take a backup before migration.

---

## Step 3

Import into Amazon RDS

```
mysql \
-h <RDS_ENDPOINT> \
-u admin \
-p \
commercecore_db < commercecore_backup.sql
```

---

## Step 4

Verify Import

```
USE commercecore_db;

SHOW TABLES;
```

All Django tables should exist.

---

## Step 5

Update Django

Modify `.env`

```
DB_NAME=commercecore_db
DB_USER=admin
DB_PASSWORD=********
DB_HOST=<RDS_ENDPOINT>
DB_PORT=3306
```

---

## Step 6

Restart Gunicorn

```
sudo systemctl restart gunicorn
```

---

## Step 7

Verify Website

Test

- Home page
- Products
- Login
- Cart
- Orders

If everything works,

CommerceCore is now using Amazon RDS.

---

# Connection Flow

```
Browser
     │
     ▼
Nginx
     │
     ▼
Gunicorn
     │
     ▼
Django ORM
     │
     ▼
MySQL Driver
     │
     ▼
Amazon RDS
```

---

# Database Connection Flow

```
settings.py
      │
      ▼
Environment Variables
      │
      ▼
DATABASES
      │
      ▼
Django ORM
      │
      ▼
MySQL Client
      │
      ▼
Amazon RDS Endpoint
```

---

# Part 5 — Backup & Recovery

---

## Automated Backups

AWS automatically performs backups.

Features

- Daily backup
- Transaction logs
- Configurable retention
- Point-in-Time Recovery support

---

## Manual Snapshots

Created manually before important deployments.

Characteristics

- Never expire automatically
- Can be restored anytime
- Ideal before production releases

Example

```
Production Database
       │
Take Snapshot
       │
       ▼
Manual Snapshot
```

---

## Point-in-Time Recovery (PITR)

Purpose

Restore the database to any second within the configured backup retention period.

Example

```
09:30 AM
09:35 AM
09:40 AM
09:45 AM
```

If data is deleted at

```
09:45 AM
```

restore to

```
09:44:59 AM
```

Almost no data is lost.

---

## Restore Process

Important

Amazon RDS **never overwrites** the existing database.

Instead

```
Production DB
       │
       ├────────► Continues Running
       │
       ▼
Restore
       │
       ▼
New RDS Instance
```

After verification

```
Update .env

↓

Restart Gunicorn

↓

Application uses restored database
```

---

## Manual Snapshot vs PITR

| Manual Snapshot | PITR |
|-----------------|------|
| Created manually | Automatic |
| Never expires | Limited by retention |
| Fixed point | Any second |
| Before deployments | After incidents |

---

# Production Backup Strategy

A recommended production workflow:

```
Production Database
        │
        ├──────── Daily Automated Backup
        │
        ├──────── Transaction Logs
        │
        ├──────── Manual Snapshot Before Release
        │
        └──────── Test Restore Periodically
```

---

# CommerceCore Final Architecture

```
                Internet
                     │
                Elastic IP
                     │
                  Nginx
                     │
                 Gunicorn
                     │
                Django App
                     │
                Django ORM
                     │
             Private AWS Network
                     │
              Amazon RDS MySQL
```

---

# Advantages After Migration

- Database separated from application server
- Easier scaling
- Automated backups
- Disaster recovery
- Better security
- Managed infrastructure
- Production-ready architecture

---

# Common Commands

## Export Database

```bash
mysqldump -u root -p commerceCore_db > commercecore_backup.sql
```

---

## Import into RDS

```bash
mysql \
-h <RDS_ENDPOINT> \
-u admin \
-p \
commercecore_db < commercecore_backup.sql
```

---

## Connect to RDS

```bash
mysql \
-h <RDS_ENDPOINT> \
-u admin \
-p
```

---

## Verify Tables

```sql
USE commercecore_db;

SHOW TABLES;
```

---

## Restart Gunicorn

```bash
sudo systemctl restart gunicorn
```

---

## Check Gunicorn

```bash
sudo systemctl status gunicorn
```

---

# Interview Questions

### Why use Amazon RDS instead of MySQL on EC2?

Amazon RDS provides a managed database service with automated backups, monitoring, scaling, maintenance, snapshots, and disaster recovery, allowing engineers to focus on application development instead of database administration.

---

### Why keep RDS private?

The database should only be accessible by application servers inside the VPC. Exposing MySQL directly to the internet increases security risks.

---

### What is the purpose of Security Groups?

Security Groups act as virtual firewalls. The RDS Security Group allows MySQL traffic only from the EC2 Security Group over port 3306.

---

### What is Point-in-Time Recovery?

PITR restores a database to any specific second within the configured backup retention period by combining automated backups with transaction logs.

---

### Does restoring overwrite the production database?

No. Amazon RDS always creates a new database instance during a restore operation. The original production database remains unchanged.

---

### Why take a manual snapshot before deployment?

If a deployment introduces schema changes or data corruption, a manual snapshot provides a reliable rollback point that never expires until deleted.

---

# Key Takeaways

- Amazon RDS separates the database from the application server.
- EC2 communicates with RDS over a private VPC network.
- Security Groups protect the database from public access.
- Django connects to RDS through environment variables.
- Automated backups and manual snapshots improve disaster recovery.
- Point-in-Time Recovery minimizes data loss.
- This architecture closely matches production deployments used in modern Django applications.