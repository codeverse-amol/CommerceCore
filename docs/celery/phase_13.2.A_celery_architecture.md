# Celery Architecture

Reference notes for introducing Celery into CommerceCore — a Django + Redis stack that has not used a task queue before.

## What is Celery?

Celery is a distributed task queue: a system for taking work out of the HTTP request/response cycle and running it in the background. Django hands off a unit of work, Redis carries the message, and a separate worker process actually runs the code.

```
Django
   ↓
Redis
   ↓
Celery Worker
```

That three-line diagram is the entire mental model. Everything below is just naming and detailing each link in that chain.

## Producer

The producer is whatever creates and sends a task — in CommerceCore, that's Django. A view or signal handler decides "this doesn't need to block the response" and hands the work off instead of running it inline.

```python
# inside a Django view, after the order is saved
send_order_confirmation_email.delay(order_id=101)
```

Django's job ends there. It doesn't wait for the email to send.

## Task

A task is a registered Python function, plus the arguments it needs to run:

```
Task:      send_order_confirmation_email
Arguments: order_id = 101
```

```python
# commercecore/tasks.py
@app.task(bind=True, max_retries=3)
def send_order_confirmation_email(self, order_id):
    ...
```

Calling `.delay(...)` (or `.apply_async(...)`) doesn't run this function — it serializes the task name and arguments into a message and sends that message to the broker.

## Broker

The broker is the transport layer between producer and worker. In CommerceCore, that's Redis.

```
Django
  │  task message
  ▼
Redis Broker
  │  task message
  ▼
Celery Worker
```

The broker's only job is to hold and move messages — it does not run any code. Nothing about Redis knows how to execute `send_order_confirmation_email()`; it just knows how to store the message until a worker asks for it.

## Queue

A queue is where task messages sit inside the broker, waiting to be picked up:

```
Redis Broker
┌─────────────────────────────┐
│         Task Queue          │
├─────────────────────────────┤
│ send_email(order=101)       │
│ send_email(order=102)       │
│ cleanup_cart(cart=50)       │
└─────────────────────────────┘
```

By default everything goes through one queue, but tasks can be routed to named queues (e.g. `emails`, `cleanup`) so specific workers only pull specific kinds of work.

## Consumer

The consumer is the part of a worker process that connects to the broker and pulls messages off the queue. It's not a separate service — it's a component inside the worker, alongside the part that actually executes the code.

```
Celery Worker
 ├── Consumer      → connects to broker, receives messages
 └── Execution Pool → runs the task function
```

Worth internalizing: "consumer" and "worker" are not two servers talking to each other. They're two responsibilities inside the same process.

## Worker

The worker is the process that executes tasks. It consumes a message via its consumer component, then hands the function and its arguments to its execution pool to actually run.

```bash
# start a worker with 4 concurrent execution slots
celery -A commercecore worker -l info --concurrency=4
```

```
Celery Worker
      │
      ▼
send_order_confirmation_email(order_id=101)
      │
      ▼
   SMTP
```

## Task Lifecycle

Following one task end to end:

1. Django creates the order, then creates a task message for `send_order_confirmation_email`.
2. The message is sent to Redis and sits in the queue.
3. A worker's consumer picks up the message.
4. The worker's execution pool runs the function.
5. The result (success, failure, or return value) is written to a result backend, if one is configured.

| State | Meaning |
|---|---|
| `PENDING` | Sent, not yet picked up by a worker |
| `STARTED` | A worker has begun executing it |
| `SUCCESS` | Completed; return value available in the result backend |
| `FAILURE` | Raised an exception |
| `RETRY` | Failed but will be retried per the task's retry policy |
| `REVOKED` | Cancelled before, or during, execution |

## Two Components Your Notes Didn't Cover Yet

The topics above are enough to understand the flow, but a real implementation needs two more pieces:

| Component | Role |
|---|---|
| **Result Backend** | Optional store for task state and return values (a second Redis DB, Postgres, etc.). Skip it if you only ever fire-and-forget with `.delay()`; add it once Django needs to check whether a task succeeded or what it returned. It is *not* the same thing as the broker, even if you point both at Redis. |
| **Beat** | A scheduler process that emits tasks on a fixed schedule — the mechanism behind cron-like jobs such as `cleanup_expired_carts`. It doesn't execute anything itself; it just drops tasks onto the same broker on a timer. |

```bash
celery -A commercecore beat -l info
```

