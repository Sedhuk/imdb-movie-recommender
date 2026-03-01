import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def open_imdb_2024(driver, start):
    url = f"https://www.imdb.com/search/title/?year=2024&start={start}"
    driver.get(url)
    time.sleep(3)
    
def get_movie_links(driver, limit=50):
    movies = []

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'ipc-title-link-wrapper')]"))
    )

    elements = driver.find_elements(By.XPATH, "//a[contains(@class,'ipc-title-link-wrapper')]")

    for elem in elements[:limit]:
        title = elem.text
        link = elem.get_attribute("href")

        # Avoid duplicate or invalid links
        if "/title/" in link:
            movies.append((title, link))

    return movies

def get_storyline(driver, movie_url):
    driver.get(movie_url)
    time.sleep(2)

    try:
        storyline = driver.find_element(By.XPATH, "//span[@data-testid='plot-xl']").text
    except:
        try:
            storyline = driver.find_element(By.XPATH, "//span[@data-testid='plot-l']").text
        except:
            storyline = "Not Available"

    return storyline

def main():
    driver = setup_driver()

    all_movies = []
    start = 1

    while True:
        print(f"Scraping page starting at {start}...")

        open_imdb_2024(driver, start)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'ipc-title-link-wrapper')]"))
            )
        except:
            print("No more movies found. Ending pagination.")
            break

        elements = driver.find_elements(By.XPATH, "//a[contains(@class,'ipc-title-link-wrapper')]")

        if not elements:
            break

        for elem in elements:
            title = elem.text
            link = elem.get_attribute("href")

            if "/title/" in link:
                all_movies.append((title, link))

        start += 50  # Move to next page
        time.sleep(2)

    print(f"Total movies collected: {len(all_movies)}")

    # Remove duplicates
    all_movies = list(set(all_movies))

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
    df.to_csv("imdb_2024_full_movies.csv", index=False)

    print("Full 2024 data saved successfully!")

if __name__ == "__main__":
    main()