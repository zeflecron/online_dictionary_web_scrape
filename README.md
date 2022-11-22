# Online Dictionary Web Scrape
Web scraping an online dictionary called Linguee

The web scraping is specifically only for German verbs (base form)

It is mainly a learning experience on using:
- a web scraping library (beautiful soup)
- type hints
- separation of long functions
- unit testing and integration testing

# How to run it (commands are based on windows OS)
1. Download, extract, and open online_dictionary_web_scrape_v1.0+
2. Create a virtual environment in the directory using cmd: `python -m venv venv`
3. Activate the virtual environment: `venv\Scripts\activate.bat`
4. Install the dependencies: `pip install -r requirements.txt`
5. Use an IDE and run `main.py` (see step 6 in case):
   - PyCharm: https://www.jetbrains.com/pycharm/
   - VSCode: https://code.visualstudio.com/
6. Due to testing, the bottom section of the code may still be commented, uncomment the desired action

## Additional info
1. Uses Python 3.9
2. Linguee blocks the user after certain number of queries and it heavily depends on the proxies as well as internet providers for this to function
