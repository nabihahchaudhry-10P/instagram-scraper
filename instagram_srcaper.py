import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

# Function to perform keyword-based search on Instagram
def search_instagram(keyword):
    base_url = 'https://www.instagram.com/explore/tags/'
    url = base_url + keyword + '/'
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve data from Instagram. Status code: {response.status_code}")
        return None

# Function to parse HTML and extract post data
def extract_post_data(keyword, html):
    soup = BeautifulSoup(html, 'html.parser')
    posts = []
    for post in soup.find_all('body'):
        post_data = {}
        post_data['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        post_data['hashtag'] = keyword
        img_element = post.find('img')
        if img_element:
            print("Image found!")
            img_src = img_element['src']
            post_data['image_url'] = img_src
        # Additional data will be extracted: poster's info, URLs, number of shares, likes, views etc.
        posts.append(post_data)
    return posts

def insert_into_mongodb(posts):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['instagram']
        collection = db['posts']
        collection.insert_many(posts)
        client.close()
    except:
        print("Error occured while inserting Instagram data into MongoDB")

def main():
    keyword = input("Enter a keyword to search on Instagram: ")
    html = search_instagram(keyword)
    if html:
        posts = extract_post_data(keyword, html)
        if posts:
            insert_into_mongodb(posts)
            print("Data successfully stored in MongoDB.")
        else:
            print("No posts found.")
    else:
        print("Failed to retrieve data from Instagram.")

if __name__ == "__main__":
    main()
