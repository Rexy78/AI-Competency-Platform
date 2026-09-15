# Java Backend Technical Interview Questions

High-frequency questions asked in top Java / Spring Boot interviews:

## Concepts & Answers
- **ArrayList vs LinkedList**: ArrayList is backed by a dynamic array offering O(1) random access but O(N) worst-case insertion/deletion. LinkedList uses a doubly-linked list with O(1) node insertion/deletion once positioned, but O(N) traversal.
- **HashMap Internals**: Uses an array of buckets (Node/Entry). Collisions handled via linked lists; converts to Red-Black Tree in Java 8+ when bucket threshold exceeds TREEIFY_THRESHOLD (8) for O(log N) worst-case lookup.
- **Spring Boot Annotations**: `@SpringBootApplication` combines `@Configuration`, `@EnableAutoConfiguration`, `@ComponentScan`.
- **JPA N+1 Problem**: Occurs when fetching parent entities causes N additional select queries for lazy-loaded children. Solved using `JOIN FETCH`, `@EntityGraph`, or batch fetching (`@BatchSize`).
