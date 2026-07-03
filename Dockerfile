# Use the official Python image from DockerHub as the base image.
# The slim variant keeps the image small and reduces the attack surface.
FROM python:3.12-slim-bullseye

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file first and install dependencies.
# Copying it before the rest of the source code lets Docker cache this
# layer, so dependencies are only reinstalled when requirements.txt changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and the directories for logs and QR codes,
# and give the non-root user ownership so it can write to them.
RUN useradd -m myuser && mkdir logs qr_codes && chown myuser:myuser logs qr_codes

# Copy the rest of the application's source code into the container,
# setting ownership to 'myuser'
COPY --chown=myuser:myuser . .

# Switch to the non-root user for security: if the application is ever
# compromised, the attacker does not get root inside the container.
USER myuser

# ENTRYPOINT fixes the executable; CMD supplies default arguments that
# can be overridden at 'docker run' time (e.g. --url http://www.njit.edu).
ENTRYPOINT ["python", "main.py"]
CMD ["--url", "http://github.com/kaw393939"]
