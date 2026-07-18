# Phase 11 - Part 3: Security Groups

## Objective

Understand how Amazon EC2 communicates securely with Amazon RDS using Security Groups.

---

# What is a Security Group?

A Security Group acts as a virtual firewall.

It controls

- Incoming traffic (Inbound)
- Outgoing traffic (Outbound)

Every EC2 and RDS instance is protected by one or more Security Groups.

---

# CommerceCore Network Architecture

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
         EC2 Security Group
                    │
            TCP Port 3306
                    │
                    ▼
        RDS Security Group
                    │
                    ▼
             Amazon RDS

Only EC2 can communicate with RDS.

---

# VPC

Virtual Private Cloud (VPC)

Selected

Default VPC

Purpose

Provides a private network where EC2 and RDS can communicate securely.

Resources inside the same VPC communicate using private IP addresses.

---

# EC2 Security Group

Name

launch-wizard-3

Responsibilities

- SSH (22)
- HTTP (80)
- Django/Application traffic
- Communication with Amazon RDS

---

# RDS Security Group

Created

commercecore-rds-sg

Purpose

Protect only the database.

Dedicated Security Groups are preferred over using the default Security Group.

---

# Port 3306

MySQL communicates using

TCP Port 3306

Diagram

EC2

↓

3306

↓

Amazon RDS

No other ports are required.

---

# Inbound Rule

Configured

Type

MySQL/Aurora

Protocol

TCP

Port

3306

Source

launch-wizard-3

Diagram

launch-wizard-3

↓

TCP 3306

↓

commercecore-rds-sg

Only EC2 instances attached to launch-wizard-3 may access the database.

---

# Outbound Rule

Default

Allow All Outbound

This is sufficient for CommerceCore.

---

# Why Not 0.0.0.0/0?

Never expose MySQL to the Internet.

Wrong

Internet

↓

MySQL

Correct

Internet

↓

EC2

↓

Amazon RDS

Only application servers should communicate with databases.

---

# Private Connectivity

The connection never leaves AWS.

Browser

↓

EC2

↓

Private AWS Network

↓

Amazon RDS

Benefits

- Lower latency
- Better security
- No public database endpoint required

---

# Security Flow

User

↓

HTTP

↓

EC2 Security Group

↓

Django

↓

TCP 3306

↓

RDS Security Group

↓

Amazon RDS

Every request passes through multiple security layers.

---

# Production Best Practices

✔ Separate Security Groups

✔ Private Database

✔ Allow only Port 3306

✔ Restrict Source to EC2 Security Group

✔ Never allow public MySQL access

✔ Keep database inside the VPC

---

# Common Mistakes

❌ Using the default Security Group for everything

❌ Opening MySQL to the Internet

❌ Allowing all ports

❌ Placing EC2 and RDS in different VPCs

❌ Forgetting Security Group rules

---

# Interview Questions

### Why create a separate RDS Security Group?

It isolates database access and follows the principle of least privilege.

---

### Why use Port 3306?

3306 is the default TCP port for MySQL.

---

### Why use the EC2 Security Group as the source?

Only trusted EC2 instances can connect to the database.

---

### Why disable Public Access?

Databases should never be directly accessible from the Internet.

---

### How does EC2 communicate with RDS?

EC2 connects over the private AWS network inside the same VPC through Security Group rules allowing TCP port 3306.

---

# Key Takeaways

✔ Understood VPC networking

✔ Created a dedicated RDS Security Group

✔ Configured secure inbound rules

✔ Enabled private communication between EC2 and RDS

✔ Followed production security best practices