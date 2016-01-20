########################################################################
#
# This is an importable module that stores functions can classes to 
# perform various post-processing operations on the data output by
# APM-FLOW##x64.EXE. It assumes the data remains in its standard ImageJ
# format with only one data array per file. Any future modifications to the 
# data files may cause unexpected results or failure of these routines.
#
# Written by: Matthew Stadelman
# Date Written: 2015/10/01
# Last Modfied: 2016/01/04
#
########################################################################
#
# Module Dependencies:
import os
import re
#
########################################################################
#
# Class definitions
#
# this class holds the characteristics of a flow field
class FlowField:
    def __init__(self,infile):
        self.infile  = infile
        self.outfile = ""
        self.nx = 0
        self.nz = 0
        self.dataMap = []
        self.histData = []
        self.pctle_dict = {}
        self.profile_dict = {}
#
# this class facilitates argument processing
class ArgProcessor:
    def __init__(self,field,map_func = lambda x : x, min_num_vals = 1,out_type = "single" ,expected_val = "##",err_desc_str="to have a numeric value"):
        self.field = field
        self.map_func = map_func
        self.min_num_vals = min_num_vals
        self.out_type = out_type
        self.expected_val = expected_val
        self.err_desc_str = err_desc_str
#
# this class extendends Error base class to create an ActionError based on inputs
class ActionError(Exception):
    def __init__(self,action):
        self.msg  = "Undefined action: '"+action+"' supplied, format is action=arg .\n"
        self.msg += "Where arg is one of the following hist, hist_range, profile or pctle."
#
# this class holds the error strings and validation function
class ValidateArgs:
    #
    # setting up arg processor objects for each action type
    hist_arg_processing = {
        "num_bins" :  ArgProcessor("num_bins",map_func = lambda x : int(x), min_num_vals = 1,out_type = "single" ,expected_val = "##",err_desc_str="to have a numeric value")
    }
    #
    hist_logscale_arg_processing = {
        "num_bins" :  ArgProcessor("num_bins",map_func = lambda x : int(x), min_num_vals = 1,out_type = "single" ,expected_val = "##",err_desc_str="to have a numeric value")
    }
    #
    hist_range_arg_processing = {
        "num_bins" :  ArgProcessor("num_bins",map_func = lambda x : int(x), min_num_vals = 1,out_type = "single" ,expected_val = "##",err_desc_str="to have a numeric value"),
        "range" :  ArgProcessor("range",map_func = lambda x : float(x), min_num_vals = 2,out_type = "list" ,expected_val = "##,##",err_desc_str="to have two numeric values")
    }
    #
    profile_arg_processing = {
        "locs" :  ArgProcessor("locs",map_func = lambda x : float(x), min_num_vals = 1,out_type = "list" ,expected_val = "##1,##2,##3,...,##N",err_desc_str="to have 1 -> N numeric values"),
        "dir" :  ArgProcessor("dir",map_func = lambda x : x, min_num_vals = 1,out_type = "single" ,expected_val = "val",err_desc_str="val is either x or z")    
    }
    #
    pctle_arg_processing = {
        "perc" :  ArgProcessor("range",map_func = lambda x : float(x), min_num_vals = 1,out_type = "list" ,expected_val = "##1,##2,##3,...,##N",err_desc_str="to have 1 -> N numeric values")
    }
    #
    #
    action_processors = {
        "hist" : hist_arg_processing,
        "hist_logscale" : hist_logscale_arg_processing,
        "hist_range" : hist_range_arg_processing,
        "profile" : profile_arg_processing,
        "pctle" : pctle_arg_processing
    }
    #
    # generates an error message 
    def input_error(err=KeyError,action="",field="",expected="",desc_str="",received=""):
        if  (isinstance(err,KeyError)):
            msg = "Error - action="+action+" requires "+field+"="+expected+" argument."
        elif (isinstance(err,IndexError)):
            msg = "Error - action="+action+" requires "+field+"="+expected+" "+desc_str+". Recieved: '"+received+"'"
        elif (isinstance(err,ValueError)):
            msg = "Error - action="+action+" requires "+field+"="+expected+" "+desc_str+". Recieved: '"+received+"'"
        else:
            print("Unknown Error Type Provided.")
            raise err
        return msg   
    #
    # validation function
    def validate(actionDict,argDict):
        #
        try:
            action = argDict["action"]
            if not (argDict["action"] in  actionDict.keys()):
                raise ActionError(action)
        except KeyError:
            print("Error - No action provided, arguments must include action=arg.")
            print("Where arg is one of the following hist, hist_range, profile or pctle")
            return False
        except ActionError as err:
            print(err.msg)
            return False
        #
        # getting processor dict
        arg_processing = ValidateArgs.action_processors[action] 
        #
        # validating arguments for supplied action
        valid = True
        for field in arg_processing.keys():
            try:
                #processing inputs
                if (arg_processing[field].out_type == "single"):
                    input_val = arg_processing[field].map_func(argDict[field])
                    if (input_val == ""):
                        raise IndexError
                    argDict[field] = input_val
                else:
                    input_list = list(filter(None,argDict[field].split(',')))
                    input_list = list(map(arg_processing[field].map_func,input_list))
                    if (len(input_list) < arg_processing[field].min_num_vals): #checking length
                        raise IndexError
                    argDict[field] = input_list
            except KeyError as err:
                msg = ValidateArgs.input_error(err,action,field,expected=arg_processing[field].expected_val)
                print(msg)
                valid = False
            except ValueError as err:
                msg = ValidateArgs.input_error(err,action,field,expected=arg_processing[field].expected_val,desc_str=arg_processing[field].err_desc_str,received=argDict[field])
                print(msg)
                valid = False
            except IndexError as err:
                msg = ValidateArgs.input_error(err,action,field,expected=arg_processing[field].expected_val,desc_str=arg_processing[field].err_desc_str,received=argDict[field])
                print(msg)
                valid = False
        try:
            argDict["files"] = list(filter(None,argDict["files"].split(",")))
            if (len(argDict["files"]) == 0):
                raise KeyError
        except KeyError:
            print("Error - No input files provided, input files must be specfied by files=file1,file2,...,fileN")
            return False 
        #
        return valid
