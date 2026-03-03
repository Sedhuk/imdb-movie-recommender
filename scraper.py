import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Setup WebDriver (Ensure you have the correct driver for your browser)
driver = webdriver.Chrome() 

# CSV Setup
csv_file = open('imdb_movies_2024(1).csv', 'w', newline='', encoding='utf-8')
writer = csv.writer(csv_file)
writer.writerow(['Title', 'Storyline'])

def scrape_imdb():
    for month in range(1, 13):
        # Format month as 01, 02, etc.
        month_str = f"{month:02d}"
        url = f"https://www.imdb.com/search/title/?title_type=feature&release_date=2024-{month_str},2024-{month_str}"
        
        print(f"Processing: {url}")
        driver.get(url)

        # 1. Click "See More" until all data is loaded
        while True:
            try:
                # Wait up to 5 seconds for the button to be clickable
                see_more_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".ipc-see-more__button"))
                )
                driver.execute_script("arguments[0].click();", see_more_btn)
                time.sleep(2)  # Brief pause for content to render
            except (NoSuchElementException, TimeoutException):
                print(f"Finished loading all results for month {month_str}")
                break

        # 2. Extract data once the button is gone
        items = driver.find_elements(By.CSS_SELECTOR, ".ipc-metadata-list-summary-item")
        print(f"Found {len(items)} items for month {month_str}")
        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, ".ipc-title__text").text
                # Removing the rank number from the title (e.g., "1. Gladiator II")
                clean_title = title.split('. ', 1)[-1] if '. ' in title else title
                
                storyline = item.find_element(By.CSS_SELECTOR, ".ipc-html-content-inner-div").text
                
                writer.writerow([clean_title, storyline])
            except Exception as e:
               print(f"Error extracting an item: {e}")
               continue

    print("Scraping Complete!")
    csv_file.close()
    driver.quit()

scrape_imdb()