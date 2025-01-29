import time

from selenium_client.selenium_client import SeleniumClient

def scrape_website():
    url = "https://www.google.com"

    with SeleniumClient() as client:
        try:
            client.navigate(url)
            time.sleep(5)
        except:
            raise Exception("Failed to scrape website")

if __name__ == "__main__":
    scrape_website()