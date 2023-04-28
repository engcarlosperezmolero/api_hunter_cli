import subprocess
import sys


def install_chromium():
    try:
        # Install the playwright package if not already installed
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])

        # Install the Chromium browser for playwright
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        print("Chromium installation for Playwright is successful.")
    except subprocess.CalledProcessError as error:
        print("An error occurred during Chromium installation for Playwright.")
        sys.exit(error.returncode)


if __name__ == "__main__":
    install_chromium()
