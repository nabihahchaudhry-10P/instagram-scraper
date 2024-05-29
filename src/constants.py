from enum import Enum, unique

@unique
class Constants(Enum):
    base_url = "https://www.instagram.com/"
    tag_url = "https://www.instagram.com/explore/tags/"
    login_url = "https://www.instagram.com/accounts/login/"
    
@unique
class Messages(Enum):
    option = "Select the option 1) Post Search \t 2) User Search: "
    tag = "Enter a tag to search on Instagram: "
    username = "Enter a username to search on Instagram: "
    search = "Searching Instagram... \n"
    mongo_db_error = "Error occurred while inserting Instagram data into MongoDB:\n {}"
    post_error = "Unable to get data from Instagram: {}"
    db_insertion_successfully = "Data successfully stored in MongoDB."
    no_post_found = "No posts found."
    no_user_found = "No user found."
    total_posts = "Total: {} post(s)"
    total_errors = "Total: {} error(s)"
    total_seconds = "Total: {} second(s)"
    ig_post_error = "Error going on IG picture link & extracting additional post data. Error: {}"
    program_title = "\n\t\t\t*** INSTAGRAM SCRAPER ***\n"
    
@unique
class MongoDB(Enum):
    base_url = "mongodb://localhost:27017/"
    client = "instagram"
    posts = "posts"
    user = "user"

@unique
class UserCredentials(Enum):
    username = 'test'
    password = 'test'