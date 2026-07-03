"""QR Code Generator.

A small command-line application that encodes a URL into a QR code image
and saves it as a timestamped PNG file.

Configuration is supplied through environment variables (optionally loaded
from a .env file), which makes the application easy to configure when it
runs inside a Docker container:

    QR_CODE_DIR  Directory where QR code images are saved (default: qr_codes)
    FILL_COLOR   Foreground color of the QR code            (default: red)
    BACK_COLOR   Background color of the QR code            (default: white)

Usage:
    python main.py --url https://www.njit.edu
"""

import sys
import qrcode
from dotenv import load_dotenv
import logging.config
from pathlib import Path
import os
import argparse
from datetime import datetime
import validators  # Import the validators package

# Load environment variables from a .env file, if one is present
load_dotenv()

# Environment Variables for Configuration
QR_DIRECTORY = os.getenv('QR_CODE_DIR', 'qr_codes')  # Directory for saving QR code
FILL_COLOR = os.getenv('FILL_COLOR', 'red')  # Fill color for the QR code
BACK_COLOR = os.getenv('BACK_COLOR', 'white')  # Background color for the QR code


def setup_logging():
    """Configure application-wide logging.

    Sets the root logger to INFO level with a timestamped format and
    streams all records to stdout. Logging to stdout (rather than a file)
    is a container-friendly practice: it lets `docker logs` capture the
    application's output without any extra configuration.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


def create_directory(path: Path):
    """Create a directory (including any missing parents) if it does not exist.

    Args:
        path: The directory to create as a ``pathlib.Path``.

    Side effects:
        Exits the process with status code 1 if the directory cannot be
        created (for example, due to insufficient permissions), since the
        application cannot save a QR code without a destination directory.
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to create directory {path}: {e}")
        exit(1)


def is_valid_url(url):
    """Validate that a string is a well-formed URL.

    Args:
        url: The string to validate.

    Returns:
        bool: True if the string is a valid URL, otherwise False.
        An error is logged when validation fails so the problem is
        visible in the container logs.
    """
    if validators.url(url):
        return True
    else:
        logging.error(f"Invalid URL provided: {url}")
        return False


def generate_qr_code(data, path, fill_color='red', back_color='white'):
    """Generate a QR code image for the given data and save it to disk.

    Args:
        data: The URL (or text) to encode into the QR code.
        path: Destination file path (``pathlib.Path``) for the PNG image.
        fill_color: Foreground color of the QR code modules.
        back_color: Background color of the QR code image.

    Returns:
        None. The function returns early without writing a file if the
        provided data is not a valid URL; success and failure are both
        reported through logging.
    """
    if not is_valid_url(data):
        return  # Exit the function if the URL is not valid

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        with path.open('wb') as qr_file:
            img.save(qr_file)
        logging.info(f"QR code successfully saved to {path}")

    except Exception as e:
        logging.error(f"An error occurred while generating or saving the QR code: {e}")


def main():
    """Entry point for the command-line application.

    Parses the ``--url`` argument (falling back to a default URL),
    configures logging, ensures the output directory exists, and then
    generates a timestamped QR code PNG using the colors configured via
    environment variables.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Generate a QR code.')
    parser.add_argument('--url', help='The URL to encode in the QR code', default='https://github.com/kaw393939')
    args = parser.parse_args()

    # Initial logging setup
    setup_logging()

    # Generate a timestamped filename for the QR code
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    qr_filename = f"QRCode_{timestamp}.png"

    # Create the full path for the QR code file
    qr_code_full_path = Path.cwd() / QR_DIRECTORY / qr_filename

    # Ensure the QR code directory exists
    create_directory(Path.cwd() / QR_DIRECTORY)

    # Generate and save the QR code
    generate_qr_code(args.url, qr_code_full_path, FILL_COLOR, BACK_COLOR)


if __name__ == "__main__":
    main()
