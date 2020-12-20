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
import xlsxwriter
import matplotlib as mpl
import dateutil.parser as parser
from matplotlib.legend import Legend
from numpy.lib.function_base import average
from matplotlib.widgets import MultiCursor

os.chdir(os.getcwd()) # change the directory to the current working dir


regex_time = '(\d\d[:|.]\d\d[:|.]\d\d[:|.|+]\d\d\d|\d[:|.]\d\d[:|.]\d\d[:|.|+]\d\d\d|\d[:|.]\d\d[:|.]\d\d[:|.|+]\d\d|\d\d[:|.]\d\d[:|.]\d\d|\d[:|.]\d\d[:|.]\d\d)'
regex_date = '(\d\d\d\d[-|.|/]\d\d[-|.|/]\d\d|\d\d[-|.|/]\d\d[-|.|/]\d\d|\d[-|.|/]\d\d[-|.|/]\d\d|\d\d[-|.|/]\d\d[-|.|/]\d\d|\d\d[-|.|/]\d\d[-|.|/]\d\d\d\d|\d[-|.|/]\d\d[-|.|/]\d\d\d\d|\d\d\d\d[-|.|/]\d\d[-|.|/]\d|\d\d[-|.|/]\d\d[-|.|/]\d)'


window = tk.Tk()
window.title('CatSV - CSV Tool') #window title
window.geometry('1100x768') # window size Should be 383x378. If the users has custom scaling enabled, this will need to be change. if the user is using custom scaling in win10, ya window is going to be FU
# window.resizable(0, 0) # do not allow resizing

#declaring a bunch of vars

