########################################################################
#
# Description: This program will read the provided flow file(s) and
#     generate the desired output based on the command line arguments. 
#     Output types are a full histogram, range histogram, log-binned histogram, 
#     percentiles of data or a set of velocity profiles in a given direction. 
#     Flags being applied are prefereed to preceed any other type of argument. 
#     Type of action is required next, followed by its parameters and 
#     then an input file(s) are provided.
#
# Written by: Matthew Stadelman
# Date Written: 2015/10/01
# Last Modfied: 2015/10/22
#
########################################################################
#
# Command Line Input Parameters:
#     Flags:
#           -m:  "Multi-File Output", at the end of the run a group data 
#                  file will be created and output in the current directory
#           -mo: "Multi-File Ouput Only", this flag prevents output of 
#                  sub files. Instead only outputting the combined data
#                  from all files. Can be used in conjuction with 
#                  other two flags that modify output type (-so, -sw)
#           -so: "Screen Only Output", instead of writing file(s) the data
#                  will be output to the screen, in CSV files commas become tabs
#           -sw: "Screen and Write Output", prints data to screen and 
#                  ouptuts CSV file(s) 
#           -ow: "Overwrite", allows program to overwrite an existsing file
#
#     Actions:
#           hist: "Histogram", does a full min -> max val histogram of 
#                  each input file
#           hist_range: "Range Histogram", does a histrogram for the
#                  provided percentile range, i.e. 10th - 90th percentile
#           hist_logscale: "Logrithmic Binned Histogram" full range of data
#                  with special logic to handle negatives and values inbetween -1 and 1
#           profile: "Flowrate Profile", outputs a vector of cells 
#                  in either the X or Z direction straight from the flow file. Location 
#                  is based on percentage, i.e. 10% outputs a line at 10cm of a 100cm long field
#           pctle: "Percentile", outputs one or more percentiles from the
#                  flow field
#
#     Action-Inputs:
#           hist: num_bins=### files=file1,file2,...,fileN
#
#           hist_range: num_bins=### range=##,## files=file1,file2,...,fileN
#
#           hist_logscale: num_bins=### files=file1,file2,...,fileN
#
#           profile: locs=##1,##2,##3,...,##N files=file1,file2,...,fileN
#
#           pctle: perc=##1,##2,##3,...,##N files=file1,file2,...,fileN
# 
#
########################################################################
#
# Sample Inputs
#
# Single file
#     PYTHON PROCESS_DATA_MAP.PY action=hist num_bins=100 file=TEST_FLOW_FILE.CSV
#
# Multiple files
#     PYTHON PROCESS_DATA_MAP.PY action=hist_range num_bins=100 range=10,90 files=TEST_FLOW_FILE1.CSV,TEST_FLOW_FILE2.CSV
#
# Multiple files and group output
#     PYTHON PROCESS_DATA_MAP.PY -m action=profile locs=25,50,75 files=TEST_FLOW_FILE1.CSV,TEST_FLOW_FILE2.CSV
#
# Single file with screen output   
#     PYTHON PROCESS_DATA_MAP.PY -so action=pctle perc=10,5,50,75,100 files=TEST_FLOW_FILE1.CSV
#
# Multiple files and group only output to screen and file
#     PYTHON PROCESS_DATA_MAP.PY -mo -sw action=pctle perc=10,5,50,75,100 files=TEST_FLOW_FILE1.CSV,TEST_FLOW_FILE2.CSV
#
########################################################################
#
# Module Imports
#
import os
import re
import datetime
from AP_MAP_DATA_TOOLS import *
#
########################################################################
#
# Driver functions passing global vars to processing functions
# where field is an instance of the class FlowField
#
# passes arguments to calcHistograms
def hist(field,argDict,groupDataDict,globalMinMax = False):
    # 
    num_bins = int(argDict["num_bins"])
    #
    # getting 1% and 99% percentiles for each flow as the 2nd and N-1 points of histogram
    dataMap = list(field.dataMap) #prevents mutation of orginal map
    dataMap.sort()
    #
    if (globalMinMax):
        minMax = globalMinMax
    else:
        low = calc_percentile(1.00,dataMap)
        high = calc_percentile(99.0,dataMap)
        field.pctle_dict = {1.00:low,99.0:high}
        minMax = [low,high]
    field.histData = calcHistogram(num_bins,dataMap,minMax)
    #
    # passing flow dict to group data
    groupDataDict[field.infile] = list(field.histData)
    return
