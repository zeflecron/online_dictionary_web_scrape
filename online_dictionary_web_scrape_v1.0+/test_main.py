import unittest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
import requests
import main


# some parts can be changed using Mock() for better testing
class TestLinguee(unittest.TestCase):
    # shows the beginning of testing
    @classmethod
    def setUpClass(cls):
        print('Set up class')

    # shows the end of testing
    @classmethod
    def tearDownClass(cls):
        print('Tear down class')

    # shows the beginning of a segment of testing
    def setUp(self):
        self.linguee = main.Linguee(['nehmen'], 'test_result.xlsx',
                                     url='https://www.linguee.com/english-german/search?source=auto&query=nehmen')
        self.req = requests.get(self.linguee.url,
                                headers=self.linguee.headers,
                                timeout=3)
        self.soup = BeautifulSoup(self.req.content, 'html.parser')
        print('Setting Up')

    # shows the end of a segment of testing
    def tearDown(self):
        print('Tearing Down\n')

    def test_get_proxies(self):
        result = self.linguee.get_proxies()
        unexpected = []
        self.assertNotEqual(unexpected, result)

    def test_check_proxy(self):
        not_proxy = '10:100'
        self.linguee.check_proxy(not_proxy)
        result = self.linguee.successful_proxies
        expected = []
        unexpected = ['10:100']
        self.assertEqual(expected, result)
        self.assertNotEqual(unexpected, result)

    def test_test_page(self):
        result = self.linguee.test_page()
        expected = 'Success'
        unexpected = 'Failed'
        if result == 'Failed':
            expected, unexpected = unexpected, expected
        self.assertEqual(expected, result)
        self.assertNotEqual(unexpected, result)

    def test_get_word_list(self):
        result = self.linguee.get_word_list('nehmen')
        expected = ['nehmen', 'abnehmen', 'annehmen', 'aufnehmen',
                    'ausnehmen', 'beinehmen', 'darnehmen', 'einnehmen',
                    'empnehmen', 'entnehmen','ernehmen','genehmen',
                    'hinnehmen','hernehmen','nachnehmen','niedernehmen',
                    'uebernehmen','umnehmen','unternehmen','vernehmen',
                    'vornehmen','wegnehmen','widernehmen','zernehmen',
                    'zunehmen','zusammennehmen']
        unexpected = []
        self.assertEqual(expected, result)
        self.assertNotEqual(unexpected, result)

    def test_limit_checker(self):
        self.linguee.try_ctr = 201
        self.linguee.limit_checker('nehmen')
        result = self.linguee.break_loop
        expected = True
        unexpected = False
        self.assertEqual(expected, result)
        self.assertNotEqual(unexpected, result)

    def test_extract_get_request(self):
        not_proxies = {
            'http': 'http://' + '10:100',
            'https': 'https://' + '10:100'
        }
        result = self.linguee.extract_get_request(self.linguee.url,
                                                  not_proxies)
        expected = None
        self.assertEqual(expected, result)
        self.assertEqual(self.linguee.try_ctr, 1)

    def test_extract_change_proxy(self):
        self.linguee.successful_proxies = ['10:100']
        result = self.linguee.extract_change_proxy()
        expected = {
            'http': 'http://' + '10:100',
            'https': 'https://' + '10:100'
        }
        self.assertEqual(expected, result)
        self.assertEqual(self.linguee.bad_proxy, True)

    # order of mock reads from bottom to top when using patch
    # used because it is calling methods and not returning anything
    @patch('main.Linguee.limit_checker')
    @patch('main.Linguee.extract_get_request')
    @patch('main.Linguee.extract_change_proxy')
    def test_extract_main(self, mock_extract_change_proxy,
                          mock_extract_get_request, mock_limit_checker):
        self.linguee.break_loop = True
        self.linguee.extract_main('nehmen', '10:100')
        self.assertFalse(mock_extract_change_proxy.called)
        self.assertFalse(mock_extract_get_request.called)
        self.assertTrue(mock_limit_checker.called)

    def test_scrape_block_check(self):
        self.linguee.break_loop = True
        result = self.linguee.scrape_block_check(self.soup, 'nehmen')
        expected = self.soup
        self.assertEqual(expected, result)

    def test_scrape_data(self):
        result = self.linguee.scrape_data(self.soup)
        expected = [{'word': 'nehmen', 'definition': 'have'}]
        if self.linguee.data_scraped == []:
            self.assertNotEqual(expected, result)
        else:
            self.assertEqual(expected, result)

    @patch('main.Linguee.scrape_block_check')
    @patch('main.Linguee.scrape_data')
    def test_scrape_main(self, mock_scrape_data, mock_scrape_block_check):
        self.linguee.break_loop = True
        self.linguee.scrape_main(self.soup, 'nehmen')
        self.assertTrue(mock_scrape_block_check.called)
        self.assertFalse(mock_scrape_data.called)

    def test_remove_duplicates(self):
        some_value = [
            [
                {'word': 'nehmen', 'definition': 'have'},
                {'word': 'nehmen', 'definition': 'take'},
                {'word': 'unternehmen', 'definition': 'undertake'}
            ],
            [
                {'word': 'binden', 'definition': 'bind'},
                {'word': 'verbinden', 'definition': 'bind'},
            ]
        ]
        result = self.linguee.remove_duplicates(some_value)
        expected = [
            [
                {'word': 'nehmen', 'definition': 'have'},
                {'word': 'unternehmen', 'definition': 'undertake'}
            ],
            [
                {'word': 'binden', 'definition': 'bind'},
                {'word': 'verbinden', 'definition': 'bind'},
            ]
        ]
        self.assertEqual(expected, result)

    def test_convert_to_dict(self):
        some_value = [
            [
                {'word': 'nehmen', 'definition': 'have'},
                {'word': 'unternehmen', 'definition': 'undertake'}
            ],
            [
                {'word': 'binden', 'definition': 'bind'},
                {'word': 'verbinden', 'definition': 'bind'},
            ]
        ]
        result = self.linguee.convert_to_dict(some_value)
        expected = {
            'nehmen': ['nehmen', 'unternehmen'],
            'nehmen def': ['have', 'undertake'],
            'nehmen space': ['|', '|', '|', '|', '|', '|', '|', '|', '|',
                             '|', '|', '|', '|', '|', '|', '|', '|', '|',
                             '|', '|', '|', '|', '|', '|', '|', ],
            'binden': ['binden', 'verbinden'],
            'binden def': ['bind', 'bind'],
            'binden space': ['|', '|', '|', '|', '|', '|', '|', '|', '|',
                             '|', '|', '|', '|', '|', '|', '|', '|', '|',
                             '|', '|', '|', '|', '|', '|', '|', ]
        }
        self.assertEqual(expected, result)

    @patch('builtins.print')
    def test_save_to_excel(self, mock_print):
        some_value = {
            'nehmen': ['nehmen', 'unternehmen'],
            'nehmen def': ['have', 'undertake'],
            'nehmen space': ['|', '|', '|', '|', '|', '|', '|', '|', '|',
                             '|', '|', '|', '|', '|', '|', '|', '|', '|',
                             '|', '|', '|', '|', '|', '|', '|', ],
            'binden': ['binden', 'verbinden'],
            'binden def': ['bind', 'bind'],
            'binden space': ['|', '|', '|', '|', '|', '|', '|', '|', '|',
                             '|', '|', '|', '|', '|', '|', '|', '|', '|',
                             '|', '|', '|', '|', '|', '|', '|', ]
        }
        file = 'test.xlsx'
        self.linguee.save_to_excel(some_value, file)
        mock_print.assert_called_with('File has been saved at', file)

    @patch('main.Linguee.remove_duplicates')
    @patch('main.Linguee.convert_to_dict')
    @patch('main.Linguee.save_to_excel')
    def test_save_data(self, mock_save_to_excel,
                       mock_convert_to_dict, mock_remove_duplicates):
        some_value = [[{'word': 'nehmen', 'definition': 'have'}]]
        self.linguee.save_data(some_value)
        self.assertTrue(mock_remove_duplicates.called)
        self.assertTrue(mock_convert_to_dict.called)
        self.assertTrue(mock_save_to_excel.called)

    @patch('main.Linguee.save_to_excel')
    def test_combine_excel(self, mock_save_to_excel):
        some_excel = ['test.xlsx', 'test.xlsx']
        file = 'test_combine.xlsx'
        self.linguee.combine_excel(some_excel, file)
        self.assertTrue(mock_save_to_excel.called)

    @patch('main.Linguee.get_proxies')
    def test_execute_generate_successful_proxies(self, mock_get_proxies):
        self.linguee.execute_generate_successful_proxies()
        self.assertTrue(mock_get_proxies.called)

    @patch('builtins.print')
    def test_execute_main(self, mock_print):
        self.linguee.successful_proxies = ['10:100']
        self.linguee.break_loop = True
        self.linguee.execute_main()
        mock_print.assert_called_with('Finished executing')


if __name__ == '__main__':
    unittest.main()
