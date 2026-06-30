# ChatGPT Responses

Here is the complete, production-ready GitHub Actions workflow file that handles linting, testing, and multi-stage secure container publication to Docker Hub.

```yaml
name: CI/CD Production Pipeline

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  # --- Stage 1: Integration & Testing ---
  test:
    name: Build & Test Application
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository Code
        uses: actions/checkout@v4

      - name: Setup Node.js Runtime environment
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm' # Automates cache handling for node_modules dependencies

      - name: Install Dependencies (Clean Install)
        run: npm ci

      # Generates build artifacts to verify compilation integrity before running tests
      - name: Build Application Codebase
        run: npm run build --if-present

      - name: Execute Test Suite
        run: npm test

  # --- Stage 2: Containerization & Continuous Deployment ---
  deploy:
    name: Build & Publish Container Image
    runs-on: ubuntu-latest
    needs: test # Enforces that the pipeline stops if tests fail
    if: github.event_name == 'push' && github.ref == 'refs/heads/main' # Only push to Docker Hub on actual merge/push events

    steps:
      - name: Checkout Repository Code
        uses: actions/checkout@v4

      # Sets up QEMU for potential multi-architecture builds down the line
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      # Sets up Docker Buildx for enhanced layer caching features
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Authenticate to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and Push Docker Image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          # Re-tags the image with both the commit SHA (for traceability) and 'latest'
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/node-app:latest
            ${{ secrets.DOCKER_USERNAME }}/node-app:${{ github.sha }}
          cache-from: type=gha # Leverages GitHub Actions native cache storage for layer caching
          cache-to: type=gha,mode=max

```
