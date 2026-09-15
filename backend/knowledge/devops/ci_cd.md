# Continuous Integration & Continuous Deployment (CI/CD)

CI/CD bridges software development and IT operations through automated pipelines.

## Pipeline Stages
- Build: Compile code, install dependencies, linting, unit test execution
- Test: Integration tests, code coverage thresholds, security vulnerability scans (SAST/DAST)
- Package: Multi-stage Docker image build, semantic tagging, registry push (Docker Hub / ECR / GHCR)
- Deploy: Automated rollout to staging and production (GitHub Actions, GitLab CI, Jenkins, ArgoCD)
