# Kubernetes (K8s) & Container Orchestration

Kubernetes automates deployment, scaling, and management of containerized applications.

## Key Primitives
- Pods: Smallest deployable units wrapping one or more containers
- Deployments: Declarative updates for Pods with rolling updates and rollbacks
- Services: ClusterIP, NodePort, LoadBalancer for networking and load balancing
- Ingress: HTTP/HTTPS routing into cluster services
- ConfigMaps & Secrets: Decoupling configuration and sensitive data from image builds
- Namespaces: Virtual cluster separation for environments (dev, staging, prod)