class cat:

    class Alpha:

        def __init__(self, dataframe, time_header, target_header, temp_header, lower = -1, upper = 2, offset = 0, divisions = 20, max_cycles = 10, stdev_ceiling = 0.0001, sample_rate = '30s', \
                    timestamp_format='%H:%M:%S', show_graph=False, report=False, save_report_as='alpha_report.xlsx'): #Initialize all of the settings when the class is called
            self.df = dataframe
            self._stdev_df = 0

            self.data_file  = 0
            self.alpha_lower  = lower
            self.alpha_upper  = upper
            self.alpha_offset  = offset
            self.alpha_divisions  = divisions
            self.sample_rate  = sample_rate
            self.max_cycles = max_cycles
            self.stdev_ceiling = stdev_ceiling
            
            self.time_header  = time_header
            self.target_header = target_header
            self.temp_header = temp_header
            self.timestamp_format  = timestamp_format

            self.corrected_target = []
            self.stdev_plot_info = []
            self.alpha_num_set = []

            self.ref_temp = 0
            self.final_alpha_number = 0

            self.find_alpha() # this runs all of the methods needed to generate the new alpha number. The final number is placed into final_alpha_number var.

            if show_graph:
                self.graph_data()

            if report:
                self.export_report(save_report_as)

            # self.alpha_num_set.clear()


        def upper_header(self):  
            # Capitalize all of the headers and drop any duplicate entrys in the time column
            df = self.df
            df_headers = list(df)
            for i in range(len(df_headers)):
                df_headers[i] = df_headers[i].upper()
            df = df[0:]
            df.columns = df_headers
            df = df.drop_duplicates(subset=['TIME'])
            # print('-->', df)
            self.df = df

            
        def col_by_num(self, col):
            # Return a column by index pos
            df = self.df
            try:
                df_headers = list(df)
                return df_headers[col]
            except IndexError:
                return 0


        def next_alphas(self): 
            # Generate the next set of alpha numbers from the upper and lower bounds and round them to 15 places
            count = 1
            step_size = 0
            next_alpha_numbers = []
            diff = self.alpha_upper-self.alpha_lower
            step_size = diff / self.alpha_divisions
            last = self.alpha_upper
            next_alpha_numbers.clear()
            while count <= self.alpha_divisions:
                next = round(last-step_size, 6)
                next_alpha_numbers.append(next)
                last = next
                count += 1
            next_alpha_numbers.append(self.alpha_upper)
            next_alpha_numbers.sort()
            for i in range(len(next_alpha_numbers)):
                next_alpha_numbers[i] = round(next_alpha_numbers[i], 15)
            self.alpha_num_set.clear()
            self.alpha_num_set = next_alpha_numbers
        # self.alpha_lower = min(self.alpha_num_set)
            # self.alpha_upper = max(self.alpha_num_set)

        
        def fix_timestamp(self):
            formated_timestamps = 0
            # print(self.df[self.time_header][:5])
            formated_timestamps = pd.to_datetime(self.df[self.time_header], format=self.timestamp_format)
            self.df[self.time_header] = formated_timestamps
            # print('~125-->', self.df)


        def sampling(self):  
            # resample the class df\
            # this is buggy. Need to figure out how to resample to a freq that does not jive with the current timestamps.
            # If multiple files are selected and the lowest unit of those two timestamps is not chosen the resampling will fail.
            # Idealy I would like to sample everything to 1 second and then set the frequency, but asFreq does not seem to work??
            df = self.df
            df = df.set_index(self.time_header).resample('1s').interpolate()
            # df = df.resample(self.sample_rate)
            df = df.asfreq(self.sample_rate).reset_index()
            # print(df)
            self.df = df


        def apply_alpha(self):
            count_a = 0
            count_r = 0
            corrected_target = []
            alpha_lst = self.alpha_num_set
            target = self.df[self.target_header]
            temp_lst = self.df[self.temp_header]
            self.ref_temp = average(temp_lst).round(5)
            # print('target: ', target)
            while count_a <= len(alpha_lst)-1:
                corrected_target.append([])
                while count_r <= len(target)-1:
                    # print('134:',count_a,' target=', target[count_r],', alpha_lst=', alpha_lst[count_a],', temp=', temp_lst[count_r],', ref_temp=', ref_temp)
                    correction = (target[count_r] / ((alpha_lst[count_a]*(temp_lst[count_r]-self.ref_temp))+1))+self.alpha_offset # apply alpha number
                    corrected_target[count_a].append(correction)
                    count_r += 1 # inc for loop
                self.df[alpha_lst[count_a]] = corrected_target[count_a]
                # print('168: ', count_a)
                count_r = 0 # reset count for while loop
                count_a += 1
            self.corrected_target = corrected_target


        def st_dev(self):
            alpha_set_lst = self.alpha_num_set
            target = self.corrected_target
            _stdev_lst = []
            _stdev_df = []
            # print('-->', target)

            for i in range(len(target)):
                # print('148STDEV: ', np.std(target[i]), 'A set: ', alpha_set_lst[i])
                _stdev_lst.append([np.std(target[i]),alpha_set_lst[i]]) # load the stdev and associated alpha number
                self.stdev_plot_info.append([np.std(target[i]),alpha_set_lst[i]]) # load the stdev and associated alpha number
                target[i].insert(0, 'Corrected')

            _stdev_df = pd.DataFrame(_stdev_lst, columns=['STDEV', 'ALPHA'])
            # _stdev_df = _stdev_df.set_index('STDEV')
            _stdev_df = _stdev_df.sort_values(by=['STDEV'], ascending=True)
            _stdev_df = _stdev_df.nsmallest(2, 'STDEV')
            stdev_col_df = _stdev_df['STDEV'].tolist()
            alpha_col_df = _stdev_df['ALPHA'].tolist()
            # _stdev_df = _stdev_df.drop('STDEV', axis=1)
            # print('-->', _stdev_df['ALPHA'])
            _stdev_df = _stdev_df.iloc[0:0]
            _stdev_df = pd.DataFrame(self.stdev_plot_info, columns=['STDEV', 'ALPHA']).set_index('STDEV')
            _stdev_df = _stdev_df.sort_index().reset_index()
            self.stdev_df = _stdev_df
            alpha_list = _stdev_df['ALPHA'].tolist()
            zero_count = 0 
            while True:
                if alpha_list[zero_count] == 0:
                    zero_count += 1
                else:
                    self.final_alpha_number = alpha_list[zero_count]
                    break


            self.alpha_lower = float(alpha_col_df[1])
            self.alpha_upper = float(alpha_col_df[0])

            return stdev_col_df[0]


        def find_alpha(self):
            _max_cycles = 0
            _last_stdev = 0

            self.upper_header()
            self.fix_timestamp()
            self.sampling()
            self.next_alphas()
                    
            while True:
                self.apply_alpha()
                _w_stdev = self.st_dev()
                self.next_alphas()

                _max_cycles += 1
                if _w_stdev < self.stdev_ceiling:
                    if _last_stdev == _w_stdev:
                        print('!!!!!!!-- {} == {} --!!!!!!!'.format(_w_stdev, _w_stdev))
                        break
                
                print('Cycles: {} / {} | Last STDEV vs Current: {} / {}'.format(_max_cycles, self.max_cycles, _last_stdev, _w_stdev))
                if _max_cycles >= self.max_cycles:
                    break
                _last_stdev = _w_stdev

            self.df.T.drop_duplicates().T


        def graph_data(self, dpi=100, figsize=(11,7)):

            fig, axes = plt.subplots(2,2, dpi=dpi, figsize=figsize)

            # Top left
            axes[0][0].set_title('Sensor & Sensor with α')
            # Top Right
            axes[0][1].set_title('Temperature')
            # Bottom Left
            # axes[1][0].set_title(str('Final ') + str(self.alpha_divisions) + str(' calculations | α = ') + str(self.final_alpha_number))
            axes[1][0].set_title('Final {} calculations | α = {}'.format(self.alpha_divisions, self.final_alpha_number))

            # Bottom Right
            axes[1][1].set_title('{} calculations'.format(len(self.stdev_df)))

            # Raw sensor data and sensor data with alpha applied (Top left)
            self.df.plot(kind='line', use_index=True, x=self.time_header, y=[self.target_header, self.final_alpha_number], ax=axes[0][0])

            # Raw temperature data (Top right)
            self.df.plot(kind='line',use_index=True, x=self.time_header, y=self.temp_header, ax=axes[0][1])

            guide_line = MultiCursor(fig.canvas, (axes[0][0], axes[0][1]), lw=1, horizOn=False, vertOn=True)

            # Final alpha calculations with final alpha number highlighted red (Bottom Left)
            self.stdev_df[:self.alpha_divisions+self.alpha_divisions+20].plot(kind='scatter',x='ALPHA',y='STDEV', ax=axes[1][0])
            self.stdev_df[:1].plot(kind='scatter',x='ALPHA',y='STDEV', color='red', ax=axes[1][0])

            # All alpha calculations with final alpha number highlighted red (Bottom Right)
            self.stdev_df.plot(kind='scatter',x='ALPHA',y='STDEV', ax=axes[1][1])
            self.stdev_df[:1].plot(kind='scatter',x='ALPHA',y='STDEV', color='red', ax=axes[1][1])

            plt.subplots_adjust(hspace=0.5)
            plt.show()


        def export_report(self, save_as='alpha_report.xlsx'):
            
            header_on_row = 6

            workbook = xlsxwriter.Workbook(save_as)
            worksheet = workbook.add_worksheet()
            # chartsheet = workbook.add_chartsheet()

            # excel cell data formats
            bold = workbook.add_format({'bold': 1})
            datetime = workbook.add_format({'num_format': 'yyy-mm-dd hh:mm:ss'})
            number_dig = workbook.add_format({'num_format': '0.00000'})
            alpha_edit = workbook.add_format({'num_format': '0.000000', })
            alpha_no_edit = workbook.add_format({'num_format': '0.000000', })
            alpha_edit.set_bg_color('#B4DFB3')
            offsets_edit = workbook.add_format({'num_format': '0.000', })
            offsets_no_edit = workbook.add_format({'num_format': '0.000', })
            offsets_edit.set_bg_color('#B4DFB3')

            # Add the worksheet data that the charts will refer to.
            headings = [self.time_header, self.temp_header, self.target_header, 'Alpha Number', 'Projected', 'Ref Temp', 'Neg Offset', 'Pos Offset']
            # put all of the data into a list
            data = [self.df[self.time_header].tolist(), # Time A
                    self.df[self.temp_header].tolist(), # Temp B
                    self.df[self.target_header].tolist(), # Target C
                    [], # Alpha D
                    [], # Projected E
                    [], # Ref Temp F
                    [], # Neg Offset G
                    [], # Pos Offset H
            ]

            total_rows = len(self.df)+header_on_row
            count = header_on_row+1 
            while count <= total_rows:
                data[3].append(self.final_alpha_number)
                data[5].append(self.ref_temp)
                worksheet.write_formula('D{}'.format(count), '=D{}'.format(count-1), alpha_no_edit) # Alpha number 
                worksheet.write_formula('E{}'.format(count), '=(C{}/((D{}*(B{}-F{}))+1))-G{}+H{}'.format(count,count,count,count,count,count), number_dig) # Projected
                worksheet.write_formula('G{}'.format(count), '=G{}'.format(count-1), offsets_no_edit) # Neg Offset
                worksheet.write_formula('H{}'.format(count), '=H{}'.format(count-1), offsets_no_edit) # Pos Offset
                count += 1

            print('test {} test {}'.format(total_rows,total_rows))
            # correction = (target[count_r] / ((alpha_lst[count_a]*(temp_lst[count_r]-ref_temp))+1))+self.alpha_offset # apply alpha number

            ######################Head##############################
            worksheet.write('A1', 'Average', number_dig)
            worksheet.write_formula('H1', '=AVERAGE(E{}:E{})'.format(header_on_row+1, total_rows), alpha_no_edit)
            worksheet.write('A2', 'STDEV', number_dig)
            worksheet.write_formula('H2', '=STDEV(E{}:E{})'.format(header_on_row+1, total_rows), alpha_no_edit)
            worksheet.write('A3', 'Max', number_dig)
            worksheet.write_formula('H3', '=MAX(E{}:E{})'.format(header_on_row+1, total_rows), alpha_no_edit)
            worksheet.write('A4', 'Min', number_dig)
            worksheet.write_formula('H4', '=MIN(E{}:E{})'.format(header_on_row+1, total_rows), alpha_no_edit)
            # worksheet.write('A5', 'Span', number_dig)
            # worksheet.write_formula('H5', '=SPAN(E{}:E{})'.format(header_on_row+1, total_rows), number_dig)

            ######################BODY###############################
            # add the header row
            worksheet.write_row('A{}'.format(header_on_row), headings, bold)
            # Timestamp
            worksheet.write_column('A{}'.format(header_on_row+1), data[0], datetime)
            # Temp
            worksheet.write_column('B{}'.format(header_on_row+1), data[1], number_dig)
            # Target
            worksheet.write_column('C{}'.format(header_on_row+1), data[2], number_dig)
            # Alpha Number
            worksheet.write('D{}'.format(header_on_row+1), self.final_alpha_number, alpha_edit)
            # Projected
            # formula is done in the while loop above
            # Ref Temp
            worksheet.write_column('F{}'.format(header_on_row+1), data[5], number_dig)
            # Ref Temp ---- Need to finish this. the formula needs  to be added to each cell to copy the one above.
            worksheet.write('G{}'.format(header_on_row+1), 0, offsets_edit)
            # Ref Temp
            worksheet.write('H{}'.format(header_on_row+1), 0, offsets_edit)

            # set the column widths
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 20)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 20)
            worksheet.set_column('F:F', 20)
            worksheet.set_column('G:G', 10)
            worksheet.set_column('H:H', 10)

            # Create a new chart object. In this case an embedded chart.
            chart = workbook.add_chart({'type': 'scatter'})

            # add data to the chart
            chart.add_series({
                'name':   '=Sheet1!$C${}'.format(header_on_row),
                'categories': '=Sheet1!$A${}:$A${}'.format(header_on_row+1, total_rows),
                'values': '=Sheet1!$C${}:$C${}'.format(header_on_row+1, total_rows),
                'marker': {'type': 'circle', 'size': 3},
            })

            chart.add_series({
                'name':   '=Sheet1!$E${}'.format(header_on_row),
                'categories': '=Sheet1!$A${}:$A${}'.format(header_on_row+1, total_rows),
                'values': '=Sheet1!$E${}:$E${}'.format(header_on_row+1, total_rows),
                'marker': {'type': 'circle', 'size': 3},
            })
            # set temperature to the second y axes
            chart.add_series({
                'name':   '=Sheet1!$B${}'.format(header_on_row),
                'categories': '=Sheet1!$A${}:$A${}'.format(header_on_row+1, total_rows),
                'values': '=Sheet1!$B${}:$B${}'.format(header_on_row+1, total_rows),
                'marker': {'type': 'circle', 'size': 3},
                'y2_axis': 1, 
            })

            # Add a chart title and some axis labels.
            chart.set_title({'name': 'Alpha Number: {}'.format(self.final_alpha_number)})
            chart.set_legend({'position': 'bottom'})

            # set the x axis. set as a text_axis because I can not get the acual date to work.
            chart.set_x_axis({
                'name': self.time_header,
                'text_axis': True,
                'min': data[0][1],
                'max': data[0][-1],
                'num_font':  {'rotation': -20}
            })
            chart.set_y_axis({'name': self.target_header, 'major_gridlines': {'visible': 0}})
            chart.set_y2_axis({'name': self.temp_header})

            worksheet.freeze_panes(header_on_row, 0)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('I{}'.format(header_on_row+1), chart, {'x_scale': 1.5, 'y_scale': 2, 'x_offset': 30, 'y_offset': 30})

            workbook.close()
            os.startfile(save_as)


    def __init__(self):
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
    def sd(self, prompt=False): #select directory, call fil dialog box
        if prompt:
            self.selected_dir = os.chdir(filedialog.askdirectory(title = "Select the folder that contains your CSV trend files"))
        self.selected_dir = os.chdir('C://Users//accou//Desktop//CatSV//Concat test//test_data')
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

    def time_format(self, df_time_col):
        old_time_col = df_time_col.tolist() # get the timestamp from the df so we can build datetime
        old_time_col = pd.Series(old_time_col)
        new_time_col = old_time_col.str.extract(pat = regex_time)
        return new_time_col

    def date_format(self, df_date_col):
        old_date_col = df_date_col.tolist() # get the timestamp from the df so we can build datetime
        old_date_col = pd.Series(old_date_col)
        new_date_col = old_date_col.str.extract(pat = regex_date)
        return new_date_col

    def get_data(self, selected_files): # get all of the data, concatinate and sort
        try:
            rows_to_skip = float(w_spn_header_row.get()) # get the spinbox value and sub 1 since we need to skip 1 less row than the header
            rows_to_skip = int(rows_to_skip.__round__())
            w_lb_columns.delete(0, 'end') # clear the listbox
        except ValueError:
            print('some wierd characters are hanging out in the header row spinbox')
            messagebox.showwarning(title='Select a real row', message='Some wierd characters are hanging out in the header row spinbox! The row number must be and integer.')

        # try:
        df_list = [] # the list all of the dataframes will be put into
        reject_list = [] # a list of the files, if any, that have been rejected because they do not have date or time info. Used for the message box
        for row_index in selected_files:
            print(f'Selected file inedexs: {row_index}')

        # this whole loop is to find the date and time columns and format them correctly. 
        # if you dont do this identical time points will not combine because the timestamp 
        # is not formated in the same way.
        for row_index in selected_files:
            # for each item selected in the files listbox
            file_name = w_lb_files.get(row_index) # get the value from the row index
            print(file_name) 
            file_contents_df = pd.read_csv(file_name, skiprows=(rows_to_skip)) # read the current file
            file_contents_df_header = list(file_contents_df)
            file_contents_df_header = self.lst_to_upper(file_contents_df_header)
            file_contents_df = file_contents_df[0:] # remove the header for replacement
            file_contents_df.columns = file_contents_df_header # load in the new header that is all caps. for searching reasons down the line
            dt_col_search = file_contents_df.tail(1) # get the last row 
            dt_col_search = dt_col_search.values.tolist() # convert the  last df row into a list
            dt_col_search = pd.Series(dt_col_search[0]) # convert the list into a pd series so we can do a regex search of all the items
            time_col_result = dt_col_search.str.contains(regex_time) # use regnex to identify if the column matches a known time format
            date_col_result = dt_col_search.str.contains(regex_date) # use regnex to identify if the column matches a known date format

            # print(f'Date Search results: \n{date_col_result}')
            # print(f'Time Search results: \n{time_col_result}')

            time_index_count = 0
            time_col = 0
            for t in time_col_result: # get the index of any found timestamps
                if t == True:
                    time_col = file_contents_df_header[time_index_count]
                time_index_count += 1

            date_index_count = 0
            date_col = 0
            for d in date_col_result: 
                if d == True:
                    date_col = file_contents_df_header[date_index_count]
                    # print(f'date_index: {date_index_count}')
                date_index_count += 1

            if (time_col) and (date_col): # if the file contains both date and time info then load in new formated time and dates, create a new datetime index, and append the file into the df_list
                new_time_col = self.time_format(file_contents_df[time_col]) # reformat time
                new_date_col = self.date_format(file_contents_df[date_col]) # reformat date
                # print(f'~183 - New Date Col: \n {new_date_col}')

                file_contents_df[time_col] = new_time_col # load the modified time into the df
                file_contents_df[date_col] = new_date_col # load the modified date into the df
                new_datetime_index = file_contents_df[date_col] + ' ' + file_contents_df[time_col] # make the new datetime index, this gives and indexable item for pd to use. This is done
                                                                                                   # so the dataframes will concatinate properly

                file_contents_df['datetime_index'] = pd.to_datetime(new_datetime_index, infer_datetime_format=True) # format the column as datetime so that it is indexable
                file_contents_df = file_contents_df.set_index('datetime_index') # set the datetime_index as the index
                # print(f'{file_name}: \n {file_contents_df} \n -------------------------------------------------------------------------')
                df_list.append(file_contents_df) # add the df to out df_list
            else:
                reject_list.append(file_name) # if time and date are not found, then add the filename to this list.

        if reject_list:
            messagebox.showwarning(title='Missing timestamp info', message=f'The following files were not loaded because they are missing timestamp information: {reject_list}')

        if df_list: # got df?
        #     # try:
            df = pd.concat(df_list, sort=False) # combine all csv files. This combine any like columns
            df = df.drop_duplicates(subset=time_col, keep='first') # drop any duplicate times. if this is not done, there can be problems with resampling
            self.header = list(df) # get the header of the concatinated dataframe

            # print('Concat df:')
            # print(df)
            # df.to_csv('output.csv')

            w_lb_columns_var.set(self.header) # update the columns listbox. Done with the sorted DF so all self.header entrys are unique
            w_dd_date_col['value'] = self.header # fill the drop downs with all of the column names.
            w_dd_time_col['value'] = self.header
            w_dd_target_col['value'] = self.header
            w_dd_temp_col['value'] = self.header

            # If the date or time search came back with results, change the drop downs to those columns so the user does not have to
            if date_col:
                w_dd_date_col.set(date_col)
            if time_col:
                w_dd_time_col.set(time_col)

            self.concat_df = df
            # except:
                # print('Something went wrong in get_data method. The program was unable to concatinate the dataframes')
                # messagebox.showerror(title='Failed to concatinate files', message='Something went wrong in get_data method. The program was unable to concatinate the files. This is usualy caused by combining files that do not share the same data structure.')

        # else:
        #     print('Something happened while trying to read the selected file. Make sure eveything \
        #         selected starts on the same row and have the same timestamp headers')
        #     messagebox.showerror(title='Nothing in DF', message='Something went wrong in get_data method. While the program was able to read the files, nothing seems to be in the dataframe.')

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
        df = self.resample_data(df1, w_dd_sample_rate.get())
        # df = df.reset_index(drop=True)
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

    def b_graph_data(self):
        print('b_graph')
        print(self.concat_df)
        self.graph_data(self.concat_df)

    def get_alpha(self):
        #(self, dataframe, time_header, target_header, temp_header, lower = -1, upper = 2, offset = 0, divisions = 20, max_cycles = 10, stdev_ceiling = 0.0001, sample_rate = '30s', \
                    # timestamp_format='%H:%M:%S', show_graph=False, report=False, save_report_as='alpha_report.xlsx'
        m = self.Alpha(dataframe=self.concat_df,time_header=w_dd_time_col.get(),target_header=w_dd_target_col.get(),temp_header=w_dd_temp_col.get(), divisions=int(w_txt_div.get('1.0', 'end-1c')),report=True, show_graph=True) # load class
#, sample_rate=w_dd_sample_rate.get()
# lower=w_txt_lower_b.get('1.0', 'end-1c'), 
# upper=w_txt_upper_b.get('1.0', 'end-1c'), offset=w_txt_offset.get('1.0', 'end-1c'), divisions=w_txt_div.get('1.0', 'end-1c'), max_cycles=w_txt_max_cycles.get('1.0', 'end-1c'), \
# stdev_ceiling=w_txt_STDEV.get('1.0', 'end-1c')

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

# Select all files in listoxgra
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
w_b_graph = Button(w_col_2, text='Graph Selected', width=button_width, command=m.b_graph_data)
w_b_graph.grid(row=0, column=6, padx=5, pady=5)

# Gen Alpha Button
w_b_alpha = Button(w_col_2, text='Find Alpha', width=button_width, command=m.get_alpha)
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