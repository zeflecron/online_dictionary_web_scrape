# Online Dictionary Web Scrape
Web scraping an online dictionary called Linguee

The web scraping is specifically only for German verbs (base form)

It is mainly a learning experience on using:
- a web scraping library (beautiful soup)
- type hints
- separation of long functions
- unit testing and integration testing

# How to run it (commands are based on windows OS)
1. Open online_dictionary_web_scrape_v1.0+
2. Put all the folders and files into a directory
3. Create a virtual environment in that directory using cmd: `python -m venv venv`
4. Activate the virtual environment: `venv\Scripts\activate.bat`
5. Install the dependencies: `pip install -r requirements.txt`
6. Use an IDE (like PyCharm) and run `main.py` (see step 7 in case)
7. Due to testing, the bottom section of the code may still be commented, uncomment the desired action

## Additional info
1. Uses Python 3.9
2. Linguee can block user after certain number of queries
3. Heavily depends on proxies and internet service provider conditions
4. About legality, it should be fine as the intention was never nefarious
