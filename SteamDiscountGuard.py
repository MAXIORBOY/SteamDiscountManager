import tkinter as tk
import pandas as pd
from tkinter import messagebox
import json


class SteamDiscountGuard:
    def __init__(self, data_file_name="steam_discounts.csv", priority_titles_file_name="priority_titles.json"):
        self.data_file_name = data_file_name
        self.priority_titles_file_name = priority_titles_file_name

        self.data = self.get_data_from_file()
        self.priority_titles = self.get_priority_titles()

        self.priority_titles_on_discount_dictionary = self.check_which_priority_titles_are_on_discount()
        if len(self.priority_titles_on_discount_dictionary.keys()):
            self.message = self.format_message_to_user()
            self.send_messagebox_to_user()

    def get_data_from_file(self):
        return pd.read_csv(self.data_file_name)

    def get_priority_titles(self):
        with open(self.priority_titles_file_name, "r") as f:
            priority_titles_dictionary = json.load(f)

        return priority_titles_dictionary["Titles"]

    def check_which_priority_titles_are_on_discount(self):
        priority_titles_on_discount = {}
        for priority_title in self.priority_titles:
            if len(self.data[self.data["Name"] == priority_title]):
                priority_titles_on_discount[priority_title] = list(self.data[self.data["Name"] == priority_title].iloc[0])[1:3]

        return priority_titles_on_discount

    def format_message_to_user(self):
        number_of_priority_titles_on_discount = len(list(self.priority_titles_on_discount_dictionary.keys()))
        if number_of_priority_titles_on_discount > 1:
            message = f"There are {number_of_priority_titles_on_discount} titles from your priority list on discount!\n\n"
        else:
            message = f"There is {number_of_priority_titles_on_discount} title from your priority list on discount!\n\n"

        for priority_title_on_discount in list(self.priority_titles_on_discount_dictionary.keys()):
            message += f"* {priority_title_on_discount} is now on {self.priority_titles_on_discount_dictionary[priority_title_on_discount][0]}% discount. Price: {self.priority_titles_on_discount_dictionary[priority_title_on_discount][1]}"

        return message

    def send_messagebox_to_user(self):
        window = tk.Tk()
        window.title("Steam Discount Guard")
        window.withdraw()

        m_box = messagebox.showinfo("Steam Discount Guard", self.message)
        if m_box == 'ok':
            window.destroy()
