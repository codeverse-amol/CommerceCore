# Phase 11 - Part 2: Create Amazon RDS Instance

## Objective

Create a production-style Amazon RDS MySQL instance for CommerceCore and understand every configuration option selected during database creation.

---

# Architecture Before

                Browser
                    │
                    ▼
                 Nginx
                    │
                    ▼
                Gunicorn
                    │
                    ▼
                 Django
                    │
                    ▼
          MySQL (Installed on EC2)

---

# Architecture After

                Browser
                    │
                    ▼
                 Nginx
                    │
                    ▼
                Gunicorn
                    │
                    ▼
                 Django
                    │
                    ▼
              Amazon RDS (MySQL)

The application server and database are now separated.

---

# 1. Engine

Selected

MySQL Community

### Why?

CommerceCore already uses MySQL.

Changing to PostgreSQL would require migration.

Other engines like Oracle or SQL Server require commercial licenses.

✅ Best choice for CommerceCore

---

# 2. Engine Version

Selected

MySQL 8.4 LTS

### Why?

- Latest Long-Term Support release
- Security updates
- Stable
- Django compatible

Production systems should always use supported versions.

---

# 3. Template

Selected

Free Tier

### Why?

Suitable for learning projects.

Production workloads generally use Production templates.

---

# 4. Availability

Selected

Single-AZ Deployment

Diagram

AZ-1

RDS

### Why?

✔ Lower cost

✔ Simple architecture

✔ Good for CommerceCore

Production systems often use Multi-AZ.

---

# 5. DB Identifier

Selected

commercecore-db

### Why?

Professional naming.

Instead of

database-1

use

commercecore-db

This makes infrastructure easier to manage.

---

# 6. Initial Database

Created

commercecore_db

### Why?

Without specifying it, only the server would be created.

The database would need to be created manually later.

---

# 7. Credentials

Username

admin

Password

Strong custom password

Stored securely.

Later this will be added to

.env

---

# 8. Authentication

Selected

Password Authentication

### Why?

Simple

Secure

Works perfectly with Django

IAM Authentication is mainly used in enterprise environments.

---

# 9. Instance Class

Selected

db.t4g.micro

### Why?

Low cost

Enough resources for CommerceCore

Suitable for learning and development

Production systems typically use larger instance classes.

---

# 10. Storage

Selected

General Purpose SSD (gp2)

20 GB

### Why?

Balanced performance

Low cost

Suitable for web applications

---

# 11. Connectivity

Selected

Default VPC

Private Networking

### Why?

The RDS instance resides inside the same VPC as EC2.

Communication remains within AWS's private network.

---

# 12. Public Access

Selected

No

Diagram

Internet

    │

    ✗

Amazon RDS

### Why?

Databases should never be directly exposed to the Internet.

Only application servers should access them.

---

# 13. Encryption

Selected

Enabled

AWS KMS

### Why?

Protects stored data.

Industry best practice.

---

# 14. Monitoring

Selected

Database Insights (Standard)

### Why?

Provides useful performance metrics.

Enhanced Monitoring is unnecessary for CommerceCore.

---

# 15. Automated Backup

Selected

Enabled

Retention

1 Day

### Why?

AWS Free Plan limits backup retention.

Production systems often retain backups for:

- 7 days
- 14 days
- 30 days

depending on business requirements.

---

# 16. Maintenance

Selected

Automatic Minor Version Upgrade

### Why?

Automatically installs security and bug-fix releases.

Recommended for most projects.

---

# Final Architecture

                Browser
                    │
                    ▼
                 Nginx
                    │
                    ▼
                Gunicorn
                    │
                    ▼
                 Django
                    │
                    ▼
          Amazon RDS (MySQL)

---

# Why Companies Use Amazon RDS

- Managed backups
- Automatic updates
- High availability
- Encryption
- Monitoring
- Scaling
- Reduced maintenance

Developers focus on application development instead of database administration.

---

# Common Mistakes

❌ Choosing Public Access = Yes

❌ Using default database names

❌ Weak passwords

❌ Forgetting backups

❌ Using unsupported MySQL versions

❌ Storing credentials inside source code

---

# Interview Questions

### Why did you choose MySQL?

CommerceCore already uses MySQL, making migration simple while maintaining compatibility with Django.

---

### Why Single-AZ?

Lower cost and sufficient for development.

Production systems usually use Multi-AZ for higher availability.

---

### Why disable Public Access?

Databases should only be reachable from application servers inside the VPC.

---

### Why enable encryption?

To protect stored data and follow security best practices.

---

### Why Amazon RDS instead of MySQL on EC2?

Because AWS manages:

- Backups
- Updates
- Monitoring
- High Availability
- Storage

allowing developers to focus on the application.

---

# Key Takeaways

✔ Created a managed MySQL instance

✔ Understood every configuration option

✔ Followed production-oriented practices

✔ Prepared CommerceCore for migration to Amazon RDS