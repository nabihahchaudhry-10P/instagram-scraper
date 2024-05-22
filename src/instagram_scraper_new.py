import datetime
import time
from selenium import webdriver
from pymongo import MongoClient
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from logger import MyLogger
from constants import MongoDB
from constants import Messages
from constants import Constants
from constants import UserCredentials

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
        url = Constants.tag_url.value + self.keyword + "/"
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
    

    def login_user(self):
        url = Constants.login_url.value
        self.driver.get(url)

        # Wait to finish loading to get all dynamically-loaded content on webpage
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
        )

        # Find the username and password input fields
        username_field = self.driver.find_element(By.NAME, 'username')
        password_field = self.driver.find_element(By.NAME, 'password')

        # Replace with your Instagram credentials
        username = UserCredentials.username.value
        password = UserCredentials.password.value

        # Enter the username and password
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Submit the form
        password_field.send_keys(Keys.RETURN)

    
    def search_user(self):
        """Search Instagram Posts"""
        start_dt = datetime.datetime.now()

        self.login_user()
        # Wait for a few seconds to ensure login is successful
        time.sleep(10)

        self.driver.get(f'{Constants.base_url.value}{self.keyword}')

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "header"))
        )
        user_data = dict()
        header_sections = self.driver.find_elements(By.CSS_SELECTOR, "header > section")
        
        user_data['img'] = header_sections[0].find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
        user_data['username'] = self.keyword
        try:
            second_div = header_sections[1].find_element(By.CSS_SELECTOR, 'svg[aria-label="Verified"]')
            user_data['is_verified'] = True
        except NoSuchElementException:
            user_data['is_verified'] = False

        count_list = header_sections[2].find_elements(By.CSS_SELECTOR, "li")
        user_data['posts'] = count_list[0].find_element(By.CSS_SELECTOR, 'span > span').text
        user_data['followers'] = count_list[1].find_element(By.CSS_SELECTOR, 'span > span').text
        user_data['following'] = count_list[2].find_element(By.CSS_SELECTOR, 'span > span').text


        user_data['name'] = header_sections[3].find_element(By.CSS_SELECTOR, 'span').text
        user_data['bio'] = header_sections[3].find_element(By.CSS_SELECTOR, 'h1').text
        
        end_dt = datetime.datetime.now()
        time_diff = end_dt - start_dt
        self.logger.info(Messages.total_seconds.value.format(time_diff.seconds))
        
        return [user_data]



    def insert_into_mongodb(self, posts, type):
        """Insert Posts into MongoDB"""
        try:
            client = MongoClient(MongoDB.base_url.value)
            data_base = client[MongoDB.client.value]
            collection = data_base[MongoDB.posts.value] if type == 1 else data_base[MongoDB.user.value]
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
                self.insert_into_mongodb(posts, type=1)
            else:
                self.logger.info(Messages.no_post_found.value)
        except Exception as error:
            self.logger.error(Messages.post_error.value.format(error))
    
    def get_user(self):
        """Get User from server"""
        self.logger.info(Messages.search.value)
        try:
            user = self.search_user()
            if user:
                self.insert_into_mongodb(user, type=2)
            else:
                self.logger.info(Messages.no_user_found.value)
        except Exception as error:
            self.logger.error(Messages.post_error.value.format(error))


if __name__ == "__main__":
    print(Messages.program_title.value)
    option = int(input(Messages.option.value))
    if option == 1:
        tag = input(Messages.tag.value)
        instagram_scraper = Scraper(tag)
        instagram_scraper.get_posts()
    elif option == 2:
        username = input(Messages.username.value)
        instagram_scraper = Scraper(username)
        instagram_scraper.get_user()
    else:
        raise ValueError('Incorrect value')
    
