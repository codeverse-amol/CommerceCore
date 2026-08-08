# Phase 13 — Redis & Celery

**Status:** 🚧 In Progress  
**Day 3 Topic:** Phase 13.1B — Redis Data Types

> Today's goal is understanding **Redis Data Types**.

## The Mental Model

```
KEY ──▶ TYPED VALUE
          ├─ String
          ├─ List
          ├─ Hash
          ├─ Set
          ├─ Sorted Set
          ├─ Stream
          └─ (Array / JSON / Geo / ... — specialized types)

Pub/Sub sits outside this model — it's messaging, not storage.
```

Redis isn't `key → string`. It's `key → data structure`. The right structure is the one whose native operations match how the data will be *queried*, not just how it will be stored.

## 1. Core Types

| Type | Structure | Core commands | Good fit |
|---|---|---|---|
| String | single value | `SET` `GET` `INCR` `DECR` | counters, flags, cached tokens |
| List | ordered, duplicates OK | `LPUSH` `RPUSH` `LRANGE` `LPOP` | simple queues, recent-N feeds |
| Hash | field→value map under one key | `HSET` `HGET` `HGETALL` | a cached object (e.g. a product) |
| Set | unique, unordered | `SADD` `SISMEMBER` `SINTER` | tags, dedup, membership checks |
| Sorted Set | unique + score, auto-ranked | `ZADD` `ZRANGE` `ZREVRANGE` | leaderboards, "top N" rankings |
| Stream | append-only, replayable log | `XADD` `XREAD` `XREADGROUP` | durable event/order log |
| Pub/Sub | fire-and-forget messaging | `SUBSCRIBE` `PUBLISH` | live notifications |

## 2. String

Stores text, numbers, tokens, or binary data. Also doubles as an atomic counter.

```
SET product:101:views 152
INCR product:101:views          # → 153
```

Incrementing in Redis avoids a write to the primary database on every single event — the counter lives in memory and can be flushed to MySQL periodically instead of on every hit.

## 3. List

An ordered sequence, efficient at both ends — the natural fit for a simple queue.

```
RPUSH email_queue "email-1"     # add to tail
LPOP  email_queue                # consume from head
LRANGE email_queue 0 -1          # read all
```

A worker process pops from one end while producers push to the other. This is also the mechanism Celery uses under the hood when Redis is configured as its broker — Redis provides the list/queue primitive, Celery provides the task-processing system on top of it.

## 4. Hash

Groups related fields under a single key — the closest thing Redis has to an object.

```
HSET product:101 name "Alienware" price 150000 stock 8 category "Laptop"
HGET product:101 stock           # → 8
HGETALL product:101              # → all fields
```

`HSET` accepts any number of field/value pairs in one call, so a full object can be written in a single round trip rather than one command per field.

## 5. Set

An unordered collection of unique values — good whenever the question is "does this exist" or "is this a member," not "what order is this in."

```
SADD product:101:tags "Laptop" "Gaming" "Dell"
SISMEMBER product:101:tags "Gaming"     # → 1
```

Duplicate adds are no-ops; the set silently keeps one copy.

## 6. Sorted Set

Like a Set, but every member carries a score, and Redis keeps members ordered by that score automatically.

```
ZADD product:views 100 product:101
ZADD product:views 250 product:102
ZADD product:views 175 product:103

ZRANGE    product:views 0 -1 WITHSCORES   # ascending — lowest score first
ZREVRANGE product:views 0 -1 WITHSCORES   # descending — highest score first
```

For rankings and leaderboards ("most viewed," "top scorers") the descending form is almost always the one that's wanted — `ZREVRANGE` on any Redis version, or `ZRANGE key 0 -1 REV` on Redis 6.2+.

## 7. Stream

An append-only, persisted log of entries, each a set of field/value pairs. Unlike Pub/Sub, a Stream keeps its history — consumers can join late and replay from any point, and consumer groups provide at-least-once delivery across multiple readers (conceptually similar to Kafka, built directly into Redis).

```
XADD  orders:events * order_id 501 status "placed"
XREAD COUNT 10 STREAMS orders:events 0
```

