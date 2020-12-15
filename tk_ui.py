from datetime import datetime 
import glob
import os
import sys
import time
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import Menu, Menubutton, filedialog, messagebox
from tkinter.constants import N,S,E,W

window = tk.Tk()
window.title('CatSV - CSV Tool') 
window.geometry('1024x768')
window.resizable(0, 0)

def show_widgets():
    col_0 = tk.Frame(window, width=30).grid(row=0, column=0,ipady=5,ipadx=5,padx=5,pady=5,columnspan=2,rowspan=19)
    col_1 = tk.Frame(window, width=30).grid(row=0, column=3,ipady=5,ipadx=5,padx=5,pady=5,columnspan=2,rowspan=19)
    col_2 = tk.Frame(window).grid(row=0, column=5,ipady=5,ipadx=5,padx=5,pady=5,columnspan=4,rowspan=1)
    col_3 = tk.Frame(window).grid(row=2, column=5,ipady=5,ipadx=5,padx=5,pady=5,columnspan=4,rowspan=18)

    # Col 0
    
    var_sel_dir = tk.StringVar()
    b_sel_dir = tk.Button(col_0, text='Select Directory', width=28)
    b_sel_dir.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

    header_row_lbl = tk.Label(col_0, text='Header row:', anchor=E, width=14)
    header_row_lbl.grid(row=1,column=0, padx=5, pady=5)

    header_row_spn = tk.Spinbox(col_0, from_=0, to=20, width=5) 
    header_row_spn.grid(row=1,column=1, padx=5, pady=5)

    b_import = tk.Button(col_0, text='Import Selection', width=28)
    b_import.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    fl = tk.StringVar()
    file_list = tk.StringVar()
    files_lb = tk.Listbox(col_0, listvariable=fl, selectmode=tk.MULTIPLE, height=29, width=30).grid(row=3, column=0, columnspan=2, rowspan=16, padx=5, pady=5, sticky=(N,S,E,W))

    # # Col 1

    b_select_all = tk.Button(col_1, text='Select all', width=28)
    b_select_all.grid(row=0, column=3, padx=5, pady=5, columnspan=2)

    file_list1 = tk.StringVar()
    files_lb1 = tk.Listbox(col_1, listvariable=file_list, selectmode=tk.MULTIPLE, width=30).grid(row=1, column=3, columnspan=2, rowspan=18, padx=5, pady=5, sticky=(N,S,E,W))

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

    date_col_lbl = tk.Label(col_3, text='Date Col:', anchor=E, width=14)
    date_col_lbl.grid(row=2, column=5, padx=5, pady=5)

    dd_date_col = ttk.Combobox(col_3, value=15, width=14)
    dd_date_col.grid(row=2, column=6, padx=5, pady=5)


    time_col_lbl = tk.Label(col_3, text='Time Col:', anchor=E, width=14)
    time_col_lbl.grid(row=2, column=7, padx=5, pady=5)

    dd_time_col = ttk.Combobox(col_3, value=15, width=14)
    dd_time_col.grid(row=2, column=8, padx=5, pady=5)


    sample_rate_lbl = tk.Label(col_3, text='Sample Rate:', anchor=E, width=14)
    sample_rate_lbl.grid(row=3, column=5, padx=5, pady=5)

    dd_sample_rate = ttk.Combobox(col_3, value=[30,15,10,5,1,0.5,0.25,0.1], width=14)
    dd_sample_rate.grid(row=3, column=6, padx=5, pady=5)


    fill_type_lbl = tk.Label(col_3, text='Fill Method:', anchor=E, width=14)
    fill_type_lbl.grid(row=3, column=7, padx=5, pady=5)

    dd_fill_type = ttk.Combobox(col_3, value=['interpolate', 'backfill', 'forward fill', 'Zero Fill', 'NaN Fill'], width=14)
    dd_fill_type.grid(row=3, column=8, padx=5, pady=5)


    fill_type_lbl = tk.Label(col_3, text='----------Alpha Settings----------------------------------------------------------------------------------', width=72)
    fill_type_lbl.grid(row=4, column=5, padx=5, pady=5, columnspan=5)

    target_col_lbl = tk.Label(col_3, text='Target Col:', anchor=E, width=14)
    target_col_lbl.grid(row=5, column=5, padx=5, pady=5)

    dd_target_col = ttk.Combobox(col_3, value=15, width=14)
    dd_target_col.grid(row=5, column=6, padx=5, pady=5)

    temp_col_lbl = tk.Label(col_3, text='Temp Col:', anchor=E, width=14)
    temp_col_lbl.grid(row=5, column=7, padx=5, pady=5)

    dd_temp_col = ttk.Combobox(col_3, value=15, width=14)
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

show_widgets()

window.mainloop()

