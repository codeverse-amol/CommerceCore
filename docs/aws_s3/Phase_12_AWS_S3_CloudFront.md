# CommerceCore – Phase 12 Documentation - final

Document Version: 1.0

Last Updated:
July 2026

Author:
Amol Bandgar

Project:
CommerceCore


# AWS S3 + CloudFront Integration

**Project:** CommerceCore

**Phase:** 12

**Technology Stack**

- Django
- Python
- MySQL (Amazon RDS)
- Amazon EC2
- Amazon S3
- Amazon CloudFront
- IAM
- django-storages
- boto3

---
CommerceCore/
└── docs/
    └── Phase_12_AWS_S3_CloudFront.md

1. Overview
2. Objectives
3. AWS Services Used
4. Core Concepts
5. Django Configuration
6. Amazon S3 Configuration
7. IAM Configuration
8. CloudFront Configuration
9. Upload Flow
10. Download Flow
11. Request Lifecycle
12. High-Level AWS Architecture
13. Versioning
14. Lifecycle Rules
15. Storage Classes
16. Presigned URLs
17. Cost Optimization
18. Security
19. CommerceCore Implementation Summary
20. Common Troubleshooting
21. Interview Questions (20+)
22. AWS Best Practices (25+)
23. Deployment Checklist
24. Key Learnings
25. Conclusion

---
Prerequisites

- AWS Account

- EC2 Running

- RDS Running

- Django Project

- IAM Access

- Python

- boto3

- django-storages

---
# 1. Overview

## Objective

The objective of Phase 12 is to migrate CommerceCore's media storage from the local EC2 filesystem to Amazon S3 and securely deliver media through Amazon CloudFront.

Instead of storing uploaded product images on the application server, CommerceCore now stores media in a private Amazon S3 bucket while CloudFront acts as the public Content Delivery Network (CDN).

This architecture provides:

- Scalable object storage
- Faster media delivery
- Better security
- Lower operational cost
- High availability
- Separation of application and storage

---

## Why Amazon S3?

Initially Django stores uploaded files inside:

```
MEDIA_ROOT/
```

This works for development but becomes problematic in production because:

- Files are stored on a single EC2 instance.
- Replacing the server may result in data loss.
- Multiple EC2 instances cannot easily share local files.
- Storage is limited by EC2 disk capacity.

Amazon S3 solves these problems by providing highly durable object storage that is independent of the application server.

---

## Why CloudFront?

CloudFront sits in front of Amazon S3 and provides:

- Global Content Delivery Network (CDN)
- Edge caching
- Reduced latency
- Lower S3 request costs
- Secure access through Origin Access Control (OAC)

Instead of every user downloading images directly from S3, CloudFront caches objects at edge locations around the world.

---

# 2. Phase Objectives

At the completion of Phase 12, CommerceCore successfully implements:

- Amazon S3 integration
- Secure IAM authentication
- Django storage backend configuration
- Media uploads to Amazon S3
- CloudFront CDN
- Private S3 bucket
- Origin Access Control (OAC)
- S3 Versioning
- Lifecycle Rules
- Storage Classes
- Presigned URLs
- Cost Optimization
- Production-ready AWS architecture

---

# 3. AWS Services Used

| AWS Service | Purpose |
|-------------|---------|
| Amazon EC2 | Hosts Django application |
| Amazon RDS | Stores relational data |
| Amazon S3 | Stores uploaded media files |
| CloudFront | Content Delivery Network |
| IAM | Secure authentication |
| Origin Access Control | Allows CloudFront to securely access S3 |

---

## Responsibility of Each Service

### Amazon EC2

Runs:

- Ubuntu
- Python
- Django
- Gunicorn
- Nginx

Purpose:

Host the application.

---

### Amazon RDS

Stores:

- Users
- Products
- Orders
- Categories
- Cart
- Image paths

Does NOT store:

- Images
- Videos
- Documents

---

### Amazon S3

Stores:

- Product images
- User uploaded files
- Documents
- Media assets

Purpose:

Durable object storage.

---

### CloudFront

Provides:

