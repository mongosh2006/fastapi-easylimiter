# strategies.py
import hashlib
import redis.asyncio as redis
from typing import Optional, Tuple

class BaseRedisStrategy:
    """Base class for Redis-backed rate limiting strategies with integrated ban logic."""

    def __init__(self, redis_client: redis.Redis, ban_after: int = 8, initial_ban: int = 300, max_ban: int = 86400, ban_counter: int = 3600, site_ban: bool = True):
        self.redis = redis_client
        self.ban_after = ban_after
        self.initial_ban = initial_ban
        self.max_ban = max_ban
        self.ban_counter = ban_counter
        self.site_ban = site_ban

    def _key(self, identifier: str, limit: int, window: int) -> str:
        hashed = hashlib.sha256(identifier.encode()).hexdigest()[:16]
        strategy = self.__class__.__name__[:4].lower()
        return f"rl:{strategy}:{hashed}:{limit}:{window}"

    def _ban_key(self, identifier: str, limit: Optional[int] = None, window: Optional[int] = None) -> str:
        hashed = hashlib.sha256(identifier.encode()).hexdigest()[:16]
        if self.site_ban:
            return f"ban:{hashed}"
        else:
            strategy = self.__class__.__name__[:4].lower()
            return f"rl:{strategy}:{hashed}:{limit}:{window}:ban"

    def _meta_key(self, rl_key: str) -> str:
        """Single meta key to store both offenses and consecutive ban count."""
        return f"{rl_key}:meta"


class FixedWindowStrategy(BaseRedisStrategy):
    """Fixed-window rate limiting with atomic ban doubling using a single meta key."""

    LUA_SCRIPT = """
    local rl,ban,meta=KEYS[1],KEYS[2],KEYS[3]
    local lim,win,ba,ib,mb=tonumber(ARGV[1]),tonumber(ARGV[2]),tonumber(ARGV[3]),tonumber(ARGV[4]),tonumber(ARGV[5])
    local now=tonumber(redis.call('TIME')[1])
    local ws=now-now%win

    local bt=redis.call('TTL',ban)
    if bt>0 then return {0,0,0,bt,ws+win,now} end

    local c=tonumber(redis.call('GET',rl) or '0')
    if c<lim then
        local nc=redis.call('INCR',rl)
        redis.call('EXPIREAT',rl,ws+win)
        return {1,nc,lim-nc,0,ws+win,now}
    end

    local o=tonumber(redis.call('HINCRBY', meta, 'off', 1))
    redis.call('EXPIRE',meta,win*2)

    if o>=ba then
        local bc=tonumber(redis.call('HINCRBY', meta, 'bc', 1))
        local d=math.min(ib*(2^(bc-1)), mb)
        redis.call('SET',ban,'1','EX',d)
        redis.call('HSET',meta,'off',0)
        local meta_ttl = math.max(d, tonumber(ARGV[6]))
        redis.call('EXPIRE',meta,meta_ttl)
        return {0,c,0,d,ws+win,now}
    end

    return {0,c,0,0,ws+win,now}
    """

    def __init__(self, redis_client: redis.Redis, ban_after: int = 8, initial_ban: int = 300, max_ban: int = 86400, ban_counter: int = 3600, site_ban: bool = True):
        super().__init__(redis_client, ban_after, initial_ban, max_ban, ban_counter, site_ban)
        self.lua = self.redis.register_script(self.LUA_SCRIPT)

    async def hit(self, identifier: str, limit: int, window: int) -> Tuple[bool, int, int, int, int]:
        rl_key = self._key(identifier, limit, window)
        ban_key = self._ban_key(identifier, limit, window)
        meta_key = self._meta_key(rl_key)

        result = await self.lua(
            keys=[rl_key, ban_key, meta_key],
            args=[limit, window, self.ban_after, self.initial_ban, self.max_ban, self.ban_counter]
        )
        return result[0]==1, int(result[2]), int(result[4]), int(result[3]), int(result[5])


