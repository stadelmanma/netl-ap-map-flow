########################################################################
#
# This program will act as a driver allowing bulk runs of APM-FLOW
# Using various parameters, it updates and outputs a verison of the 
# FRACTURE_INITIALIZATION.INP file instead of directly interacting with
# the FORTRAN program
#
# Written by: Matthew Stadelman
# Created: 2015/09/29
# Last Modified: 2015/10/01
#
########################################################################
#
# Module Imports
#
import os
import re
#
########################################################################
#
# Class declarations 
#
# defining lineInput class and methods
class lineInput:
    #
    # defines the object, and initializes keyword and value
    def __init__(self,line):
        self.line = line
        line_arr = list(filter(None,re.split('\s',line)))
        self.line_arr = line_arr
        try:
            m = re.match(r'[; ]*([a-zA-z,-]*)',line_arr[0])
            self.keyword = m.group(1)
        except IndexError:
            print("Error - Bad line input provided - line: '",line,"'")
            self.keyword = ""
        #
        # if line has a colon the field after it will be used as the value
        # otherwise the whole line is considered the value
        if (re.search(r':',line)):
            for ifld in range(len(line_arr)):
              if (re.search(r':',line_arr[ifld])):
                  try:
                      self.value = line_arr[ifld+1]
                      self.value_index = ifld+1
                  except IndexError:
                      self.value = "NONE"
                      self.value_index = ifld+1
        else:
            self.value = line
            self.value_index = -1
    #
    # updates the line and line_arr with new value
    def update_value(self,new_value):
        line_arr = self.line_arr
        index = self.value_index
        if (index > 0):
            line_arr[index] = new_value
        else:
            line_arr = list(filter(None,re.split('\s',new_value)))        
        self.line = ' '.join(line_arr)
        self.line_arr = line_arr
        self.value = new_value
#
########################################################################
#
# Function definitions
#
# function to open and parse contents of input file 
def parse_input_file(filename,content_list,content_dict):
    input_file = open(filename,'r')
    content = input_file.read()
    input_file.close()
    #
    # parsing contents into a dictionary
    content_arr = content.split('\n')
    for l in range(len(content_arr)):
        line = content_arr[l]
        line_arr = list(filter(None,re.split('\s',line)))
        #
        # skipping empty arrays
        if (len(line_arr) == 0):
          continue
        #
        # cleaning junk off line_arr[0] for use as a key
        m = re.match(r'[; ]*([a-zA-z,-]*)',line_arr[0])
        key = m.group(1)
        content_dict[key] = lineInput(line) #storing object
        content_list.append(key) #storing order of inputs
#
# function builds the output file from the lineInput objects
def build_input_file(content_list,content_dict):
    content = ""
    #
    # builidng content from lineInput class line attribute
    for key in content_list:
        content += content_dict[key].line+"\n"
    #
    # outputting the new file
    return content
#
# function to create the names of the 5 output files based on parameters
# updates line input objects accordingly
# will also make directories if they do not exist
def construct_file_names(content_dict,curr_params,return_inp_bak):
    #
    # base names of files, stuff between $'s is an input keyword and will be replaced by the current value in use
    curr_params["MAP_TYPE"] = "AVG"
    base_names = {}
    base_names['APER-MAP']      = ".\SHEARING_FRAC_TEST7-8\$APER-MAP$_ApertureMapCropped-10avg.txt"
    base_names['SUMMARY-PATH']  = ".\SHEARING_FRAC_TEST7-8\$MAP_TYPE$_MAPS\DP_COMPARE\$APER-MAP$\$APER-MAP$-$MAP_TYPE$-MLOG-$OUTFLOW-SIDE$-$OUTLET-PRESS$PSI-RF$ROUGHNESS$.TXT"
    base_names['APER-FILE']     = ".\SHEARING_FRAC_TEST7-8\$MAP_TYPE$_MAPS\DP_COMPARE\$APER-MAP$\$APER-MAP$-$MAP_TYPE$-APER-$OUTFLOW-SIDE$-$OUTLET-PRESS$PSI-RF$ROUGHNESS$.CSV"
    base_names['STAT-FILE']     = ".\SHEARING_FRAC_TEST7-8\$MAP_TYPE$_MAPS\DP_COMPARE\$APER-MAP$\$APER-MAP$-$MAP_TYPE$-STAT-$OUTFLOW-SIDE$-$OUTLET-PRESS$PSI-RF$ROUGHNESS$.CSV"
    base_names['FLOW-FILE']     = ".\SHEARING_FRAC_TEST7-8\$MAP_TYPE$_MAPS\DP_COMPARE\$APER-MAP$\$APER-MAP$-$MAP_TYPE$-FLOW-$OUTFLOW-SIDE$-$OUTLET-PRESS$PSI-RF$ROUGHNESS$.CSV"
    base_names['PRESS-FILE']    = ".\SHEARING_FRAC_TEST7-8\$MAP_TYPE$_MAPS\DP_COMPARE\$APER-MAP$\$APER-MAP$-$MAP_TYPE$-PRES-$OUTFLOW-SIDE$-$OUTLET-PRESS$PSI-RF$ROUGHNESS$.CSV"
    base_names['VTK-FILE']      = ".\SHEARING_FRAC_TEST7-8\$MAP_TYPE$_MAPS\DP_COMPARE\$APER-MAP$\$APER-MAP$-$MAP_TYPE$-VTKL-$OUTFLOW-SIDE$-$OUTLET-PRESS$PSI-RF$ROUGHNESS$.vtk"
    base_names['input_backup']  = ".\SHEARING_FRAC_TEST7-8\$MAP_TYPE$_MAPS\DP_COMPARE\INP_FILES\FRACTURE_INITIAIZATION-$APER-MAP$-$MAP_TYPE$-$OUTFLOW-SIDE$-$OUTLET-PRESS$PSI-RF$ROUGHNESS$.INP"
    for param in curr_params.keys():
        pattern = re.compile('\$'+param+'\$',flags=re.I)
        for outfile in base_names.keys():
            base_names[outfile] = pattern.sub(curr_params[param],base_names[outfile])
    #
    # checking existance of directories
    # and updating the lineInput objects
    for outfile in base_names.keys():
        try: 
            content_dict[outfile].update_value(base_names[outfile])
        except KeyError:
            if (outfile == 'input_backup'):
                pass
            else:
                print('Error - outfile: '+outfile+' not defined in initialization file')
                print('')
                print('')
                raise KeyError(outfile)
        path = base_names[outfile][::-1] #reverse string to get split to split last instance of \
        path = path.split('\\',1)[-1]
        path = path[::-1]
        if (not os.path.isdir(path)):
            syscmd = 'mkdir '+path
            os.system(syscmd)  
    #
    # returning the input file backup name if desired 
    if (return_inp_bak):
        return(base_names['input_backup'])