## Full Architecture (Multiple Workers + Result Backend)

```
                     Django (Producer)
                            │
                            │ apply_async()
                            ▼
                    ┌───────────────┐
                    │ Broker (Redis)│
                    │  ┌─────────┐  │
                    │  │ Queue   │  │
                    │  └─────────┘  │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          Worker 1       Worker 2      Worker 3
        (Consumer +    (Consumer +   (Consumer +
         Exec Pool)     Exec Pool)    Exec Pool)
              │             │             │
              ▼             ▼             ▼
          Task runs     Task runs     Task runs
              │
              ▼
      Result Backend (optional)
```

`Beat` sits alongside this, feeding the same broker on a schedule rather than in response to a request.

## Setting It Up

```python
# commercecore/celery.py
from celery import Celery

app = Celery(
    "commercecore",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",  # separate DB index from the broker
)
```

```bash
celery -A commercecore worker -l info --concurrency=4
celery -A commercecore beat -l info
```

## Choosing the Right Broker

| | Redis | RabbitMQ | Amazon SQS |
|---|---|---|---|
| Setup effort | Low — often already running for cache | Moderate | Low if already on AWS |
| Throughput | High for small messages | High; handles larger messages better | High, fully managed |
| Delivery guarantees | Best-effort; no native ack, more prone to loss on crash | Strong — durable queues, native acks | Strong — managed, durable |
| Can double as result backend | Yes | No — needs a separate backend | No |
| Runtime worker control (inspect, revoke, rate-limit) | Yes | Yes | Limited |
| Best for | Small/medium teams, moderate volume, simplicity | Production systems needing durability or high task volume | Teams already deep in AWS wanting a managed broker |

**Guidance**
- Start with **Redis** if it's already running for caching and task volume is moderate — it minimizes moving parts, which is the right call for a first implementation.
- Move to **RabbitMQ** once message durability actually matters (payments, inventory, anything where a lost message is a real problem) or Redis's throughput becomes the bottleneck.
- Consider **SQS** if the team is AWS-native and would rather not operate a broker at all.
- A common production pattern is RabbitMQ as the broker with Redis (or Postgres) as the result backend — RabbitMQ's delivery guarantees paired with Redis's fast result lookups.

For a first CommerceCore implementation, Redis for both broker and result backend (different DB indexes) is the right starting point — it's already in the stack, and durability trade-offs only start to matter at a scale CommerceCore isn't at yet.

## Scaling Workers

Three independent scaling levers, often confused with each other:

```
Concurrency          Multiple Workers        Multiple Machines
(inside 1 process)   (same machine)          (horizontal)

Worker               Worker A  Worker B      Host 1: Worker
 ├─ slot 1              │         │          Host 2: Worker
 ├─ slot 2            tasks     tasks        Host 3: Worker
 ├─ slot 3
 └─ slot 4
```

- `--concurrency=N` sets how many tasks one worker process runs in parallel (threads/processes/greenlets, depending on pool type).
- Running several `celery worker` instances adds isolation — separate queues, independent restart lifecycles.
- Adding machines scales background capacity independently of the web tier, which is the whole point of moving work off the request path.

## How This Maps to CommerceCore

| Concept | CommerceCore |
|---|---|
| Producer | Django views / signal handlers |
| Task | `send_order_confirmation_email`, `cleanup_expired_carts`, `send_low_stock_notification` |
| Broker | Redis — ideally a separate DB index or instance from the cache |
| Queue | Default queue to start; split into named queues later if needed |
| Consumer | Part of the `celery worker` process — no separate setup needed |
| Worker | `celery worker` process(es) acting against MySQL, S3, SMTP |
| Beat | Scheduler for `cleanup_expired_carts` and similar periodic jobs |
| Result backend | Not required on day one — add it once a task's success/failure needs to be checked from Django |

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
                    Django
                ┌──────┼──────┐
                │      │      │
                ▼      ▼      ▼
             MySQL    S3    Redis
                             │
                             ▼
                       Celery Worker
                             │
                 ┌───────────┼───────────┐
                 ▼           ▼           ▼
              Emails     Cleanup    Notifications
```


Remember:
```
- Django creates the task.
- Redis acts as the broker.
- Queue holds waiting task messages.
- Celery Worker consumes and executes tasks.
- Celery allows background processing.
- Multiple workers allow the background-processing layer to scale independently.
- The HTTP request does not need to wait for the background task to finish.
```