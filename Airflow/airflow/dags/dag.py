# Import necessary libraries
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from selenium import webdriver
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import datetime
import json
from pymongo.mongo_client import MongoClient
from datetime import datetime


# Define the function to scrape data from the BBC website
def scrape_bbc_website():

    # credentials to access to database in mongodb
    uri = "MONGODB_Link"

    # Create a new client and connect to the server
    # client = MongoClient(uri, server_api=ServerApi('1'))
    client = MongoClient(
        uri,
        tls=True,
        tlsAllowInvalidCertificates=True,  # Use this only for testing
        socketTimeoutMS=30000,
        connectTimeoutMS=30000
    )

    # Initialize MongoDB client and connect to the database
    db = client['bbc_articles']
    collection = db['articles']
    options = Options()
    options.headless = True

    # Path to your geckodriver executable
    driver = webdriver.Firefox(
        options=options, executable_path='/path/to/geckodriver')

    # Initialize a new Firefox browser instance using Selenium WebDriver
    driver = webdriver.Firefox()

    # Define today's date in the format '2024-05-24'
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Navigate to the BBC website
    driver.get("https://www.bbc.com/")

    # Retrieve the page source from the browser and parse it using BeautifulSoup
    # 'html.parser' is specified as the parser to use
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find the navbar element
    navbar_menu = soup.find("nav", {"class": "sc-df0290d6-9 ePpHOZ"})

    # Initialize lists to store element names and their corresponding links
    menu_names = []
    menu_links = []

    # Initialize lists to store scraped data
    article_data = []

    # Iterate over the elements inside the navbar and extract their names and links
    for item in navbar_menu.find_all("a"):
        menu_name = item.text.strip()
        # Use driver.current_url to get the current URL
        menu_link = urljoin(driver.current_url, item.get("href"))
        menu_names.append(menu_name)
        menu_links.append(menu_link)

    # Selecting a subset of menu names and links
    menu_names = menu_names[1:8]
    menu_links = menu_links[1:8]

    # Iterate over each menu link
    for menu_name, menu_link in zip(menu_names, menu_links):

        # Navigate to each menu in the BBC website
        driver.get(menu_link)
        # Add a short delay to allow the page to fully load
        time.sleep(2)

        # --------------------------------------- Articles related to sport --------------------------------------- #
        if menu_name == 'Sport':

            print(
                "---------------------------------------------------------------------------------\n")
            print(
                f"------------------------ Menu Name : {menu_name} -------------------------------\n")

            # Retrieve the page source from the browser and parse it using BeautifulSoup
            menu_soup = BeautifulSoup(driver.page_source, 'html.parser')
            navbar_submenu = menu_soup.find(
                "div", {"class": "ssrcss-1h87eia-MenuListContainer e14xdrat2"})

            if navbar_submenu:

                # Iterate over the elements inside the submenu and extract their names and links
                for item in navbar_submenu.find_all("a"):
                    submenu_name = item.text.strip()
                    submenu_link = urljoin(
                        driver.current_url, item.get("href"))

                    if submenu_name == 'Home':

                        pass

                    else:

                        print(
                            f"------------------ Submenu Name : {submenu_name} ------------------------------\n")
                        # Navigate to each submenu in the BBC website
                        driver.get(submenu_link)
                        # Add a short delay to allow the page to fully load
                        time.sleep(2)

                        # Retrieve the page source from the browser and parse it using BeautifulSoup
                        submenu_soup = BeautifulSoup(
                            driver.page_source, 'html.parser')

                        # Get the card articles
                        article_cards = submenu_soup.find_all(
                            "div", {"type": "article"})

                        # Iterate over each card
                        for card in article_cards:

                            # Get the link of each article
                            article_link = urljoin(
                                driver.current_url, card.find("a")["href"])
                            print(
                                f"------------------ Article Link : {article_link} ------------------------------\n")

                            # Navigate to each article in the BBC website
                            driver.get(article_link)
                            # Add a short delay to allow the page to fully load
                            time.sleep(2)

                            # Retrieve the page source from the browser and parse it using BeautifulSoup
                            article_soup = BeautifulSoup(
                                driver.page_source, 'html.parser')

                            # Find the title of article
                            title_element = article_soup.find(
                                "h1", {"id": "main-heading"})
                            if title_element is not None:
                                title = title_element.text.strip()
                            else:
                                title = ''

                            # get subtitle
                            subtitle_element = article_soup.find(
                                "b", {"class": "ssrcss-1xjjfut-BoldText e5tfeyi3"})
                            if subtitle_element is not None:
                                subtitle = subtitle_element.text.strip()
                            else:
                                subtitle = ''

                            # get date published
                            script_tag = article_soup.find(
                                "script", type="application/ld+json")
                            date_published = None
                            if script_tag:
                                script_content = script_tag.string
                                json_content = json.loads(script_content)
                                date_published = json_content.get(
                                    'datePublished')

                                # Continue only if the datePublished is today
                                if date_published and date_published.startswith(today_date):

                                    # get the author name
                                    authors = [author.text.strip() for author in article_soup.find_all(
                                        "div", {"class": "ssrcss-68pt20-Text-TextContributorName e8mq1e96"})]

                                    # Get text of article
                                    text = ''
                                    text_container = article_soup.find_all(
                                        "div", {"data-component": "text-block"})
                                    for container in text_container:
                                        text_elements = container.find_all(
                                            "p", {"class": "ssrcss-1q0x1qg-Paragraph e1jhz7w10"})
                                        for element in text_elements:
                                            text += element.text.strip() + " "

                                    # Initialize an empty list to store the image links
                                    image_links = []
                                    image_blocks = article_soup.find_all(
                                        "div", {"data-component": "image-block"})
                                    for block in image_blocks:
                                        img_tag = block.find("img")
                                        if img_tag:
                                            src = img_tag.get("src")
                                            image_links.append(src)

                                    # Get Video link (I put empty because when i try to watch the video inside those article : )
                                    # ! (they show a alert that my location is restricted to watch this content) !
                                    video_links = []

                                    # Get topics
                                    topics = []
                                    topic_tags = article_soup.find_all(
                                        "a", {"class": "ssrcss-1ef12hb-StyledLink ed0g1kj0"})
                                    for topic_tag in topic_tags:
                                        topics.append(topic_tag.text)

                                    # Append the scraped data into article_data
                                    article_data.append({
                                        "Menu": menu_name,
                                        "Submenu": submenu_name,
                                        "Title": title,
                                        "Subtitle": subtitle,
                                        "Authors": authors,
                                        "date_published": date_published,
                                        "Text": text,
                                        "Images": image_links,
                                        "Video": video_links,
                                        "Topics": topics,
                                    })

                                    print(
                                        '---------------------------------------------------------------------------------\n')

        # ------- Process All other articles, Exclude sports articles from processing due to their different format; -------- #
        else:

            print(
                '---------------------------------------------------------------------------------\n')
            print(
                f"------------------ Menu Name : {menu_name} ------------------------------\n")

            # Retrieve the page source from the browser and parse it using BeautifulSoup
            menu_soup = BeautifulSoup(driver.page_source, 'html.parser')
            navbar_submenu = menu_soup.find(
                "nav", {"class": "sc-44f1f005-1 cexzQM"})

            if navbar_submenu:

                # Iterate over the elements inside the submenu and extract their names and links
                for item in navbar_submenu.find_all("a"):

                    # Get the submenu names and link
                    submenu_name = item.text.strip()
                    submenu_link = urljoin(
                        driver.current_url, item.get("href"))
                    print(
                        f"------------------ Submenu Name : {submenu_name} ------------------------------\n")

                    # Navigate to each submenu in the BBC website
                    driver.get(submenu_link)
                    # Add a short delay to allow the page to fully load
                    time.sleep(2)

                    # Retrieve the page source from the browser and parse it using BeautifulSoup
                    submenu_soup = BeautifulSoup(
                        driver.page_source, 'html.parser')

                    # Get the card articles
                    article_cards = submenu_soup.find_all(
                        "div", {"data-testid": "liverpool-card"})

                    # Iterate over each article card
                    for card in article_cards:

                        # Get the Article link
                        article_link = urljoin(
                            driver.current_url, card.find("a")["href"])
                        print(
                            f"------------------ Article Link : {article_link} ------------------------------\n")

                        # Find the title of article
                        title_element = card.find(
                            "h2", {"data-testid": "card-headline"})
                        if title_element is not None:
                            title = title_element.text.strip()
                        else:
                            title = ''

                        # get subtitle
                        subtitle_element = card.find(
                            "p", {"data-testid": "card-description"})
                        if subtitle_element is not None:
                            subtitle = subtitle_element.text.strip()
                        else:
                            subtitle = ''

                        # Visit each article link and scrape additional data
                        driver.get(article_link)
                        # Add a short delay to allow the page to fully load
                        time.sleep(2)

                        # Retrieve the page source from the browser and parse it using BeautifulSoup
                        article_soup = BeautifulSoup(
                            driver.page_source, 'html.parser')

                        # Find the script tag with type application/ld+json
                        script_tag = article_soup.find(
                            "script", type="application/ld+json")

                        if script_tag:
                            # Extract the content of the script tag
                            script_content = script_tag.string

                            # Load the JSON content
                            json_content = json.loads(script_content)

                            # Extract the datePublished
                            date_published = json_content.get('datePublished')

                            # Continue only if the datePublished is today
                            if date_published and date_published.startswith(today_date):

                                # Get authors of article
                                authors = [author.text.strip() for author in article_soup.find_all(
                                    "span", {"data-testid": "byline-name"})]

                                # Get text of article
                                text = ""
                                text_elements = article_soup.find_all(
                                    "p", {"class": "sc-eb7bd5f6-0 fYAfXe"})
                                for element in text_elements[:-1]:
                                    text += element.text.strip() + " "

                                # Initialize an empty list to store the image links
                                image_links = []

                                # Find all div elements with data-component="image-block"
                                image_blocks = article_soup.find_all(
                                    "div", {"data-component": "image-block"})

                                # Iterate over each image block
                                for block in image_blocks:
                                    # Find the img tag inside the image block
                                    img_tag = block.find("img")
                                    # Check if img tag is found
                                    if img_tag:
                                        # Get the value of the src attribute
                                        src = img_tag.get("src")
                                        # Append the src value to the image_links list
                                        image_links.append(src)

                                # Start of Get video link --------------------------------------------------------------------------
                                # Extract the JSON data from the script tag
                                script_tag = article_soup.find(
                                    'script', {'id': '__NEXT_DATA__', 'type': 'application/json'})

                                # Initialize a list for video links & article_contents
                                video_links = []
                                article_contents = []

                                # Check if the script_tag was found and process it
                                if script_tag is not None:
                                    try:
                                        json_data = json.loads(
                                            script_tag.string)

                                        # Navigate to the relevant part of the JSON structure
                                        try:
                                            page_key = next(
                                                key for key in json_data['props']['pageProps']['page'] if 'news' in key and 'articles' in key)
                                            article_contents = json_data['props']['pageProps']['page'][page_key]['contents']
                                        except StopIteration:
                                            pass

                                        # Extract video links if article_contents is not empty
                                        if article_contents:
                                            for block in article_contents:
                                                if block['type'] == 'video':
                                                    for sub_block in block['model']['blocks']:
                                                        if sub_block['type'] == 'media':
                                                            for sub_sub_block in sub_block['model']['blocks']:
                                                                if sub_sub_block['type'] == 'mediaMetadata':
                                                                    video_id = sub_sub_block['model']['id']
                                                                    video_links.append(
                                                                        f"https://www.bbc.co.uk/iplayer/episode/{video_id}")
                                    except json.JSONDecodeError:
                                        pass

                                # End of Get video link --------------------------------------------------------------------------

                                # Get topics
                                topics = []
                                topic_tags = article_soup.find_all(
                                    "a", {"class": "sc-3df0d64d-0 kMyFYO"})
                                for topic_tag in topic_tags:
                                    topics.append(topic_tag.text)

                                # Store scraped data
                                article_data.append({
                                    "Menu": menu_name,
                                    "Submenu": submenu_name,
                                    "Title": title,
                                    "Subtitle": subtitle,
                                    "Authors": authors,
                                    "date_published": date_published,
                                    "Text": text,
                                    "Images": image_links,
                                    "Video": video_links,
                                    "Topics": topics,
                                })
                                print(
                                    '---------------------------------------------------------------------------------\n')

    # Insert the list into the collection
    result = collection.insert_many(article_data)

    # Print the number of inserted documents
    print('Number of records added to DB is :', len(result.inserted_ids))

    driver.close()


# Define the DAG
dag = DAG(
    'scrape_bbc_website_dag',
    default_args={'start_date': days_ago(1)},
    schedule_interval='0 23 * * *',  # Runs daily at 23:00
    catchup=False
)

# Define the task using PythonOperator
scrape_bbc_website_task = PythonOperator(
    task_id='scrape_bbc_website_task',
    python_callable=scrape_bbc_website,
    dag=dag
)

# Set task dependencies if needed
scrape_bbc_website_task
