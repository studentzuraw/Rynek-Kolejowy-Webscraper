# Rynek-Kolejowy-Webscraper

Rynek-Kolejowy-Webscraper is designed to scrape news articles from the "Rynek Kolejowy" website and store the data in a database. It uses Selenium with Firefox WebDriver to navigate the website and extract the required information.

## Installation

###### 1. Download the package from github.
###### 2. Download [geckodriver](https://github.com/mozilla/geckodriver/releases) from: https://github.com/mozilla/geckodriver/releases
###### 3. Place geckodriver.exe in folder geckodriver and put that inside project folder
###### 4. Download [Mozilla Firefox](https://www.mozilla.org/pl/) from: https://www.mozilla.org/pl/
###### 5. Install dependencies:

```bash
pip install selenium
pip install requests
```

### Usage:
Run the script using the command:
```bash
py webscraper.py
```

## Note

Script was tested for:
- geckodriver-v0.33.0-win64
- Firefox 115 on Windows 10
- Python 3.11.1
- Selenium 4.10.0
- Requests 2.31.0
