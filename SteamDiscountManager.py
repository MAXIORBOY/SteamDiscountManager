import tkinter as tk
import pandas as pd
from tkscrolledframe import ScrolledFrame
from tkinter import font
from tkinter import ttk
import os
import time
import datetime
from SteamDiscountScrapper import SteamDiscountScrapper
import json


class SteamDiscountManager:
    def __init__(self, data_file_name="steam_discounts.csv", priority_titles_file_name="priority_titles.json", user_prefs_file_name="user_prefs.json"):
        self.data_file_name = data_file_name
        self.priority_titles_file_name = priority_titles_file_name
        self.data = None
        self.get_data_from_file()
        self.data_modification_time = None
        self.get_data_modification_time()

        self.priority_titles = self.get_priority_titles()

        self.columns = list(self.data.columns)
        self.columns_width = (50, 10, 12, 12, 16, 19)
        self.columns_parameters = {"Discount": (0, 100, 5), "New Price": (0, 1000, 10), "Positive Reviews": (0, 100, 5), "Number of Reviews": (0, 100000, 2500)}
        self.name_max_chars = 50
        self.sort_types = ('Ascending', 'Descending')

        self.user_prefs_file_name = user_prefs_file_name
        self.user_prefs_dictionary = self.get_user_prefs_data()

        self.current_data = self.data
        self.window = None

        self.create_new_window()

    def create_new_window(self):
        self.window = tk.Tk()
        self.window.title('Steam Discount Manager')

    def get_priority_titles(self):
        with open(self.priority_titles_file_name, "r") as f:
            priority_titles_dictionary = json.load(f)

        return priority_titles_dictionary["Titles"]

    def get_user_prefs_data(self):
        with open(self.user_prefs_file_name, "r") as f:
            user_prefs_dictionary = json.load(f)

        return user_prefs_dictionary

    def set_current_data(self):
        self.current_data = self.data

    def window_config(self, width_adjuster=0.85, height_adjuster=0.55):
        self.window.attributes('-topmost', 1)
        self.window.attributes('-topmost', 0)
        self.window.focus_force()
        self.window.update()
        self.window.geometry('%dx%d+%d+%d' % (self.window.winfo_width(), self.window.winfo_height(), width_adjuster * ((self.window.winfo_screenwidth() / 2) - (self.window.winfo_width() / 2)), height_adjuster * ((self.window.winfo_screenheight() / 2) - (self.window.winfo_height() / 2))))

    def get_data_modification_time(self):
        self.data_modification_time = datetime.datetime.strptime(time.ctime(os.path.getmtime(self.data_file_name)), "%a %b %d %H:%M:%S %Y").strftime("%d-%m-%Y, %H:%M:%S")

    def get_data_from_file(self):
        self.data = pd.read_csv(self.data_file_name)

    def save_user_prefs(self):
        with open(self.user_prefs_file_name, "w") as f:
            json.dump(self.user_prefs_dictionary, f)

    def select_data_and_save_user_prefs(self, discount_value=None, new_price=None, positive_reviews=None, number_of_reviews=None):
        data = self.data
        if discount_value is not None:
            data = data[data["Discount"] >= discount_value]
        if new_price is not None:
            data = data[data["New Price"] <= new_price]
        if positive_reviews is not None:
            data = data[data["Positive Reviews"] >= positive_reviews]
        if number_of_reviews is not None:
            data = data[data["Number of Reviews"] >= number_of_reviews]

        for priority_title in self.priority_titles:
            priority_row = self.data[self.data["Name"] == priority_title]
            if len(priority_row):
                data = priority_row.append(data)

        self.current_data = data

    def sort_data(self, column, sort_type):
        self.current_data = self.current_data.sort_values(by=[column], ascending=bool(sort_type == 'Ascending'))

    def make_table_header(self, given_frame):
        frame = tk.Frame(given_frame)
        for i in range(len(self.columns)):
            l_box = tk.Listbox(frame, bg=self.window['bg'], width=self.columns_width[i], height=1, justify=tk.CENTER, font=font.Font(family='Helvetica', size=12, weight='bold'))
            l_box.insert(0, self.columns[i])
            l_box.pack(side=tk.LEFT)
        frame.pack(fill=tk.X)

    def format_element(self, column, element):
        if column == 'Name':
            if len(element) > self.name_max_chars:
                return f'{element[:self.name_max_chars]}...'
            else:
                return element
        elif column == 'Discount' or column == 'Positive Reviews' or column == 'Number of Reviews':
            if pd.notna(element):
                forward_string, back_string = '', ''
                if column == 'Discount':
                    forward_string = '-'
                    back_string = '%'
                if column == 'Positive Reviews':
                    back_string = '%'
                return f'{forward_string}{int(element)}{back_string}'
            else:
                return ''
        elif column == 'Old Price' or column == 'New Price':
            if pd.notna(element):
                return float(element)
            else:
                return ''

    def sort_button_fun(self, sort_by_column, type_sort):
        self.window.destroy()
        self.sort_data(sort_by_column, type_sort)

        self.user_prefs_dictionary["Sort Column"] = sort_by_column
        self.user_prefs_dictionary["Sort Type"] = type_sort

        self.save_user_prefs()
        self.create_new_window()
        self.manager_window()

    def filter_button_fun(self, filter_user_prefs):
        self.window.destroy()
        discount_value, new_price, positive_reviews, number_of_reviews = filter_user_prefs
        self.select_data_and_save_user_prefs(discount_value, new_price, positive_reviews, number_of_reviews)

        self.user_prefs_dictionary["Discount"] = discount_value
        self.user_prefs_dictionary["New Price"] = new_price
        self.user_prefs_dictionary["Positive Reviews"] = positive_reviews
        self.user_prefs_dictionary["Number of Reviews"] = number_of_reviews

        self.save_user_prefs()
        self.create_new_window()
        self.manager_window()

    def update_button_fun(self):
        self.window.destroy()
        SteamDiscountScrapper()
        self.get_data_from_file()
        self.get_data_modification_time()
        self.set_current_data()
        self.create_new_window()
        self.manager_window()

    def manager_window(self):
        tk.Label(self.window, text="Steam Discount Manager", bd=4, font=font.Font(family='Helvetica', size=14, weight='bold')).pack()
        frame = tk.Frame(self.window)
        tk.Label(frame, text=f'Data from: {self.data_modification_time}', font=font.Font(family='Helvetica', size=12, weight='normal')).pack(side=tk.LEFT)
        tk.Label(frame, text='      ', font=12).pack(side=tk.LEFT)
        button = tk.Button(frame, text='UPDATE', bd=4, font=12, command=lambda: [self.update_button_fun()])
        button.pack()
        frame.pack()

        tk.Label(self.window, text='', font=12).pack()
        outer_frame = tk.Frame(self.window)
        self.make_table_header(outer_frame)

        sf = ScrolledFrame(outer_frame, width=1100, height=500)
        sf.bind_scroll_wheel(self.window)
        sf.pack()
        inner_frame = sf.display_widget(tk.Frame)

        for i in range(self.current_data.shape[0]):
            frame = tk.Frame(inner_frame)
            row = list(self.current_data.iloc[i])
            for j in range(len(self.columns)):
                l_box = tk.Listbox(frame, width=self.columns_width[j], height=1, justify=tk.CENTER, font=font.Font(family='Helvetica', size=12, weight='normal'))

                l_box.insert(0, self.format_element(self.columns[j], row[j]))
                if i % 2 == 1:
                    l_box.itemconfig(0, bg='gray90')
                if row[0] in self.priority_titles:
                    l_box.itemconfig(0, fg='red')
                l_box.pack(side=tk.LEFT)
            frame.pack()

        tk.Label(outer_frame, text=f"Titles: {self.current_data.shape[0]}", bd=4, font=font.Font(family='Helvetica', size=12, weight='normal')).pack(anchor='w')
        outer_frame.pack()

        i = 0
        spinbox_values = [tk.IntVar() for _ in range(4)]
        frame = tk.Frame(self.window)
        tk.Label(frame, text='Filters:', bd=4, font=font.Font(family='Helvetica', size=12, weight='bold')).pack()
        for column in list(self.columns_parameters.keys()):
            tk.Label(frame, text=f'{column}:', font=font.Font(family='Helvetica', size=12, weight='normal')).pack(side=tk.LEFT)
            tk.Spinbox(frame, from_=self.columns_parameters[column][0], to=self.columns_parameters[column][1], textvariable=spinbox_values[i], width=6, bd=4, font=12, increment=self.columns_parameters[column][2], state="readonly", readonlybackground='white').pack(side=tk.LEFT)
            if self.user_prefs_dictionary[column] is not None:
                spinbox_values[i].set(self.user_prefs_dictionary[column])

            tk.Label(frame, text='      ', font=12).pack(side=tk.LEFT)
            i += 1

        button = tk.Button(frame, text='SELECT', bd=4, font=12, command=lambda: [self.filter_button_fun(tuple([value.get() for value in spinbox_values]))])
        button.pack()
        frame.pack()

        frame = tk.Frame(self.window)
        tk.Label(frame, text='\n', font=12).pack()
        tk.Label(frame, text='Sorting:', bd=4, font=font.Font(family='Helvetica', size=12, weight='bold')).pack()

        sort_by_column_value = tk.StringVar(value="Name")
        if self.user_prefs_dictionary["Sort Column"] is not None:
            sort_by_column_value.set(self.user_prefs_dictionary["Sort Column"])

        tk.Label(frame, text='Sort by:', bd=4, font=font.Font(family='Helvetica', size=12, weight='normal')).pack(side=tk.LEFT)
        combobox = ttk.Combobox(frame, width=20, textvariable=sort_by_column_value, state="readonly")
        combobox['values'] = self.columns
        combobox.pack(side=tk.LEFT)

        tk.Label(frame, text='      ', font=12).pack(side=tk.LEFT)

        type_sort_value = tk.StringVar(value="Descending")
        if self.user_prefs_dictionary["Sort Type"] is not None:
            type_sort_value.set(self.user_prefs_dictionary["Sort Type"])

        tk.Label(frame, text='Type:', bd=4, font=font.Font(family='Helvetica', size=12, weight='normal')).pack(side=tk.LEFT)
        combobox = ttk.Combobox(frame, width=15, textvariable=type_sort_value, state="readonly")
        combobox['values'] = self.sort_types
        combobox.pack(side=tk.LEFT)

        tk.Label(frame, text='      ', font=12).pack(side=tk.LEFT)
        button = tk.Button(frame, text='SORT', bd=4, font=12, command=lambda: [self.sort_button_fun(sort_by_column_value.get(), type_sort_value.get())])
        button.pack()

        frame.pack()

        self.window_config()
        self.window.mainloop()


if __name__ == "__main__":
    SteamDiscountManager().manager_window()
