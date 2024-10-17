#!/usr/bin/python
from bs4 import BeautifulSoup
import requests
from hurry.filesize import size


def fetch_content_info(url):
    """Fetch content type and title from the given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for non-2xx status codes

        content_type = response.headers.get("content-type", "").lower()
        content_length = response.headers.get("content-length")

        if content_length is None:
            content_length = "Not provided"

        soup = BeautifulSoup(response.text, "html.parser")
        # Get title and decode it properly
        title = soup.title.string.strip() if soup.title else "No title found"
        return title, content_type, content_length

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None, None, None


def main(msg):
    output = []
    words = msg.split()
    for word in words:
        if "://" in word:
            title, content_type, content_length = fetch_content_info(word)
            if title:
                output.append(title)
            else:
                output.append(content_type or "Unknown")

            # Only append content length if it's a valid integer
            if content_length and content_length.isdigit():
                output.append(size(int(content_length)))

    if output:
        return " ".join(output).encode("utf-8", "replace")
    return False


if __name__ == "__main__":
    messages = [
        "https://russell.ballestrini.net for a good read",
        "erbody dance https://www.youtube.com/watch?v=LaTGrV58wec",
        "OUCH! https://russell.ballestrini.net/uploads/2012/06/dedication-eye-chemical-burn.jpg",
        "click the image to watch the video https://media.unturf.com/c/b02853d2-7976-11ec-934a-257a83652528/hook-blues-traveler-official-video",
    ]

    for msg in messages:
        result = main(msg)
        if result:
            print(f"Processed: {msg}\nResult: {result.decode('utf-8')}")
