"""
RSS SCRAPPER
1. This file extracts the RSS feed from the given URLS and returns the entries in a list format. It uses the feedparser library to parse the RSS feed and extract the
relevant information.
It also cleans the data by removing any HTML tags and special characters from the entries. The cleaned entries are then stored in a list and returned as output.

2. RSS elements:-
    i. The most commonly used elements in RSS feeds (regardless of version) are title, link, description, publication date, and entry ID.
    ii. The publication date comes from the 'pubDate' element, and the entry ID comes from the 'guid' element.
    iii. The channel elements are available in d.feed
    iv. The entry elements are available in d.entries, which is a list. You access items in the list in the same order in which they appear in the original feed,
        so the first item is available in d.entries[0].

"""
import os
import psycopg2
from dotenv import load_dotenv
import feedparser
import json
from bs4 import BeautifulSoup

# Load the secure variables from your .env file
load_dotenv()

# 1. Defining the list RSS source URLs to be parsed
rss_urls = [
    "https://timesofindia.indiatimes.com/rssfeeds/-2128833038.cms",
    "https://www.thehindu.com/news/cities/feeder/default.rss"
    ]

# 2. Master Storage list for all the entries from the RSS feeds

master_articles_list = []
civic_keywords = [
    "bbmp", "bescom", "bwssb", "bmrc", "namma metro", "traffic", "power cut", "water supply", "bmtc", "bmrcl", "holiday",
    "road closure", "road repair", "road maintainence", "road construction", "road work", "road closed",
    "metro delay", "metro disruption", "metro maintenance", "metro work", "metro closed",
    "bus delay", "bus disruption", "bus maintenance", "bus strike", "bmtc strike",
    "water cut", "water disruption", "water work", "water closed",
    "power cut", "power disruption", "grid work", "grid maintenance", "scheduled power cut", "scheduled power disruption", "scheduled grid work", "scheduled grid maintenance", "scheduled power cut", "scheduled power disruption",
    "holiday", "public holiday", "bank holiday", "school holiday", "festival", "event hliday",
    "bandh", "statewide", "city wide", "citywide"
    ]

# 3. Looping through the list of RSS URLs and parsing each feed
for url in rss_urls:
    rss_feed = feedparser.parse(url)                                #parses the RSS feed from the given URL and stores it in the variable rss_feed

    # 3.1 Looping through each entry in the parsed RSS feed and cleaning the data
    for entry in rss_feed.entries:                                  #loops through each entry (post) in the parsed RSS feed

        # 3.1.1 Cleaning the description of the entry by removing any HTML tags and special characters using BeautifulSoup. This ensures that we have clean and readable text for the description of each article.
        description_soup = BeautifulSoup(entry.description, "html.parser")          #Creates a BeautifulSoup object by parsing the description of the entry as HTML
        entry.description = description_soup.get_text()                             #Extracts the text content from the BeautifulSoup object and updates the description of the entry

        title_soup = BeautifulSoup(entry.title, "html.parser")                      #Creates a BeautifulSoup object by parsing the title of the entry as HTML
        entry.title = title_soup.get_text()                                         #Extracts the text content from the BeautifulSoup object and updates the title of the entry

        # 3.1.2 Storing the cleaned data in a dictionary format for better readability and structure.
        article_data = {
            "title": entry.title,                                   #stores the title of the entry in the article_data dictionary
            "link": entry.link,                                     #stores the link of the entry in the article_data dictionary
            "description": entry.description,                       #stores the description of the entry in the article_data dictionary
            "published": entry.published,                           #stores the publication date of the entry in the article_data dictionary
            "id": entry.id,                                         #stores the entry ID of the entry in the article_data dictionary
            "published_parsed": str(entry.published_parsed)         #stores the publication date of the entry in a structured format (time.struct_time) in the article_data dictionary
        }

        # 3.2 Convert title and description to lowercase before getting into the loop
        title_lower = article_data["title"].lower()
        desc_lower = article_data["description"].lower()

        # 3.3 Filtering each rss port or article based on the presence of the civic keywords in the title or description.
        if any(keyword in article_data["title"].lower() or keyword in article_data["description"].lower() for keyword in civic_keywords):
            master_articles_list.append(article_data)

# 4. Exporting the master article list to a JSON file for better readability
with open("master_articles_list.json", "w", encoding="utf-8") as json_file:         #Using the with statement automatically closes the file when the operation is done, preventing memory leaks. utf-8 encoding is used to ensure that the file can handle non english characters without any issues.
    json.dump(master_articles_list, json_file, indent=4, ensure_ascii=False)        # 4 spaces of indentation for every nested level, increases readablity for development. ensure_ascii=False allows non-ASCII characters to be written to the file without being escaped, which is important since we will filter articles with exact string searches.

# 5. Database Insertion to Supabase

# 5.1 Getting the database URL from the environment variable.
db_url = os.environ.get("DATABASE_URL")

# 5.2 Defining variables as None here so the script does not crash in case one of them isn't working.
connection = None
cursor = None

try:
    print("Connecting to Supabase...")
    connection = psycopg2.connect(db_url)
    cursor = connection.cursor()

    # The SQL command to insert data safely. Written in 3 lines just for better readability. Computer takes it as one single line.
    insert_query = """
        INSERT INTO civic_news (title, description, link, published, rss_id, published_parsed)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (link) DO NOTHING;
    """
    #ON CONFLICT ensures that if an article with the same link already exists in the database, it will not be inserted again, preventing duplicates.

    # Loop through the completed list and push each article to the database
    for article in master_articles_list:
        cursor.execute(insert_query, (
            article["title"],
            article["description"],
            article["link"],
            article["published"],
            article["id"],
            article["published_parsed"]
        ))

    # Save the changes to the database
    connection.commit()
    print(f"Successfully processed {len(master_articles_list)} articles into the database!")

except Exception as error:
    # 2. Print the error if there's an issue when connecting to the database
    print(f"An error occurred while connecting to the database: {error}")

finally:
    # Always cleanly close the connection to prevent memory leaks on the server
    if cursor:
        cursor.close()
    if connection:
        connection.close()
        print("Database connection closed.")