#
########################################################################
#
# Execution code
#
# opening and reading file
filename = "FRACTURE_INITIALIZATION.INP"  
content_dict = {}
content_list = []
parse_input_file(filename,content_list,content_dict) 
#
# getting name of executable to use
try:
    exe_file = content_dict['EXE-FILE'].value
except KeyError:
    print('Error - No executable file specified.')
    print('Add the line EXE-FILE: (path to or local executable filename) to the input file.')
    os.sys.exit()
#
# defining a dictionary to house the arrays of values to loop through
# and a list to set the order of execution
run_parameters_list = ['ROUGHNESS','APER-MAP','OUTLET-PRESS','OUTFLOW-SIDE']
#
run_parameters_dict = {}
run_parameters_dict['ROUGHNESS'] = ['0.00']
run_parameters_dict['OUTLET-PRESS'] = ['999.70','999.63','999.49','999.22','998.44','997.53','996.82']
run_parameters_dict['OUTFLOW-SIDE'] = ['TOP']
run_parameters_dict['APER-MAP'] = ['IS-8_4']
#
# initializing index counters to 0
run_parameters_index = {}
for key in run_parameters_dict.keys():
    run_parameters_index[key] = 0
#
#
# processing paramters
run = True
input_backup = True
bot_key = run_parameters_list[0]
top_key = run_parameters_list[-1]
while (run):
    if (run_parameters_index[bot_key] == len(run_parameters_dict[bot_key])):
        #
        # incrementing or resetting indices as required
        for i in range(len(run_parameters_list)-1): #prevents it from resetting top level key
            key = run_parameters_list[i]
            next_key = run_parameters_list[i+1]
            if (run_parameters_index[key] == len(run_parameters_dict[key])):
                run_parameters_index[key] = 0 #reset if index == array length
                run_parameters_index[next_key] += 1 #increments next key and exits loop
                print("-")
            else:
                break
        #
        # final exit if top level param index equals length
        if (run_parameters_index[top_key] == len(run_parameters_dict[top_key])):
            break
    #
    # updating the required objects to reflect input changes
    string = ""
    curr_params = {}
    for key in run_parameters_list:
        curr_params[key] = run_parameters_dict[key][run_parameters_index[key]]
        content_dict[key].update_value(run_parameters_dict[key][run_parameters_index[key]])
        string += " "+key+": "+run_parameters_dict[key][run_parameters_index[key]]
    print(string)
    #
    # creating updated input file and a backup for it if desired
    if (input_backup):
        inp_bak_name = construct_file_names(content_dict,curr_params,input_backup)
        content = build_input_file(content_list,content_dict)
        #
        # updates permissions of exact matching input files to prevent error with previous 550 permissions
        if (os.path.exists(inp_bak_name)):
            syscmd = 'chmod 777 '+inp_bak_name
            os.system(syscmd)
        #
        input_file = open(inp_bak_name,'w')
        input_file.write(content)
        input_file.close()
        syscmd = 'chmod 550 '+inp_bak_name # sets file to readonly by all users
        os.system(syscmd)
    else:
        construct_file_names(content_dict,curr_params,input_backup)
        content = build_input_file(content_list,content_dict)
    #
    input_file = open(filename,'w')
    input_file.write(content)
    input_file.close()
    #
    # executing the provided executable
    os.system(exe_file)
    #
    # updating the index for the bottom level key
    run_parameters_index[bot_key] += 1 

