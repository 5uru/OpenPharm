import requests
from bs4 import BeautifulSoup
import concurrent.futures
import logging
from tqdm import tqdm
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_link(link):
    """Process a single article link and return the PDF links found."""
    try:
        response = requests.get(link, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            pdf_links = soup.select("p.plant-reference-linkpdf a")
            return [pdf_link["href"] for pdf_link in pdf_links]
        else:
            logger.warning(f"Failed to fetch {link}: Status code {response.status_code}")
    except Exception as e:
        logger.error(f"Error processing {link}: {str(e)}")

    return []

"""
for i in range(1, 356):
    url = f"http://www.ethnopharmacologia.org/recherche-dans-prelude/page/{i}/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # all link on ul > class="preludeList lwsClear"
        links = soup.select("ul.preludeList.lwsClear a")
        print(f"Page {i} : {len(links)} links found")
        # add on txt file
        with open("ethnopharmacologia_links.txt", "a") as file:
            for link in links:
                file.write(link["href"] + "\n")"""

"""# Read article links
articles_links = []
with open("ethnopharmacologia_links.txt", "r") as file:
    articles_links.extend(line.strip() for line in file)

logger.info(f"Processing {len(articles_links)} article links...")

# Create a set to store unique PDF links
all_pdf_links = set()

# Process links in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    # Submit all tasks and get future objects
    future_to_link = {executor.submit(process_link, link): link for link in articles_links}

    # Process results as they complete with progress bar
    for future in tqdm(concurrent.futures.as_completed(future_to_link), total=len(articles_links)):
        link = future_to_link[future]
        try:
            pdf_links = future.result()
            all_pdf_links.update(pdf_links)
            logger.debug(f"Found {len(pdf_links)} PDF links from {link}")
        except Exception as e:
            logger.error(f"Error retrieving result for {link}: {str(e)}")

# Write unique PDF links to file
with open("ethnopharmacologia_pdf_links.txt", "w") as file:
    for pdf_link in all_pdf_links:
        file.write(pdf_link + "\n")

logger.info(f"Completed. Total unique PDF links found: {len(all_pdf_links)}")"""


all_pdf_links = []
with open("ethnopharmacologia_pdf_links.txt", "r") as file:
    all_pdf_links.extend(line.strip() for line in file)

logger.info(f"Downloading {len(all_pdf_links)} PDF files...")
# Download PDF files on data folder
for pdf_link in tqdm(all_pdf_links):
    try:
        response = requests.get(pdf_link, timeout=30)
        if response.status_code == 200:
            with open(f"data/{pdf_link.split('/')[-1]}", "wb") as file:
                file.write(response.content)
        else:
            logger.warning(f"Failed to download {pdf_link}: Status code {response.status_code}")
    except Exception as e:
        logger.error(f"Error downloading {pdf_link}: {str(e)}")