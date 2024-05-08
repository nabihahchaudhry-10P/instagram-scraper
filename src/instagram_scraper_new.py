import time
import datetime
from logger import MyLogger
from bs4 import BeautifulSoup
from selenium import webdriver
from pymongo import MongoClient
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.instagram.com/explore/tags/"


class Scraper:
    def __init__(self, keyword):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.keyword = keyword
        self.logger = MyLogger()


    def search_instagram(self, max_page=10, max_post=1000):
        start_dt = datetime.datetime.now()
        url = BASE_URL + self.keyword + "/"
        self.driver.get(url)

        # Wait to finish loading to get all dynamically-loaded content on webpage
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
        )

        # Extract post data
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        posts = list()
        errors = 0

        # Get all IG pictures
        elements = soup.find_all("a", class_="x1i10hfl")

        for element in elements:
            if len(posts) == max_post:
                break

            data = dict(
                link=element["href"],
                image=element.find("img")["src"],
                text=element.find("img")["alt"],
                datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                hashtag=self.keyword,
            )

            posts.append(data)

        for post in posts:
            # Go on IG picture link
            self.driver.get(post["image"])
            time.sleep(0.3)

            try:
                element = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "article > div > section > div"
                )
            except Exception as error:
                self.logger.error(f"Error getting post image: {error}")
                errors += 1
                continue

            try:
                post["datetime"] = self.driver.find_element(
                    By.TAG_NAME,
                    "time"
                ).get_attribute("datetime")
            except Exception as error:
                self.logger.error(f"Error getting post datetime: {error}")
                pass

            # Count for like(s)/view(s)
            try:
                popularity_count = element.find_element(
                    By.CSS_SELECTOR,
                    "span > span"
                ).text
            except Exception as error:
                self.logger.error(f"Error getting post popularity count {error}")
                popularity_count = len(element.find_element(By.TAG_NAME, "a"))

            # Save like(s)/view(s) and video url
            try:
                post["video"] = self.driver.find_element(
                    By.TAG_NAME,
                    "video"
                ).get_attribute("src")
                post["views"] = popularity_count
            except Exception as error:
                self.logger.error(f"Error getting post likes {error}")
                post["likes"] = popularity_count

            print()

        end_dt = datetime.datetime.now()
        time_diff = end_dt - start_dt
        print(f"Total: {len(posts)} post(s)")
        print(f"Total: {errors} error(s)")
        print(f"Total: {time_diff.seconds} second(s)")

        return posts

    def insert_into_mongodb(self, posts):
        try:
            client = MongoClient("mongodb://localhost:27017/")
            data_base = client["instagram"]
            collection = data_base["posts"]
            collection.insert_many(posts)
            client.close()
            print("Data successfully stored in MongoDB.")
            self.logger.info("Successfully added post(s) to the database")
        except Exception as error:
            self.logger.error(f"Error adding post(s) to database: {error}")
            print(f"Error occurred while inserting Instagram data into MongoDB:\n {error}")

    def get_posts(self):
        print("Searching Instagram...\n")
        try:
            posts = self.search_instagram(1, 9)
            if posts:
                self.insert_into_mongodb(posts)
            else:
                print("No posts found.")
        except Exception as error:
            self.logger.error(f"Unable to get data from Instagram: {error}")
            print(f"Unable to get data from Instagram: {error}")


if __name__ == "__main__":
    keyword = input("Enter a keyword to search on Instagram: ")
    instagram_scraper = Scraper(keyword)

    instagram_scraper.get_posts()