#
########################################################################
#
# Function definitions  
#
# function to read input file and load lists of flow rates into
# the supplied dictionary
def parseFlowFile(filename,dataMap,delim):
    input_file = open(filename,'r')
    content = input_file.read()
    input_file.close()
    #
    content_arr = list(filter(None,content.split('\n')))
    start_index = 0
    #
    #finding first line of flow data
    for l in range(len(content_arr)):
        line = content_arr[l]
        if not (re.search('#',line)):
            start_index = l
            break
    #
    # processing each line of file converting strings to floats
    nx = 0
    nz = 0
    for l in range(start_index,len(content_arr)):
        num_arr = list(filter(None,re.split(delim,content_arr[l])))
        if (nx == 0):
            nx = len(num_arr)
        elif (nx != len(num_arr)):
            print("Warning: number of columns changed from",nx," to ",len(num_arr)," on data row: ",l+1)
        #
        num_arr = [float(num) for num in num_arr]
        dataMap += num_arr
        nz += 1
    #
    return (nx,nz)
#
# function to load all of the files
def loadInfileList(infileList,delim):
    flowFields = []
    #
    # loading and parsing each input file
    for infile in infileList:
        #
        # constructing object
        field = FlowField(infile)
        #
        # opening and reading file to populate dictionary
        field.nx,field.nz = parseFlowFile(field.infile,field.dataMap,delim)
        print('Finished Reading File: '+field.infile)
        #
        flowFields.append(field)
    #
    return(flowFields)
#
# this calcualtes a histogram for the entire data range
# using min and max as the first and last bins holding extrema
def calcHistogram(numBins,mapData,minMax):
    #
    # setting initial values
    histData = []
    minMax.sort()
    step = (minMax[1] - minMax[0])/(numBins-3.0)
    lowVal = mapData[0]
    highVal = minMax[0]
    numVals = 0
    #
    # calculating number of data points in each bin
    for i in range(len(mapData)):
        flow = mapData[i]
        if ((flow >= lowVal) and (flow < highVal)):
            numVals += 1
        else:
            histData.append([lowVal,highVal,numVals])
            numVals = 0
            lowVal = highVal
            highVal += step
            if (lowVal >= minMax[1]):
                highVal = mapData[-1]*1.001 #increased so mapData[-1] fits in the range
            # catching transition data point if its in the bin
            if ((flow >= lowVal) and (flow < highVal)):
                numVals += 1
    histData.append([lowVal,highVal,numVals])
    #
    return histData
#
# this calulates a histogram only for data in a specific range
def calcHistogramRange(numBins,mapData,minMax):
    #
    # setting initial values
    histData = []
    minMax.sort()
    step = (minMax[1] - minMax[0])/(numBins-1.0)
    lowVal = minMax[0]
    highVal = minMax[0]+step
    numVals = 0
    #
    # calculating number of data points in each bin
    i = 0
    while (lowVal < minMax[1]):
        flow = mapData[i]
        if ((flow >= lowVal) and (flow < highVal)):
            numVals += 1
        elif (flow >= highVal):
            histData.append([lowVal,highVal,numVals])
            numVals = 0
            lowVal = highVal
            highVal += step
        #
        i += 1
        if (i == len(mapData)):
           break
    #
    return histData
