# Phase 13 — Redis & Celery

**Status:** ✅ Completed 
**Day 4 Topic:** Phase 13.1C — Redis Installation & Hands-On Practice

> Today's goal is  **Redis Installation & Hands-On Practice** and Complete Phase 13.1.
> 
# Phase 13.1D — Redis Installation & Hands-On Practice

Setting up Redis locally on Windows, exercising the core data types via `redis-cli`, and wiring Django up to it as a cache backend.

## 1. Architecture at a Glance

```
CommerceCore
     │
     ▼
   Django ──────┬──────────────┐
                 │              │
                 ▼              ▼
              MySQL           Redis
         (source of truth)   (cache)
```

Redis sits alongside MySQL as a fast, in-memory layer — not a replacement for the database, but a place for data that's expensive to recompute and safe to lose (cache entries, counters, queues, session data).

## 2. Choosing a Windows Redis Setup

Redis doesn't ship a native Windows build. On Windows you're choosing between running the real Linux binary in a virtualized layer, or a native Windows-compatible port.

| Option | How it works | Best for | Trade-offs |
|---|---|---|---|
| **Docker** | Runs the official Redis image in a container | Devs already using Docker; mirrors production | Needs Docker Desktop + virtualization enabled |
| **WSL2** | Runs the real Linux Redis binary inside a Linux subsystem | Wanting genuine Linux behavior without containers | Extra one-time setup; the Redis process stops when the WSL session/terminal closes unless you configure it as a service |
| **Memurai** | Native Windows port of Redis, installed as a Windows service, official Redis partner for Windows | Teams that want Redis running as a first-class Windows service, no virtualization | Separate build from Redis OSS (kept in sync); free Developer edition, paid tiers for production features |

**Recommendation for CommerceCore: Docker.** The production target is a containerized/service-oriented stack (Django → Redis → Celery), so running Redis in Docker locally now means the dev environment already matches how the pieces will talk to each other later.

## 3. Running Redis via Docker

Confirm Docker is available:

```powershell
docker --version
docker ps
```

Start a Redis container:

```powershell
docker run -d --name commercecore-redis -p 6379:6379 redis
```

| Flag | Meaning |
|---|---|
| `-d` | Run in detached/background mode |
| `--name commercecore-redis` | Container name |
| `-p 6379:6379` | Map Windows port 6379 → container port 6379 |
| `redis` | Official Redis image from Docker Hub |

> For anything beyond local experimentation, pin a version tag (e.g. `redis:7-alpine`) instead of the floating default tag, so the environment is reproducible.

Verify it's up:

```powershell
docker ps
```

```
CONTAINER ID   IMAGE    PORTS
xxxxxxx        redis    0.0.0.0:6379->6379/tcp
```

```
Windows localhost:6379 ──▶ Docker ──▶ Redis container :6379
```

## 4. Redis Server vs. Redis Client

A recurring source of confusion worth being explicit about:

```
                    Redis Server
                    (the process:
                  memory, keys, data)
                          ▲
             ┌────────────┼────────────┐
             │             │             │
         redis-cli      redis-py      Celery
        (manual CLI)  (Django app)   (later phase)
```

The Docker container runs the **server**. `redis-cli`, `redis-py`, and Celery are all **clients** — different ways of talking to the same server.

Open a CLI session into the running container:

```powershell
docker exec -it commercecore-redis redis-cli
```

```
127.0.0.1:6379> PING
PONG
```

## 5. Redis CLI Command Reference

Core commands worth having muscle memory for:

| Type | Commands | Example |
|---|---|---|
| Health check | `PING` | `PING` → `PONG` |
| String | `SET`, `GET`, `EXISTS`, `DEL` | `SET name "Amol"` → `OK` |
| Counter | `INCR` | `INCR product:101:views` → atomically increments an integer-valued string |
| Expiry | `EXPIRE`, `TTL` | `EXPIRE key 30` then `TTL key` |
| Hash | `HSET`, `HGET`, `HGETALL` | `HSET product:101 name "Alienware" price 150000 stock 8` |
| List | `LPUSH`, `LRANGE` | `LPUSH email_queue "email-1"` |
| Set | `SADD`, `SMEMBERS`, `SISMEMBER` | `SADD product:101:tags "gaming"` |
| Sorted set | `ZADD`, `ZRANGE ... WITHSCORES` | `ZADD product:popularity 100 product:101` |
| Introspection | `KEYS *`, `SCAN`, `TYPE` | see warning below |
| Server info | `INFO` | version, memory, clients, uptime |