This is the structure to reach for when a durable order/audit log or reliable multi-consumer processing is needed — something plain Pub/Sub, being fire-and-forget, cannot provide.

## 8. Pub/Sub

A messaging channel, not a data store. Publishers send messages to a channel with no knowledge of who — if anyone — is listening.

```
SUBSCRIBE notifications
PUBLISH   notifications "New order received"
```

If no subscriber is connected at the moment a message is published, that message is gone — there is no history and no replay. This makes Pub/Sub well suited to real-time, ephemeral events (live notifications, broadcasts) and unsuited to anything that needs guaranteed delivery — that's what Streams are for.

## 9. TTL (Time To Live)

Not a data structure itself, but a property that can be attached to any key — central to Redis's role as a cache.

```
EXPIRE key 600            # expire in 600 seconds
TTL    key                 # remaining seconds; -1 = no expiry, -2 = key doesn't exist
SET    key value EX 600    # set value and expiry in one call
```

## 10. Choosing a Type

**A single object (e.g. a cached product):**
```
Nested fields/arrays or geo-indexed search needed?
 ├─ yes → JSON
 └─ no  → Per-field TTL or Redis Search indexing needed?
           ├─ yes → Hash
           └─ no  → Hash (default choice for most objects)
```

**A collection of unique items (e.g. tags, rankings):**
```
Arbitrary or score-based order needed?
 ├─ yes → Sorted Set
 └─ no  → Extra data per item, no set algebra needed?
           ├─ yes → Hash
           └─ no  → Set
```

**An ordered/append-heavy sequence (e.g. logs, queues):**
```
Priority order, lexicographic order, or set ops needed?
 ├─ yes → Sorted Set
 └─ no  → Index-addressed access, a ring buffer, or server-side range aggregation needed?
           ├─ yes → Array
           └─ no  → Timestamp order or multiple consumer groups needed?
                     ├─ yes → Stream
                     └─ no  → List
```

## 11. Specialized Types

Beyond the core set, Redis ships several purpose-built types for specific workloads:

| Type | What it's for |
|---|---|
| **Array** *(Redis 8.8+)* | sparse, index-addressable values with native ring buffers and server-side range aggregation |
| JSON | nested documents, queryable by path via Redis Search |
| Geospatial | radius / bounding-box queries on coordinates |
| Probabilistic (HyperLogLog, Bloom filter, etc.) | approximate counts over huge datasets, tiny memory footprint |
| Time series | timestamped numeric data |
| Vector set | similarity search over embeddings (AI/RAG use cases) |

**Array vs. List for bounded histories:** Lists have no built-in ring buffer — a fixed-size "last N items" pattern means combining `LPUSH` with `LTRIM`. Arrays provide this natively:

```
ARRING recent_views:101 20 product_id     # keeps only the last 20, auto-overwrites oldest
ARSET  events:orderA 0 "placed"
ARGET  events:orderA 0                    # → "placed"
AROP   metrics:101 0 -1 SUM               # server-side aggregate, no per-element fetch
```

`LPUSH`/`LTRIM` is enough when only "the last N items" is needed. `Array` is the better fit when direct index access or in-Redis aggregation over a range is also required.

## 12. Redis vs. MySQL

```
MySQL → source of truth (relational, durable, transactional)
Redis → fast layer on top (cache, counters, queues, temp state)
```

MySQL owns the permanent business data — products, orders, users. Redis holds a fast, often temporary, representation of a slice of that data for low-latency access.

## 13. CommerceCore — What Maps Where

| Need | Type | Example key |
|---|---|---|
| View counter | String | `product:101:views` |
| Cached product | Hash | `product:101` |
| Unique tags | Set | `product:101:tags` |
| Most-viewed ranking | Sorted Set | `product:views` |
| Durable order/audit log | Stream | `orders:events` |
| Live notification | Pub/Sub | `notifications` |
| Email/task queue | List | `email_queue` |

---
**Recap:** String = one value · List = ordered · Hash = object · Set = unique · Sorted Set = ranked · Stream = durable log · Pub/Sub = real-time, no memory · Array = index-addressed + ring buffer.