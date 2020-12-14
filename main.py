from datetime import datetime 
import glob
import os
import sys
import time
import tkinter as tk
from tkinter import ttk
from tkinter import Menu, Menubutton, filedialog, messagebox
from tkinter.ttk import *
from tkinter.constants import N,S,E,W


import numpy as np
import pandas as pd

os.chdir(os.getcwd()) # change the directory to the current working dir

output_file = 'COMBINED_FILE.csv' # the name of the output file
timestamp_keyword = 'TIME' # the word used to search for the timestamp col. I beleave this can be a list.
start_header_row = 14
timestamp_keyword = timestamp_keyword.upper()


window = tk.Tk()
window.title('CatSV - CSV Tool') #window title
window.geometry('1024x768') # window size Should be 383x378. If the users has custom scaling enabled, this will need to be change. if the user is using custom scaling in win10, ya window is going to be FU
# window.resizable(0, 0) # do not allow resizing

#declaring a bunch of vars
sorted_df = ''
selected_dir = ''
current_file_sel = ''
csv_list  = ''
header = ''

class cat:

    def __init__(self):
        print("in init")
        
    def sd(self): #select directory, call fil dialog box
        global selected_dir
        selected_dir = os.chdir(filedialog.askdirectory(title = "Select the folder that contains your CSV trend files"))
        # selected_dir = os.chdir(os.getcwd())
        var2.set(self.filenames())

    def filenames(self): # get csv file list from the cur dir.
        global csv_list
        csv_list = [i for i in glob.glob('*.{}'.format('csv'))]
        return csv_list

    def list_upper(self, list_to_change):
        count = 0
        while count < len(list_to_change): # This will make the header all lower case for searching
            print(count)
            print(list_to_change[count])
            list_to_change[count] = list_to_change[count].upper()
            count += 1
        return list_to_change

    def change_dir(self): 
        self.sd()
        #update things....

    def open_dir(self): # open the current dir
            os.startfile(os.curdir)

    def select_all_files(self):
        for i in range(files_lb.size()):
            files_lb.selection_set(i)

    def select_all_col(self):
        for i in range(columns_lb.size()):
            columns_lb.selection_set(i)

    def strptime_with_offset(self, string, format='%m/%d/%Y %H:%M:%S'):
        base_dt = datetime.strptime(string[:-4], format)
        # offset = int(string[:-4])
        # delta = datetime.timedelta(hours=offset/100, minutes=offset%100)
        return base_dt # + delta

    def get_data(self, files): # get all of the data, concatinate and sort
        global sorted_df
        global header
        rows_to_skip = (int(header_row.get()) - 1) # get the spinbox value and sub 1 since we need to skip 1 less row than the header
        columns_lb.delete(0, 'end') # clear the listbox

        df = [pd.read_csv(files_lb.get(f), skiprows=(rows_to_skip)) for f in files] # read all of the csv files selected

        if df: # got df?
            concat_df = pd.concat(df, sort=False) # combine all csv files
            timestamp_index = 0
            header = list(concat_df) # get the header of the concatinated dataframe
            # header = list(df)
            print(header)

            header = self.list_upper(header) # upper case everything in da list
            
            #search the header series for the keyword, if it is present, then search every header item
            if timestamp_keyword in header: 
                for i in header: #for every item in the header
                    if timestamp_keyword in i: # search for the keyword in every list item contained in i
                        timestamp_index = header.index(i) # return the index of the list item that matched

            concat_df = concat_df[0:] # remove the header for replacement
            concat_df.columns = header # load in the new header that is all caps. for searching reasons down the line

            old_time_col = concat_df[concat_df.columns[timestamp_index]] # get the timestamp from the df so we can build datetime
            
            new_timestamps = concat_df['DATE'] + ' ' + old_time_col # combine the date and time into just the time col 
            
            new_timestamps = new_timestamps.apply(self.strptime_with_offset) # strip everythin out and format the datetime correctly for to_datetime
            
            new_timestamps = pd.to_datetime(new_timestamps, format='%m/%d/%Y %H:%M:%S') # convert new_timestamp object to datetime for use with resampling                                          

            concat_df[concat_df.columns[timestamp_index]] = new_timestamps # update the concatinated datafames timestamp column with clean time man 

            sorted_df = concat_df.sort_values(by='TIME') # sort the dataframe based on the timestamp col
            sorted_DF_header = list(sorted_df)
            var3.set(sorted_DF_header) # update the columns listbox. Done with the sorted DF so all header entrys are unique
            dd_date_col['value'] = sorted_DF_header
            dd_time_col['value'] = sorted_DF_header
            dd_target_col['value'] = sorted_DF_header
            dd_temp_col['value'] = sorted_DF_header




    def save_data(self, files, col):
        global sorted_df
        col_to_drop = []
        count = 0

        col_lbl = [columns_lb.get(c) for c in col] # get a list of all the selected items in the col listbox

        col_lb = self.list_upper(col_lbl)

        for a in header:
            if a not in col_lbl:
                print("Appending: " + a)
                col_to_drop.append(a)

        try:
            sorted_df = sorted_df.drop(columns=col_to_drop, errors='ignore')
            sorted_df = sorted_df.drop_duplicates(subset='TIME')
        except:
            pass
        #sorted_df.to_csv(output_file, columns=col_lbl, mode='a', index=False, encoding='utf-8-sig')
        print('DF: ')

        print(sorted_df)
        sorted_df.to_csv('combined2.csv', index=False) # , columns=col_lbl

        sorted_df = sorted_df.set_index('TIME').resample('1s').interpolate() # resample the dataframe, this needs to be a multiple what the final rate will be. 
        sorted_df = sorted_df.asfreq(freq='1S') # grab this frequency of time from the resampled dataframe
        sorted_df = sorted_df.reset_index() # reset the index so TIME is included in the save
        sorted_df = sorted_df.fillna(0) # fill all NaN's with 0
        sorted_df = sorted_df.round(5)
        sorted_df.info(verbose=True)
        try:
            sorted_df.to_csv(output_file, index=False) # , columns=col_lbl
            # if messagebox.askquestion("Success!", "Your file was saved! Would you like to open it?"):
            #     os.startfile(output_file) # open the newly saved file
        except PermissionError:
            print('Failed to write to file... :(')
            messagebox.showinfo("Oh no! Permission denied!", "Your file failed to save, permission was denied!")
        except:
            print('Failed to write to file... :(')
            messagebox.showinfo("Oh no! Something terrible has happened!", "The file failed to save.")

    def select_time(self):
        selected_col = columns_lb.curselection()
        print()
        print('')
        col_len = len(selected_col)
        count = 0
        if col_len == 1:
            columns_lb.itemconfig(selected_col, background='orange', fg='black')
        elif col_len < 1:
            messagebox.showinfo("Oh no!", 'You need to select one column for time.')
        else:
            messagebox.showinfo("Oh no!", 'You can only select one time column!')

    def files_to_columns(self):
        global current_file_sel
        current_file_sel = files_lb.curselection() # get a list of selected files
        if current_file_sel: # if something is selected
            self.get_data(current_file_sel) # call get data function with the list of selected files
            files_in_dir = self.filenames() # return a list of CSV files
            for n in range(len(files_in_dir)): # clear any previously highlighted items in the file names list box
                files_lb.itemconfig(n, background='', fg='black')
            for s in current_file_sel: #Highlight the files that have been selected and call the get_data function
                files_lb.itemconfig(s, bg='orange', fg='black')
                print(files_lb.get(s))
        else:
            print('nothing has been selected...')
            messagebox.showinfo("User Error", "Select a file to load!")


    def save_selection(self): #save selected colums into combined_data.csv
        global current_file_sel
        selection_col = columns_lb.curselection()
        self.save_data(current_file_sel, selection_col)

    def all_about_me(self):
        messagebox.showinfo("Created by:", "Created by Anthony Brinkhuis. 2020.")    