**Expiry lifecycle:**

```
SET key ──▶ EXPIRE 30 ──▶ TTL counts down ──▶ key auto-deleted
                                                (TTL now returns -2)
```

`TTL` returns `-1` if the key exists but has no expiry set, and `-2` if the key doesn't exist at all (never existed, or already expired). This mechanism is what Phase 13.7 (Django caching) relies on under the hood.

**List order:** `LPUSH` inserts at the *head* of the list, so pushing `email-1`, `email-2`, `email-3` in that order and then running `LRANGE email_queue 0 -1` returns them most-recently-pushed-first: `email-3`, `email-2`, `email-1`.

**Sorted sets** rank by score, ascending by default — `ZRANGE ... WITHSCORES` on a popularity set returns the lowest-score item first, which is exactly what you want for leaderboard-style queries.

**`KEYS *` vs `SCAN`:** `KEYS *` is fine for local development but should never be run casually against a production instance — it scans the entire keyspace in a single blocking operation. `SCAN` iterates the keyspace incrementally via a cursor and is the production-safe equivalent.

## 6. Connecting Django to Redis

Django ships a built-in Redis cache backend (available since Django 4.0) that talks to Redis directly through `redis-py` — no third-party cache package required for basic caching.

**Install the client:**

```powershell
pip install redis
pip show redis
```

**`.env`:**

```
REDIS_URL=redis://127.0.0.1:6379/0
```

The `/0` selects Redis logical database 0 (Redis supports multiple numbered databases per instance; `0` is the default).

**`settings/base.py`:**

```python
REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://127.0.0.1:6379/0"
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}
```

```
Django ──(redis-py)──▶ 127.0.0.1:6379 ──▶ Redis container
```

## 7. Verifying the Connection End-to-End

**From the Django side:**

```python
python manage.py shell
```

```python
>>> from django.core.cache import cache
>>> cache.set("commercecore:test", "Redis is working", 60)
>>> cache.get("commercecore:test")
'Redis is working'
```

**From the Redis side** — don't just trust Django; check the other end of the connection:

```powershell
docker exec -it commercecore-redis redis-cli
```

```
127.0.0.1:6379> SCAN 0
127.0.0.1:6379> KEYS *
```

Django doesn't store the key exactly as `commercecore:test`. Its default key function combines an optional key prefix and the cache version with your key, as `<prefix>:<version>:<key>`. With no `KEY_PREFIX` configured, that comes out as `:1:commercecore:test` — the leading colon is the empty prefix, `1` is the default cache version. That's the key you'll actually find in `KEYS *`, and `TYPE :1:commercecore:test` will report `string`.

> The `60` in `cache.set(..., 60)` is a 60-second timeout. If you check Redis well after setting the value, an empty `TYPE`/`GET` result usually just means the entry expired — not a broken connection.

## 8. Out of Scope for This Lesson

Deliberately not covered yet — these come in later phases as CommerceCore's Redis usage grows:

- Celery / Celery Beat (Phase 13.2)
- Redis authentication
- Redis Cluster / Sentinel
- Production persistence (RDB/AOF) tuning
- Advanced cache eviction policies

Current checklist:

- ✅ Redis installed and running (Docker)
- ✅ Redis CLI verified (`PING` → `PONG`)
- ✅ Core data types exercised (string, hash, list, set, sorted set, TTL)
- ✅ `redis-py` installed
- ✅ Django connected to Redis via the cache framework

## 9. How This Maps to CommerceCore

**Now:**

```
CommerceCore → Django ──┬── MySQL   (source of truth)
                          └── Redis   (cache)
```

**After Phase 13.2–13.5:**

```
CommerceCore → Django ──┬── MySQL
                          └── Redis ──┬── Cache
                                       └── Celery → Worker → Background Tasks
```

Redis is stepping into two roles going forward: it's already the Django cache backend, and starting in 13.2 it becomes the message broker that Celery workers pull background jobs from. Everything practiced in this lesson — the server/client distinction, basic commands, and TTL behavior — carries directly into how Celery uses Redis as a queue.