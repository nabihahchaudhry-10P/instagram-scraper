from enum import Enum, unique

@unique
class Constants(Enum):
    base_url = "https://www.instagram.com/explore/tags/"
    
@unique
class Messages(Enum):
    input = "Enter a keyword to search on Instagram: "
    search = "Searching Instagram... \n"
    mongo_db_error = "Error occurred while inserting Instagram data into MongoDB:\n {}"
    post_error = "Unable to get data from Instagram: {}"
    db_insertion_successfully = "Data successfully stored in MongoDB."
    no_post_found = "No posts found."
    total_posts = "Total: {} post(s)"
    total_errors = "Total: {} error(s)"
    total_seconds = "Total: {} second(s)"
    ig_post_error = "Error going on IG picture link & extracting additional post data. Error: {}"
    program_title = "\n\t\t\t*** INSTAGRAM SCRAPER ***\n"
    
@unique
class MongoDB(Enum):
    base_url = "mongodb://localhost:27017/"
    client = "instagram"
    data = "posts"