#!/usr/bin/python3
"""
Module: webscraper.py

Description:
This script is designed to scrape news articles from the "Rynek Kolejowy" website
and store the data in a database. It uses Selenium with Firefox WebDriver to navigate
the website and extract the required information.

Author:
[Krzysztof H.]

Date:
[18.07.2023]

Python Version:
[3.11.1]

Dependencies:
- requests
- selenium

Database Handling:
This script requires the 'database_handling' module to interact with the database. 
The module must be present in the same dir or dir included in the PYTHONPATH.

Execution:
Run the script using the command:
$ py webscraper.py

Note:
- The script uses the custom 'database_handling' module to interact with the database.
- The script requires Firefox browser and the 'geckodriver' executable 
to be installed and accessible in the system path for Selenium to work.
- The 'images' folder will be used to store downloaded images from news articles.
"""
import os
import time

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

import database_handling as dbh

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
)
MAIN_PAGE_URL = "https://www.rynek-kolejowy.pl"

page_urls = [
    ("https://www.rynek-kolejowy.pl/biznes.html", "Biznes"),
    ("https://www.rynek-kolejowy.pl/infrastruktura.html", "Infrastruktura"),
    ("https://www.rynek-kolejowy.pl/pasazer.html", "Pasazer"),
    ("https://www.rynek-kolejowy.pl/prawo.html", "Prawo"),
    ("https://www.rynek-kolejowy.pl/tabor.html", "Tabor"),
    (
        "https://www.rynek-kolejowy.pl/zintegrowany-transport.html",
        "Zintegrowany Transport",
    ),
    ("https://www.rynek-kolejowy.pl/innowacje.html", "Innowacje"),
]

# webdriver settings
FireFoxDriverPath = os.path.join(os.getcwd(), "geckodriver", "geckodriver.exe")
firefox_service = Service(FireFoxDriverPath)
firefox_option = Options()
firefox_option.set_preference("general.useragent.override", USER_AGENT)
firefox_option.add_argument("--headless")
browser = webdriver.Firefox(service=firefox_service, options=firefox_option)
browser.implicitly_wait(7)


def remove_popups():
    """Remove popups from the website by adding cookies."""
    cookies_consent_cookie = {
        "name": "euconsent-v2",
        "value": "CPu_hvvPu_hvvExAAAPLDNCgAAAAAAAAAAAAJiwAATFgAAAA.YAAAAAAAAAAA",
        "path": "/",
        "domain": ".www.rynek-kolejowy.pl",
        "secure": True,
    }
    browser.add_cookie(cookies_consent_cookie)

    remove_popup_cookie = {
        "name": "_popup",
        "value": "0",
        "path": "/",
        "domain": ".www.rynek-kolejowy.pl",
    }
    browser.add_cookie(remove_popup_cookie)

    browser.refresh()


def scrape_main_pages(page_url):
    """
    Scrape the main pages with specific tag eg. Biznes for links to news articles.

    Parameters:
        page_url (str): The URL of the news article page to scrape.

    Returns:
        list: A list of URLs of news articles found on the page.
    """
    try:
        browser.get(page_url)
        time.sleep(3)
    except TimeoutException:
        print("Page has not loaded. Refreshing...")
        browser.refresh()

    messages_links_set = set()
    print("Scraping messages for:", page_url)

    div_elements = browser.find_elements(By.CLASS_NAME, "listaWiadomosciv3")
    for div in div_elements:
        try:
            a_tags = div.find_elements(By.TAG_NAME, "a")
            for a_tag in a_tags:
                href = a_tag.get_attribute("href")
                if "#disqus_thread" not in href:
                    messages_links_set.add(href)

        except NoSuchElementException as exception:
            print("Error: Element not found -", exception)
            continue

    output_list = list(messages_links_set)
    print("Found:", str(len(output_list)), "elements")
    return output_list