#
# this calculates a histogram using a log scale where the percentile of
# 1 determines how many bins to have between 0 and 1
# may merge this with hist range by independently creating a tuple list of bins
def calcHistogramLog(bin_list,flow_data):
    histData = []
    bin = bin_list[0]
    i = 0
    b = 0
    num_vals = 0
    while (True):
        flow = flow_data[i]
        if ((flow >= bin[0]) and (flow < bin[1])):
            num_vals += 1
            i += 1
        else:
            histData.append([bin[0],bin[1],num_vals])
            num_vals = 0
            b += 1
            if (b == len(bin_list)):
                break
            bin = bin_list[b]
        #        
        if (i == len(flow_data)):
           for b in range(b,len(bin_list)):
               bin = bin_list[b]
               histData.append([bin[0],bin[1],num_vals])
               num_vals = 0 #setting to 0 for all subsequent bins
           break
    return histData
#
# this routine will create a list of tuples where the first val in the 
# tuple is the low and the second val is the high. low <= data < high
# the percentile locations of -1 0 and 1 will be considered as appropraite 
# to distribute bins evenly within the range
def calc_log_bins(num_bins,flow_data):
    min_val = flow_data[0]
    max_val = flow_data[-1]
    num_arr = [min_val]
    perc_arr = [0.0]
    #
    # getting percentiles of key scaling numbers -1, 0 and 1
    if (min_val < 0):
        num_arr.append(-1.0)
        perc_arr.append(calc_percentile_num(-1.0,flow_data,True))
        low_zero = calc_percentile_num(0.0,flow_data,False)
        high_zero = calc_percentile_num(0.0,flow_data,True)
        num_arr.append(0.0)
        perc_arr.append((low_zero+high_zero)/2)
    elif (min_val > 0):
        num_arr[0] = 0.0
    else:
        num_arr.append(0.0)
        perc_arr.append(calc_percentile_num(0.0,flow_data,False))
    # end if
    #
    num_arr.append(1.0)
    perc_arr.append(calc_percentile_num(1.0,flow_data,False)) 
    num_arr.append(max_val)
    perc_arr.append(1.0)
    #
    num_bins_arr = []
    for i in range(len(perc_arr)-1):
        if (num_arr[i+1] == num_arr[i]):
            continue
        num_bins_arr.append(int(num_bins*(perc_arr[i+1]-perc_arr[i]))+1)
    #
    # creating the list of bins for the data set
    bins = []
    for i in range(len(num_arr)):
        if (num_arr[i] == 0.0):
            num_bins_arr.insert(i,0) #allows num_bins to skip 0
            continue
        elif (num_arr[i] == -1.0):
            scale_fact = (1 + 5**0.5)/2 #golden ratio
            logscale_high = list(-scale_fact**n for n in range(-num_bins_arr[i],0))
            logscale_low = list(-scale_fact**n for n in range(-num_bins_arr[i],0))
            logscale_low.insert(0,-1.0)
            logscale_high.append(0.0)  
        elif (num_arr[i] < 0):
            scale_fact = abs(num_arr[i])**(1/num_bins_arr[i])
            logscale_high = list(-scale_fact**n for n in range(num_bins_arr[i]))
            logscale_low = list(-scale_fact**n for n in range(num_bins_arr[i]+1))
        elif (num_arr[i] == 1.0):
            scale_fact = (1 + 5**0.5)/2 #golden ratio
            logscale_high = list(scale_fact**n for n in range(-num_bins_arr[i]+1,0))
            logscale_low = list(scale_fact**n for n in range(-num_bins_arr[i]+1,0))
            logscale_high.append(1.0)  
            logscale_low.insert(0,0.0)
        else:
            scale_fact = num_arr[i]**(1/num_bins_arr[i])
            logscale_high = list(scale_fact**n for n in range(1,num_bins_arr[i]))
            logscale_low = list(scale_fact**n for n in range(num_bins_arr[i]))
            logscale_high.append(num_arr[i])
        logscale_low.sort()
        logscale_high.sort()
        bins += list(zip(logscale_low,logscale_high)) 
    # decreasing lowermost limit of the first bin to prevent missing the first point
    if (bins[0][0] > 0):
        pass
        #bins[0] = (bins[0][0]*0.95,bins[0][1])
    else:
        bins[0] = (bins[0][0]*1.05,bins[0][1])
    #increasing the uppermost limit of the last bin so the final data point is captured.
    bins[-1] = (bins[-1][0],bins[-1][1]*1.05)
    #
    return bins 
#
# this function calculates the provided percentile
# assumes list has been sorted
def calc_percentile(perc,flow_list):
    tot_vals = float(len(flow_list))
    num_vals = 0.0
    #
    # stepping through list
    for i in range(len(flow_list)):
        flow_index = i
        if ((num_vals/tot_vals*100.0) >= perc):
            break
        else:
            num_vals += 1
    #
    #
    return(flow_list[flow_index])