class SlidingWindowStrategy(BaseRedisStrategy):
    """Sliding window log rate limiting with atomic ban doubling using a single meta key."""

    LUA_SCRIPT = """
    local rl,ban,meta=KEYS[1],KEYS[2],KEYS[3]
    local lim,win,ba,ib,mb=tonumber(ARGV[1]),tonumber(ARGV[2]),tonumber(ARGV[3]),tonumber(ARGV[4]),tonumber(ARGV[5])
    local now=tonumber(redis.call('TIME')[1])
    local cut=now-win

    local bt=redis.call('TTL',ban)
    if bt>0 then
        local old=redis.call('ZRANGE',rl,0,0,'WITHSCORES')[2]
        return {0,0,0,bt,old and tonumber(old)+win or now+win,now}
    end

    redis.call('ZREMRANGEBYSCORE',rl,'-inf',cut)
    local cnt=redis.call('ZCARD',rl)

    if cnt<lim then
        redis.call('ZADD',rl,now,now)
        redis.call('EXPIRE',rl,win+60)
        local old=tonumber(redis.call('ZRANGE',rl,0,0,'WITHSCORES')[2] or now)
        return {1,lim-cnt-1,old+win,0,old+win,now}
    end

    local o=tonumber(redis.call('HINCRBY', meta, 'off', 1))
    redis.call('EXPIRE',meta,win*2)

    if o>=ba then
        local bc=tonumber(redis.call('HINCRBY', meta, 'bc', 1))
        local d=math.min(ib*(2^(bc-1)), mb)
        redis.call('SET',ban,'1','EX',d)
        redis.call('HSET',meta,'off',0)
        local meta_ttl = math.max(d, tonumber(ARGV[6]))
        redis.call('EXPIRE',meta,meta_ttl)
        return {0,0,0,d,now+win,now}
    end

    local old=tonumber(redis.call('ZRANGE',rl,0,0,'WITHSCORES')[2] or now-win)
    return {0,0,old+win,0,old+win,now}
    """

    def __init__(self, redis_client: redis.Redis, ban_after: int = 8, initial_ban: int = 300, max_ban: int = 86400, ban_counter: int = 3600, site_ban: bool = True):
        super().__init__(redis_client, ban_after, initial_ban, max_ban, ban_counter, site_ban)
        self.lua = self.redis.register_script(self.LUA_SCRIPT)

    async def hit(self, identifier: str, limit: int, window: int) -> Tuple[bool, int, int, int, int]:
        rl_key = self._key(identifier, limit, window)
        ban_key = self._ban_key(identifier, limit, window)
        meta_key = self._meta_key(rl_key)

        result = await self.lua(
            keys=[rl_key, ban_key, meta_key],
            args=[limit, window, self.ban_after, self.initial_ban, self.max_ban, self.ban_counter]
        )
        return result[0]==1, int(result[1]), int(result[4]), int(result[3]), int(result[5])


class MovingWindowStrategy(BaseRedisStrategy):
    """Moving window (sliding window counter) with atomic ban doubling using a single meta key."""

    LUA_SCRIPT = """
    local base,ban,meta=KEYS[1],KEYS[2],KEYS[3]
    local lim,win,ba,ib,mb=tonumber(ARGV[1]),tonumber(ARGV[2]),tonumber(ARGV[3]),tonumber(ARGV[4]),tonumber(ARGV[5])
    local now=tonumber(redis.call('TIME')[1])
    local cw=math.floor(now/win)
    local ck,pk=base..':'..cw,base..':'..(cw-1)
    local rst=(cw+1)*win

    local bt=redis.call('TTL',ban)
    if bt>0 then return {0,0,0,bt,rst,now} end

    local curr=tonumber(redis.call('GET',ck) or '0')
    local prev=tonumber(redis.call('GET',pk) or '0')
    local wc=math.floor(prev*(win-now%win)/win+curr)

    if wc<lim then
        local nc=redis.call('INCR',ck)
        redis.call('EXPIRE',ck,win*2)
        wc=math.floor(prev*(win-now%win)/win+nc)
        return {1,math.max(0,lim-wc),rst,0,rst,now}
    end

    local o=tonumber(redis.call('HINCRBY', meta, 'off', 1))
    redis.call('EXPIRE',meta,win*2)

    if o>=ba then
        local bc=tonumber(redis.call('HINCRBY', meta, 'bc', 1))
        local d=math.min(ib*(2^(bc-1)), mb)
        redis.call('SET',ban,'1','EX',d)
        redis.call('HSET',meta,'off',0)
        local meta_ttl = math.max(d, tonumber(ARGV[6]))
        redis.call('EXPIRE',meta,meta_ttl)
        return {0,0,0,d,rst,now}
    end

    return {0,0,rst,0,rst,now}
    """

    def __init__(self, redis_client: redis.Redis, ban_after: int = 8, initial_ban: int = 300, max_ban: int = 86400, ban_counter: int = 3600, site_ban: bool = True):
        super().__init__(redis_client, ban_after, initial_ban, max_ban, ban_counter, site_ban)
        self.lua = self.redis.register_script(self.LUA_SCRIPT)

    async def hit(self, identifier: str, limit: int, window: int) -> Tuple[bool, int, int, int, int]:
        rl_key = self._key(identifier, limit, window)
        ban_key = self._ban_key(identifier, limit, window)
        meta_key = self._meta_key(rl_key)

        result = await self.lua(
            keys=[rl_key, ban_key, meta_key],
            args=[limit, window, self.ban_after, self.initial_ban, self.max_ban, self.ban_counter]
        )
        return result[0]==1, int(result[1]), int(result[4]), int(result[3]), int(result[5])
