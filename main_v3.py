from datetime import datetime 
import glob
import os
import sys
import time
import tkinter as tk
from tkinter import ttk
from tkinter import Menu, Menubutton, filedialog, messagebox
from tkinter.ttk import *
from tkinter.constants import DISABLED, FALSE, N,S,E,W
import matplotlib.pyplot as plt


import numpy as np
import pandas as pd

os.chdir(os.getcwd()) # change the directory to the current working dir


regex_time = '(\d\d[:|.]\d\d[:|.]\d\d[:|.|+]\d\d\d|\d[:|.]\d\d[:|.]\d\d[:|.|+]\d\d\d|\d[:|.]\d\d[:|.]\d\d[:|.|+]\d\d|\d\d[:|.]\d\d[:|.]\d\d|\d[:|.]\d\d[:|.]\d\d)'
regex_date = '(\d\d\d\d[-|.|/]\d\d[-|.|/]\d\d|\d\d[-|.|/]\d\d[-|.|/]\d\d|\d[-|.|/]\d\d[-|.|/]\d\d|\d\d[-|.|/]\d\d[-|.|/]\d\d|\d\d[-|.|/]\d\d[-|.|/]\d\d\d\d|\d[-|.|/]\d\d[-|.|/]\d\d\d\d|\d\d\d\d[-|.|/]\d\d[-|.|/]\d|\d\d[-|.|/]\d\d[-|.|/]\d)'


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
        w_lb_files_var.set(self.filenames())

    def filenames(self): # get csv file list from the cur dir.
        self.csv_list = [i for i in glob.glob('*.{}'.format('csv'))]
        return self.csv_list

    def lst_to_upper(self, list_to_change): # Take a single dem. list and capitalize everything
        for i in list_to_change: 
            list_to_change[list_to_change.index(i)] = list_to_change[list_to_change.index(i)].upper()
        return list_to_change

    def lst_search(self, list_to_search, item): # Take a single dem. list and capitalize everything
        item = item.upper()
        try:
            for list_item in list_to_search:
                print(f'{list_item} = {item}') 
                if item in list_item.upper():
                    return list_item
        except:
            print('Something went wrong in the lst_search method.')

    def open_dir(self): # open the current dir
            os.startfile(os.curdir)

    def files_to_columns(self):
        self.current_file_sel = w_lb_files.curselection() # get a list of selected files
        if self.current_file_sel: # if something is selected
            self.get_data(self.current_file_sel) # call get data function with the list of selected files
            files_in_dir = self.filenames() # return a list of CSV files in the CWD
        else:
            print('nothing has been selected...')
            messagebox.showinfo("User Error", "Select a file to load!")


    def time_n_date(self, df1):
        date_col = w_dd_date_col.get()
        time_col = w_dd_time_col.get()
        df = df1
        print('timendate pre:')
        print(df)

        old_time_col = df[time_col].tolist() # get the timestamp from the df so we can build datetime
        old_time_col = pd.Series(old_time_col)
        new_time_col = old_time_col.str.extract(pat = regex_time)

        old_date_col = df[date_col].tolist()
        old_date_col = pd.Series(old_date_col)
        new_date_col = old_date_col.str.extract(pat = regex_date)

        df[time_col] = pd.to_datetime(new_date_col[0] + ' ' + new_time_col[0], infer_datetime_format=True) # convert new_timestamp object to datetime for use with resampling format='%m/%d/%Y %H:%M:%S'                                         

        print('timendate post:')
        print(df.info())
        # df = df.reset_index(drop=True)
        return df
        # self.sorted_df = df

        # print('self.sorted_df:')
        # print(self.sorted_df)

    # def resample_data(self, df1):
    #     #must be called before files_to_col
    #     df = df1.reset_index(drop=True)
    #     # if w_dd_fill_type.get() != 'No Samp/fill':
    #     if w_dd_fill_type.get() == 'Interpolate':
    #         df = df.set_index(w_dd_time_col.get()).resample('100ms').interpolate() # resample the dataframe, this needs to be a multiple what the final rate will be. 
    #     else:
    #         df = df.set_index(w_dd_time_col.get()).resample('100ms',).fillna(method=w_dd_fill_type.get())
    
    #     df = df.asfreq(freq=w_dd_sample_rate.get()) # grab this frequency of time from the resampled dataframe
    #     df = df.reset_index(drop=True) # reset the index so TIME is included in the save
    #     df = df.round(10)
    #     df.info(verbose=True)
    #     return df



    def get_data(self, files): # get all of the data, concatinate and sort
        try:
            rows_to_skip = float(w_spn_header_row.get()) # get the spinbox value and sub 1 since we need to skip 1 less row than the header
            rows_to_skip = int(rows_to_skip.__round__())
            w_lb_columns.delete(0, 'end') # clear the listbox
        except ValueError:
            print('some wierd characters are hanging out in the header row spinbox')
            messagebox.showwarning(title='Select a real row', message='Some wierd characters are hanging out in the header row spinbox! The row number must be and integer.')

        try:
            df = [pd.read_csv(w_lb_files.get(f), skiprows=(rows_to_skip),  encoding ='UTF8') for f in files] # read all of the csv files selected
        except:
            print('Something went wrong in method get_data. The program was unable to read the selected file')
            messagebox.showerror(title='Failed to read files', message='Something went wrong in method get_data. The program was unable to read the selected file.')

        if df: # got df?
            # try:
                df = pd.concat(df, sort=False) # combine all csv files. This should combine any identical headers
                self.header = list(df) # get the header of the concatinated dataframe

                # print(self.header)

                self.header = self.lst_to_upper(self.header) # upper case everything in da list
                df = df[0:] # remove the header for replacement
                df.columns = self.header # load in the new header that is all caps. for searching reasons down the line

                print('df:')
                print(df)
        
                w_lb_columns_var.set(self.header) # update the columns listbox. Done with the sorted DF so all self.header entrys are unique
                w_dd_date_col['value'] = self.header
                w_dd_time_col['value'] = self.header
                w_dd_target_col['value'] = self.header
                w_dd_temp_col['value'] = self.header

                # If the dat or time search came back with results, change the drop downs to those columns so the user does not have to
                self.header_date_col = self.lst_search(self.header, 'DATE')
                if self.header_date_col:
                    w_dd_date_col.set(self.header_date_col)

                self.header_time_col = self.lst_search(self.header, 'TIME')
                if self.header_time_col:
                    w_dd_time_col.set(self.header_time_col)

                self.concat_df = self.time_n_date(df)



                # return concat_df
                # concat_df = 0
            # except:
                # print('Something went wrong in get_data method. The program was unable to concatinate the dataframes')
                # messagebox.showerror(title='Failed to concatinate files', message='Something went wrong in get_data method. The program was unable to concatinate the files. This is usualy caused by combining files that do not share the same data structure.')

        else:
            print('Something happened while trying to read the selected file. Make sure eveything \
                selected starts on the same row and have the same timestamp headers')
            messagebox.showerror(title='Nothing in DF', message='Something went wrong in get_data method. While the program was able to read the files, nothing seems to be in the dataframe.')

    def header_sel_inv(self): 
        # Get a list of columns that are not selected
        # should be called after get_data and befor resampling
        # this is to drop any unwanted data from the DF before performing interpolation
        header_sel_col_inv = []
        header_sel_col_index = w_lb_columns.curselection()
        header_sel_col = [w_lb_columns.get(c) for c in header_sel_col_index] # get a list of all the selected items in the col listbox
        for a in self.header: # Global var of the header
            if a not in header_sel_col:  # this is inverting the list of selected columns and retuning one with eveything that was not selected so they can be dropped
                print("Appending: " + a)
                header_sel_col_inv.append(a)
        return header_sel_col_inv

    def resample_data(self, df1, freq, round_place=10):
        #must be called before files_to_col
        date_col = w_dd_date_col.get()
        time_col = w_dd_time_col.get()
        # header_inv = self.header_sel_inv()
        df = df1
        print(f'resample_prePRE:\n {df}')

        # df = df.drop(columns=header_inv)
        # df = df1.reset_index(drop=True)
        # if w_dd_fill_type.get() != 'No Samp/fill':
        # df = df[~df.index.duplicated(keep='first')]
        print(f'resample_dups:\n {df}')
        # df = df[df[time_col].duplicated(keep='first')]
        df = df.drop_duplicates(subset=time_col, keep="first")
        df = df.set_index(pd.DatetimeIndex(df[time_col]))  #.sort(time_col)
        print(f'resample_pre:\n {df}')
        if w_dd_fill_type.get() == 'Interpolate':
            print('interp')
            df = df.resample('100ms').interpolate() # resample the dataframe, this needs to be a multiple what the final rate will be. 
        else:
            print('other')
            df = df.resample('100ms',).fillna(method=w_dd_fill_type.get())

        # df = df.drop_duplicates(subset=time_col, keep="first")
        df = df.asfreq(freq=freq) # grab this frequency of time from the resampled dataframe
        # df = df.reset_index(drop=True) # reset the index so TIME is included in the save
        df = df.round(round_place)
        df.info(verbose=True)
        print(f'resample_set_freq_post:\n{df}') 
        return df
        # return df


    def save_data(self,df1):
        header_sel_col_index = w_lb_columns.curselection()
        header_sel_col = [w_lb_columns.get(c) for c in header_sel_col_index] # get a list of all the selected items in the col listbox
        dd_time_col = w_dd_time_col.get()
        df = self.resample_data(df1, w_dd_sample_rate.get())
        try:
            df.to_csv('OUTPUT_FILE.csv', columns=header_sel_col, index=False) # , columns=col_lbl
            self.sd(prompt=False)
            os.startfile('OUTPUT_FILE.csv') # open the newly saved file
        except PermissionError:
            print('Failed to write to file... :(')
            messagebox.showinfo("Oh no! Permission denied!", "Your file failed to save, permission was denied!")
        except:
            print('Failed to write to file... :(')
            messagebox.showinfo("Oh no! Something terrible has happened!", "The file failed to save.")

       

    def graph_data(self, df1, dpi=100, figsize=(11,7)):
        df = self.resample_data(df1)
        df = df.reset_index(drop=True)
        print(df)
        # df = df.drop_duplicates(subset=time_col, keep="first")
        header_sel_col_index = w_lb_columns.curselection()
        header_sel_col = [w_lb_columns.get(c) for c in header_sel_col_index]

        lc = 0
        try:
            while lc < len(header_sel_col):
                if w_dd_time_col.get() in header_sel_col[lc]:
                    header_sel_col.pop(lc)
                lc += 1
        except KeyError:
            pass
        print(header_sel_col)
        
        df.plot(y=header_sel_col)
        plt.show()

    def b_save_date(self):
        self.save_data(self.concat_df)

    # def b_graph_data(self):
    #     print('b_graph')
    #     print(self.sorted_df)
    #     self.graph_data(self.sorted_df)



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
w_b_sel_dir = Button(w_col_0, text='Select Directory', width=28, command=m.sd)
w_b_sel_dir.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

