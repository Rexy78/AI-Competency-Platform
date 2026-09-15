# Hibernate & Spring Data JPA

Hibernate is an Object-Relational Mapping (ORM) framework for Java, implementing the Java Persistence API (JPA / Jakarta Persistence) specification.

## Core Concepts
- Entity mappings: `@Entity`, `@Table`, `@Id`, `@GeneratedValue`, `@Column`
- Relationships: `@OneToOne`, `@OneToMany`, `@ManyToOne`, `@ManyToMany`
- Fetch types: `FetchType.LAZY` vs `FetchType.EAGER` (avoiding N+1 query problems via `JOIN FETCH` or `@EntityGraph`)
- Cascading operations: `CascadeType.ALL`, `CascadeType.PERSIST`
- Repositories: `JpaRepository<T, ID>`, derived query methods (`findByEmail`), custom `@Query` with JPQL or native SQL
