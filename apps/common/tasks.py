from celery import shared_task




# Background Processing Patterns
# 1. retry

@shared_task(bind=True, max_retries=3)
def retry_demo(self):
    print("Executing retry_demo")

    try:
        raise Exception("Demo failure")

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)


# Restart Celery worker: celery -A core worker -l INFO --pool=solo

# Open another terminal and run: python manage.py shell

# Then:
# from apps.common.tasks import retry_demo
# retry_demo.delay()


# 2. countdown
@shared_task
def countdown_demo():
    print("Countdown task executed!")    

# Then restart your worker.

# From Django shell: from apps.common.tasks import countdown_demo

# Now execute: countdown_demo.apply_async(countdown=10)

# 3. ETA - Execute at a Specific Time
@shared_task
def eta_demo():
    print("ETA task executed!")    
# Then restart your worker.
# Then open Django shell: python manage.py shell
# Import it:
# from apps.common.tasks import eta_demo

# Now schedule it 10 seconds from now:
# from datetime import datetime, timedelta

# eta_time = datetime.now() + timedelta(seconds=10)
# eta_demo.apply_async(eta=eta_time)



# 4. Delay
@shared_task
def order_demo(order_id):
    print(f"Processing order {order_id}")

# You can do in shell:
# order_demo.delay(81)

# .delay() vs .apply_async()

# |     Method       |           Purpose          |
# |------------------|----------------------------|
# | `.delay()`       | Simple task execution      |
# | `.apply_async()` | Advanced task execution    |
# | `countdown`      | Execute after a delay      |
# | `eta`            | Execute at a specific time |

# Example
# Simple .delay():
# send_email.delay(order_id)

# With countdown:
# send_email.apply_async(
#     args=[order_id],
#     countdown=30,
# )

# With ETA:
# send_email.apply_async(
#     args=[order_id],
#     eta=some_datetime,
# )


# 5. Task Chaining
@shared_task
def chain_step_one():
    print("Step 1: Create order")
    return "order-created"


@shared_task
def chain_step_two(result):
    print(f"Step 2: Process payment for {result}")
    return "payment-completed"


@shared_task
def chain_step_three(result):
    print(f"Step 3: Send email after {result}")



# Then in Django shell:
# from celery import chain
# from apps.common.tasks import (
#     chain_step_one,
#     chain_step_two,
#     chain_step_three,
# )

# Run:
# workflow = chain(
#     chain_step_one.s(),
#     chain_step_two.s(),
#     chain_step_three.s(),
# )

# Finally:
# workflow.delay()

# Why .s()?
# This:
# chain_step_one.s()
# creates a signature describing how Celery should execute the task.

# Then:
# workflow.delay()
# actually sends the complete chain to Celery.



# 6. Error Handling
# Retry vs Error Handling
# Task fails
#    │
#    ├── Retry configured?
#    │       │
#    │       └── Yes → try task again
#    │
#    └── Eventually fails
#            │
#            └── Error handling → log / notify / cleanup / record failure



@shared_task
def error_handling_demo():
    try:
        print("Starting task...")

        # Simulate an error
        result = 10 / 0

        print(f"Result: {result}")

    except Exception as e:
        print(f"Task failed: {e}")
        return "Task handled successfully"




# This is much closer to how real background-processing systems work.

# Payment task
#      ↓
# Payment provider unavailable
#      ↓
# Retry after 5 sec
#      ↓
# Try again
#      ↓
# Try again
#      ↓
# 3 retries exhausted
#      ↓
# Task permanently fails
#      ↓
# Error handling / monitoring