# Header row Label and spinbox
w_header_row_lbl = Label(w_col_0, text='Header row:', anchor=E, width=14)
w_header_row_lbl.grid(row=1,column=0, padx=5, pady=5)

w_spn_header_row = Spinbox(w_col_0, from_=0, to=20, width=5) 
w_spn_header_row.grid(row=1,column=1, padx=5, pady=5)
w_spn_header_row.set(13)

# Select all files in listox
w_b_select_all = Button(w_col_1, text='Select all', width=13)
w_b_select_all.grid(row=2, column=0, padx=5, pady=5)

# Import Button
w_b_import = Button(w_col_0, text='Import', width=13, command=m.files_to_columns)
w_b_import.grid(row=2, column=1, padx=5, pady=5)

# Files listbox
w_lb_files_var = tk.StringVar()
w_lb_files = tk.Listbox(w_col_0, listvariable=w_lb_files_var, selectmode=tk.MULTIPLE, height=29, width=30, exportselection=False)
w_lb_files.grid(row=3, column=0, columnspan=2, rowspan=16, padx=5, pady=5, sticky=(N,S,E,W))


# Col 3
# Select all columns in listbox
w_b_select_all = Button(w_col_1, text='Select all', width=28)
w_b_select_all.grid(row=0, column=3, padx=5, pady=5, columnspan=2)

