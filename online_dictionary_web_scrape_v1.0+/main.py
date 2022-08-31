import requests
import time
import random
import pandas as pd
from itertools import cycle
from typing import Any, Optional
from bs4 import BeautifulSoup
import concurrent.futures

'''
    BOTH MAIN AND THE TEST MIGHT NOT WORK CONSISTENTLY BECAUSE IT DEPENDS ON 
        THE WEBSITE, THE PROXY, AND MAYBE THE INTERNET PROVIDER

    This Linguee class is only used for scraping german verbs

    Linguee has 4 parameters (all csv) when instantiating
        words     : list[str]
            the words that wants to be scraped
        filename  : str (xlsx)
            excel file for result
        limit     : int (optional) [default is 200]
            sets the max failed attempts before stopping
        url       : str (optional) [default is None]
            only used to check if website can be accessed or not

    Other variables includes:
        ResultAlies        = an alias for type hints
        headers            = to identify types of apps, OS, version, etc. to 
                             allow data target to decide the HTML layout
        data_scraped       = to temporarily save the scraped data of a word
        successful_proxies = to list all available proxies
        try_ctr            = to track how many attempts have failed
        bad_proxy          = to tell other methods of a bad proxy
        break_loop         = to stop all loops once limit is reached

    Run the method `execute_main` to start scraping
    Run the method `combine_excel` to combine excel files

    Note: combine_excel has the option to have a different file name from
          the instantiation of Linguee

    Example code
    `
    linguee = Linguee(['nehmen'], 'result.xlsx', 100)
    linguee.execute()
    linguee.combine_excel(['result.xlsx', 'result_2.xlsx'], 'combined.xlsx')
    `
'''


