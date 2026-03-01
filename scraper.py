import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ------------------------------
# Setup Chrome Driver
# ------------------------------
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


# ------------------------------
# Extract Storyline
# ------------------------------
def get_storyline(driver, movie_url):
    driver.get(movie_url)
    time.sleep(2)

    try:
        storyline = driver.find_element(
            By.XPATH,
            "//span[@data-testid='plot-xl']"
        ).text
    except:
        try:
            storyline = driver.find_element(
                By.XPATH,
                "//span[@data-testid='plot-l']"
            ).text
        except:
            storyline = "Not Available"

    return storyline


# ------------------------------
# Main Scraper
# ------------------------------
def main():
    driver = setup_driver()

    all_movies = []
    start = 1
    MAX_MOVIES = 1000  # Change this if needed

    print("Starting IMDb 2024 scraping...\n")

    while len(all_movies) < MAX_MOVIES:

        print(f"Scraping page starting at {start}...")

        url = (
            "https://www.imdb.com/search/title/"
            "?title_type=feature"
            "&release_date=2024-01-01,2024-12-31"
            f"&start={start}&count=50"
        )

        driver.get(url)
        time.sleep(3)

        elements = driver.find_elements(
            By.XPATH,
            "//div[contains(@class,'ipc-metadata-list-summary-item')]"
            "//a[contains(@href,'/title/tt')]"
        )

        if not elements:
            print("No more movies found.")
            break

        page_count = 0

        for elem in elements:
            title = elem.text
            link = elem.get_attribute("href")

            if title and "/title/tt" in link:
                all_movies.append((title, link))
                page_count += 1

            if len(all_movies) >= MAX_MOVIES:
                break

        print(f"Movies found on this page: {page_count}")
        start += 50
        time.sleep(2)

    print(f"\nTotal movies collected: {len(all_movies)}\n")

    # ------------------------------
    # Extract Storylines
    # ------------------------------
    movie_data = []

    for index, (title, link) in enumerate(all_movies):
        print(f"Scraping {index+1}/{len(all_movies)}: {title}")

        storyline = get_storyline(driver, link)

        movie_data.append({
            "Movie Name": title,
            "Storyline": storyline
        })

        time.sleep(1)

    driver.quit()

    df = pd.DataFrame(movie_data)
    df.to_csv("imdb_2024_movies.csv", index=False)

    print("\nData saved successfully as imdb_2024_movies.csv")


# ------------------------------
if __name__ == "__main__":
    main()