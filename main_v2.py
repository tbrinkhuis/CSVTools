from datetime import datetime 
import glob
import os
import sys
import time
import tkinter as tk
from tkinter import ttk
from tkinter import Menu, Menubutton, filedialog, messagebox
from tkinter.ttk import *
from tkinter.constants import DISABLED, N,S,E,W


import numpy as np
import pandas as pd

os.chdir(os.getcwd()) # change the directory to the current working dir

window = tk.Tk()
window.title('CatSV - CSV Tool') #window title
window.geometry('1100x768') # window size Should be 383x378. If the users has custom scaling enabled, this will need to be change. if the user is using custom scaling in win10, ya window is going to be FU
# window.resizable(0, 0) # do not allow resizing

#declaring a bunch of vars

class cat:

    def __init__(self):
        print("in init")
        
    def sd(self, prompt=True): #select directory, call fil dialog box
        if prompt:
            self.selected_dir = os.chdir(filedialog.askdirectory(title = "Select the folder that contains your CSV trend files"))
        # self.selected_dir = os.chdir(os.getcwd())
        w_files_lb.set(self.filenames())

    def filenames(self): # get csv file list from the cur dir.
        self.csv_list = [i for i in glob.glob('*.{}'.format('csv'))]
        return self.csv_list

    def lst_to_upper(list_to_change): # Take a single dem. list and capitalize everything
        for i in list_to_change: 
            list_to_change[list_to_change.index(i)] = list_to_change[list_to_change.index(i)].upper()
        return list_to_change

    def lst_to_search(list_to_search): # Take a single dem. list and capitalize everything
        for i in list_to_search: 
            list_to_search[list_to_search.index(i)] = list_to_search[list_to_search.index(i)].upper()
        return list_to_search

    def open_dir(self): # open the current dir
            os.startfile(os.curdir)

    def get_data(self, files): # get all of the data, concatinate and sort
        rows_to_skip = int(w_spn_header_row.get()) # get the spinbox value and sub 1 since we need to skip 1 less row than the header
        w_lb_columns.delete(0, 'end') # clear the listbox

        df = [pd.read_csv(w_lb_files.get(f), skiprows=(rows_to_skip)) for f in files] # read all of the csv files selected

        if df: # got df?
            self.concat_df = pd.concat(df, sort=False) # combine all csv files
            self.header = list(self.concat_df) # get the header of the concatinated dataframe

            print(self.header)

            self.header = self.lst_to_upper(self.header) # upper case everything in da list
            
            #search the header series for the keyword, if it is present, then search every header item
            if 'TIME' in self.header: 
                for i in self.header: #for every item in the self.header
                    if 'TIME' in i: # search for the keyword in every list item contained in i
                        self.time_index_inf = i # return the index of the list item that matched

            if 'DATE' in self.header: 
                for i in self.header: #for every item in the self.header
                    if 'DATE' in i: # search for the keyword in every list item contained in i

                        self.date_index_inf = i # return the index of the list item that matched

            self.concat_df = self.concat_df[0:] # remove the header for replacement
            self.concat_df.columns = self.header # load in the new header that is all caps. for searching reasons down the line


            # sorted_df = concat_df.sort_values(by='TIME') # sort the dataframe based on the timestamp col
            # concat_df_header = list(concat_df)
            w_lb_columns_var.set(self.header) # update the columns listbox. Done with the sorted DF so all self.header entrys are unique
            w_dd_date_col['value'] = self.header
            w_dd_time_col['value'] = self.header
            w_dd_target_col['value'] = self.header
            w_dd_temp_col['value'] = self.header
        else:
            print('Something happened while trying to read the selected file. Make sure eveything \
                selected starts on the same row and have the same timestamp headers')



m = cat()

button_width = 18
combo_col_width = 22
combo_width = 10
lbl_width = 16
text_width = 10

# Dir, Import, Sel all buttons, row spinbox, and files listbox
w_col_0 = Frame(window, width=30).grid(row=0, column=0,ipady=5,ipadx=5,padx=5,pady=5,columnspan=2,rowspan=19)
# Sel all button and col listbox
w_col_1 = Frame(window, width=30).grid(row=0, column=3,ipady=5,ipadx=5,padx=5,pady=5,columnspan=2,rowspan=19)
# save, graph, alpha, alpha report buttons
w_col_2 = Frame(window).grid(row=0, column=5,ipady=5,ipadx=5,padx=5,pady=5,columnspan=4,rowspan=1)
# settings area
w_col_3 = Frame(window).grid(row=2, column=5,ipady=5,ipadx=5,padx=5,pady=5,columnspan=4,rowspan=18)