- Image caching
- Global delivery
- HTTPS delivery
- Reduced S3 requests

---

### IAM

Provides:

- Authentication
- Authorization
- Least privilege access

---

### Origin Access Control (OAC)

Allows:

CloudFront

↓

Private S3

Without making the bucket public.

---

# 4. Core Concepts

Before implementing Amazon S3, it is important to understand the following concepts.

---

## Object Storage

Amazon S3 is an Object Storage service.

Every uploaded file becomes an Object.

Example:

```
products/alienware.webp
```

Each object contains:

- Object Key
- File Content
- Metadata
- Storage Class
- Version ID (if enabled)

---

## Bucket

A Bucket is a container that stores objects.

Example:

```
commercecore-media
```

Inside the bucket:

```
commercecore-media

↓

products/

↓

alienware.webp

↓

iphone.webp

↓

samsung.webp
```

---

## Object Key

The object key is the unique identifier inside a bucket.

Example:

```
products/alienware.webp
```

Notice:

This is NOT a folder.

Amazon S3 uses prefixes to organize objects.

---

## Static Files vs Media Files

| Static Files | Media Files |
|--------------|-------------|
| CSS | Product Images |
| JavaScript | User Uploads |
| Django Admin CSS | Documents |
| Fonts | Avatars |

Static files belong to the application.

Media files are uploaded while the application is running.

CommerceCore currently stores only media files in S3.

---

## Why Images Are Not Stored in MySQL

CommerceCore stores:

```
products/alienware.webp
```

inside MySQL.

The actual binary image is stored in S3.

Benefits:

- Smaller database
- Better performance
- Easier backups
- Better scalability

---

# 5. Amazon S3 Configuration

The following configuration was completed during Phase 12.

---

## Bucket

Bucket Name

```
commercecore-media
```

---

## Region

Same region as:

- EC2
- RDS

Benefits:

- Lower latency
- Lower data transfer cost

---

## Block Public Access

Enabled.

Purpose:

Prevent accidental public access.

---

## Object Ownership

Configured:

Bucket Owner Enforced

Purpose:

Disable ACLs.

Access is controlled entirely through IAM policies.

---

## Default Encryption

Enabled.

Purpose:

Encrypt objects stored in Amazon S3.

---

## Versioning

Enabled.

Purpose:

Recover:

- Deleted objects
- Overwritten objects

---

# 6. IAM Configuration

CommerceCore uses a dedicated IAM User.

Root account credentials are never used by the application.

---

## IAM Policy

Configured using Least Privilege.

Permissions include:

- GetObject
- PutObject
- DeleteObject
- ListBucket

Only the CommerceCore bucket is accessible.

---

## Credentials

Stored inside:

```
.env
```

Variables:

```
AWS_ACCESS_KEY_ID

AWS_SECRET_ACCESS_KEY

AWS_STORAGE_BUCKET_NAME

AWS_S3_REGION_NAME
```

Purpose:

Secure communication between Django and Amazon S3.

---

## Why Least Privilege?

If credentials are compromised, the attacker can only access the required bucket instead of the entire AWS account.

---

# 7. Django Integration

CommerceCore integrates Amazon S3 using:

```
django-storages

boto3
```

---

## Installed Packages

```
pip install django-storages

pip install boto3
```

---

## Storage Backend

```python
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    }
}
```

Purpose:

Replace local filesystem storage with Amazon S3.

---

## Environment Variables

```
AWS_ACCESS_KEY_ID

AWS_SECRET_ACCESS_KEY

AWS_STORAGE_BUCKET_NAME

AWS_S3_REGION_NAME
```

---

## CloudFront Domain

```
AWS_S3_CUSTOM_DOMAIN
```

Used for generating image URLs.

Example:

```
https://d3mwhkx1k5fsh6.cloudfront.net/products/alienware.webp
```

---

## File Overwrite

```
AWS_S3_FILE_OVERWRITE=False
```

Purpose:

Every upload receives a unique filename.

Benefits:

- No accidental overwrite
- Better CloudFront caching
- No cache invalidation

---

## Upload Directory