#
# this function calculates the  percentile of the provided number
# assumes list has been sorted if last is true it goes to data > num
# if last is false then it breaks on data >= num
def calc_percentile_num(num,flow_list,last):
    tot_vals = float(len(flow_list))
    num_vals = 0.0
    #
    # stepping through list
    for i in range(len(flow_list)):
        if ((last == True) and (flow_list[i] > num)):
            break
        elif ((last == False) and (flow_list[i] >= num)):
            break
        else:
            num_vals += 1
    #
    perc = num_vals/tot_vals
    #
    return(perc)
#
# this function returns either of a row or column of cells as a vector in the X or Z direction
# for use in creating flow profiles
def get_data_vect(flow_data,nx,nz,direction,start_id=0):
    if (direction.lower() == 'x'):
        # getting row index
        if (start_id >= nz):
            start_id = nz
        elif (start_id <= 0):
            start_id = 1
        out_data = flow_data[(start_id-1)*nx:(start_id)*nx]
        return(out_data)
         
    elif (direction.lower() == 'z'):
        if (start_id >= nx):
            start_id = nx
        elif (start_id <= 0):
            start_id = 1
        #
        outdata = []
        start_id = start_id - 1
        for iz in range(nz):
            outdata.append(flow_data[iz*nx+start_id])
        return(outdata)
    else:
        print("Error - invalid direction supplied, can only be X or Z")
        return False
#
#
def avgAllAboveVal(flowData,minVal):
  flowData = list(flowData) #failsafe to prevent accidental mutation
  flowData = list(filter(lambda num : num > minVal,flowData))
  avg = sum(flowData)/len(flowData)
  return(avg)
#
#
def avgAllBelowVal(flowData,maxVal):
  flowData = list(flowData) #failsafe to prevent accidental mutation
  flowData = list(filter(lambda num : num < maxVal,flowData))
  avg = sum(flowData)/len(flowData)
  return(avg)
#
# outputting flow profile vector to CSV in same directory as flow file
def outputProfileData(filename,profile_dict):
    #
    direction = profile_dict["dir"].upper()
    locs = profile_dict["locs"]
    start_ids = profile_dict["start_ids"]
    #
    # naming file,
    ldot = filename.rfind(".")
    prof_outfile = filename[:ldot]+"-PROFILE-"+direction+"-AXIS"+filename[ldot:]
    #
    # outputting data
    content = direction+"-AXIS PROFILE DATA FROM FILE: "+filename+"\n"
    i = 0
    for row_id in start_ids:
        content +="LOCATION: "+str(locs[i])+"%, ROW NUMBER: "+str(row_id)+"\n"
        content += ','.join([str(val) for val in profile_dict['data'][row_id]])+"\n"
        i += 1
    content += "\n"
    #
    return(content,prof_outfile)
#
# outputting histogram values to CSV in same directory as flow file
def outputHistData(filename,histData):
    #
    # getting index of last occurance of flow and the backslash
    ldot = filename.rfind(".")
    #
    # naming file, appends 'HISTOGRAM' before the extension
    hist_outfile = filename[:ldot]+"-HISTOGRAM"+filename[ldot:]
    #
    # outputting data
    content = "HISTOGRAM DATA FROM FILE: "+filename+"\n"
    content += "LOW VALUE,HIGH VALUE,NUM DATA POINTS\n"
    for i in range(len(histData)):
        content += str(histData[i][0])+","+str(histData[i][1])+","+str(histData[i][2])+",\n"
    content += "\n"
    #
    return(content,hist_outfile)
    #
#
# outputting percentile data to CSV in same directory as flow file
def outputPctlData(filename,pctle_dict):
    #
    # getting index of last occurance of flow and the backslash
    ldot = filename.rfind(".")
    #
    # naming ouput file
    pctle_outfile = filename[:ldot]+"-PERCENTILES"+filename[ldot:]
    #
    # outputting data
    content = "PERCENTILE DATA FROM FILE: "+filename+"\n"
    content += "PERCENTILE,\n"
    #
    perc_keys = list(pctle_dict.keys())
    perc_keys.sort()
    for perc in perc_keys:
        content += str(perc)+","+str(pctle_dict[perc])+"\n"
    content += "\n"
    #
    #
    return(content,pctle_outfile)
    #
#
# this function takes the content from multiple files can joins it side by side
def multi_output_columns(flowFields_arr):
    # splitting content of each outfile
    num_lines = 0
    for field in flowFields_arr:
        content_arr = field.outfile_content.split("\n")
        field.outfile_arr = list(content_arr)
        num_lines = len(content_arr) if (len(content_arr) > num_lines) else num_lines
    # processing content
    content_arr = []
    max_len = 0
    for l in range(num_lines):
        line_arr = []
        for field in flowFields_arr:
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
#