# Col 0

# Select Dir button
w_b_sel_dir = Button(col_0, text='Select Directory', width=28, command=m.sd)
w_b_sel_dir.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

# Header row Label and spinbox
w_header_row_lbl = Label(col_0, text='Header row:', anchor=E, width=14)
w_header_row_lbl.grid(row=1,column=0, padx=5, pady=5)

w_spn_header_row = Spinbox(col_0, from_=0, to=20, width=5, textvariable=14) 
w_spn_header_row.grid(row=1,column=1, padx=5, pady=5)
w_spn_header_row.set(14)

# Select all files in listox
w_b_select_all = Button(col_1, text='Select all', width=13, command=m.select_all_files)
w_b_select_all.grid(row=2, column=0, padx=5, pady=5)

# Import Button
w_b_import = Button(col_0, text='Import', width=13, command=m.files_to_columns)
b_import.grid(row=2, column=1, padx=5, pady=5)

# Files listbox
w_lb_files_var = tk.StringVar()
w_lb_files = tk.Listbox(col_0, listvariable=files_lb_var, selectmode=tk.MULTIPLE, height=29, width=30, exportselection=False)
w_lb_files.grid(row=3, column=0, columnspan=2, rowspan=16, padx=5, pady=5, sticky=(N,S,E,W))


# Col 3
# Select all columns in listbox
w_b_select_all = Button(col_1, text='Select all', width=28, command=m.select_all_col)
w_b_select_all.grid(row=0, column=3, padx=5, pady=5, columnspan=2)

# Listbox for file columns
w_lb_columns_var = tk.StringVar()
w_lb_columns = tk.Listbox(col_1, listvariable=columns_lb_var, selectmode=tk.MULTIPLE, width=30, exportselection=False)
w_lb_columns.grid(row=1, column=3, columnspan=2, rowspan=18, padx=5, pady=5, sticky=(N,S,E,W))

# Col 5 Row 0
# Save selected button
w_b_save = Button(col_2, text='Save Selected', width=button_width, command=m.save_selection)
w_b_save.grid(row=0, column=5, padx=5, pady=5)

# Graph button
w_b_graph = Button(col_2, text='Graph Selected', width=button_width, command=m.stop)
w_b_graph.grid(row=0, column=6, padx=5, pady=5)

# Gen Alpha Button
w_b_alpha = Button(col_2, text='Find Alpha', width=button_width)
b_alpha.grid(row=0, column=7, padx=5, pady=5)

# Save Alpha Report
w_b_alpha_report = Button(col_2, text='Save Alpha Report', width=button_width)
w_b_alpha_report.grid(row=0, column=8, padx=5, pady=5)

# Col 5 Row 1

w_sep_settings = Label(col_3, text='----------Settings----------------------------------------------------------------------------------------', width=72)
w_sep_settings.grid(row=1, column=5, padx=5, pady=5, columnspan=5)

w_date_col_lbl = Label(col_3,text='Date Col:', anchor=E, width=lbl_width)
w_date_col_lbl.grid(row=2, column=5, padx=5, pady=5)

w_dd_date_col_var = tk.StringVar
w_dd_date_col = ttk.Combobox(col_3, textvariable=dd_date_col_var, width=combo_col_width, postcommand=m.stop) # , textvariable=var3
w_dd_date_col.grid(row=2, column=6, padx=5, pady=5)

w_time_col_lbl = Label(col_3, text='Time Col:', anchor=E, width=lbl_width)
w_time_col_lbl.grid(row=2, column=7, padx=5, pady=5)

w_dd_time_col_var = tk.StringVar
w_dd_time_col = ttk.Combobox(col_3, textvariable=dd_time_col_var, value=15, width=combo_col_width)
w_dd_time_col.grid(row=2, column=8, padx=5, pady=5)


w_sample_rate_lbl = Label(col_3, text='Sample Rate:', anchor=E, width=lbl_width)
w_sample_rate_lbl.grid(row=3, column=5, padx=5, pady=5)