# Listbox for file columns
w_lb_columns_var = tk.StringVar()
w_lb_columns = tk.Listbox(w_col_1, listvariable=w_lb_columns_var, selectmode=tk.MULTIPLE, width=30, exportselection=False)
w_lb_columns.grid(row=1, column=3, columnspan=2, rowspan=18, padx=5, pady=5, sticky=(N,S,E,W))

# Col 5 Row 0
# Save selected button
w_b_save = Button(w_col_2, text='Save Selected', width=button_width, command=m.b_save_date)
w_b_save.grid(row=0, column=5, padx=5, pady=5)

# Graph button
w_b_graph = Button(w_col_2, text='Graph Selected', width=button_width)
w_b_graph.grid(row=0, column=6, padx=5, pady=5)

# Gen Alpha Button
w_b_alpha = Button(w_col_2, text='Find Alpha', width=button_width)
w_b_alpha.grid(row=0, column=7, padx=5, pady=5)

# Save Alpha Report
w_b_alpha_report = Button(w_col_2, text='Save Alpha Report', width=button_width)
w_b_alpha_report.grid(row=0, column=8, padx=5, pady=5)

# Col 5 Row 1

w_sep_settings = Label(w_col_3, text='----------Settings----------------------------------------------------------------------------------------', width=72)
w_sep_settings.grid(row=1, column=5, padx=5, pady=5, columnspan=5)

