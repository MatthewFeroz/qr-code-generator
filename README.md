# QR Code Generator — Dockerized (IS601 Module 7)

A command-line Python application that encodes a URL into a QR code PNG,
packaged as a secure Docker image and built/tested automatically with
GitHub Actions.

- **GitHub repository:** https://github.com/MatthewFeroz/qr-code-generator
- **DockerHub image:** https://hub.docker.com/r/matthewferoz/qr-code-generator-app

## How it works

`main.py` accepts a `--url` argument, validates it, and saves a QR code as
`qr_codes/QRCode_<timestamp>.png`. Behavior is configured through
environment variables so the same image can be reconfigured at run time:

| Variable      | Purpose                          | Default    |
|---------------|----------------------------------|------------|
| `QR_CODE_DIR` | Directory where PNGs are saved   | `qr_codes` |
| `FILL_COLOR`  | QR code foreground color         | `red`      |
| `BACK_COLOR`  | QR code background color         | `white`    |

## Running locally (without Docker)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py --url https://www.njit.edu
```

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Docker usage

Build the image:

```bash
docker build -t qr-code-generator-app .
```

Run a container with the default URL:

```bash
docker run -d --name qr-generator qr-code-generator-app
docker logs qr-generator
```

Run with a custom URL and a volume mount so the QR code is saved to your
host machine:

```bash
docker run -d --name qr-generator \
  -v "$PWD/qr_codes:/app/qr_codes" \
  qr-code-generator-app --url http://www.njit.edu
```

Clean up:

```bash
docker stop qr-generator && docker rm qr-generator
```

Or use Docker Compose (builds the image, sets environment variables,
mounts `./qr_codes`, and runs against the NJIT homepage):

```bash
docker compose up --build
```

Pull the published image from DockerHub instead of building it:

```bash
docker pull matthewferoz/qr-code-generator-app
docker run --rm -v "$PWD/qr_codes:/app/qr_codes" \
  matthewferoz/qr-code-generator-app --url http://www.njit.edu
```

## Security design of the Dockerfile

- **Minimal base image** — `python:3.12-slim-bullseye` keeps the attack
  surface and image size small.
- **Non-root user** — the app runs as `myuser`, so a compromised process
  has no root privileges inside the container.
- **Scoped ownership** — only `logs/` and `qr_codes/` are writable by the
  application user.
- **Layer caching** — `requirements.txt` is copied and installed before
  the source code, so dependency layers are reused across rebuilds.
- **ENTRYPOINT + CMD** — the executable is fixed while default arguments
  remain overridable at `docker run` time.

## Continuous Integration

`.github/workflows/ci.yml` runs on every push and pull request to `main`:

1. **test** — installs pinned dependencies and runs the pytest suite
   (7 tests) on Python 3.12.
2. **docker** — builds the image, then smoke-tests it by running a real
   container and asserting the "QR code successfully saved" log line.
   When `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN` secrets are configured,
   it also pushes `matthewferoz/qr-code-generator-app:latest` to DockerHub.

## Evidence

- Captured container run logs: [`docs/evidence/container-logs.txt`](docs/evidence/container-logs.txt)
- Reflection document: [`docs/reflection.md`](docs/reflection.md)