```
products/
```

Configured using:

```python
upload_to="products/"
```

---

# 8. CloudFront Configuration

CloudFront sits between the browser and Amazon S3.

Architecture:

```
Browser

↓

CloudFront

↓

Origin Access Control

↓

Private S3 Bucket
```

---

## Why CloudFront?

Without CloudFront:

```
Browser

↓

S3
```

Problems:

- Higher latency
- More S3 requests
- No CDN

---

With CloudFront:

```
Browser

↓

Nearest Edge Location

↓

Private S3
```

Benefits:

- Lower latency
- Better performance
- Lower cost
- Global availability

---

## Origin Access Control (OAC)

CommerceCore uses:

Origin Access Control

instead of a public bucket.

Flow:

```
CloudFront

↓

Authenticated AWS Request

↓

Private S3
```

Direct access:

```
https://bucket.s3.amazonaws.com/file.webp
```

Result:

```
AccessDenied
```

CloudFront access:

```
https://d3mwhkx1k5fsh6.cloudfront.net/file.webp
```

Result:

```
Image Loaded Successfully
```

---

## CloudFront Caching

When a user requests an image:

### Cache Hit

```
Browser

↓

CloudFront

↓

Cached Image

↓

Browser
```

No request reaches Amazon S3.

---

### Cache Miss

```
Browser

↓

CloudFront

↓

Private S3

↓

CloudFront Cache

↓

Browser
```

Future users receive the cached image.

---

# 9. Upload Flow

When an administrator uploads a product image through Django Admin or any product management page, the file is stored directly in Amazon S3 instead of the EC2 server.

---

## Upload Pipeline

```
Admin/User

↓

Django Form

↓

ImageField

↓

django-storages

↓

boto3

↓

Amazon S3

↓

Object Key Returned

↓

MySQL (Amazon RDS)
```

---

## Step-by-Step Upload Flow

### Step 1

The administrator selects an image.

Example:

```
alienware.webp
```

---

### Step 2

The browser sends the image as part of the HTTP request.

```
multipart/form-data
```

---

### Step 3

Django receives:

```python
request.FILES
```

The uploaded file is assigned to:

```python
product.image
```

---

### Step 4

Since CommerceCore uses:

```python
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    }
}
```

Django does NOT save the image locally.

Instead it calls:

```
django-storages
```

---

### Step 5

django-storages internally uses:

```
boto3
```

to execute:

```
PutObject
```

against Amazon S3.

---

### Step 6

Amazon S3 stores:

```
products/alienware.webp
```

---

### Step 7

Amazon S3 returns:

```
Object Key
```

Example:

```
products/alienware.webp
```

---

### Step 8

Django stores only the object key inside MySQL.

```
Product

id

title

price

image

↓

products/alienware.webp
```

No image binary is stored in the database.

---

## Upload Summary

```
Browser

↓

Django

↓

django-storages

↓

boto3

↓

Amazon S3

↓

MySQL stores object key
```

---

# 10. Download Flow

Displaying an image is completely different from uploading it.

Django does NOT download the image.

Instead, Django generates the image URL.

---

## Image URL

When the template contains:

```django
{{ product.image.url }}
```

django-storages generates:

```
https://d3mwhkx1k5fsh6.cloudfront.net/products/alienware.webp
```

---

## Browser Flow

```
Browser

↓

CloudFront

↓

Cache?

↓

Yes

↓

Return Cached Image

OR

↓

Private S3

↓

Return Image

↓

CloudFront Cache

↓

Browser
```

---

## Cache Hit

When the image already exists inside the CloudFront edge cache:

```
Browser

↓

CloudFront

↓

Image Returned
```

Advantages:

- Very fast
- No S3 request
- Lower cost

---

## Cache Miss

When the image is requested for the first time:

```
Browser

↓

CloudFront

↓

Private S3

↓

Image Downloaded

↓

Cached

↓

Browser
```

Future requests become Cache Hits.

---

## Why CloudFront?

Without CloudFront:

```
Browser

↓

Amazon S3
```

Every request reaches Amazon S3.

---