def compare_lists(output_list):
    """
    Compare the output list with the database and redirected lists.

    Parameters:
        output_list (list): The list of URLs of news articles to compare.

    Returns:
        tuple: A tuple containing a new output list with unique URLs and the number of duplicates.
    """
    database_output = dbh.fetch_links("news_table")
    redirected_output = dbh.fetch_links("redirected_table")

    new_output_list = [item for item in output_list if item not in database_output]

    new_output_list = [
        item for item in new_output_list if item not in redirected_output
    ]

    duplicates = len(output_list) - len(new_output_list)
    return new_output_list, duplicates


def download_image(photo_url, photo):
    """
    Download an image from the given URL.

    Parameters:
        photo_url (str): The URL of the image to download.
        photo (str): The filename to save the downloaded image as.
    """
    try:
        with requests.get(photo_url, timeout=300) as response:
            response.raise_for_status()

            # Save the image to the 'images' folder
            photo_path = os.path.join("images", photo)
            with open(photo_path, "wb") as file:
                file.write(response.content)
            print("Image downloaded successfully")

    except requests.exceptions.RequestException as exception:
        print("Failed to download image:", str(exception))


def scrape_specific_pages(new_output_list, tag):
    """
    Scrape specific pages for data and insert into the database.

    Parameters:
        new_output_list (list): The list of URLs of news articles to scrape.
        tag (str): The tag representing the topic of the news articles.
    """
    new_output_list, duplicates = compare_lists(new_output_list)
    print("Total Duplicates found:", duplicates)

    for counter, link in enumerate(new_output_list, start=1):
        try:
            browser.get(link)
            time.sleep(3)
        except TimeoutException:
            print("Page has not loaded. Refreshing...")
            browser.refresh()

        current_link = browser.current_url
        print(f"Scraping page: {counter} out of {len(new_output_list)}")

        if current_link == link:
            try:
                topic = browser.find_element(By.CLASS_NAME, "wiadTit").text

                message_lead_element = browser.find_element(
                    By.CLASS_NAME, "WiadomoscLead"
                )
                message_lead = message_lead_element.text

                wiad_szczegol_element = browser.find_element(
                    By.CLASS_NAME, "wiadSzczegol"
                )
                szczegol_text_parts = wiad_szczegol_element.text.split("⚫")
                author, date = map(str.strip, szczegol_text_parts[:2])

                # Weird nesting, page contains a single photo, set of photos or video
                try:
                    image_element = browser.find_element(
                        By.CSS_SELECTOR, "img.fotoWiadomosc"
                    )
                    photo_url = image_element.get_attribute("src")
                    photo = os.path.basename(photo_url)
                except NoSuchElementException:
                    try:
                        main_div_element = browser.find_element(By.ID, "main-1")
                        image_element = main_div_element.find_element(
                            By.TAG_NAME, "img"
                        )
                        photo_url = image_element.get_attribute("src")
                        photo = os.path.basename(photo_url)
                    except NoSuchElementException:
                        photo = "No photo"
                        print("Photo for this news has not been found.")

                if photo != "No photo":
                    download_image(photo_url, photo)

                print("link:", link)
                print("topic:", topic)
                print("tag:", tag)
                print("date:", date)
                print("photo:", photo)
                print("message_lead:", message_lead)
                print("author:", author)

                dbh.insert_data(
                    "news_table",
                    link,
                    tag,
                    date,
                    topic,
                    photo,
                    message_lead,
                    author,
                )
                print()

            except NoSuchElementException as exception:
                print("Error: Element not found -", exception)
                print("link with error:", link)
                print()
                continue

        else:
            print("Page was redirected.")
            print("redirected to:", current_link)
            print("desired page:", link)
            dbh.insert_data("redirected_table", link)
            print()

    if not new_output_list:
        print("No new news in topic:", tag)
        print()


def main():
    """
    Main function to control the scraping process.
    """
    start = time.time()
    browser.get(MAIN_PAGE_URL)
    remove_popups()

    for url, tag in page_urls:
        output_list = scrape_main_pages(url)
        scrape_specific_pages(output_list, tag)

    browser.quit()
    end = time.time()
    print("Program was running for %.2f seconds:" % (end - start))


if __name__ == "__main__":
    main()