w_date_col_lbl = Label(w_col_3,text='Date Col:', anchor=E, width=lbl_width)
w_date_col_lbl.grid(row=2, column=5, padx=5, pady=5)

w_dd_date_col_var = tk.StringVar
w_dd_date_col = ttk.Combobox(w_col_3, textvariable=w_dd_date_col_var, width=combo_col_width) # , textvariable=var3
w_dd_date_col.grid(row=2, column=6, padx=5, pady=5)

w_time_col_lbl = Label(w_col_3, text='Time Col:', anchor=E, width=lbl_width)
w_time_col_lbl.grid(row=2, column=7, padx=5, pady=5)

w_dd_time_col_var = tk.StringVar
w_dd_time_col = ttk.Combobox(w_col_3, textvariable=w_dd_time_col_var, value=15, width=combo_col_width)
w_dd_time_col.grid(row=2, column=8, padx=5, pady=5)


w_sample_rate_lbl = Label(w_col_3, text='Sample Rate:', anchor=E, width=lbl_width)
w_sample_rate_lbl.grid(row=3, column=5, padx=5, pady=5)

w_dd_sample_rate_var = tk.StringVar
w_dd_sample_rate = ttk.Combobox(w_col_3, textvariable=w_dd_sample_rate_var, value=['30s','15s','10s','5s','1s','500ms','100ms'], width=combo_width)
w_dd_sample_rate.grid(row=3, column=6, padx=5, pady=5)
w_dd_sample_rate.set('30s')

w_fill_type_lbl = Label(w_col_3, text='Fill Method:', anchor=E, width=lbl_width)
w_fill_type_lbl.grid(row=3, column=7, padx=5, pady=5)