With CloudFront:

```
Browser

↓

Nearest Edge Location

↓

Private S3 (only once)
```

This significantly reduces latency.

---

# 11. Complete Request Lifecycle

When a customer opens a product page, two independent request flows occur.

---

## Flow 1 — HTML Request

```
Browser

↓

Nginx

↓

Gunicorn

↓

Django

↓

Amazon RDS

↓

HTML Response

↓

Browser
```

Django generates the HTML page.

---

## Flow 2 — Image Request

After receiving HTML:

Browser discovers:

```html
<img src="https://d3mwhkx1k5fsh6.cloudfront.net/products/alienware.webp">
```

Now a second request begins.

```
Browser

↓

CloudFront

↓

Private S3

↓

Browser
```

Notice:

The browser does NOT ask Django for the image.

---

## Complete Lifecycle

```
Customer

↓

Browser

↓

Nginx

↓

Gunicorn

↓

Django

↓

Amazon RDS

↓

HTML

↓

Browser

↓

CloudFront

↓

Private S3

↓

Browser
```

Application requests and media requests are completely separate.

---

# 12. High-Level AWS Architecture

CommerceCore follows a layered architecture.

```
                    Internet

                        │

                        ▼

                 Customer Browser

                        │

                        ▼

                 CloudFront CDN

              ┌─────────┴─────────┐

              │                   │

              ▼                   ▼

      Nginx + Gunicorn       Private S3 Bucket

              │                   ▲

              ▼                   │

            Django          django-storages

              │

              ▼

         Amazon RDS
```

---

## Responsibilities

| Component | Responsibility |
|------------|----------------|
| Browser | User Interface |
| CloudFront | CDN |
| Nginx | Reverse Proxy |
| Gunicorn | WSGI Server |
| Django | Business Logic |
| Amazon RDS | Relational Database |
| Amazon S3 | Object Storage |

---

## Why Separate Services?

Each AWS service specializes in one responsibility.

Benefits:

- Easier scaling
- Better reliability
- Better maintenance
- Better security

---

# 13. Versioning

Amazon S3 Versioning allows multiple versions of the same object.

CommerceCore enables Versioning on the media bucket.

---

## Why Versioning?

Suppose:

```
products/laptop.webp
```

is accidentally deleted.

Without Versioning:

Image is permanently lost.

---

With Versioning:

Amazon S3 stores:

```
Version 1

↓

Version 2

↓

Version 3
```

Any version can be restored.

---

## Benefits

- Recover deleted objects
- Recover overwritten objects
- Maintain object history
- Safer deployments

---

## CommerceCore Configuration

```
Versioning

↓

Enabled
```

---

## Relationship with Django

CommerceCore also uses:

```
AWS_S3_FILE_OVERWRITE=False
```

This generates unique filenames.

Versioning provides an additional safety layer if an object is overwritten or deleted outside the application's normal workflow.

---

# 14. Lifecycle Rules

Lifecycle Rules automatically move objects between storage classes or delete old data.

---

## CommerceCore Lifecycle

```
30 Days

↓

Standard-IA
```

---

## Why?

Recently uploaded images are frequently accessed.

Older images receive fewer requests.

Keeping them in Standard Storage increases costs unnecessarily.

---

## Lifecycle Example

```
Day 1

↓

S3 Standard

↓

30 Days

↓

Standard IA
```

---

## Benefits

- Lower storage costs
- Automatic management
- No application changes required

---

# 15. Storage Classes

Amazon S3 provides multiple storage classes.

---

| Storage Class | Purpose |
|---------------|---------|
| Standard | Frequently accessed objects |
| Standard-IA | Infrequently accessed objects |
| One Zone-IA | Lower-cost single Availability Zone storage |
| Intelligent-Tiering | Automatically optimizes storage tier |
| Glacier Instant Retrieval | Archived data with quick retrieval |
| Glacier Flexible Retrieval | Long-term archive |
| Glacier Deep Archive | Lowest-cost archival storage |

---

## CommerceCore

Currently uses:

```
S3 Standard

↓

Standard IA
```

