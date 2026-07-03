# Module 7 Reflection — Dockerizing the QR Code Generator

**Course:** IS601 — Summer 2026
**Author:** Matthew Feroz

## What I did

For this assignment I containerized a Python QR code generator. Starting
from the provided application, I wrote a Dockerfile that builds a secure,
minimal image; verified the container end-to-end (default run, log
inspection, volume mounts, and command-line overrides); wired up a GitHub
Actions pipeline that runs the test suite and builds/smoke-tests the image
on every push; and published the image to DockerHub as
`matthewferoz/qr-code-generator-app`.

## Key experiences

**ENTRYPOINT vs CMD finally clicked.** I had previously treated these as
interchangeable. Splitting them — `ENTRYPOINT ["python", "main.py"]` with
`CMD ["--url", ...]` as a default argument — made the container behave
like a real CLI tool: `docker run qr-code-generator-app --url
http://www.njit.edu` swaps only the argument, not the executable. Seeing
the override work from both `docker run` and the `command:` key in
docker-compose.yml tied the whole model together.

**Layer caching changes how you order a Dockerfile.** Copying
`requirements.txt` and running `pip install` *before* copying the rest of
the source means code changes rebuild in about a second instead of
re-downloading every dependency. Watching the cached layers get reused on
the second build made the reasoning concrete.

**Environment variables are the bridge between code and container.**
Because the app reads `QR_CODE_DIR`, `FILL_COLOR`, and `BACK_COLOR` from
the environment, the same immutable image can produce different output in
different deployments — configuration lives in the run command or compose
file, not in the code.

**Volumes make container output real.** A container's filesystem
disappears when the container is removed, so the generated PNGs initially
existed only inside the container. Mounting `./qr_codes:/app/qr_codes`
made the QR codes appear on my host machine, which is also how I verified
the app actually worked.

## Challenges faced

**Running as a non-root user surfaced permission issues by design.** The
first thing I noticed is that `myuser` cannot write anywhere it isn't
explicitly given ownership. The Dockerfile has to create `logs/` and
`qr_codes/` and `chown` them *before* switching users, and the `COPY`
of source code needs `--chown=myuser:myuser`. Getting the order of those
instructions right is the difference between a working container and a
`PermissionError`.

**Making CI green without leaking credentials.** The workflow needs
DockerHub credentials to push the image, but hardcoding them is not an
option and a missing secret shouldn't fail the build. I solved this by
guarding the login/push steps with a condition on the secret so the
pipeline always tests and builds, and only pushes when
`DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN` repository secrets exist.

**Testing code that touches the filesystem.** The unit tests need to
verify that a real PNG is written without polluting the repository. Using
pytest's `tmp_path` fixture kept every test isolated, and checking the
PNG magic bytes (`\x89PNG...`) proved the output is a genuine image rather
than just a non-empty file.

## What I learned

Docker eliminates the "it works on my machine" problem by making the
runtime environment part of the artifact. The image I pushed to DockerHub
carries its own Python version and pinned dependencies, so it runs
identically on my Mac, on the GitHub Actions Ubuntu runner, and on any
machine that pulls it. Combined with CI that refuses to build the image
unless the tests pass, this is the core DevOps loop: version-controlled
code, automated verification, and a reproducible, shippable artifact.
