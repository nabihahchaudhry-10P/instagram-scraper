from bs4 import BeautifulSoup
from logger import MyLogger
from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to perform keyword-based search on Instagram
def search_instagram(keyword):
    try:
        base_url = 'https://www.instagram.com/explore/tags/'
        url = base_url + keyword + '/'
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait to finish loading to get all dynamically-loaded content on webpage
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )

        return driver.page_source
    except Exception as e:
        print(f"Error fetching posts:\n {e}")
        return None

# Function to parse HTML and extract post data
def extract_post_data(keyword, html):
    soup = BeautifulSoup(html, 'html.parser')
    all_posts = []
    rows = soup.find_all('div', class_='_ac7v')

    for row in rows:
        posts = row.find_all('a', class_='x1i10hfl')
        for post in posts:
            post_data = {}
            post_data['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            post_data['hashtag'] = keyword
            post_data['link'] = post['href']
            post_data['img_text'] = post.find('img')['alt']
            post_data['img_link'] = post.find('img')['src']
            
            all_posts.append(post_data)
            
    return all_posts

def insert_into_mongodb(posts):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['instagram']
        collection = db['posts']
        collection.insert_many(posts)
        client.close()
        print("Data successfully stored in MongoDB.")
    except Exception as e:
        print(f"Error occurred while inserting Instagram data into MongoDB:\n {e}")

def main():
    keyword = input("Enter a keyword to search on Instagram: ")
    html = search_instagram(keyword)
    if html:
        posts = extract_post_data(keyword, html)
        if posts:
            insert_into_mongodb(posts)
        else:
            print("No posts found.")
    else:
        print("Failed to retrieve data from Instagram.")

if __name__ == "__main__":
    main()
