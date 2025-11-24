# fastapi‑easylimiter
[![GitHub stars](https://img.shields.io/github/stars/cfunkz/fastapi-easylimiter?style=social)](https://github.com/cfunkz/fastapi-easylimiter/stargazers) 
[![GitHub forks](https://img.shields.io/github/forks/cfunkz/fastapi-easylimiter?style=social)](https://github.com/cfunkz/fastapi-easylimiter/network/members) 
[![GitHub issues](https://img.shields.io/github/issues/cfunkz/fastapi-easylimiter)](https://github.com/cfunkz/fastapi-easylimiter/issues) 
[![GitHub license](https://img.shields.io/github/license/cfunkz/fastapi-easylimiter)](https://github.com/cfunkz/fastapi-easylimiter/blob/main/LICENSE) 
[![PyPI](https://img.shields.io/pypi/v/fastapi-easylimiter)](https://pypi.org/project/fastapi-easylimiter/)
---

An **ASGI async rate-limiting middleware** for FastAPI with **Redis**, designed to handle **auto-generated routes** (e.g., FastAPI-Users) without decorators, for simplicity and ease of use.
---

## Features

- Path based rules (`/api/*`, `/auth/*`, `/api/users/me`, etc)
- Fixed, Sliding & Moving window algorithms (Lua)
- `RateLimit`, `RateLimit-Policy`, `Retry-After` headers
- ASGI async middleware for FastAPI/Starlette
- Asyncio Redis support
- Easy to configure
- No decorators needed
- HTML/JSON error responses
- Site-wide or per-endpoint bans, with configurable durations
---

## TODO

- In-memory option
- Forwarded-For handling
- Better websocket support
---

## Rule Matching

### Single Rule
Use these when you want a rule to apply to one specific endpoint only.
```python
"/api/users/me": (20, 60, "sliding")
```

This applies only to requests where the normalized path is exactly:
```python
/api/users/me
```

Nothing else matches.
Not `/api/users/me/profile`, not `/api/users/me/123`, not `/api/users`.

### Prefix Wildcards
A rule ending with `/*` applies to all sub-paths under a given prefix, as one shared rate-limit bucket.
```python
"/api/*": (100, 60, "sliding")
```

This matches:
```python
/api
/api/
/api/users
/api/users/123
/api/anything/here/nested
```

### How Rule applies
Rules are normalized and sorted so that:

- Exact matches come before wildcard matches.
- Longer prefixes take priority over shorter prefixes (so `/api/users/*` overrides `/api/*`)
- A request may match multiple rules, if so, ALL matching rules run, and the strictest one determines whether the request is allowed.
- Bans will double with each offense, up to the configured maximum ban length.
## Installation

```bash
pip install fastapi-easylimiter
```

---

## Usage

```python
from fastapi import FastAPI
import redis.asyncio as redis
from middleware.rate import RateLimitMiddleware

app = FastAPI()

redis_client = redis.from_url("redis://localhost:6379/0")

app.add_middleware(
    RateLimitMiddleware,
    redis=redis,
    rules={
        "/*": (200, 60, "moving"),           
        "/api/*": (10, 1, "sliding"),
        "/api/auth/*": (3, 1, "sliding"),
        "/api/users/me": (3, 30, "fixed"),
    },
    exempt=[],
    ban_offenses=15,
    ban_length="3m",
    ban_max_length="30m",
    ban_counter_ttl="1h",
    site_ban=True,
    )
```

> Example: `/api/auth/login` matches `/api/auth` and `/api`. If **any** rule is exceeded → `429` returned. If banned → `403` returned.

---

### Redis Key Patterns
| Key Pattern                                   | Example                                 | Used For                                           |
| --------------------------------------------- | --------------------------------------- | -------------------------------------------------- |
| `rl:fixe:{hash}:{limit}:{window}`             | `rl:fixe:a1b2c3d4e5f6a7b8:100:60`       | Fixed-window counter                               |
| `rl:slid:{hash}:{limit}:{window}`             | `rl:slid:a1b2c3d4e5f6a7b8:60:60`        | Sliding window request log                         |
| `rl:movi:{hash}:{limit}:{window}:{window_id}` | `rl:movi:a1b2c3d4e5f6a7b8:100:60:12345` | Moving window per-subwindow counter                |
| `{rl_key}:meta`                               | `rl:fixe:a1b2c3d4e5f6a7b8:100:60:meta`  | Stores both: `offenses` & `ban_count` for doubling |
| `ban:{hash}`                                  | `ban:a1b2c3d4e5f6a7b8`                  | Active ban flag                                    |
---

### Middleware Parameters
| Parameter        | Type                              | Required | Description                          |
| ---------------- | --------------------------------- | -------- | ------------------------------------ |
| `redis`          | `redis.asyncio.Redis`             | Yes      | Redis async client                   |
| `rules`          | `Dict[str, Tuple[int, int, str]]` | Yes      | Path → (limit, period, strategy)     |
| `exempt`         | `Optional[List[str]]`             | No       | Paths that bypass rate limits        |
| `ban_offenses`   | `int`                             | No       | Offenses before ban triggers         |
| `ban_length`     | `str`                             | No       | Initial ban length                   |
| `ban_max_length` | `str`                             | No       | Maximum exponential ban ceiling      |
| `ban_counter_ttl`| `int`                             | No       | TTL for ban metadata (default 3600s) |
| `site_ban`       | `bool`                            | No       | Enable site-wide bans or per-endpoint|
---

## Tests
Used [Ratelimit Tester](https://github.com/cfunkz/ratelimit-tester) for testing rate-limit atomicity.

## Screenshot

<img width="1070" height="571" alt="image" src="https://github.com/user-attachments/assets/4579f130-ac83-457b-8fd1-eda720ce8123" />
<img width="1128" height="582" alt="image" src="https://github.com/user-attachments/assets/23752a35-5bff-4ed1-bd72-e90fe6c41e00" />
<img width="448" height="745" alt="image" src="https://github.com/user-attachments/assets/1f8c415a-5baf-4635-9408-2ced64a75b0c" />
---

## Contributing

Contributions and forks are always welcome! Adapt, improve, or extend for your own needs.

[![Buy Me a Coffee](https://cdn.ko-fi.com/cdn/kofi3.png?v=3)](https://ko-fi.com/cfunkz81112)