Future enhancements could use Intelligent-Tiering if object access patterns become unpredictable.

---

# 16. Presigned URLs

A Presigned URL allows temporary access to a private S3 object.

The bucket remains private.

Only users with the generated URL can access the object until it expires.

---

## Use Cases

- Invoice download
- Medical reports
- Private documents
- Temporary file sharing

---

## Flow

```
User

↓

Django

↓

boto3

↓

Generate Presigned URL

↓

Temporary URL

↓

User Downloads File
```

---

## Expiration

Example:

```
5 Minutes

10 Minutes

1 Hour
```

After expiration:

```
Access Denied
```

---

## CommerceCore

Product images are delivered using CloudFront.

Presigned URLs are not required for public product images.

However, they are useful for future features involving private customer documents or secure file downloads.

---

# 17. Cost Optimization

Amazon S3 and CloudFront provide several features that help reduce storage and data transfer costs without changing application code.

---

## 17.1 Lifecycle Rules

CommerceCore uses Lifecycle Rules to automatically transition older objects to a lower-cost storage class.

Current Lifecycle:

```
Day 0 - Day 30

↓

S3 Standard

↓

After 30 Days

↓

S3 Standard-IA
```

Benefits:

- Lower storage cost
- Automatic management
- No application changes
- Better long-term cost optimization

---

## 17.2 CloudFront Caching

Without CloudFront:

```
Browser

↓

Amazon S3
```

Every request reaches Amazon S3.

With CloudFront:

```
Browser

↓

Nearest Edge Location

↓

Cached Image
```

Benefits:

- Fewer S3 requests
- Lower bandwidth cost
- Lower latency
- Better user experience

---

## 17.3 Unique File Names

CommerceCore uses:

```python
AWS_S3_FILE_OVERWRITE = False
```

Benefits:

- Prevent accidental overwrite
- Avoid CloudFront cache invalidation
- Better cache utilization

---

## 17.4 Storage Classes

Older files move automatically from:

```
S3 Standard

↓

S3 Standard-IA
```

This reduces monthly storage cost.

---

## 17.5 Recommended Cost Practices

- Enable Lifecycle Rules
- Use CloudFront
- Remove unused objects
- Monitor AWS Cost Explorer
- Configure AWS Budgets
- Avoid unnecessary cache invalidations
- Store only required media

---

# 18. Security

Security is one of the most important parts of any production deployment.

CommerceCore follows AWS security best practices.

---

## 18.1 Private S3 Bucket

Bucket Visibility

```
Private
```

Direct access:

```
https://bucket.s3.amazonaws.com/image.webp
```

Result:

```
AccessDenied
```

---

## 18.2 IAM Least Privilege

The application receives only the permissions it requires.

Allowed:

- GetObject
- PutObject
- DeleteObject
- ListBucket

Nothing else.

---

## 18.3 Environment Variables

Sensitive values are never stored inside source code.

Stored inside:

```
.env
```

Examples:

```
AWS_ACCESS_KEY_ID

AWS_SECRET_ACCESS_KEY

AWS_STORAGE_BUCKET_NAME
```

---

## 18.4 Block Public Access

Enabled.

Purpose:

Prevent accidental exposure of objects.

---

## 18.5 Object Encryption

Default encryption enabled.

Benefits:

- Secure storage
- Compliance
- Data protection

---

## 18.6 CloudFront + OAC

Only CloudFront can access S3.

Users cannot directly access the bucket.

```
Browser

↓

CloudFront

↓

Private Bucket
```

---

# 19. CommerceCore Implementation Summary

The following AWS components were successfully implemented.

| Feature | Status |
|----------|--------|
| Amazon S3 | ✅ |
| IAM User | ✅ |
| Least Privilege Policy | ✅ |
| django-storages | ✅ |
| boto3 | ✅ |
| Private Bucket | ✅ |
| Block Public Access | ✅ |
| Versioning | ✅ |
| Lifecycle Rule | ✅ |
| CloudFront | ✅ |
| Origin Access Control | ✅ |
| Upload Verification | ✅ |
| Download Verification | ✅ |

