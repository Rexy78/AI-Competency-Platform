# Microservices Architecture

Microservices architecture designs software as a collection of small, autonomous, loosely coupled services organized around business domains.

## Core Patterns
- API Gateway (routing, rate limiting, SSL termination, auth verification)
- Service Discovery (Eureka, Consul, Kubernetes DNS)
- Communication: Synchronous REST / gRPC vs Asynchronous Event-Driven (Kafka, RabbitMQ)
- Database-per-service pattern and distributed transaction handling (Saga pattern)
- Resiliency patterns: Circuit Breakers (Resilience4j), retries, fallbacks
- Observability: Distributed tracing (OpenTelemetry, Jaeger), centralized logging (ELK / Loki), metrics (Prometheus, Grafana)
