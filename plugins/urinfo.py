#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
from hurry.filesize import size


def fetch_content_info(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for non-2xx status codes

        content_type = response.headers.get("content-type", "Unknown")
        content_length = response.headers.get("content-length")

        if "text/html" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else None
            return title, content_type, content_length

        # For other content types, you might not get a 'title', so return what you can.
        return None, content_type, content_length
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

            if content_length:
                output.append(size(int(content_length)))

    if output:
        return " ".join(output).encode("ascii", "replace")
    return False


if __name__ == "__main__":
    messages = [
        "http://russell.ballestrini.net for a good read",
        "erbody dance http://www.youtube.com/watch?v=12VUjgYMm1U",
        "OUCH! http://russell.ballestrini.net/wp-content/uploads/2012/06/dedication-eye-chemical-burn.jpg",
    ]

    for msg in messages:
        result = main(msg)
        if result:
            print(f"Processed: {msg}\nResult: {result.decode('ascii')}")