#
# passes arguments to calcHistogramRange
def hist_range(field,argDict,groupDataDict,globalMinMax = False):
    #
    num_bins = argDict["num_bins"]
    minMax = argDict["range"]
    low_pct = minMax[0]
    high_pct = minMax[1]    
    #
    # getting provided percentiles for each flow as the first and last points of histogram
    dataMap = list(field.dataMap) #prevents mutation of orginal map
    dataMap.sort()
    #
    if (globalMinMax):
        minMax = globalMinMax
    else:
        low = calc_percentile(low_pct,dataMap)
        high = calc_percentile(high_pct,dataMap)
        field.pctle_dict = {minMax[0]:low,minMax[1]:high}
        minMax = [low,high]
      #
    field.histData = calcHistogramRange(num_bins,dataMap,minMax)
    #
    # passing flow dict to group data
    groupDataDict[field.infile] = list(field.histData)
    return
#
# passes arguments to logscale version of hist
def hist_logscale(field,argDict,groupDataDict,globalMinMax = False):
    #
    num_bins = argDict["num_bins"]
    #
    # getting provided percentiles for each flow as the first and last points of histogram
    dataMap = list(field.dataMap) #prevents mutation of orginal map
    dataMap.sort()
    #
    bins = calc_log_bins(num_bins,dataMap)
    field.histData = calcHistogramLog(bins,dataMap)
    #
    # passing flow dict to group data
    groupDataDict[field.infile] = list(field.histData)
    return
#
# passes arguemnts to get_data_vect
def profile(field,argDict,groupDataDict):
    #
    dataMap = list(field.dataMap)
    nx = field.nx
    nz = field.nz
    #
    direction = argDict["dir"]
    locs = list(argDict["locs"])
    locs.sort()
    if (direction.lower() == 'x'):
      start_ids = [(int(l/100.0*nz)+1) for l in locs] #first row is bottom of fracture
    elif (direction.lower() == 'z'):                     
      start_ids = [(int(l/100.0*nx)+1) for l in locs] #first column is left side of fracture
    else:                                                
      print("Error - Invalid direction: '"+direction+"' supplied. Valid values are x or z.")
      os.sys.exit()
    #
    field.profile_dict["dir"] = direction
    field.profile_dict["locs"] = list(locs)
    field.profile_dict["start_ids"] = list(start_ids)
    # add in a loop to do data averaging to combine multiple vectors
    field.profile_dict["data"] = {}
    for start_id in start_ids:
        field.profile_dict["data"][start_id] = get_data_vect(dataMap,nx,nz,direction,start_id)
    #
    # passing profile dict to group data
    groupDataDict[field.infile] = dict(field.profile_dict)
    return
#
# passes arguments to calc_percentile
def pctle(field,argDict,groupDataDict):
    #argument validation
    perc_list = argDict["perc"]
    perc_list.sort()
    #
    # getting requested percentiles for each flow component
    dataMap = list(field.dataMap) #prevents mutation of orginal map
    dataMap.sort()
    #
    for perc in perc_list:
        field.pctle_dict[perc] = calc_percentile(perc,dataMap)
    #
    # passing flow dict to group data
    groupDataDict[field.infile] = dict(field.pctle_dict)   
    return
#
#
#
########################################################################
#
# Global variable definitions
#
# dictionary to hold action functions and their respective output function
actionDict = {
    "hist" : [hist,outputHistData],
    "hist_logscale" : [hist_logscale,outputHistData],
    "hist_range" : [hist_range,outputHistData],
    "profile" : [profile,outputProfileData],
    "pctle" : [pctle,outputPctlData]
}
# dictionary for handling flags in argument list
flagDict = {
    "-m" : False,
    "-mo": False,
    "-so": False,
    "-sw": False,
    "-ow": False,
}
# dictionary storing command line arguments
argDict = {
    "delim" : ',',
    "flag_list" : []
}
# list holding FlowField objects
flowFields = []
# dictionary holding all group data incase the -m flag is applied
groupDataDict = {}
#
########################################################################
#
# Command Line Argument Processing and Validation
#
# checking number of args and if > 1 processing them
if (len(os.sys.argv) <= 1):
    print("Error - this program requires command line arguments")
    os.sys.exit("Exiting...")
else:
    for i in range(1,len(os.sys.argv)):
        arg = os.sys.argv[i]
        if (re.match("^-",arg)):
            if (arg in flagDict.keys()):
                flagDict[arg] = True
                argDict["flag_list"].append(arg)
            else:
                print("Error - Invalid flag: '"+arg+"' provided.")
                os.sys.exit()
        else:
            # splitting arg into a key,value pair
            kv_pair = arg.split("=")
            if (len(kv_pair) < 2):
                print("Error - Invalid argument: '"+arg+"' provided. Required to have form of arg=values")
                os.sys.exit()               
            argDict[kv_pair[0]] = kv_pair[1]
#
# validating arguements
valid = ValidateArgs.validate(actionDict,argDict)
if not (valid):
  os.sys.exit()
