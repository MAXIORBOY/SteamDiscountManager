from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import string
import time
import pandas as pd
import os


class SteamDiscountScrapper:
    def __init__(self, limit=1000, save_file_name="steam_discounts.csv"):
        self.webdriver_path = f'{os.getcwd()}\\chromedriver.exe'
        self.webdriver = webdriver.Chrome(self.webdriver_path)

        self.limit = limit
        self.scroll_pause_time = 1
        self.max_wait_time = 5
        self.save_file_name = save_file_name

        self.results = self.scrap_data()
        self.discount_data = self.format_scrapped_data()
        self.save_data()

    def scroll_down_to_bottom(self):
        last_height = self.webdriver.execute_script("return document.body.scrollHeight")

        while True:
            self.webdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(self.scroll_pause_time)

            new_height = self.webdriver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def scrap_data(self):
        self.webdriver.set_window_position(-10000, 0)
        self.webdriver.get("https://store.steampowered.com/search/?filter=topsellers&specials=1")
        self.scroll_down_to_bottom()
        result_table = WebDriverWait(self.webdriver, self.max_wait_time).until(EC.presence_of_element_located((By.ID, "search_resultsRows")))
        results = result_table.find_elements_by_class_name("responsive_search_name_combined")

        return results

    @staticmethod
    def get_column_names():
        return "Name", "Discount", "New Price", "Old Price", "Positive Reviews", "Number of Reviews"

    def format_scrapped_data(self):
        def extract_digits_from_text_as_integer(text):
            digits = ''
            for char in text:
                if char in string.digits:
                    digits += char

            return int(digits)

        def extract_value_from_price_as_float(price):
            price_value = ''
            last_separator = ''
            index = 0
            separator_index = 0

            for char in price:
                if char in string.digits:
                    price_value += char
                    index += 1
                elif char in string.punctuation or char in string.whitespace:
                    last_separator = char
                    separator_index = index

            new_price_value = ''
            index = 0
            for char in price_value:
                if index == separator_index:
                    new_price_value += last_separator
                new_price_value += char

                index += 1

            return float(new_price_value.replace(last_separator, '.'))

        data = []
        i = 0

        for result in self.results:
            if self.limit is not None:
                if not(i < self.limit):
                    break
            try:
                name = str(WebDriverWait(result, self.max_wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, "col.search_name"))).text)
                if name == '':
                    continue
                name = name.replace('\n', ' ')
            except:
                continue

            try:
                discount = str(WebDriverWait(result, self.max_wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, "col.search_discount"))).text)
                if discount != '':
                    discount_value = extract_digits_from_text_as_integer(discount)
                else:
                    discount_value = None
            except:
                discount_value = None

            try:
                prices = str(WebDriverWait(result, self.max_wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, "col.search_price.discounted"))).text)
                if prices != '':
                    old_price, new_price = prices.split('\n')
                    old_price = extract_value_from_price_as_float(old_price)
                    new_price = extract_value_from_price_as_float(new_price)
                else:
                    old_price, new_price = None, None
            except:
                old_price, new_price = None, None

            try:
                review = str(WebDriverWait(result, self.max_wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, "col.search_reviewscore"))).find_element_by_tag_name("span").get_attribute("data-tooltip-html"))
                all_reviews, rest_of_string = review.split('<br>')
                percentage_of_positive_reviews, rest_of_string = rest_of_string.split('%')
                percentage_of_positive_reviews = int(percentage_of_positive_reviews)
                number_of_reviews = extract_digits_from_text_as_integer(rest_of_string)

            except:
                all_reviews, percentage_of_positive_reviews, number_of_reviews = None, None, None

            data.append([name, discount_value, new_price, old_price, percentage_of_positive_reviews, number_of_reviews])

            i += 1

        self.webdriver.quit()

        return pd.DataFrame(data, columns=list(self.get_column_names()))

    def save_data(self):
        self.discount_data.to_csv(self.save_file_name, index=False)
