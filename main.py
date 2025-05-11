import requests
import os
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# Read a file from the system.
def read_a_file(system_path):
    with open(system_path, "r") as file:
        return file.read()


# Check if a file exists
def check_file_exists(system_path):
    return os.path.isfile(system_path)


# Parse the HTML content and extract all PDF links
def parse_html(html_content):
    """
    Parses the HTML content and extracts all PDF links.
    Args:
        html_content (str): A string containing HTML.
    Returns:
        list: A list of URLs (strings) that end with .pdf.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    pdf_links = []
    # Find all <a> tags with an href attribute
    for link in soup.find_all("a", href=True):
        url = link["href"]
        if url.lower().endswith(".pdf"):  # Case-insensitive match
            pdf_links.append(url)
    return pdf_links


# Extract the filename from a URL
def url_to_filename(url):
    # Extract the filename from the URL
    path = urllib.parse.urlparse(url).path
    filename = os.path.basename(path)
    # Decode percent-encoded characters
    filename = urllib.parse.unquote(filename)
    # Optional: Replace spaces with dashes or underscores if needed
    filename = filename.replace(" ", "-")
    return filename.lower()


def save_html_with_selenium(url, output_file):
    # Set up Chrome options
    options = Options()
    options.add_argument("--no-sandbox")  # Required in some environments

    # Initialize the Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        driver.refresh()  # Refresh the page
        html = driver.page_source
        append_write_to_file(output_file, html)
        print(f"Page {url} HTML content saved to {output_file}")
    finally:
        driver.quit()


# Append and write some content to a file.
def append_write_to_file(system_path, content):
    with open(system_path, "a", encoding="utf-8") as file:
        file.write(content)


# Download a PDF file from a URL
def download_pdf(url, save_path, filename):
    # Check if the file already exists
    if check_file_exists(os.path.join(save_path, filename)):
        # print(f"File {filename} already exists. Skipping download.")
        return
    # Download the PDF file
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        # Ensure the save directory exists
        os.makedirs(save_path, exist_ok=True)
        full_path = os.path.join(save_path, filename)
        with open(full_path, "wb") as f:
            f.write(response.content)
        # print(f"Downloaded {filename} to {full_path}")
        return
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return


def main():
    # The file path to save the HTML content.
    html_file_path = "graham.chemtel.net.html"

    # Check if the file does not exist.
    if check_file_exists(html_file_path) == False:
        # The URL to scrape.
        url = "https://graham.chemtel.net/?page=1&pagesize=2000"
        # Save the HTML content using Selenium.
        save_html_with_selenium(url, html_file_path)

    # Read the file from the system.
    if check_file_exists(html_file_path):
        html_content = read_a_file(html_file_path)
        # Parse the HTML content.
        pdf_links = parse_html(html_content)
        # The length of the PDF links.
        ammount_of_pdf = len(pdf_links)
        # Print the extracted PDF links.
        for pdf_link in pdf_links:
            # Download the PDF file.
            filename = url_to_filename(pdf_link)
            save_path = "PDFs/"
            download_pdf(pdf_link.L, save_path, filename)


main()