class Linguee:
    ResultAlias = list[list[dict[str, str]]]
    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) '
            'Gecko/20100101 Firefox/80.0 '
            'Chrome/11.0.672.2 Safari/534.20'
    }
    data_scraped = []
    successful_proxies = []
    try_ctr = 0
    bad_proxy = False
    break_loop = False

    def __init__(self, words: list[str], filename: str,
                 limit: int = 200, url: Optional[str] = None) -> None:
        self.words = words
        self.filename = filename
        self.limit = limit
        self.url = url

    # SECTION: ROTATING PROXY
    # REFERENCE: https://github.com/jhnwr/rotatingproxies
    # get the list of free proxies
    @staticmethod
    def get_proxies() -> list[str]:
        req = requests.get('https://free-proxy-list.net/')
        soup = BeautifulSoup(req.content, 'html.parser')
        table = soup.find('tbody')
        proxies = []
        for row in table:
            if (row.find_all('td')[4].text == 'elite proxy') or \
                    (row.find_all('td')[4].text == 'anonymous'):
                proxy = ':'.join([row.find_all('td')[0].text,
                                  row.find_all('td')[1].text])
                proxies.append(proxy)
            else:
                pass
        return proxies

    def check_proxy(self, proxy: str) -> None:
        # NOTE: if no concurrent.futures, use this:
        #   proxy = random.choice(proxylist)
        proxies = {'http': 'http://' + proxy, 'https': 'https://' + proxy}
        try:
            # https://httpbin.org/ip doesn't block anything
            req = requests.get('https://httpbin.org/ip', headers=self.headers,
                               proxies=proxies, timeout=1)
            print(req.json(), req.status_code)
            self.successful_proxies.append(proxy)

        # e is not printed because it will spam very long messages
        except Exception as e:
            pass

    # SECTION: CHECKERS
    # used to check if page even works to begin with
    def test_page(self) -> Any:
        try:
            response = requests.get(self.url)
            if not response.ok:
                return 'Failed'
            else:
                return 'Success'
        except Exception as e:
            return e

    # get all possible prefix variation of word (for german only)
    # reflexive verbs (sich ...) will automatically be considered
    def get_word_list(self, word: str) -> list[str]:
        word_list = [
            word,
            'ab' + word,
            'an' + word,
            'auf' + word,
            'aus' + word,
            'bei' + word,
            'dar' + word,
            'ein' + word,
            'emp' + word,
            'ent' + word,
            'er' + word,
            'ge' + word,
            'hin' + word,
            'her' + word,
            'nach' + word,
            'nieder' + word,
            # umlaut not part of standard ASCII charset, use ue to exchange it
            'ueber' + word,
            'um' + word,
            'unter' + word,
            'ver' + word,
            'vor' + word,
            'weg' + word,
            'wider' + word,
            'zer' + word,
            'zu' + word,
            'zusammen' + word
        ]
        return word_list

    # used to stop looping when limit is reached
    # prevents infinite loop of bad/blocked proxies
    def limit_checker(self, keyword: str) -> None:
        if self.try_ctr > self.limit:
            print('Limit has been reached!')
            print('Last word before stopping:', keyword)
            self.break_loop = True

    # SECTION: EXTRACT
    def extract_get_request(self, url: str, proxies: dict[str, str]) -> Any:
        try:
            req = requests.get(url, headers=self.headers,
                               proxies=proxies, timeout=1)
            print('Worked!')
            return req

        # e is not printed because it will spam very long messages
        except Exception as e:
            self.try_ctr += 1
            print('Failed!')

    def extract_change_proxy(self) -> dict[str, str]:
        print('Bad proxy, trying a random one')
        self.bad_proxy = True
        proxy = random.choice(self.successful_proxies)
        proxies = {
            'http': 'http://' + proxy,
            'https': 'https://' + proxy
        }
        return proxies

    # checks if proxy can even connect to the website
    def extract_main(self, keyword: str, proxy: str) -> BeautifulSoup:
        # links don't follow PEP8 79/80 character rule
        url = f'https://www.linguee.com/english-german/search?source=auto&query={keyword}'
        req = None
        proxies = {
            'http': 'http://' + proxy,
            'https': 'https://' + proxy
        }
        failed_attempts = 0

        while req is None:
            self.limit_checker(keyword)

            # only if limit is reached, use no proxies
            #   even if your ip is blocked
            if self.break_loop:
                req = requests.get(url, headers=self.headers, timeout=3)
            else:
                req = self.extract_get_request(url, proxies)

            # this breaks the loop automatically
            if req is not None:
                soup = BeautifulSoup(req.content, 'html.parser')
                return soup

            failed_attempts += 1

            # change proxy if it fails multiple times
            if failed_attempts % 5 == 0:
                proxies = self.extract_change_proxy()

    # SECTION: SCRAPE
    def scrape_block_check(self, soup: BeautifulSoup, keyword: str) \
            -> BeautifulSoup:
        block_check = soup.find('h1').text.strip()

        # checks if the website has already blocked the proxy
        while block_check == ('You have sent too many requests causing '
                             'Linguee to block your computer'):
            if self.break_loop:
                break

            self.try_ctr += 1
            self.limit_checker(keyword)
            print('Proxy blocked, trying a random one')
            self.bad_proxy = True

            # change the soup temporarily for this instance
            random_proxy = random.choice(self.successful_proxies)
            temp_soup = self.extract_main(keyword, random_proxy)
            soup = temp_soup
            block_check = soup.find('h1').text.strip()

        return soup

    def scrape_data(self, soup: BeautifulSoup) -> None:
        variations = soup.select('.lemma')
        for variation in variations:
            word_type = variation.find('span', class_='tag_wordtype')

            # makes sure that if word_type doesn't exist it doesn't show error
            if word_type is None:
                strip_type = None
            else:
                strip_type = word_type.text.strip()

            # only want to get the first definition of the verb
            # can be changed to noun, past-participle, etc.
            if strip_type == 'verb':
                the_word = variation.find('h2', class_='lemma_desc') \
                    .find('a', class_='dictLink').text.strip()
                definition = variation.find('div', class_='lemma_content') \
                    .find('a', class_='dictLink').text.strip()
                word_dict = {'word': the_word, 'definition': definition}
                self.data_scraped.append(word_dict)

    def scrape_main(self, soup: BeautifulSoup, keyword: str) -> Any:
        soup = self.scrape_block_check(soup, keyword)
        if not self.break_loop:
            result = self.scrape_data(soup)
            return result

    # SECTION: SAVE AND COMBINE DATA
    def remove_duplicates(self, final_result: ResultAlias) -> ResultAlias:
        refined_result = []
        for results in final_result:
            seen = []
            new_result = []
            for data in results:
                key = list(data.keys())[0]
                if data[key] not in seen:
                    seen.append(data[key])
                    new_result.append(data)
            refined_result.append(new_result)
        return refined_result

    # converts into dict that contains list as values
    def convert_to_dict(self, refined_result: ResultAlias) \
            -> dict[str, list[str]]:
        temp_dict = {}
        for results in refined_result:
            word = [keyword['word'] for keyword in results][0]
            temp_dict[word] = [keyword['word'] for keyword in results]
            temp_dict[word + ' def'] = [keyword['definition'] for keyword in
                                        results]
            # used to space out between different word results
            temp_dict[word + ' space'] = ['|' for _ in range(25)]

        return temp_dict

    def save_to_excel(self, dict_to_save: dict[str, list[str]],
                      save_file: str = None) -> None:
        save_file = self.filename if save_file is None else save_file
        writer = pd.ExcelWriter(save_file, engine='openpyxl')

        # allows different number of rows for each result column
        df = pd.DataFrame.from_dict(dict_to_save, orient='index')

        # the previous command applies the x as y and y as x
        df = df.transpose()
        df.to_excel(writer, index=False)
        writer.save()

        print('File has been saved at', save_file)

    def save_data(self, result: ResultAlias) -> None:
        refined_result = self.remove_duplicates(result)
        dict_to_save = self.convert_to_dict(refined_result)
        self.save_to_excel(dict_to_save)

    # only used when all proxies are blocked midway
    #   and multiple excels files are then created
    # can use *args, but it can be confusing to readers
    def combine_excel(self, excel_files: list[str],
                      save_file: str = None) -> None:
        save_file = self.filename if save_file is None else save_file
        temp_dict = {}
        for file in excel_files:
            xls = pd.ExcelFile(file)
            df = xls.parse(xls.sheet_names[0])
            for word in list(df.keys()):
                temp_dict[word] = list(df[word])
        self.save_to_excel(temp_dict, save_file)

    # SECTION: EXECUTION
    def execute_generate_successful_proxies(self) -> None:
        proxy_list = self.get_proxies()
        print(len(proxy_list), 'total proxies to check')

        # checks each proxy at a very fast rate
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.check_proxy, proxy_list)

    def execute_main(self) -> None:
        self.execute_generate_successful_proxies()
        if len(self.successful_proxies) > 0:
            proxy_cycle = cycle(self.successful_proxies)
            final_list = []

            for word in self.words:
                chosen_proxy = next(proxy_cycle)
                print('\n\nUsing proxy:', chosen_proxy)
                print('-' * 20)
                print('Extracting the word', word)
                word_variations = self.get_word_list(word)

                for word_variation in word_variations:
                    # if proxy shows error on previous word, go to next proxy
                    if self.bad_proxy:
                        chosen_proxy = next(proxy_cycle)
                        self.bad_proxy = False
                        print('Proxy was bad, switching to:', chosen_proxy)

                    the_soup = self.extract_main(
                        word_variation, chosen_proxy)
                    self.scrape_main(the_soup, word_variation)

                    if self.break_loop:
                        break

                # in conjunction with word_variation
                if self.break_loop:
                    break

                final_list.append(self.data_scraped)
                self.data_scraped = []

            self.save_data(final_list)
            print('Finished executing')
        else:
            print('No proxies available')


