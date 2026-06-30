# Claude Sonnet Responses

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '20'
  IMAGE_NAME: ${{ secrets.DOCKER_USERNAME }}/node-web-app

jobs:
  # ============================================================
  # Job 1: Install dependencies and run tests
  # ============================================================
  test:
    name: Test
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Node.js ${{ env.NODE_VERSION }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

  # ============================================================
  # Job 2: Build the Docker image (validates Dockerfile on every
  # push/PR, but doesn't push -- pushing happens in the deploy job)
  # ============================================================
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: test

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: false
          tags: ${{ env.IMAGE_NAME }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ============================================================
  # Job 3: Log in to Docker Hub and push the image
  # Only runs on a direct push to main (not on PRs, since PRs from
  # forks won't have access to the repo's secrets anyway).
  # ============================================================
  deploy:
    name: Push to Docker Hub
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ${{ env.IMAGE_NAME }}:${{ github.sha }}
            ${{ env.IMAGE_NAME }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Design Notes
The pipeline is split into three jobs (`test` → `build` → `deploy`) chained with `needs`, so a failure at any stage stops the pipeline before it reaches Docker Hub — tests must pass before the image is even built, and the image must build successfully before anything is pushed.

The `build` job runs on every push and PR to validate that the Dockerfile actually builds, but doesn't push anything (`push: false`). The `deploy` job rebuilds and pushes, gated by `if: github.event_name == 'push' && github.ref == 'refs/heads/main'`. This guard matters because PRs (including ones from forked repos) don't have access to repository secrets like `DOCKER_PASSWORD`, so attempting a Docker Hub login on a PR run would simply fail — explicitly excluding PRs from the deploy job avoids that broken run rather than relying on the secret being silently empty.

The image is tagged both with the commit SHA (`${{ github.sha }}`, as required) and `latest`, since the SHA tag gives an audit trail while `latest` keeps a convenient floating reference for anyone pulling without specifying a version — drop the `latest` line if you want strictly immutable SHA-only tags.

`docker/build-push-action` is used instead of raw `docker build`/`docker push` commands, since it handles Buildx caching (`cache-from`/`cache-to: type=gha`) automatically, which meaningfully speeds up repeated builds by reusing layers across workflow runs.
