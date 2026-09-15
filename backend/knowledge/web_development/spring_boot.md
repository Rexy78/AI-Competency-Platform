# Spring Boot

Spring Boot is an opinionated, production-ready framework built on top of the Spring ecosystem for Java.

## Why Spring Boot Matters
- Rapid setup with Spring Initializr and starter dependencies
- Embedded servers (Tomcat, Netty) eliminating separate WAR deployments
- Auto-configuration and dependency injection (`@Autowired`, `@Service`, `@Repository`, `@RestController`)
- Production-grade metrics, health checks, and externalized configuration via Spring Actuator

## Standard Architecture
- Controller Layer: `@RestController`, `@GetMapping`, `@PostMapping`, `@RequestBody`, `@PathVariable`
- Service Layer: Business logic and transaction management (`@Transactional`)
- Persistence Layer: Spring Data JPA, Hibernate, EntityManager, Repository interfaces
- Security: Spring Security, JWT token filters, OAuth2

## Learning Roadmap
1. Core Java OOP and Maven/Gradle build tools
2. Spring Boot basics and dependency injection
3. RESTful API development with validation (`@Valid`) and exception handlers (`@ControllerAdvice`)
4. Database persistence with Spring Data JPA and MySQL/PostgreSQL
5. Security with JWT and containerization with Docker