m = cat()


col_0 = tk.Frame(window, width=30).grid(row=0, column=0,ipady=5,ipadx=5,padx=5,pady=5,columnspan=2,rowspan=19)
col_1 = tk.Frame(window, width=30).grid(row=0, column=3,ipady=5,ipadx=5,padx=5,pady=5,columnspan=2,rowspan=19)
col_2 = tk.Frame(window).grid(row=0, column=5,ipady=5,ipadx=5,padx=5,pady=5,columnspan=4,rowspan=1)
col_3 = tk.Frame(window).grid(row=2, column=5,ipady=5,ipadx=5,padx=5,pady=5,columnspan=4,rowspan=18)

# Col 0

b_sel_dir = tk.Button(col_0, text='Select Directory', width=28, command=m.sd)
b_sel_dir.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

header_row_lbl = tk.Label(col_0, text='Header row:', anchor=E, width=14)
header_row_lbl.grid(row=1,column=0, padx=5, pady=5)

header_row = tk.Spinbox(col_0, from_=0, to=20, width=5) 
header_row.grid(row=1,column=1, padx=5, pady=5)

b_import = tk.Button(col_0, text='Import Selection', width=28, command=m.files_to_columns)
b_import.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

var2 = tk.StringVar()
files_lb = tk.Listbox(col_0, listvariable=var2, selectmode=tk.MULTIPLE, height=29, width=30)
files_lb.grid(row=3, column=0, columnspan=2, rowspan=16, padx=5, pady=5, sticky=(N,S,E,W))

# # Col 1

b_select_all = tk.Button(col_1, text='Select all', width=28)
b_select_all.grid(row=0, column=3, padx=5, pady=5, columnspan=2)

var3 = tk.StringVar()
columns_lb = tk.Listbox(col_1, listvariable=var3, selectmode=tk.MULTIPLE, width=30)
columns_lb.grid(row=1, column=3, columnspan=2, rowspan=18, padx=5, pady=5, sticky=(N,S,E,W))

# Col 2

b_save = tk.Button(col_2, text='Save Selected', width=16)
b_save.grid(row=0, column=5, padx=5, pady=5)

b_sampling = tk.Button(col_2, text='Graph Selected', width=16)
b_sampling.grid(row=0, column=6, padx=5, pady=5)

