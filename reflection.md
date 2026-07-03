# Module 7 Reflection on Dockerizing the QR Code Generator

Matthew Feroz, IS601, Summer 2026

## What I did

For this project I containerized a Python QR code generator. I wrote a Dockerfile that builds a small, secure image, made sure the container actually worked end to end, set up a GitHub Actions pipeline that tests the code and builds the image on every push, and then published the image to DockerHub as matthewferoz/qr-code-generator-app.

## Key experiences

I learned a ton on this project. The ENTRYPOINT and CMD split finally made sense to me. ENTRYPOINT locks in the program and CMD is just a default argument, so if I run the container with a different --url I'm only swapping the argument, not the entirety of the program. The same trick works from the command key in docker-compose.

## Challenges faced

Running as a non-root user caused permission errors on purpose, and I hit them. The Dockerfile has to create and chown the logs and qr_codes folders before switching users, and the source copy needs the chown flag too. 

The CI pipeline also needs DockerHub credentials to push the image, but I didn't want a missing secret to break the build. So I put the login and push steps behind a condition. The workflow always tests and builds, and it only pushes when the repository secrets are actually there.

Testing code that writes files took some thought too. The pytest tmp_path fixture kept every test isolated, and checking the PNG magic bytes proved the output was a real image and not just some non-empty file.

## What I learned

Docker kills the "bro it works on my machine" problem by making the environment part of the thing you ship. The image carries its own Python version and pinned dependencies, so it runs the same on my Mac, on the CI runner, and on any machine that pulls it. Pair that with a pipeline that only builds the image when the tests pass and you've basically got the core DevOps loop.

Before this I had only ever used Docker to run other people's stuff. Now I've actually built with it, and it's way less intimidating than it looked.