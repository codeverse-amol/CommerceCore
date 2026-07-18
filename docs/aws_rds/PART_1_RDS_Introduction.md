# Phase 11 – Part 1: Introduction to Amazon RDS

## Objective

Understand what **Amazon RDS (Relational Database Service)** is, why organizations use it in production, how it improves the CommerceCore architecture, and the fundamentals of **pricing, security, and networking**.

---

# What is Amazon RDS?

**Amazon RDS (Relational Database Service)** is a **fully managed relational database service** provided by AWS.

Instead of installing, configuring, updating, and maintaining a database server yourself, AWS manages the database infrastructure while developers focus on building applications.

Amazon RDS supports several relational database engines:

- MySQL
- PostgreSQL
- MariaDB
- Oracle
- Microsoft SQL Server

For **CommerceCore**, we'll use **MySQL**.

---

# Why Companies Use Amazon RDS

In traditional deployments, developers are responsible for database administration tasks such as:

- Installing MySQL
- Configuring the server
- Applying OS and database patches
- Taking backups
- Monitoring health
- Managing storage
- Recovering from failures

Amazon RDS automates these responsibilities.

AWS manages:

- MySQL installation
- Operating system maintenance
- Security patches
- Automatic backups
- Storage management
- Performance monitoring
- Failure recovery

Developers continue managing:

- Database schema
- Tables
- SQL queries
- Django models
- Migrations
- Application logic

---

# CommerceCore Architecture

## Current Architecture

```text
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
MySQL (EC2)
```

Everything runs on a single EC2 instance.

## Production Architecture

```text
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
```

Benefits:

- Better scalability
- Better reliability
- Easier maintenance
- Managed backups
- High availability
- Improved security

---

# MySQL on EC2 vs Amazon RDS

| MySQL on EC2 | Amazon RDS |
|--------------|------------|
| Install MySQL manually | AWS manages installation |
| Manual configuration | Managed configuration |
| Manual backups | Automated backups |
| Manual patching | Automatic maintenance |
| Database shares EC2 resources | Dedicated managed database |
| Manual monitoring | Built-in monitoring |
| Harder to scale | Easy scaling |

---

# Request Flow

```text
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
Amazon RDS
    │
    ▼
Response
```

Only Django communicates with the database.

---

# What Changes in Django?

Before:

```env
DB_HOST=localhost
```

After:

```env
DB_HOST=mydb.xxxxxxxxx.ap-south-1.rds.amazonaws.com
```

Everything else remains unchanged:

- Models
- ORM
- Migrations
- SQL Queries
- Business Logic

---

# Pricing Overview

Amazon RDS uses **pay-as-you-go** pricing.

## Cost Factors

| Component | Description |
|-----------|-------------|
| DB Instance | Compute (vCPU & RAM) |
| Storage | SSD storage |
| Backup Storage | Automated backups & snapshots |
| Data Transfer | Charges may apply depending on traffic |

Choose the smallest suitable instance for learning projects.

> **Best Practice:** Stop or delete unused RDS instances to avoid unnecessary charges.

---

# Security

## 1. Security Groups

Acts as a firewall.

```text
Internet
     │
     ▼
    EC2
     │
     ▼
RDS Security Group
     │
     ▼
Amazon RDS
```

Only EC2 is allowed to connect to MySQL (port 3306).

## 2. Encryption

RDS supports encryption for:

- Database storage
- Automated backups
- Snapshots
- Read replicas

## 3. IAM Integration

IAM controls who can manage RDS resources.

| User | Permission |
|------|------------|
| AWS Administrator | Manage RDS |
| Django Application | Connect using MySQL credentials |

---

# Networking

## VPC

Every RDS instance runs inside a Virtual Private Cloud.

```text
AWS Account
    │
    ▼
   VPC
    │
    ├── EC2
    └── Amazon RDS
```

## DB Subnet Group

```text
VPC
 │
 ├── Subnet A
 ├── Subnet B
 └── Subnet C

        │
        ▼

 DB Subnet Group

        │
        ▼

 Amazon RDS
```

Used for availability and failover.

## Public vs Private Access

### Public (Not Recommended)

```text
Internet
     │
     ▼
Amazon RDS
```

### Private (Recommended)

```text
Internet
     │
     ▼
    EC2
     │
     ▼
Amazon RDS
```

---

# Real-World Use Cases

## E-Commerce

- Products
- Customers
- Orders
- Inventory

## Banking

- Customer Accounts
- Transactions
- Loan Records

## SaaS

- User Profiles
- Billing
- Reports
- Analytics

---

# Advantages

- Managed MySQL
- Automated Backups
- Automatic Patching
- Monitoring
- Easy Scaling
- High Availability
- Read Replicas
- Better Security
- Lower Maintenance

---

# Key Concepts

| Concept | Description |
|----------|-------------|
| RDS Endpoint | Database hostname used by Django |
| Security Group | Firewall for database access |
| Automated Backups | Scheduled backups managed by AWS |
| Multi-AZ | High availability |
| Read Replica | Scale read traffic |
| VPC | Private AWS network |
| DB Subnet Group | Subnets where RDS runs |
| IAM | AWS resource permissions |
| Encryption | Protects stored data |

---

# Interview Questions

### 1. What is Amazon RDS?

Amazon RDS is a fully managed relational database service that automates installation, backups, monitoring, patching, storage management, and recovery.

### 2. Why use Amazon RDS instead of MySQL on EC2?

- Managed service
- Automatic backups
- Easier maintenance
- Better reliability
- Easier scaling
- Production-ready

### 3. Did your Django code change after moving to RDS?

No. Only the `DB_HOST` changed to the RDS endpoint.

### 4. Can users access Amazon RDS directly?

No. Only the Django application running on EC2 can connect through Security Groups.

### 5. What is a DB Subnet Group?

A collection of subnets where Amazon RDS instances are deployed for high availability.

### 6. IAM vs MySQL Users?

IAM manages AWS resources. MySQL users manage database access.

### 7. Why keep RDS private?

To prevent direct internet access and improve security.

---

# CommerceCore Takeaway

## Current

```text
EC2
├── Django
├── Gunicorn
├── Nginx
└── MySQL
```

## Production

```text
EC2
├── Django
├── Gunicorn
└── Nginx
        │
        ▼
Amazon RDS (MySQL)
```

This architecture is secure, scalable, maintainable, and production-ready.