# add more if needed
# total words = 70
list_of_words = ['arbeiten', 'atmen', 'binden', 'bieten', 'bereiten',
                 'brauchen', 'brechen', 'bringen', 'danken', 'denken',
                 'druecken', 'fahren', 'fallen', 'fangen', 'fehlen',
                 'finden', 'geben', 'greifen', 'halten', 'haengen',
                 'holen', 'hoeren', 'kaempfen', 'kennen', 'kommen',
                 'kundigen', 'laden', 'lassen', 'legen', 'meiden',
                 'nehmen', 'oeffnen', 'passen', 'raten', 'rechnen',
                 'reden', 'rufen', 'sammeln', 'scheiden', 'scheinen',
                 'schlafen', 'schlagen', 'schliessen', 'sehen', 'setzen',
                 'sichern', 'sitzen', 'sprechen', 'springen', 'stecken',
                 'stehen', 'steigen', 'streichen', 'stossen', 'stoeren',
                 'stuetzen', 'tauschen', 'tragen', 'trauen', 'treiben',
                 'walten', 'warten', 'weisen', 'werben', 'werfen',
                 'wischen', 'wissen', 'zeichnen', 'zeugen', 'ziehen']

# used when program stops midway or just want to scrape some, not all
#   because scraping all 70 takes a while and depends on availability of proxy
partial_list_1 = ['arbeiten', 'binden', 'bringen', 'halten', 'laden']
partial_list_2 = ['passen', 'setzen']
partial_list_3 = ['streichen']

result_files = ['results_1.xlsx', 'results_2.xlsx']

# NOTE: rate limit until blocked can potentially be checked in API
# OPTIMIZE: make a proxy list refresh that refreshes every few minutes

start = time.perf_counter()

# comment everything when unit testing
# linguee = Linguee(partial_list_1, 'results_1.xlsx')
# linguee.execute_main()
# linguee.combine_excel(result_files, 'final_res.xlsx')

end = time.perf_counter()
print('\n\nTotal time taken:', end - start)