b_alpha = tk.Button(col_2, text='Find Alpha', width=16)
b_alpha.grid(row=0, column=7, padx=5, pady=5)

b_graph = tk.Button(col_2, text='Save Alpha Report', width=16)
b_graph.grid(row=0, column=8, padx=5, pady=5)

# Col 3

fill_type_lbl = tk.Label(col_3, text='----------Settings----------------------------------------------------------------------------------------', width=72)
fill_type_lbl.grid(row=1, column=5, padx=5, pady=5, columnspan=5)

date_col_lbl = tk.Label(col_3,text='Date Col:', anchor=E, width=14)
date_col_lbl.grid(row=2, column=5, padx=5, pady=5)

var_date_col = tk.StringVar
dd_date_col = ttk.Combobox(col_3, textvariable=var_date_col, state='readonly', width=14) # , textvariable=var3
dd_date_col.grid(row=2, column=6, padx=5, pady=5)


time_col_lbl = tk.Label(col_3, text='Time Col:', anchor=E, width=14)
time_col_lbl.grid(row=2, column=7, padx=5, pady=5)

var_time_col = tk.StringVar
dd_time_col = ttk.Combobox(col_3, textvariable=var_time_col, value=15, width=14)
dd_time_col.grid(row=2, column=8, padx=5, pady=5)


sample_rate_lbl = tk.Label(col_3, text='Sample Rate:', anchor=E, width=14)
sample_rate_lbl.grid(row=3, column=5, padx=5, pady=5)

var_sample_rate = tk.StringVar
dd_sample_rate = ttk.Combobox(col_3, textvariable=var_sample_rate, value=[30,15,10,5,1,0.5,0.25,0.1], width=14)
dd_sample_rate.grid(row=3, column=6, padx=5, pady=5)


fill_type_lbl = tk.Label(col_3, text='Fill Method:', anchor=E, width=14)
fill_type_lbl.grid(row=3, column=7, padx=5, pady=5)

var_fill_type = tk.StringVar
dd_fill_type = ttk.Combobox(col_3, textvariable=var_fill_type, value=['interpolate', 'backfill', 'forward fill', 'Zero Fill', 'NaN Fill'], width=14)
dd_fill_type.grid(row=3, column=8, padx=5, pady=5)


fill_type_lbl = tk.Label(col_3, text='----------Alpha Settings----------------------------------------------------------------------------------', width=72)
fill_type_lbl.grid(row=4, column=5, padx=5, pady=5, columnspan=5)

target_col_lbl = tk.Label(col_3, text='Target Col:', anchor=E, width=14)
target_col_lbl.grid(row=5, column=5, padx=5, pady=5)

var_target_col = tk.StringVar
dd_target_col = ttk.Combobox(col_3, textvariable=var_target_col, value=15, width=14)
dd_target_col.grid(row=5, column=6, padx=5, pady=5)

temp_col_lbl = tk.Label(col_3, text='Temp Col:', anchor=E, width=14)
temp_col_lbl.grid(row=5, column=7, padx=5, pady=5)

var_temp_col = tk.StringVar
dd_temp_col = ttk.Combobox(col_3, textvariable=var_temp_col, value=15, width=14)
dd_temp_col.grid(row=5, column=8, padx=5, pady=5)


lower_b_lbl = tk.Label(col_3, text='Lower Boundary: ', anchor=E, width=14)
lower_b_lbl.grid(row=6, column=5, padx=5, pady=5)

txt_lower_b = tk.Text(col_3, height=1, width=13)
txt_lower_b.grid(row=6, column=6, padx=5, pady=5)


upper_b_lbl = tk.Label(col_3, text='Upper Boundary: ', anchor=E, width=14)
upper_b_lbl.grid(row=6, column=7, padx=5, pady=5)

txt_upper_b = tk.Text(col_3, height=1, width=13)
txt_upper_b.grid(row=6, column=8, padx=5, pady=5)


div_lbl = tk.Label(col_3, text='Divisions: ', anchor=E, width=14)
div_lbl.grid(row=7, column=5, padx=5, pady=5)

txt_div = tk.Text(col_3, height=1, width=13)
txt_div.grid(row=7, column=6, padx=5, pady=5)


max_cycles_lbl = tk.Label(col_3, text='Maximum Cycles: ', anchor=E, width=14)
max_cycles_lbl.grid(row=7, column=7, padx=5, pady=5)

txt_max_cycles = tk.Text(col_3, height=1, width=13)
txt_max_cycles.grid(row=7, column=8, padx=5, pady=5)


STDEV_lbl = tk.Label(col_3, text='STDEV Ceiling: ', anchor=E, width=14)
STDEV_lbl.grid(row=8, column=5, padx=5, pady=5)

txt_STDEV = tk.Text(col_3, height=1, width=13)
txt_STDEV.grid(row=8, column=6, padx=5, pady=5)


offset_lbl = tk.Label(col_3, text='Offset: ', anchor=E, width=14)
offset_lbl.grid(row=8, column=7, padx=5, pady=5)

txt_offset = tk.Text(col_3, height=1, width=13)
txt_offset.grid(row=8, column=8, padx=5, pady=5)

window.mainloop()