w_dd_sample_rate_var = tk.StringVar
w_dd_sample_rate = ttk.Combobox(col_3, textvariable=dd_sample_rate_var, value=['30s','15s','10s','5s','1s','500ms','250ms','100ms'], width=combo_width)
w_dd_sample_rate.grid(row=3, column=6, padx=5, pady=5)


w_fill_type_lbl = Label(col_3, text='Fill Method:', anchor=E, width=lbl_width)
w_fill_type_lbl.grid(row=3, column=7, padx=5, pady=5)

w_dd_fill_type_var = tk.StringVar
w_dd_fill_type = ttk.Combobox(col_3, textvariable=dd_fill_type_var, value=['interpolate', 'backfill', 'forward fill', 'Zero Fill', 'NaN Fill'], width=combo_width)
w_dd_fill_type.grid(row=3, column=8, padx=5, pady=5)


w_sep_alpha_settings = Label(col_3, text='----------Alpha Settings----------------------------------------------------------------------------------', width=72)
w_sep_alpha_settings.grid(row=4, column=5, padx=5, pady=5, columnspan=5)

w_target_col_lbl = Label(col_3, text='Target Col:', anchor=E, width=lbl_width)
w_target_col_lbl.grid(row=5, column=5, padx=5, pady=5)

w_dd_target_col_var = tk.StringVar
w_dd_target_col = ttk.Combobox(col_3, textvariable=dd_target_col_var, value=15, width=combo_col_width)
w_dd_target_col.grid(row=5, column=6, padx=5, pady=5)

w_temp_col_lbl = Label(col_3, text='Temp Col:', anchor=E, width=lbl_width)
w_temp_col_lbl.grid(row=5, column=7, padx=5, pady=5)

w_dd_temp_col_var = tk.StringVar
w_dd_temp_col = ttk.Combobox(col_3, textvariable=dd_temp_col_var, value=15, width=combo_col_width)
w_dd_temp_col.grid(row=5, column=8, padx=5, pady=5)

w_lower_b_lbl = Label(col_3, text='Lower Boundary: ', anchor=E, width=lbl_width)
w_lower_b_lbl.grid(row=6, column=5, padx=5, pady=5)

w_txt_lower_b = tk.Text(col_3, height=1, width=text_width, )
w_txt_lower_b.grid(row=6, column=6, padx=5, pady=5)
w_txt_lower_b.insert(tk.INSERT,-1)

w_upper_b_lbl = Label(col_3, text='Upper Boundary: ', anchor=E, width=lbl_width)
w_upper_b_lbl.grid(row=6, column=7, padx=5, pady=5)

w_txt_upper_b = tk.Text(col_3, height=1, width=text_width)
w_txt_upper_b.grid(row=6, column=8, padx=5, pady=5)
w_txt_upper_b.insert(tk.INSERT,2)


w_div_lbl = Label(col_3, text='Divisions: ', anchor=E, width=lbl_width)
w_div_lbl.grid(row=7, column=5, padx=5, pady=5)

w_txt_div = tk.Text(col_3, height=1, width=text_width)
w_txt_div.grid(row=7, column=6, padx=5, pady=5)
w_txt_div.insert(tk.INSERT,20)

w_max_cycles_lbl = Label(col_3, text='Maximum Cycles: ', anchor=E, width=lbl_width)
w_max_cycles_lbl.grid(row=7, column=7, padx=5, pady=5)

w_txt_max_cycles = tk.Text(col_3, height=1, width=text_width)
w_txt_max_cycles.grid(row=7, column=8, padx=5, pady=5)
w_txt_max_cycles.insert(tk.INSERT,10)


w_STDEV_lbl = Label(col_3, text='STDEV Ceiling: ', anchor=E, width=lbl_width)
w_STDEV_lbl.grid(row=8, column=5, padx=5, pady=5)

w_txt_STDEV = tk.Text(col_3, height=1, width=text_width)
w_txt_STDEV.grid(row=8, column=6, padx=5, pady=5)
w_txt_STDEV.insert(tk.INSERT,0.0001)


w_offset_lbl = Label(col_3, text='Offset: ', anchor=E, width=lbl_width)
w_offset_lbl.grid(row=8, column=7, padx=5, pady=5)

w_txt_offset = tk.Text(col_3, height=1, width=text_width)
w_txt_offset.grid(row=8, column=8, padx=5, pady=5)
w_txt_offset.insert(tk.INSERT,0.00)

window.mainloop()