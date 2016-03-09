"""
This stores the basic class and function dependencies of the
ApertureMapModelTools module.
#
Written By: Matthew Stadelman
Date Written: 2016/02/26
Last Modifed: 2016/02/26
#
"""
########################################################################
#  Required Modules: re, os
########################################################################
#
import os
import re
#
########################################################################
#  Basic classes 
########################################################################
#
# this class holds the characteristics of a flow field
class DataField:
    r"""
    Base class to store raw data from an infile and the output data 
    generated by different routines
    """
    def __init__(self,infile,delim='auto'):
        self.infile  = infile
        self.outfile = ""
        self.nx = 0
        self.nz = 0
        self.data_map = []
        self.output_data = {}
        self.parse_data_file(delim)
    #
    def copy_data(self,obj):
        r"""
        Copies data properites of the field onto another object created 
        """
        obj.infile = self.infile
        obj.nx = self.nx
        obj.nz = self.nz
        obj.data_map = list(self.data_map)
    #
    def parse_data_file(self,delim='auto'):
        r"""
        Reads the field's infile data and then populates the data_map array 
        and sets the fields nx and nz properties.
        """
        #
        if (delim == 'auto'):
            infile = open(self.infile,'r')
            line = infile.readline();
            infile.close()
            #
            m = re.search(r'[0-9.]+(\D+)[0-9.]+',line)
            delim = m.group(1).strip()
        #
        with open(self.infile,'r') as infile:
            content = infile.read()
            content_arr = list(filter(None,content.split('\n')))
        #
        # processing each line of file a leading '#' is treated as a comment line
        nx = 0
        nz = 0
        for l in range(len(content_arr)):
            if (re.match('#',content_arr[l])): 
                continue
            #
            num_arr = list(filter(None,re.split(delim,content_arr[l])))
            num_arr = [float(num) for num in num_arr]
            if (len(num_arr) == 0):
                continue
            #
            if (nx == 0):
                nx = len(num_arr)
            elif (nx != len(num_arr)):
                print("warning: number of columns changed from",nx," to ",len(num_arr)," on data row: ",l+1)
            #
            self.data_map += num_arr
            nz += 1
        #
        self.nx = nx
        self.nz = nz
#
# this class facilitates argument processing
class ArgProcessor:
    r"""
    Generalizes the processing of an input argument
    """
    def __init__(self,field,
                      map_func = lambda x : x,
                      min_num_vals = 1,
                      out_type = "single" ,
                      expected = "str",
                      err_desc_str="to have a value"):
        #
        self.field = field
        self.map_func = map_func
        self.min_num_vals = min_num_vals
        self.out_type = out_type
        self.expected = expected
        self.err_desc_str = err_desc_str
#
# Returns a useful error message if the user inputs an invalid action
class ActionError(Exception):
    def __init__(self,action):
        super().__init__()
        self.msg  = "Undefined action: '"+action+"' supplied, format is action=arg .\n"
        self.msg += "where arg is one of the following hist, hist_range, profile or pctle."
#
########################################################################
#  Base functions 
########################################################################
#
#
def load_infile_list(infile_list,delim='auto'):
    r"""
    Function to generate a list of DataField objects from a list of input files
    """
    field_list = []
    #
    # loading and parsing each input file
    for infile in infile_list:
        #
        # constructing object
        field = DataField(infile)
        print('Finished reading file: '+field.infile)
        #
        field_list.append(field)
    #
    return(field_list)
#
def calc_percentile(perc,data,sort=True):
    r"""
    Calculates the desired percentile of a dataset.
    """    
    tot_vals = float(len(data))
    num_vals = 0.0
    sorted_data = list(data)
    if (sort):
        sorted_data.sort()
    #
    # stepping through list
    index = 0
    for i in range(len(sorted_data)):
        index = i
        if ((num_vals/tot_vals*100.0) >= perc):
            break
        else:
            num_vals += 1
    #
    #
    return(sorted_data[index])
#
def calc_percentile_num(num,data,last=False,sort=True):
    r"""
    Calculates the percentile of a provided number in the dataset.
    If last is set to true then the last occurance of the number
    is taken instead of the first.
    """
    tot_vals = float(len(data))
    num_vals = 0.0
    sorted_data = list(data)
    if (sort):
        sorted_data.sort()
    #
    # stepping through list
    for i in range(len(sorted_data)):
        if ((last == True) and (data[i] > num)):
            break
        elif ((last == False) and (data[i] >= num)):
            break
        else:
            num_vals += 1
    #
    perc = num_vals/tot_vals
    #
    return(perc)
#
# this function returns either of a row or column of cells as a vector in the x or z direction
def get_data_vect(data_map,nx,nz,direction,start_id=0):
    if (direction.lower() == 'x'):
        # getting row index
        if (start_id >= nz):
            start_id = nz
        elif (start_id <= 0):
            start_id = 1
        vect = data_map[(start_id-1)*nx:(start_id)*nx]
        return(vect)
         
    elif (direction.lower() == 'z'):
        if (start_id >= nx):
            start_id = nx
        elif (start_id <= 0):
            start_id = 1
        #
        vect = []
        start_id = start_id - 1
        for iz in range(nz):
            vect.append(data_map[iz*nx+start_id])
        return(vect)
    else:
        print("error - invalid direction supplied, can only be x or z")
        return None
#
def multi_output_columns(data_fields): #rework this so it doesn't suck so much
    r"""
    Takes the content of several fields of output data and outputs them
    columnwise side by side
    """
    # splitting content of each outfile
    num_lines = 0
    for field in data_fields:
        content_arr = field.outfile_content.split("\n")
        field.outfile_arr = list(content_arr)
        num_lines = len(content_arr) if (len(content_arr) > num_lines) else num_lines
    # processing content
    content_arr = []
    max_len = 0
    for l in range(num_lines):
        line_arr = []
        for field in data_fields:
            try:
                line = field.outfile_arr[l].split(',')
                max_len = len(line) if (len(line) > max_len) else max_len
            except IndexError:
                line = ['']
            line_arr.append(line)
        content_arr.append(line_arr)
    #
    # creating group content
    group_content = ""
    for l in range(len(content_arr)):
        line = list(content_arr[l])
        out_str = ""
        for i in range(len(line)):
            for j in range(max_len):
                if (j < len(line[i])):
                    out_str += line[i][j]+','
                else:
                    out_str += ','
            out_str +=','
        group_content += out_str + "\n"
    return(group_content)
#
########################################################################