---

## Final Production Architecture

```
Customer

↓

Browser

↓

CloudFront

↓

Private S3

↑

django-storages

↓

Django

↓

Amazon RDS
```

---

# 20. Common Troubleshooting

| Problem | Possible Cause | Solution |
|----------|----------------|----------|
| AccessDenied | Bucket Policy | Verify OAC and Bucket Policy |
| SignatureDoesNotMatch | Wrong Credentials | Verify IAM Keys |
| InvalidAccessKeyId | Incorrect Access Key | Generate new credentials |
| NoSuchBucket | Wrong Bucket Name | Verify bucket configuration |
| Image Upload Fails | IAM Permission Missing | Check PutObject permission |
| Images Stored Locally | Wrong Storage Backend | Verify STORAGES configuration |
| CloudFront Returns Old Image | Cached Object | Invalidate cache or use unique filename |
| 403 from CloudFront | Missing OAC Policy | Update bucket policy |
| Wrong Region Error | Region mismatch | Verify AWS_S3_REGION_NAME |
| Environment Changes Not Working | Gunicorn not restarted | Restart Gunicorn service |
| Images Not Displayed | Wrong CloudFront Domain | Verify AWS_S3_CUSTOM_DOMAIN |
| Media URL Incorrect | Configuration Error | Verify MEDIA_URL |

---

## Debug Commands

Restart Gunicorn

```bash
sudo systemctl restart gunicorn
```

Restart Nginx

```bash
sudo systemctl restart nginx
```

Check Gunicorn Logs

```bash
sudo journalctl -u gunicorn -f
```

List S3 Objects

```bash
aws s3 ls s3://commercecore-media --recursive
```

---

# 21. Interview Questions

## Q1. Why use Amazon S3?

To store uploaded files separately from the application server, providing scalable and durable object storage.

---

## Q2. Why not store images on EC2?

EC2 storage is tied to the server instance and does not scale well. S3 provides persistent, shared object storage.

---

## Q3. Why CloudFront?

To cache content globally, reduce latency, reduce S3 requests, and improve performance.

---

## Q4. Why keep S3 private?

To prevent direct public access and improve security.

---

## Q5. What is Origin Access Control (OAC)?

OAC allows CloudFront to securely access a private S3 bucket without making the bucket public.

---

## Q6. What is IAM?

IAM controls authentication and authorization for AWS resources.

---

## Q7. What is Least Privilege?

Grant only the permissions required to perform specific tasks.

---

## Q8. What is django-storages?

A Django storage backend that allows FileField and ImageField to use Amazon S3 instead of the local filesystem.

---

## Q9. What is boto3?

The official AWS SDK for Python used to communicate with AWS services.

---

## Q10. What does STORAGES do?

It configures Django's storage backend for uploaded files.

---

## Q11. What is Versioning?

Versioning keeps multiple versions of an object, allowing recovery from accidental deletion or overwrite.

---

## Q12. What are Lifecycle Rules?

Rules that automatically transition or delete objects to reduce storage costs.

---

## Q13. What are Storage Classes?

Different storage tiers optimized for different access patterns and costs.

---

## Q14. What is a Presigned URL?

A temporary URL that grants time-limited access to a private S3 object.

---

## Q15. Explain Upload Flow.

Browser → Django → django-storages → boto3 → Amazon S3 → Object Key stored in MySQL.

---

## Q16. Explain Download Flow.

Browser → CloudFront → Private S3 → Browser.

---

## Q17. Why AWS_S3_FILE_OVERWRITE=False?

To generate unique filenames and avoid overwriting existing files.

---

## Q18. Why store only image paths in MySQL?

Databases are optimized for structured data, while S3 is designed for binary object storage.

---

## Q19. Difference between Static Files and Media Files?

Static files are part of the application; media files are uploaded during runtime.

---

## Q20. Explain CommerceCore AWS Architecture.

EC2 hosts Django, RDS stores relational data, S3 stores media, CloudFront delivers media globally, IAM secures access, and OAC connects CloudFront to the private S3 bucket.

---