#
# Processing Flow Field Data
flowFields = loadInfileList(argDict["files"],argDict["delim"])
#
# processing flow fields using input action
processing_fun = actionDict[argDict["action"]][0]
output_fun = actionDict[argDict["action"]][1]
for field in flowFields:
    processing_fun(field,argDict,groupDataDict)
    content,outfileName = output_fun(field.infile,groupDataDict[field.infile])
    if (argDict['action'] == "hist_logscale"):
        outfileName = re.sub(r'HISTOGRAM','HISTOGRAM_LOGSCALE',outfileName)
    field.outfileName = outfileName
    field.outfile_content = content
    #
    # skipping individual output stage if "mulit-only" flag applied
    if (flagDict["-mo"]):
        continue
    #
    if (flagDict["-so"]):
        # only printing to screen
        content = content.replace(",","\t")
        print(content)
    elif (flagDict["-sw"]):
        # printing to screen
        content = content.replace(",","\t")
        print(content) 
        print(" ")
        if ((os.path.isfile(outfileName)) and not (flagDict["-ow"])):
            #
            print("Error - File already exists: "+outfileName)
            print("Specify flag -ow to overwrite existing files")
        else:
            # writing outfile
            outfile = open(outfileName,'w')
            outfile.write(content)
            outfile.close()
            print("Output file saved as: ",outfileName)
    else:
        if ((os.path.isfile(outfileName)) and not (flagDict["-ow"])):
            #
            print("Error - File already exists.: "+outfileName)
            print("Specify flag -ow to overwrite existing files")
        else:
            # writing outfile
            outfile = open(outfileName,'w')
            outfile.write(content)
            outfile.close()
            print("Output file saved as: ",outfileName) 
#
# exiting routine if multi-flags are false
if ((flagDict["-m"] == False) and (flagDict["-mo"] == False)):
  os.sys.exit()
#
# handling mutlifile output option
action = argDict["action"]
if (action == 'hist_logscale'):
    num_bins = argDict["num_bins"]
    #
    # grouping and sorting all of the flow data to generate proper bins)
    group_map = []
    for field in flowFields:
        group_map += list(field.dataMap)
    print("sorting...")
    group_map.sort()
    #
    print("creating bins...")
    bins = calc_log_bins(num_bins,group_map)
    # recalculating histogram data for new bins
    for field in flowFields:
        dataMap = list(field.dataMap) #prevents mutation of orginal dict
        dataMap.sort()
        histData = calcHistogramLog(bins,dataMap)
        field.histData = list(histData)
        print("Completed field: ",field)
    # creating output content
    for field in flowFields:
        content,outfileName = outputHistData(field.infile,field.histData)
        field.outfileName = outfileName
        field.outfile_content = content
    # processing content of each fields outfile
    group_content = multi_output_columns(flowFields)  
    #
elif (re.match("hist",action)):
    # 
    # determining global min and max values
    minMax = [0,0]
    for field in flowFields:
        key_list = list(field.pctle_dict.keys())
        key_list.sort()
        loc_minMax = [0,0]
        loc_minMax[0] = field.pctle_dict[key_list[0]]
        loc_minMax[1] = field.pctle_dict[key_list[-1]]
        #
        minMax[0] = loc_minMax[0] if (loc_minMax[0] < minMax[0]) else minMax[0]
        minMax[1] = loc_minMax[1] if (loc_minMax[1] > minMax[1]) else minMax[1]
    #
    # recalculating histograms with global min and max
    for field in flowFields:
        processing_fun(field,argDict,groupDataDict,globalMinMax=minMax)
        content,outfileName = output_fun(field.infile,groupDataDict[field.infile])
        field.outfileName = outfileName
        field.outfile_content = content
    # processing content of each fields outfile
    group_content = multi_output_columns(flowFields)  

elif (action == "pctle"):
    # processing content of each fields outfile
    group_content = multi_output_columns(flowFields)
    
elif (action == "profile"):
    group_content = ""
    for field in flowFields:
        group_content += field.outfile_content+"\n\n"

else:
    print("Invalid action got through to multi-stage: "+action)
    os.sys.exit()
#
# ouputting group content
date_str = str(datetime.datetime.now().date())
curr_time = datetime.datetime.now().time()
curr_time = curr_time.hour*3600+curr_time.minute*60+curr_time.second
date_str = re.sub("\s+","_",date_str)
date_str = re.sub(":","_",date_str)
group_name = ".\MULTI-"+action.upper()+"-DATA-"+date_str+"_"+str(curr_time)+".CSV"
#
if (flagDict["-so"]):
    # printing to screen only
    group_content = group_content.replace(",","\t")
    print(group_content) 
    print(" ")
elif (flagDict["-sw"]):
    # printing to screen and writing outfile
    outfile = open(group_name,'w')
    outfile.write(group_content)
    outfile.close()
    #
    group_content = group_content.replace(",","\t")
    print(group_content) 
    print(" ")
    print("Multi-file output saved as: ",group_name) 
else:
    # only writing to outfile
    outfile = open(group_name,'w')
    outfile.write(group_content)
    outfile.close()
    print("Multi-file output saved as: ",group_name) 
#
#
#
#
