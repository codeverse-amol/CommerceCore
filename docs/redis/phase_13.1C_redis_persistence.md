# Phase 13 — Redis & Celery

**Status:** 🚧 In Progress  
**Day 4 Topic:** Phase 13.1C — Redis Persistence

> Today's goal is understanding **Redis Persistence**.



## 1. Why Persistence Exists

Redis keeps its working dataset in RAM, which is what makes it fast. RAM is volatile — a restart or crash wipes it clean unless Redis has written a durable copy to disk.

```
Redis
  │
  ├── RAM   → active dataset, sub-millisecond access
  └── Disk  → durable copy, survives restarts/crashes
```

Persistence is the mechanism that copies (or replays) that in-memory state to disk and reloads it on startup. Redis ships two independent mechanisms — RDB and AOF — that can be used separately or together.

## 2. RDB — Point-in-Time Snapshots

RDB persistence periodically writes the *entire* dataset to a single compact binary file (`.rdb`, `dump.rdb` by default).

```
t=0        t=60s               t=120s
 │           │                    │
 ▼           ▼                    ▼
Redis ──► snapshot ──► dump.rdb (overwritten each time)
```

**How it works internally:** Redis forks a child process. The child writes the dataset to disk while the parent keeps serving traffic (via copy-on-write memory pages). This keeps snapshotting non-blocking for normal operations, but the fork itself can briefly stall the server — noticeably so on very large datasets.

**Config directives** (`redis.conf` or `CONFIG SET`):

| Directive | Purpose |
|---|---|
| `save <seconds> <changes>` | Trigger a snapshot if N keys change within the window |
| `dbfilename` | Name of the RDB file |
| `dir` | Directory where it's saved |
| `rdbcompression` | LZF-compress string values (default `yes`) |

Example — snapshot if 3 keys change within 20 seconds:
```conf
dbfilename my_backup_file.rdb
save 20 3
```

**Trade-off:** any writes after the last successful snapshot are lost on crash.

```
snapshot@12:00 ── writes ── writes ── CRASH@12:03
                                        └─ everything since 12:00 is gone
```

**Good for:** backups, disaster recovery, cloning/replicating a dataset, fast restarts.

## 3. AOF — Append-Only File

AOF logs every write command as it executes, then replays that log on restart to rebuild the dataset.

```
SET a 1 ──┐
INCR a  ──┼──► appendonly.aof (append-only log)
HSET ... ─┘
```

Restart:

```
appendonly.aof ──► replay each entry ──► dataset rebuilt
```

Commands are logged in their **deterministic, already-resolved form** — e.g. `EXPIRE key 10` is stored as `PEXPIREAT key <absolute-ms-timestamp>`, so replay produces identical results no matter when it runs.

**fsync policy** controls the durability/performance trade-off:

| Policy | Behavior | Worst-case loss |
|---|---|---|
| `always` | fsync on every write; client waits for disk | ~0 (highest latency) |
| `everysec` *(default)* | fsync once per second, async | up to 1s of writes |
| `no` | OS decides when to flush | several seconds (OS-dependent) |

**AOF rewrite:** the log only grows, so Redis periodically compacts it in the background (`BGREWRITEAOF`, triggered automatically via `auto-aof-rewrite-percentage` / `auto-aof-rewrite-min-size`) — replacing it with the minimal set of commands needed to recreate the current dataset.

**Good for:** minimizing data loss, near-real-time durability.

## 4. Hybrid AOF (RDB Preamble)

Since Redis 4.0, an AOF rewrite doesn't have to be a pure command log. With `aof-use-rdb-preamble yes` (default in modern Redis), a rewritten AOF file starts with an RDB-formatted snapshot of the dataset at rewrite time, followed by plain AOF commands for everything written since.

```
appendonly.aof
 ├── [RDB-format preamble]        ── fast, compact to load
 └── [AOF commands since rewrite] ── the durability tail
```

This gets you RDB's fast, compact loading *and* AOF's write-level durability going forward. It's a different thing from just "running RDB and AOF side by side" (next section), though both get called "hybrid persistence" informally.

## 5. Running RDB and AOF Together

You can also enable both mechanisms independently — `save` rules for periodic snapshots, `appendonly yes` for the write log. This is the common production setup.

```conf
appendonly yes
appendfsync everysec
save 3600 1
save 300 100
save 60 10000
```

Enable AOF on a live server without restarting it:

```
CONFIG SET appendonly yes
CONFIG SET appendfsync everysec
CONFIG REWRITE   # persist the change into redis.conf
```

**On restart, if both an RDB file and an AOF file exist, Redis loads the AOF** — it's treated as the more complete, up-to-date source.

## 6. RDB vs AOF

| | RDB | AOF |
|---|---|---|
| Method | Periodic full snapshot | Continuous write log |
| File format | Compact binary | Command log (or RDB-preamble hybrid) |
| Data-loss window | Since last snapshot | Depends on fsync policy (0–~1s typically) |
| File size | Smaller | Larger (until rewrite) |
| Restart speed | Fast (load one file) | Slower (replay log); faster with RDB preamble |
| Disk I/O pattern | Spiky (fork + bulk write) | Continuous, smaller writes |
| Best for | Backups, disaster recovery, cloning | Durability, minimal data loss |

## 7. Three Things People Conflate

| Concept | Answers | Not the same as |
|---|---|---|
| **Persistence** | "How do I save data to disk?" | Backup |
| **Backup** | "Do I have a recoverable copy for a serious failure?" | Persistence |
| **Eviction** | "What do I remove when memory is full?" | Persistence |

Persistence (RDB/AOF) protects against *process restarts and crashes*. A backup is a copy kept somewhere else (another disk, object storage, a snapshot schedule) for disaster recovery. Eviction (`noeviction`, LRU, LFU, TTL-based policies) governs what happens when Redis hits `maxmemory` — a memory-management concern, unrelated to write durability.

## 8. TTL Survives Persistence

Expiration metadata is part of a key's state, so it's saved and restored along with the value — a key with `TTL 600` still expires on schedule after a restart, whether recovered from an RDB snapshot or replayed from AOF (as an absolute `PEXPIREAT`).

## 9. Choosing a Persistence Strategy

| Priority | Use |
|---|---|
| Pure cache, rebuildable from another source of truth | RDB only, or persistence off entirely |
| Fast restarts, occasional backups, some data loss OK | RDB only |
| Queue/broker semantics, low tolerance for lost writes | AOF (`everysec` or `always`) |
| General-purpose production default | Both — AOF for durability, RDB for fast restores and portable backups |
| Zero tolerance for any lost write | AOF with `appendfsync always` (accept the latency cost) |

Rule of thumb: **if losing the last few seconds/minutes of writes is genuinely fine, RDB alone is simpler. If it isn't, add AOF.**

## 10. How This Maps to CommerceCore

```
CommerceCore
     │
     ▼
   Redis
 ┌───┴────┐
 ▼         ▼
Cache    Celery Broker
```

- **Django cache** (`products:list`, etc.) — MySQL is the source of truth, so losing this on crash just means a rebuild on the next query. RDB-level durability, or none at all, is fine here.
- **Celery broker** — queued tasks (e.g. order-confirmation emails) aren't reconstructible from MySQL; losing them means the task never runs. This is where AOF-level durability matters — the exact fsync policy gets decided in **Phase 13.2 — Celery Fundamentals**.

MySQL remains the permanent source of truth in both cases. Redis persistence only protects Redis's own recovery time and the broker's in-flight state — it never replaces the database.