# 22. AWS Best Practices

## Security

- Use Private S3 Buckets
- Enable Block Public Access
- Enable Default Encryption
- Use IAM Least Privilege
- Never use Root Credentials
- Store credentials in Environment Variables
- Rotate Access Keys periodically
- Prefer IAM Roles over long-term access keys when possible

---

## Performance

- Use CloudFront
- Enable Browser Caching
- Enable Cache-Control headers
- Use unique filenames
- Keep images optimized
- Compress images before upload

---

## Cost Optimization

- Enable Lifecycle Rules
- Use Storage Classes
- Delete unused files
- Use CloudFront caching
- Configure AWS Budgets
- Monitor Cost Explorer

---

## Django Best Practices

- Use django-storages
- Use boto3
- Separate production settings
- Keep MEDIA_ROOT unused in production
- Store only object keys in the database
- Restart Gunicorn after environment changes

---

# 23. Deployment Checklist

Before deploying to production:

- [ ] Bucket created
- [ ] Correct AWS region
- [ ] Bucket is private
- [ ] Block Public Access enabled
- [ ] Default encryption enabled
- [ ] Versioning enabled
- [ ] Lifecycle Rule configured
- [ ] IAM policy verified
- [ ] Credentials stored in `.env`
- [ ] django-storages installed
- [ ] boto3 installed
- [ ] STORAGES configured
- [ ] MEDIA_URL configured
- [ ] CloudFront Distribution created
- [ ] Origin Access Control configured
- [ ] Bucket Policy updated
- [ ] Upload verified
- [ ] Download verified
- [ ] Gunicorn restarted
- [ ] Nginx restarted

---

# 24. Key Learnings

During Phase 12, the following concepts were learned and implemented:

- Amazon S3 Object Storage
- Object Keys
- Buckets
- IAM
- Least Privilege
- django-storages
- boto3
- CloudFront
- Origin Access Control
- Versioning
- Lifecycle Rules
- Storage Classes
- Presigned URLs
- Cost Optimization
- Secure Media Delivery
- Upload Flow
- Download Flow
- Request Lifecycle
- High-Level AWS Architecture

---

# Phase Summary

During Phase 12, CommerceCore successfully migrated media storage from the local EC2 filesystem to Amazon S3. CloudFront was introduced to improve global content delivery, while IAM, Origin Access Control (OAC), and a private S3 bucket ensured secure access. Additional AWS features such as Versioning, Lifecycle Rules, and Storage Classes were configured to improve reliability and optimize storage costs.

This phase established a scalable, secure, and production-ready media storage architecture aligned with AWS best practices.

---

# 25. Conclusion

Phase 12 successfully transformed CommerceCore from using local media storage to a production-ready cloud architecture based on Amazon Web Services.

Media files are now stored securely in a private Amazon S3 bucket, while CloudFront delivers content globally with low latency and high performance. Security is enforced through IAM, Origin Access Control, Block Public Access, and encryption. Operational efficiency is improved with Versioning, Lifecycle Rules, and CloudFront caching.

This architecture separates application logic, database storage, and media storage into dedicated services, making CommerceCore more scalable, maintainable, secure, and aligned with modern cloud-native best practices.

---

# Phase 12 Completion Status

| Task | Status |
|------|--------|
| Amazon S3 Integration | ✅ |
| IAM Configuration | ✅ |
| Django Storage Backend | ✅ |
| Media Upload to S3 | ✅ |
| CloudFront CDN | ✅ |
| Origin Access Control | ✅ |
| Private Bucket | ✅ |
| Versioning | ✅ |
| Lifecycle Rules | ✅ |
| Storage Classes | ✅ |
| Presigned URLs | ✅ |
| Upload Flow | ✅ |
| Download Flow | ✅ |
| Request Lifecycle | ✅ |
| AWS Architecture | ✅ |
| Cost Optimization | ✅ |
| Security Best Practices | ✅ |
| Interview Preparation | ✅ |
| Troubleshooting Guide | ✅ |
| Deployment Checklist | ✅ |

---

**End of Phase 12 Documentation**
