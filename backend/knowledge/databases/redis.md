# Redis & In-Memory Caching

Redis (Remote Dictionary Server) is an open-source, in-memory data structure store used as a database, cache, message broker, and streaming engine.

## Use Cases
- High-speed caching (Cache-Aside, Write-Through, Write-Back patterns)
- Session state management and JWT blacklisting
- Rate limiting and API throttling with token bucket algorithms
- Pub/Sub messaging and leaderboards (Sorted Sets `ZSET`)
- TTL (Time To Live) automatic expiration policies (LRU, LFU)