w_dd_fill_type_var = tk.StringVar
w_dd_fill_type = ttk.Combobox(w_col_3, textvariable=w_dd_fill_type_var, value=['Interpolate', 'backfill', 'ffill', 'pad', 'No Samp/fill'], width=combo_width)
w_dd_fill_type.grid(row=3, column=8, padx=5, pady=5)
w_dd_fill_type.set('Interpolate')


w_sep_alpha_settings = Label(w_col_3, text='----------Alpha Settings----------------------------------------------------------------------------------', width=72)
w_sep_alpha_settings.grid(row=4, column=5, padx=5, pady=5, columnspan=5)

w_target_col_lbl = Label(w_col_3, text='Target Col:', anchor=E, width=lbl_width)
w_target_col_lbl.grid(row=5, column=5, padx=5, pady=5)

w_dd_target_col_var = tk.StringVar
w_dd_target_col = ttk.Combobox(w_col_3, textvariable=w_dd_target_col_var, value=15, width=combo_col_width)
w_dd_target_col.grid(row=5, column=6, padx=5, pady=5)

w_temp_col_lbl = Label(w_col_3, text='Temp Col:', anchor=E, width=lbl_width)
w_temp_col_lbl.grid(row=5, column=7, padx=5, pady=5)

w_dd_temp_col_var = tk.StringVar
w_dd_temp_col = ttk.Combobox(w_col_3, textvariable=w_dd_temp_col_var, value=15, width=combo_col_width)
w_dd_temp_col.grid(row=5, column=8, padx=5, pady=5)

w_lower_b_lbl = Label(w_col_3, text='Lower Boundary: ', anchor=E, width=lbl_width)
w_lower_b_lbl.grid(row=6, column=5, padx=5, pady=5)

w_txt_lower_b = tk.Text(w_col_3, height=1, width=text_width, )
w_txt_lower_b.grid(row=6, column=6, padx=5, pady=5)
w_txt_lower_b.insert(tk.INSERT,-1)

w_upper_b_lbl = Label(w_col_3, text='Upper Boundary: ', anchor=E, width=lbl_width)
w_upper_b_lbl.grid(row=6, column=7, padx=5, pady=5)

w_txt_upper_b = tk.Text(w_col_3, height=1, width=text_width)
w_txt_upper_b.grid(row=6, column=8, padx=5, pady=5)
w_txt_upper_b.insert(tk.INSERT,2)


w_div_lbl = Label(w_col_3, text='Divisions: ', anchor=E, width=lbl_width)
w_div_lbl.grid(row=7, column=5, padx=5, pady=5)

w_txt_div = tk.Text(w_col_3, height=1, width=text_width)
w_txt_div.grid(row=7, column=6, padx=5, pady=5)
w_txt_div.insert(tk.INSERT,20)

w_max_cycles_lbl = Label(w_col_3, text='Maximum Cycles: ', anchor=E, width=lbl_width)
w_max_cycles_lbl.grid(row=7, column=7, padx=5, pady=5)

w_txt_max_cycles = tk.Text(w_col_3, height=1, width=text_width)
w_txt_max_cycles.grid(row=7, column=8, padx=5, pady=5)
w_txt_max_cycles.insert(tk.INSERT,10)


w_STDEV_lbl = Label(w_col_3, text='STDEV Ceiling: ', anchor=E, width=lbl_width)
w_STDEV_lbl.grid(row=8, column=5, padx=5, pady=5)

w_txt_STDEV = tk.Text(w_col_3, height=1, width=text_width)
w_txt_STDEV.grid(row=8, column=6, padx=5, pady=5)
w_txt_STDEV.insert(tk.INSERT,0.0001)


w_offset_lbl = Label(w_col_3, text='Offset: ', anchor=E, width=lbl_width)
w_offset_lbl.grid(row=8, column=7, padx=5, pady=5)

w_txt_offset = tk.Text(w_col_3, height=1, width=text_width)
w_txt_offset.grid(row=8, column=8, padx=5, pady=5)
w_txt_offset.insert(tk.INSERT,0.00)

window.mainloop()