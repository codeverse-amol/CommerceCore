from celery import shared_task

# @shared_task
# def hello_task():
#     print("Hello from Celery!")


@shared_task
def scheduled_hello_task():
    print("Celery Beat triggered the scheduled task!")