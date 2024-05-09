import datetime
from selenium import webdriver
from pymongo import MongoClient
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from logger import MyLogger
from constants import MongoDB
from constants import Messages
from constants import Constants

class Scraper:
    """Instagram Crawler"""
    def __init__(self, keyword):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.keyword = keyword
        self.logger = MyLogger()

    def search_instagram(self, max_page=10, max_post=1000):
        """Search Instagram Posts"""
        start_dt = datetime.datetime.now()
        url = Constants.base_url.value + self.keyword + "/"
        self.driver.get(url)

        # Wait to finish loading to get all dynamically-loaded content on webpage
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "article"))
        )

        # Get all IG pictures
        posts = []
        post_elements = self.driver.find_elements(By.CSS_SELECTOR, "article > div > div > div > div > div > a")

        # Extract post data
        for post_element in post_elements:
            if len(posts) == max_post:
                break

            data = {
                "link": post_element.get_attribute("href"),
                "image": post_element.find_element(By.TAG_NAME, "img").get_attribute("src"),
                "text": post_element.find_element(By.TAG_NAME, "img").get_attribute("alt"),
                "date_scraped": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "hashtag": self.keyword
            }

            posts.append(data)

        for post in posts:
            # Go on IG picture link
            try:
                self.driver.get(post["link"])

                # Wait to finish loading to get all dynamically-loaded content on webpage
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "article"))
                )

                # Extracting additional post data
                likes_component = self.driver.find_element(By.CSS_SELECTOR, "article > div > div > div > div > section > div")
                try:
                    likes_element = likes_component.find_element(By.CSS_SELECTOR, "div > div > span > a > span > span")
                    post["likes"] = likes_element.text
                except NoSuchElementException:
                    post["likes"] = likes_component.text

                time_element = self.driver.find_element(By.CSS_SELECTOR, "time.x1p4m5qa")
                post["datetime"] = time_element.get_attribute("datetime")
                post["datetime_text"] = time_element.text

                try:
                    poster_profile_component = self.driver.find_element(By.CSS_SELECTOR, "article > div > div > div > div > div > header")
                    poster_profile_element = poster_profile_component.find_element(By.CSS_SELECTOR, "div > div > div > div > div > span > a")
                    post["poster"] = poster_profile_element.text
                    post["poster_profile"] = poster_profile_element.get_attribute("href")
                except NoSuchElementException:
                    poster_profile_component = self.driver.find_element(By.CSS_SELECTOR, "header._aaqw")
                    poster_profile_element = poster_profile_component.find_element(By.CSS_SELECTOR, "div > div > div > div > div > span > a")
                    post["poster"] = poster_profile_element.text
                    post["poster_profile"] = poster_profile_element.get_attribute("href")

                # Extracting comments under the post
                comments_component = self.driver.find_element(By.CSS_SELECTOR, "ul._a9z6")
                comments = comments_component.find_elements(By.CSS_SELECTOR, "div._a9zr")
                post_comments = []

                for comment in comments:
                    post_comment = {}
                    comment_time_element = comment.find_element(By.TAG_NAME, "time")
                    post_comment["commented_at"] = comment_time_element.get_attribute("datetime")

                    try:
                        commentor_element = comment.find_element(By.TAG_NAME, "h2")
                        comment_element = comment.find_element(By.CSS_SELECTOR, "div._a9zs")
                        post_comment["commentor"] = commentor_element.text
                        post_comment["commentor_profile"] = commentor_element.find_element(By.TAG_NAME, "a").get_attribute("href")
                        post_comment["comment"] = comment_element.text

                        post_comments.append(post_comment)

                    except NoSuchElementException:
                        commentor_element = comment.find_element(By.TAG_NAME, "h3")
                        comment_element = comment.find_element(By.CSS_SELECTOR, "div._a9zs")
                        post_comment["commentor"] = commentor_element.text
                        post_comment["commentor_profile"] = commentor_element.find_element(By.TAG_NAME, "a").get_attribute("href")
                        post_comment["comment"] = comment_element.text

                        post_comments.append(post_comment)

                post["comments"] = post_comments
                post["comment_count"] = len(post_comments)

            except Exception as error:
                self.logger.error(Messages.ig_post_error.value.format(error))


        end_dt = datetime.datetime.now()
        time_diff = end_dt - start_dt
        self.logger.info(Messages.total_posts.value.format(len(posts)))
        self.logger.info(Messages.total_seconds.value.format(time_diff.seconds))

        return posts

    def insert_into_mongodb(self, posts):
        """Insert Posts into MongoDB"""
        try:
            client = MongoClient(MongoDB.base_url.value)
            data_base = client[MongoDB.client.value]
            collection = data_base[MongoDB.data.value]
            collection.insert_many(posts)
            client.close()
            self.logger.info(Messages.db_insertion_successfully.value)
        except Exception as error:
            self.logger.error(Messages.mongo_db_error.value.format(error))

    def get_posts(self):
        """Get Posts from server"""
        self.logger.info(Messages.search.value)
        try:
            posts = self.search_instagram(1, 9)
            if posts:
                self.insert_into_mongodb(posts)
            else:
                self.logger.info(Messages.no_post_found.value)
        except Exception as error:
            self.logger.error(Messages.post_error.value.format(error))


if __name__ == "__main__":
    print(Messages.program_title.value)
    keyword = input(Messages.input.value)
    instagram_scraper = Scraper(keyword)

    instagram_scraper.get_posts()
