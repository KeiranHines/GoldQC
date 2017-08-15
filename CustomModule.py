# -*- coding: utf-8 -*-
"""
Python Module: CustomModule.py
Created by: Nick Martin, GoldSim Technology Group
Creation Date: 21 May 2015
Last Edited: 15 June 2015

License: FreeBSD License (reproduced below)

Purpose:

This module contains a collection of functions and module-level global values
or parameters which provide the interface or linkage between a custom Python 
module to a GoldSim External element and more specifically to the 
CustomPython.dll.

The module-level globals are all explained below in the section where they
are defined. In terms of functions, there is generally a 1:1 mapping between
the functions defined here and the different status states for the dll which is
linked to a GoldSim external element. The one exception is for state
XF_REP_ARGUMENTS which wants both the number of inputs expected and the 
number of outputs to be returned.

The mapping/wrapping is as follows:

C language dll state -> Cython (CustomPython.pyx) --> CustomModule function

XF_INITIALIZE -> InitRoutines --> InitialChecks
XF_REP_VERSION -> ReturnCustomModuleVersion --> PyModuleVersion
XF_REP_ARGUMENTS -> NumInputsExpected --> CalcInputs
XF_REP_ARGUMENTS -> NumOutputsToProvide --> CalcOutputs
XF_CALCULATE -> DoCalcsAndReturnValues --> CustomCalculations
XF_CLEANUP -> WrapUpSimulation --> WrapUpStuff

There is one other function which is required in this module which is 
called from CustomPython.pyx but which is not currently implemented. This 
function is PythonInitializationError. You can leave this function in for
future compatibility.

This module provides a linkage between GoldSim and custom Python code. Really,
what this module does is receive the list of input arguments from the GoldSim
external element via the Cython interface in CustomPython.dll --- see
CustomPython.pyx --- and copy this input array to a list of defined data 
structure, using Python objects, for passing on to whatever custom Python 
module or implementation the user desires. The definition of these data 
structures is provided below in the DATA STRUCTURES section.

The custom Python module/code is referred to in this module as CImp (see 
anything that is CImp. ) and this custom module is loaded/accessed using the
import XXXX as CImp statement. There are a number of functions and parameters
that need to be implemented in the CImp module. These are discussed below in
the CImp REQUIREMENTS section. If CImp (the user's custom python code) is
returning values to GoldSim, then these values need to have the correct 
data structure format per the DATA STRUCTURES section.

Finally, there are two module level global lists (IN_VAR_LIST and RET_VAR_LIST)
which need to be defined to complete the GoldSim to Python interface.

IN_VAR_LIST

IN_VAR_LIST is a Python list of variables which are defined in the External 
element interface tab in the input section. In the IN_VAR_LIST an item in the
list corresponds to each External element interface variable. The items in
IN_VAR_LIST need to have the same order as the specification in the External 
element interface. Each item in IN_VAR_LIST is also a list (i.e. a nested 
list). The indexes and values which need to be defined for each nested list in
IN_VAR_LIST which corresponds to a specific variable in the External element 
input interface are defined using the globals: VAR_CNT_IND, VAR_TYPE_IND, 
VAR_DESC_IND, and VAR_TSTYPE_IND.

RET_VAR_LIST

RET_VAR_LIST is a Python list of variables which are defined in the External
element interface tab in the output section. In the RET_VAR_LIST an item in 
the list corresponds to each External element interface variable from the 
output section. The items in RET_VAR_LIST need to have the same order as the
specification in the External element interface. Each item in RET_VAR_LIST is 
also a list (i.e. a nested list). The indexes and values which need to be 
defined for each nested list in IN_VAR_LIST which corresponds to a specific
variable in the External element input interface are defined using the 
globals: VAR_CNT_IND, VAR_TYPE_IND, VAR_DESC_IND, and VAR_TSTYPE_IND.

DATA STRUCTURES

Only certain types of GoldSim elements are available to the interface of the
External element as described in the appendix to the GoldSim User's Guide. 
Additionally, GoldSim uses double values for all input and output arguments 
for/from the External element. The input and output arguments are passed from
the external element to the receiving dll (and thence to this module) as a 
pointer to an array of doubles (one pointer to an array for input arguments and
one pointer to a separate array for output arguments).

A subset of the element or data types, supported by GoldSim, are supported by
this module. Specifically, the following types are supported:

Scalar
Vector
Matrix
Time Series (single time series, scalar values)
1D Lookup table
2D Lookup table

***Vector and matrix time series are not supported. Additionally 3 D lookup
tables are not supported.

The Python data structure for each of the supported element types is as 
follows.

Scalar = float value
Vector = list of float values. The vector has number of indices equal to 
            number of float items in the list.
Matrix = list of lists of float values. Each nested list corresponds to a row
            in the matrix and has the number of items equal to number of 
            columns in the matrix. There are the same number of nested lists
            as number of rows.
Time Series = list of lists. Each nested list is a [ datetime object, value ]
            list. The number of nested lists equals the number of values in
            the time series. This is also equal to the number of time indices.
            A DateTime object is a Python Standard Library time structure. If
            it is a Calendar time time series then the datetime object is the
            standard datetime datetime structure - datetime( year, month, day,
            hour, minute, second, ... ). If the time series is an elapsed time
            time series, then the datetime object is a datetime timedelta 
            object. The timedelta object provides total time between two 
            datetime objects. To get this in seconds as required by the 
            GoldSim external element, the total_seconds() method can be used
            on the timedelta objects.
1D Lookup table = dictionary. Uses dimension, row, and value keys to store
            the appropriate values.
2D Lookup table = dictionary. Uses dimension, row, column, and value keys to
            store the appropriate values.

CImp REQUIREMENTS

This module is designed to provide the interface between your custom, pure 
Python code and GoldSim. The main feature or function of this interface is
to respond to the "states" in the CustomPython.dll which are required by the
GoldSim External element and to transfer and convert input values and output
values from the GoldSim provided array of doubles format to the Python data
structures defined in the DATA STRUCTURES section.

Custom, pure Python code then needs to provide a limited number of parameter
values to this module as well as to provide a small number of "hooks" to 
enable receipt of the input values from GoldSim and to return whatever 
values were calculated back to GoldSim. This module is designed to provide
the input information from GoldSim in the DATA STRUCTURES section formats to
custom, pure Python code and to receive information back from custom, pure
Python code in the same DATA STRUCTURES formats.

    Interface between this Module and Custom, Pure Python code
    
The main portion of the inteface is the import statement ---

import MY_MODULE as CImp

Your custom, pure Python module then needs to provide the following parameters:

CImp.CUSTOM_MODULE_VERSION --- module version which sent to Goldsim.
CImp.LOG_FILE_NAME --- The log file name which is used for checking and error
                        handling.

Currently, this module expects that your current custom python module will
implement the following functions:

CImp.SetupThings() in InitialChecks()
RetVarList = CImp.MyCustomCalculations( PyInputList ) in CustomCalculations()
CImp.WrapUpLogFile( CImp.LOG_FILE_NAME ) in WrapUpStuff()

The important function is the "MyCustomCalculations" function. This should be
the focus of your customization. For this function, the passed argument 
"PyInputList" is the inputs from GoldSim in the DATA STRUCTURES formats. The
returned value, "RetVarList" needs to be the returned values from your function
in the DATA STRUCTURES formats.

"""

"""
LICENSE

This module is available for your use under the FreeBSD License, see:
http://directory.fsf.org/wiki?title=License:FreeBSD 

FreeBSD License

Copyright (c) 2015, GoldSim Technology Group LLC
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project.
"""
#===========================================================================
# imports
import GoldQC as CImp
#BAD_NAME = "
#===========================================================================
# MODULE GLOBAL parameters/values.
# In Python, anything declared at the main module scope is a module global.
# An easy way of thinking about the main module scope in this case is that
# there is no indentation for the variable definition.
# 
# Local, function scope variables will be defined with indentation to 
#   represent their scope within the local function.
#
# GoldSim integration values.
# these module-level globals are specifications that facilitate the interface
# of the python functions with the required formats for the GoldSim External
# element. This allows the receipt and sending of values between the two
# programs.

# Type specifications. GoldSim supports a single value, vector, matrix, 
# 1-D lookup table, 2-D lookup table, 3-D lookup table and time series.
# These values always come from GoldSim (and must return to GoldSim) as
# double.
# NOTE that this module only currently supports scalar time series and 1-D 
#   and 2-D lookup tables. Also, note that GoldSim only allows lookup tables
#   in the output interface and so will not send lookup tables to an 
#   external dll.
DBL_TYPER = "Double"            # this is actually scalar
VECTOR_TYPER = "1-D Array"      # this is vector
MATRIX_TYPER = "2-D Array"      # this is matrix
TS_TYPER = "Time Series"        # time series. Only scalar supported
LUTABLE_1D_TYPER = "1-D Lookup Table"   # look-up table
LUTABLE_2D_TYPER = "2-D Lookup Table"   # look-up table
#---------------------------------------------------------------------------
# GoldSim specific Header, extra value counts.
TIME_SERIES_EXTRA = 8
LUTABLE_EXTRA = 2
#---------------------------------------------------------------------------
# fist specify the indexes for the input and output variable lists which are
# defined below.
VAR_CNT_IND = 0             # index for count (could be list if 2D)
VAR_TYPE_IND = 1            # index for the type
VAR_DESC_IND = 2            # the index for the description
VAR_TSTYPE_IND = 3          # the index for the time series type
#---------------------------------------------------------------------------
# time series types
ELAPSED_TIME = 0            # ID for elapsed time
CALENDAR_TIME = 1           # ID for calendar time
GS_TIMESERIES_TYPE_IND = 2  # index in array where time series type goes
#---------------------------------------------------------------------------
# IN_VAR_LIST provides the list of input variables provided by GoldSim. This 
# must agree with the Interface specification in type and order for the 
# External element. This list, L, is composed of nested list objects, NL, 
#       which have the format:
#           NL[0] = number of values (data values does not include header stuff)
#                   NOTE that this needs to be a list if 2 D lookup table
#                   because need the values for each dimension. Also needs to
#                   be a list if a matrix [row, col]
#           NL[1] = the type of object/value structure to return
#           NL[2] = the description for this item
#           NL[3] = the time series type; only for time series

"""
IN_VAR_LIST = [ [ 1, DBL_TYPER, "Test 1" ] ]
"""
"""
IN_VAR_LIST = [ [ 1, DBL_TYPER, "Start Time (date time)" ],
                [ [3,4], MATRIX_TYPER, "Matrix" ],
                [ 4, VECTOR_TYPER, "Vector" ],
                [ 1, DBL_TYPER, "Vector Multiplier" ],
                [ 12, TS_TYPER, "Calendar Time Series", CALENDAR_TIME ], 
                [ 12, TS_TYPER, "Elapsed Time Series", ELAPSED_TIME ],
                [ 1, DBL_TYPER, "Time Series Multiplier" ] ]
"""
IN_VAR_LIST = [ [7,VECTOR_TYPER,"inputVector" ] ]

#---------------------------------------------------------------------------
# RET_VAR_LIST provides the list of return variables to GoldSim. This must
# agree with the Interface specification in type and order for the 
# External element. This list, L, is composed of nested list objects, NL, 
#       which have the format:
#           NL[0] = number of values (data values does not include header stuff)
#                   NOTE that this needs to be a list if 2 D lookup table
#                   because need the values for each dimension. Also needs to
#                   be a list if a matrix [row, col]
#           NL[1] = the type of object/value structure to return
#           NL[2] = the description for this item
#           NL[3] = the time series type; only for time series

"""
RET_VAR_LIST = [ [ 1, DBL_TYPER, "Number of Inputs" ] ]
"""
"""
RET_VAR_LIST = [ [ 3, LUTABLE_1D_TYPER, "1D Lookup Table" ],
                 [ [4,4], MATRIX_TYPER, "Matrix" ],
                 [ 12, TS_TYPER, "Elapsed Time Series", ELAPSED_TIME ],
                 [ 1, DBL_TYPER, "Number of Inputs" ],
                 [ 12, TS_TYPER, "Calendar Time Series", CALENDAR_TIME ],
                 [ [4,3], LUTABLE_2D_TYPER, "2D Lookup Table" ],
                 [ 12, VECTOR_TYPER, "Vector" ],
                  [ 1, DBL_TYPER, "Number of Inputs" ] ]
"""

RET_VAR_LIST = [ [7,VECTOR_TYPER,"outputVector" ] ]
#---------------------------------------------------------------------------
# set the debug level. 0 = no output; 1 = will output to file input argument
# list and output return list.
DEBUG_LEVEL = 1
#---------------------------------------------------------------------------
# GoldSim uses Microsoft-based date calculations and Microsoft's version of
#   the Julian Date.
GS_START_YEAR = 1899        # starting year for GoldSim Julian Epoch
GS_START_MONTH = 12         # starting month for GoldSim Julian Epoch
GS_START_DAY = 30           # starting day for GoldSim Julian Epoch
GS_START_HOUR = 0           # the starting hour for GoldSim Julian Epoch
#---------------------------------------------------------------------------
# Lookup tables are stored in Python dictionary format. These are the keys
# for the dictionary.
LUTABLE_DIMS_KEY = "dimensions"     # the key for the lookup table dimensions
LUTABLE_ROW_KEY = "rows"    # the key for the lookup table rows
LUTABLE_COL_KEY = "cols"    # the key for the lookup table columns
LUTABLE_VALUES_KEY = "values"       # the key for the lookup table values

#===========================================================================
# Functions in this module.
def RetLUTableHeaderCnt( NumDim, LogFileName ):
    """
    Convenience function which returns the lookup table header count.
    
    Argument:
        
        NumDim = the number of lookup table dimensions.
        
    Return:
    
        The number of header values according to the dimension.
        -1 denotes error.
        
    """
    # parameters
    FuncName = "RetLUTableHeaderCnt"
    if ( NumDim < 1) or (NumDim > 3):
        # this is an error
        with open( LogFileName, 'a', 0 ) as LFID:
            LFID.write( "Invalid lookup table dimension of %d passed to " \
                        "%f.\n" % ( NumDim, FuncName ) )
        return -1
    # if are here then are good.
    return LUTABLE_EXTRA + ( NumDim - 1 )
    
def InitialChecks():
    """
    Wrapper function which is called during XF_INITIALIZE phase. It is 
    called by the function InitRoutines in CustomPython.pyx. This function
    is setup to call from the "specific" module HMS_Python in this case
    the CheckPathsAndFiles and the WriteScripts functions.
    
    Arguments:
        
        None
    
    Returns:
    
        1 for error
        0 for good
    
    """
    # python variables
    RetStatus = 0           # the return status from CheckPathsandFiles
    # just need to call our functions
    RetStatus = CImp.SetStuffUp()
    # return
    return RetStatus

def PyModuleVersion():
    """
    Wrapper function that transfers the version specified in the Specific/
    Custom implementation module back to the dll.
    
    Arguments:
        None
        
    Return:
        Version number --- will be cast to a double later
        
    """
    return CImp.CUSTOM_MODULE_VERSION

def CalcInputs():
    """
    Function which determines the number of expected inputs. This number
    comes directly from the specified input arguments that are expected from
    the more specific module implementation. These arguments are defined
    using a module-level global in this file with IN_VAR_LIST.
    
    Arguments:
        
        None
        
    Return:
        
        Number of inputs expected. -1 is an error
    
    """
    # globals
    global VAR_CNT_IND, IN_VAR_LIST, DBL_TYPER, VECTOR_TYPER, MATRIX_TYPER
    global TS_TYPER, LUTABLE_1D_TYPER, LUTABLE_2D_TYPER, VAR_TYPE_IND
    global TIME_SERIES_EXTRA
    # parameters
    FuncName = "CalcInputs"
    # local python variables
    NumInExpect = int( 0 )      # the number of inputs expected.
    NumCurVar = int( 0 )        # the number from the current variable.
    NumRows = int( 0 )          # number of rows for 2D lookup table
    NumCols = int( 0 )          # number of columns for 2D lookup table
    CurrentType = ""            # the type of the current variable.
    # to calculate just go through the list.
    for ThisList in IN_VAR_LIST:
        CurrentType = str( ThisList[ VAR_TYPE_IND ] )
        if CurrentType == DBL_TYPER:
            NumCurVar = int( ThisList[ VAR_CNT_IND ] )
        elif CurrentType == VECTOR_TYPER:
            NumCurVar = int( ThisList[ VAR_CNT_IND ] )
        elif CurrentType == MATRIX_TYPER:
            NumRows = int( ThisList[ VAR_CNT_IND ][0] )
            NumCols = int( ThisList[ VAR_CNT_IND ][1] )
            NumCurVar = NumRows * NumCols
        elif CurrentType == LUTABLE_1D_TYPER:
            # no lookup types in inputs
            with open( CImp.LOG_FILE_NAME, 'a', 0 ) as LogFID:
                LogFID.write( "Data type %s not supported for inputs by " \
                              "GoldSim.\n" % CurrentType )
            return -1
        elif CurrentType == LUTABLE_2D_TYPER:
            # no lookup table types in inputs
            with open( CImp.LOG_FILE_NAME, 'a', 0 ) as LogFID:
                LogFID.write( "Data type %s not supported for inputs by " \
                              "GoldSim.\n" % CurrentType )
            return -1
        elif CurrentType == TS_TYPER:
            NumCurVar = int( TIME_SERIES_EXTRA ) + ( 2 * 
                                            int( ThisList[ VAR_CNT_IND ] ) )
        else:
            # this is an error for an undefined type.
            with open( CImp.LOG_FILE_NAME, 'a', 0 ) as LogFID:
                LogFID.write( "Found invalid variable type of %s in " \
                              "function %s.\n" % 
                              ( CurrentType, FuncName ) )
            # log file closed
            return -1
        NumInExpect = NumInExpect + NumCurVar
    # end of for
    return NumInExpect

def CalcOutputs():
    """
    Function which determines the number of expected outputs. This number
    comes directly from the specified output variables that are expected from
    the more specific module implementation. These arguments are defined
    using a module-level global in this file with RET_VAR_LIST.
    
    Arguments:
        
        None
        
    Return:
        
        Number of outputs expected. -1 is an error
    
    """
    # globals
    global VAR_CNT_IND, RET_VAR_LIST, DBL_TYPER, VECTOR_TYPER, MATRIX_TYPER
    global TS_TYPER, LUTABLE_1D_TYPER, LUTABLE_2D_TYPER, VAR_TYPE_IND
    global TIME_SERIES_EXTRA
    # parameters
    FuncName = "CalcOutputs"
    # local python variables
    NumOutExpect = int( 0 )     # the number of outputs expected.
    NumCurVar = int( 0 )        # the number from the current variable.
    LUNumRet = int( 0 )         # the number of header values from lu table
    NumRows = int( 0 )          # number of rows for 2D lookup table
    NumCols = int( 0 )          # number of columns for 2D lookup table
    CurrentType = ""            # the type of the current variable.
    # to calculate just go through the list.
    for ThisList in RET_VAR_LIST:
        CurrentType = str( ThisList[ VAR_TYPE_IND ] )
        if CurrentType == DBL_TYPER:
            NumCurVar = int( ThisList[ VAR_CNT_IND ] )
        elif CurrentType == VECTOR_TYPER:
            NumCurVar = int( ThisList[ VAR_CNT_IND ] )
        elif CurrentType == MATRIX_TYPER:
            NumRows = int( ThisList[ VAR_CNT_IND ][0] )
            NumCols = int( ThisList[ VAR_CNT_IND ][1] )
            NumCurVar = NumRows * NumCols
        elif CurrentType == LUTABLE_1D_TYPER:
            LUNumRet = RetLUTableHeaderCnt( 1, CImp.LOG_FILE_NAME )
            if LUNumRet < 1:
                # already wrote infor to log in RetLUTableHeaderCnt
                return -1
            NumCurVar = LUNumRet + ( 2 * int( ThisList[ VAR_CNT_IND ] ) )
        elif CurrentType == LUTABLE_2D_TYPER:
            LUNumRet = RetLUTableHeaderCnt( 2, CImp.LOG_FILE_NAME )
            if LUNumRet < 1:
                # already wrote infor to log in RetLUTableHeaderCnt
                return -1
            NumRows = int( ThisList[ VAR_CNT_IND ][0] )
            NumCols = int( ThisList[ VAR_CNT_IND ][1] )
            NumCurVar = LUNumRet + NumRows + NumCols + ( NumRows * NumCols )
        elif CurrentType == TS_TYPER:
            NumCurVar = int( TIME_SERIES_EXTRA ) + ( 2 * 
                                            int( ThisList[ VAR_CNT_IND ] ) )
        else:
            # this is an error for an undefined type.
            with open( CImp.LOG_FILE_NAME, 'a', 0 ) as LogFID:
                LogFID.write( "Found invalid variable type of %s in " \
                              "function %s.\n" % 
                              ( CurrentType, FuncName ) )
            # log file closed
            return -1
        NumOutExpect = NumOutExpect + NumCurVar
    # end of for
    return NumOutExpect

def ConvertInListToMatrix( VarInList, NumRows, NumCols ):
    """
    Convenience function which converts an input list to a nested list, 
    matrix format. The input list is a matrix which goes across each row
    first. No header for a matrix.
    
    Arguments:
    
        VarInList = the input list of values for a matrix
        NumRows = the number of rows
        NumCols = the nubmer of columns
    
    Return:
    
        MatrixList = the list in matrix format.
    
    """
    # parameters
    # local variables.
    MatrixList = list()                 # the return list
    RowList = list()                    # the list for the row
    ListIndex = 0                       # the list index
    # start of function
    for ThisRow in range( NumRows ):
        RowList = list()
        for ThisCol in range( NumCols ):
            RowList.append( VarInList[ ListIndex ] )
            ListIndex = ListIndex + 1
        # have all the columns in so append the row list
        MatrixList.append( RowList )
    # end of the by row for
    return MatrixList

def ConvertInListToLookup( VarInList, NumDim, HdrLen, Dimensions ):
    """
    Convenience function which converts a list (vector format) to a lookup
    table formatted in Python structures for passing to a custom module or
    implementation. The dictionary structure is used to store the lookup
    table for passing to python. The dictionary keys are module globals.
    
    Arguments:
    
        VarInList = the input list of values for a lookup table
        NumDim = the number of dimensions for the lookup table.
        HdrLen = the number of items in the header
        Dimensions = the number of rows if 1D or a list with rows, cols if
                        2D.
    
    Return:
    
        LUDict = the lookup table Python dictionary
    
    """
    global LUTABLE_ROW_KEY, LUTABLE_COL_KEY, LUTABLE_VALUES_KEY
    global LUTABLE_DIMS_KEY
    # local variables
    ProcessList = list()        # the list with table values.
    NumRows = 0                 # the number of rows
    NumCols = 0                 # the number of columns
    LUDict = {}                 # the lookup table dictionary
    RowList = list()            # the lookup table row list
    ColList = list()            # the lookup table column list
    ValueList = list()          # the lookup table value list
    ValRowList = list()         # the row of values list for 2D
    CurrentIndex = 0            # the current index.
    # first get the list to process
    ProcessList = VarInList[HdrLen:]
    if NumDim == 1:
        NumRows = Dimensions
        # get the row values
        for ThisRow in range( NumRows ):
            RowList.append( ProcessList[ CurrentIndex ] )
            CurrentIndex = CurrentIndex + 1
        # get the dependent values
        for ThisRow in range( NumRows ):
            ValueList.append( ProcessList[ CurrentIndex ] )
            CurrentIndex = CurrentIndex + 1
        # set the dictionary values
        LUDict[ LUTABLE_DIMS_KEY ] = NumDim
        LUDict[ LUTABLE_ROW_KEY ] = RowList
        LUDict[ LUTABLE_VALUES_KEY ] = ValueList
    elif NumDim == 2:
        NumRows = Dimensions[0]
        NumCols = Dimensions[1]
        # get the row values
        for ThisRow in range( NumRows ):
            RowList.append( ProcessList[ CurrentIndex ] )
            CurrentIndex = CurrentIndex + 1
        # get the column values
        for ThisCol in range( NumCols ):
            ColList.append( ProcessList[ CurrentIndex ] )
            CurrentIndex = CurrentIndex + 1
        # get the dependent values
        for ThisRow in range( NumRows ):
            ValRowList = []
            for ThisCol in range( NumCols ):
                ValRowList.append( ProcessList[ CurrentIndex ] )
                CurrentIndex = CurrentIndex + 1
            ValueList.append( ValRowList )            
        # set the dictionary values
        LUDict[ LUTABLE_DIMS_KEY ] = NumDim
        LUDict[ LUTABLE_ROW_KEY ] = RowList
        LUDict[ LUTABLE_COL_KEY ] = ColList
        LUDict[ LUTABLE_VALUES_KEY ] = ValueList
    # end of the by dimension if
    return LUDict

def ConvertInListToTS( VarInList, HdrLen, NumIndexes ):
    """
    Convenience function which converts a list (vector format) to a time
    series. It will check to see whether we want a calendar based or elapsed
    time version. Calendar based means that the input values are Julian
    days while elapsed time means that is in seconds. 
    
    The return list has a list of [ Time, Value ] for each of the indexes. The
    time portion will be a datetime time value. If it is a calendar input 
    then the datetime value will be an actual datetime object. If it is
    elapsed time, then it will be a timedelta object.
    
    See the Python Standard Library Chpt 8 for details
        https://docs.python.org/2/library/datetime.html
        
    Arguments:
    
        VarInList = the input list of values for a lookup table
        HdrLen = the number of items in the header
        NumIndexes = the number of time indexes.
    
    Return:
    
        TSList = The time series list
    
    """
    # globals
    global ELAPSED_TIME, CALENDAR_TIME, GS_START_YEAR, GS_START_MONTH
    global GS_START_DAY, GS_START_HOUR, GS_TIMESERIES_TYPE_IND
    # local imports
    import datetime as dt
    from math import floor
    # local parameters.
    FuncName = "ConvertInListToTS"
    # DateTime version of start of GoldSim Julian epoch
    GSStartDT = dt.datetime( GS_START_YEAR, GS_START_MONTH, GS_START_DAY, 
                             GS_START_HOUR, 0 ) 
    SecondsInDay = 24.0 * 60.0 * 60.0  # seconds in a day
    # local variables
    ThisType = -1               # the type of this time series
    ProcessList = list()        # the list with table values.
    TSList = list()             # the return list
    TimeList = list()           # the list of the times
    ValueList = list()          # the list of the values
    DateVal = None              # the current delta value
    NumDays = 0                 # integer number of days
    NumDaysF = 0                # float number of days
    NumSecs = 0.0               # the number of seconds
    # first determine the type.
    ThisType = int( VarInList[ GS_TIMESERIES_TYPE_IND ] )
    # then get the list to process
    ProcessList = VarInList[HdrLen:]
    # get the Time and Value portions
    TimeList = ProcessList[:NumIndexes]
    ValueList = ProcessList[NumIndexes:]
    # now process by type and time
    for ThisInd in range( NumIndexes ):
        if ThisType == ELAPSED_TIME:
            if TimeList[ ThisInd ] >= SecondsInDay:
                NumDays = floor( TimeList[ ThisInd ] / SecondsInDay )
                NumSecs = TimeList[ ThisInd ] - ( NumDays * SecondsInDay )
            else:
                NumDays = 0
                NumSecs = TimeList[ ThisInd ]
            TSList.append( [ dt.timedelta( NumDays, NumSecs ), 
                             ValueList[ ThisInd ] ] )
        elif ThisType == CALENDAR_TIME:
            NumDaysF = TimeList[ ThisInd ] / SecondsInDay
            DateVal = GSStartDT + dt.timedelta( NumDaysF )
            TSList.append( [ DateVal, ValueList[ ThisInd ] ] )
        else:
            with open( CImp.LOG_FILE_NAME, 'a', 0 ) as LogFID:
                LogFID.write( "Invalid time type of %d in function %s.\n" % 
                              ( ThisType, FuncName ) )
            # end of with file closed
        # end of if
    # end of for loop.
    return TSList

def CreateLookupList( LUDict, HdrLen ):
    """
    Convenience function which converts the lookup table dictionary which is
    used to interface with the custom Python module to a list of float
    values in GoldSim's lookup table format.
    
    Arguments:
    
        LUDict = the dictionary structure for a lookup table
        HdrLen = the number of items in the header
    
    Return:
    
        LUTList = The lookup table list.
    
    """
    # globals
    global LUTABLE_ROW_KEY, LUTABLE_COL_KEY, LUTABLE_VALUES_KEY
    global LUTABLE_DIMS_KEY
    # local variables
    NumDim = 0                  # the number of dimensions
    NumRows = 0                 # the number of rows
    NumCols = 0                 # the number of columns
    RowList = list()            # the lookup table row list
    ColList = list()            # the lookup table column list
    ValueList = list()          # the lookup table value list
    LUTList = list()            # the return list.
    # first get the dimensions
    NumDim = LUDict[ LUTABLE_DIMS_KEY ]
    # do the list by dimensions
    if NumDim == 1:
        RowList = LUDict[ LUTABLE_ROW_KEY ]
        ValueList = LUDict[ LUTABLE_VALUES_KEY ]
        NumRows = len( RowList )
        # now write the header
        for ThisRow in range( HdrLen ):
            if ThisRow == 0:
                # number of dimensions
                LUTList.append( float( NumDim ) )
            elif ThisRow == 1:
                # the number of rows.
                LUTList.append( float( NumRows ) )
        # end of the header for
        # do the row values
        for ThisRow in range( NumRows ):
            LUTList.append( float( RowList[ ThisRow ] ) )
        # go through again and do the dependent values.
        for ThisRow in range( NumRows ):
            LUTList.append( float( ValueList[ ThisRow ] ) )
        # end of for
    elif NumDim == 2:
        RowList = LUDict[ LUTABLE_ROW_KEY ]
        ColList = LUDict[ LUTABLE_COL_KEY ]
        ValueList = LUDict[ LUTABLE_VALUES_KEY ]
        NumRows = len( RowList )
        NumCols = len( ColList )
        # now write the header
        for ThisRow in range( HdrLen ):
            if ThisRow == 0:
                # number of dimensions
                LUTList.append( float( NumDim ) )
            elif ThisRow == 1:
                # the number of columns.
                LUTList.append( float( NumRows ) )
            elif ThisRow == 2:
                # the number of rows.
                LUTList.append( float( NumCols ) )
        # end of the header for
        # do the row values
        for ThisRow in range( NumRows ):
            LUTList.append( float( RowList[ ThisRow ] ) )
        # do the column values
        for ThisCol in range( NumCols ):
            LUTList.append( float( ColList[ ThisCol ] ) )
        # do the dependent values.
        for ThisRow in range( NumRows ):
            for ThisCol in range( NumCols ):
                LUTList.append( float( ValueList[ ThisRow ][ ThisCol ] ) )
    # end of the by dimension if
    return LUTList

def CreateTSList( ValueList, NumSeries, NumSeriesPnts, TSType ):
    """
    Create a time series list in the GoldSim required format from a list of
    [DateTime, Values]
    
    Arguments:
    
        ValueList = the time series values in Python list [date, value] format
        NumSeries = the number of time series
        NumSeriesPnts = the number of indexes in the time series.
        TSType = the time series type 0 for elapsed 1 for calendar
    
    Return:
        
        List for the time series
    
    From the GoldSim manual (vol 2, p. 1039 the time series format is as
    follows:
    
    Time Series Definitions
    External functions can also read and return Time Series Definition. A Time
    Series Definition consists of the following specific sequence of values.
    1. The number 20 (this informs GoldSim that this is a Time Series)
    2. The number -3 (this is a format number that infoms GoldSim what
        version of the time series format is expected)
    3. Calendar-baed index: 0 if elapsed time; 1 if dates
    4. An index (0,1,2,3) indicating what the data represents (0=instantaneous
        value, 1=constant value over the next time interval, 2=change over the
        next time interval, 3=discrete change)
    5. The number of rows (0 for scalar time series)
    6. The number of columns (0 for scalar and vector time series)
    7. Number of series
    8. For each series, the following is repeated:
        o The total number of time points in the series
        o Time point 1, Time point 2, …, Time point n
    
    The structure of the remainder of the file depends on whether the Time
    Series Definition represents a scalar, a vector, or a matrix.
    
    For a scalar, the next sequence of values is as follows:
        o Value 1[time point 1], Value 2[time point 2], …, Value[time point n]
    
    For a vector, the next sequence of values is as follows:
        o Value[row1, time point 1], Value[row1, time point 2], …,
                Value[row1, time point n]
        o Value[row2, time point 1], Value[row2, time point 2], …,
                Value[row2, time point n]
        o …
        o Value[rowr, time point 1], Value[rowr, time point 2], …,
            Value[rowr, time point n]

    For a matrix, the next sequence of values is as follows:
        o Value[row1, column1, time point 1], Value[row1, column1, time
                point 2], …, Value[row1, column1, time point n]
        o Value[row1, column2, time point 1], Value[row1, column2, time
                point 2], …, Value[row1, column2, time point n]
        o …
        o Value[row1, columnc, time point 1], Value[row1, columnc, time
                point 2], …, Value[row1, columnc, time point n]
        o .
    
    """
    # imports
    import datetime as dt
    # globals
    global TIME_SERIES_EXTRA, ELAPSED_TIME, CALENDAR_TIME
    global GS_START_YEAR, GS_START_MONTH, GS_START_DAY, GS_START_HOUR
    global GS_TIMESERIES_TYPE_IND
    # local parameters
    # DateTime version of start of GoldSim Julian epoch
    GSStartDT = dt.datetime( GS_START_YEAR, GS_START_MONTH, GS_START_DAY, 
                             GS_START_HOUR, 0 ) 
    TSTypeDef = float( 20 )     # Value for header line 1
    TSFormatNum = float( -3 )   # Value for header line 2
    TSTypeInd = float( 0 )      # Value for header line 4
    TSNumRows = float( 0 )      # Value for header line 5
    TSNumCols = float( 0 )      # Value for header line 6
    # local variables
    RetList = list()            # the list to return
    TimeFloat = 0.0             # the current time value
    TimeDiff = None             # time delta object
    # First do the header values.
    for IndCnt in range( TIME_SERIES_EXTRA ):
        if IndCnt == 0:
            RetList.append( TSTypeDef )
        elif IndCnt == 1:
            RetList.append( TSFormatNum )
        elif IndCnt == GS_TIMESERIES_TYPE_IND:
            RetList.append( float( TSType ) )
        elif IndCnt == 3:
            RetList.append( TSTypeInd )
        elif IndCnt == 4:
            RetList.append( TSNumRows )
        elif IndCnt == 5:
            RetList.append( TSNumCols )
        elif IndCnt == 6:
            RetList.append( float( NumSeries ) )
        elif IndCnt == 7:
            RetList.append( float( NumSeriesPnts ) )
    # next do the time values
    for IndCnt in range( NumSeriesPnts ):
        if TSType == ELAPSED_TIME:
            TimeFloat = float ( (ValueList[IndCnt][0]).total_seconds() )
        elif TSType == CALENDAR_TIME:
            TimeDiff = ValueList[IndCnt][0] - GSStartDT
            TimeFloat = TimeDiff.total_seconds()
        RetList.append( TimeFloat )
    # finally do the values
    for IndCnt in range( NumSeriesPnts ):
        RetList.append( float( ValueList[IndCnt][1] ) )
    # done so return
    return RetList

def InputEcho( InputList, VarDefinition, Indexes, PyInList ):
    """
    Echo out some stuff to a text file for troubleshooting the inputs.
    
    Arguments:
    
        InputList = the input list from GoldSim external element
        VarDefinition = the definition from this file for inputs
        Indexes = the calculated indexes to break up the variables
        PyInList = the input list of variables in "Python" formats
    
    Return:
        
        None
        
    """
    # globals
    global VAR_DESC_IND, VAR_TYPE_IND, VAR_CNT_IND
    global ELAPSED_TIME, CALENDAR_TIME, VAR_TSTYPE_IND, LUTABLE_ROW_KEY
    global LUTABLE_COL_KEY, LUTABLE_VALUES_KEY, LUTABLE_DIMS_KEY, DBL_TYPER
    global VECTOR_TYPER, MATRIX_TYPER, TS_TYPER, LUTABLE_1D_TYPER
    global LUTABLE_2D_TYPER
    # local parameters
    OutFileName = "Echo_Inputs.csv"     # output file name
    Echo_Time_Fmt = "%x %X"             # datetime string format for output
    # local variables
    VarCnt = 0          # the variable counter
    CurrentType = ""    # the current variable type
    CurrentDesc = ""    # the current description
    NumRows = 0         # The current number of values to output
    NumCols = 0         # the number of columns to ouput
    TSTyper = 0         # the time series type
    #RowList = list()    # the row list for the lookup tables
    #ColList = list()    # the column list for the lookup tables
    ValueList = list()  # the value list for the lookup tables
    # start by outputting the variable information
    with open( OutFileName, 'w', 0 ) as OutFID:
        OutFID.write( "Input variable definition:\n\n" )
        OutFID.write( "Index, Length, Type, Description, Time Series Type \n" )
        for ThisVar in VarDefinition:
            CurrentType = str( ThisVar[ VAR_TYPE_IND ] )
            CurrentDesc = str( ThisVar[ VAR_DESC_IND ] )
            if CurrentType == TS_TYPER:
                OutFID.write( "%d, %d, %s, %s, %d,\n" % 
                    ( VarCnt + 1, ThisVar[VAR_CNT_IND], CurrentType, 
                      CurrentDesc, ThisVar[ VAR_TSTYPE_IND ] ) )
            elif CurrentType == MATRIX_TYPER:
                RCListStr = "\"[ %d, %d ]\"" % ( ThisVar[VAR_CNT_IND][0],
                                                 ThisVar[VAR_CNT_IND][1] )
                OutFID.write( "%d, %s, %s, %s\n" % ( VarCnt + 1, RCListStr, 
                                            CurrentType, CurrentDesc ) )
            else:
                OutFID.write( "%d, %d, %s, %s,\n" % ( VarCnt + 1, 
                            ThisVar[VAR_CNT_IND], CurrentType, CurrentDesc ) )
            VarCnt = VarCnt + 1
        OutFID.write("\n\n\n")
        # now do the list of inargs 
        VarCnt = 0
        OutFID.write("GoldSim inargs:\n\n")
        OutFID.write("Index, Value \n")
        for ThisVar in InputList:
            OutFID.write("%d, %g \n" % ( (VarCnt + 1), ThisVar ) )
            VarCnt = VarCnt + 1 
        OutFID.write("\n\n\n")
        # finally the python formatted list
        VarCnt = 0
        OutFID.write("Python-format list of input variables\n\n")
        for ThisVar in VarDefinition:
            CurrentType = str( ThisVar[ VAR_TYPE_IND ] )
            CurrentDesc = str( ThisVar[ VAR_DESC_IND ] )
            OutFID.write("%d, Type = %s, Desc = %s \n" % 
                            ( (VarCnt + 1), CurrentType, CurrentDesc ) )
            if CurrentType == DBL_TYPER:
                OutFID.write( "%g,\n\n" % PyInList[ VarCnt ] )
            elif CurrentType == VECTOR_TYPER:
                NumRows = int( ThisVar[ VAR_CNT_IND ] )
                ValueList = PyInList[ VarCnt ]
                for ThisRow in range( NumRows ):
                    OutFID.write( "%g,\n" % ValueList[ ThisRow ] )
                OutFID.write( "\n" )
            elif CurrentType == MATRIX_TYPER:
                NumRows = int( ThisVar[ VAR_CNT_IND ][0] )
                NumCols = int( ThisVar[ VAR_CNT_IND ][1] )
                ValueList = PyInList[ VarCnt ]
                for ThisRow in range( NumRows ):
                    for ThisCol in range( NumCols ):
                        OutFID.write( " %g," % 
                                            ValueList[ ThisRow ][ ThisCol ] ) 
                    OutFID.write( "\n" )
                OutFID.write( "\n" )
            #elif CurrentType == LUTABLE_1D_TYPER:
                # not currently supported ...
                #RowList = PyInList[ VarCnt ][ LUTABLE_ROW_KEY ]
                #ValueList = PyInList[ VarCnt ][ LUTABLE_VALUES_KEY ] 
                #NumRows = len( RowList )
                #OutFID.write( "Row Value, Dependent Value \n" )
                #for ThisRow in range( NumRows ):
                #    OutFID.write( "%g, %g,\n" % 
                #                ( RowList[ ThisRow ], ValueList[ ThisRow ] ) )
                #OutFID.write( "\n" )
            #elif CurrentType == LUTABLE_2D_TYPER:
                # not currently supported
                #RowList = PyInList[ VarCnt ][ LUTABLE_ROW_KEY ]
                #ColList = PyInList[ VarCnt ][ LUTABLE_COL_KEY ]
                #ValueList = PyInList[ VarCnt ][ LUTABLE_VALUES_KEY ] 
                #NumRows = len( RowList )
                #NumCols = len( ColList )
                #OutFID.write("Row\Column Values" )
                #for ThisCol in range( NumCols ):
                #    OutFID.write(", %g" % ColList[ ThisCol ] )
                #OutFID.write("\n")
                #for ThisRow in range( NumRows ):
                #    OutFID.write("%g" % RowList[ ThisRow ] )
                #    for ThisCol in range( NumCols ):
                #        OutFID.write(", %g" % ValueList[ ThisRow ][ ThisCol ] )
                #    OutFID.write("\n")
                #OutFID.write("\n")
            elif CurrentType == TS_TYPER:
                NumRows = int( ThisVar[ VAR_CNT_IND ] )
                TSTyper = int( ThisVar[ VAR_TSTYPE_IND ] )
                ValueList = PyInList[ VarCnt ]
                OutFID.write("Time, Value \n")
                for ThisRow in range( NumRows ):
                    if TSTyper == ELAPSED_TIME:
                        OutFID.write( "%g," % 
                                        ValueList[ThisRow][0].total_seconds() ) 
                    elif TSTyper == CALENDAR_TIME:
                        OutFID.write( "%s," % 
                                ValueList[ThisRow][0].strftime( Echo_Time_Fmt ) )
                    OutFID.write("%g \n" % PyInList[VarCnt][ThisRow][1])
                OutFID.write( "\n" )
            VarCnt = VarCnt + 1
    # end of with block file closed.
    return

def OutputEcho( OutputList, VarDefinition, PyOutList ):
    """
    Echo out some stuff to a text file for troubleshooting the outputs.
    
    Arguments:
    
        OutputList = the output list for the GoldSim external element.
        VarDefinition = the definition from this file for outputs. Should be
                        RET_VAR_LIST
        PyOutList = the list of "Python" structures of return values 
                        corresponding to RET_VAR_LIST
    
    Return:
        
        None
        
    """
    # globals
    global VAR_DESC_IND, VAR_TYPE_IND, VAR_CNT_IND, ELAPSED_TIME
    global CALENDAR_TIME, VAR_TSTYPE_IND, LUTABLE_ROW_KEY, LUTABLE_COL_KEY
    global LUTABLE_VALUES_KEY, LUTABLE_DIMS_KEY, DBL_TYPER, VECTOR_TYPER 
    global MATRIX_TYPER, TS_TYPER, LUTABLE_1D_TYPER, LUTABLE_2D_TYPER
    # local parameters
    OutFileName = "Echo_Outputs.csv"     # output file name
    Echo_Time_Fmt = "%x %X"             # datetime string format for output
    # parameters
    # local variables
    VarCnt = 0          # the variable counter
    CurrentType = ""    # the current variable type
    CurrentDesc = ""    # the current description
    NumRows = 0         # The current number of values to output
    NumCols = 0         # the number of columns to ouput
    TSTyper = 0         # the time series type
    RowList = list()    # the row list for the lookup tables
    ColList = list()    # the column list for the lookup tables
    ValueList = list()  # the value list for the lookup tables
    # now output
    with open( OutFileName, 'w', 0 ) as OutFID:
        # first output the variable definition from RET_VAR_LIST
        OutFID.write( "Output variable definition:\n\n" )
        OutFID.write( "Index, Length, Type, Description, Time Series Type \n" )
        for ThisVar in VarDefinition:
            CurrentType = str( ThisVar[ VAR_TYPE_IND ] )
            CurrentDesc = str( ThisVar[ VAR_DESC_IND ] )
            if CurrentType == TS_TYPER:
                OutFID.write( "%d, %d, %s, %s, %d\n" % 
                    ( VarCnt + 1, ThisVar[VAR_CNT_IND], CurrentType, 
                      CurrentDesc, ThisVar[ VAR_TSTYPE_IND ] ) )
            elif CurrentType == LUTABLE_2D_TYPER:
                RCListStr = "\"[ %d, %d ]\"" % ( ThisVar[VAR_CNT_IND][0],
                                                 ThisVar[VAR_CNT_IND][1] )
                OutFID.write( "%d, %s, %s, %s\n" % ( VarCnt + 1, RCListStr, 
                                            CurrentType, CurrentDesc ) )
            elif CurrentType == MATRIX_TYPER:
                RCListStr = "\"[ %d, %d ]\"" % ( ThisVar[VAR_CNT_IND][0],
                                                 ThisVar[VAR_CNT_IND][1] )
                OutFID.write( "%d, %s, %s, %s\n" % ( VarCnt + 1, RCListStr, 
                                            CurrentType, CurrentDesc ) )
            else:
                OutFID.write( "%d, %d, %s, %s\n" % ( VarCnt + 1, 
                            ThisVar[VAR_CNT_IND], CurrentType, CurrentDesc ) )
            VarCnt = VarCnt + 1
        OutFID.write("\n\n\n")
        # next do the Python structures returned from CImp
        VarCnt = 0
        OutFID.write("Python-format list of Output variables\n\n")
        for ThisVar in VarDefinition:
            CurrentType = str( ThisVar[ VAR_TYPE_IND ] )
            CurrentDesc = str( ThisVar[ VAR_DESC_IND ] )
            OutFID.write("%d, Type = %s, Desc = %s \n" % 
                            ( (VarCnt + 1), CurrentType, CurrentDesc ) )
            if CurrentType == DBL_TYPER:
                OutFID.write( "%g,\n\n" % PyOutList[ VarCnt ][ 0 ] )
            elif CurrentType == VECTOR_TYPER:
                NumRows = int( ThisVar[ VAR_CNT_IND ] )
                ValueList = PyOutList[ VarCnt ]
                for ThisRow in range( NumRows ):
                    OutFID.write( "%g,\n" % ValueList[ ThisRow ] )
                OutFID.write( "\n" )
            elif CurrentType == MATRIX_TYPER:
                NumRows = int( ThisVar[ VAR_CNT_IND ][0] )
                NumCols = int( ThisVar[ VAR_CNT_IND ][1] )
                ValueList = PyOutList[ VarCnt ]
                for ThisRow in range( NumRows ):
                    for ThisCol in range( NumCols ):
                        OutFID.write( " %g," % 
                                            ValueList[ ThisRow ][ ThisCol ] ) 
                    OutFID.write( "\n" )
                OutFID.write( "\n" )
            elif CurrentType == LUTABLE_1D_TYPER:
                RowList = PyOutList[ VarCnt ][ LUTABLE_ROW_KEY ]
                ValueList = PyOutList[ VarCnt ][ LUTABLE_VALUES_KEY ] 
                NumRows = len( RowList )
                OutFID.write( "Row Value, Dependent Value \n" )
                for ThisRow in range( NumRows ):
                    OutFID.write( "%g, %g,\n" % 
                                ( RowList[ ThisRow ], ValueList[ ThisRow ] ) )
                OutFID.write( "\n" )
            elif CurrentType == LUTABLE_2D_TYPER:
                RowList = PyOutList[ VarCnt ][ LUTABLE_ROW_KEY ]
                ColList = PyOutList[ VarCnt ][ LUTABLE_COL_KEY ]
                ValueList = PyOutList[ VarCnt ][ LUTABLE_VALUES_KEY ] 
                NumRows = len( RowList )
                NumCols = len( ColList )
                OutFID.write("Row\Column Values" )
                for ThisCol in range( NumCols ):
                    OutFID.write(", %g" % ColList[ ThisCol ] )
                OutFID.write("\n")
                for ThisRow in range( NumRows ):
                    OutFID.write("%g" % RowList[ ThisRow ] )
                    for ThisCol in range( NumCols ):
                        OutFID.write(", %g" % ValueList[ ThisRow ][ ThisCol ] )
                    OutFID.write("\n")
                OutFID.write("\n")
            elif CurrentType == TS_TYPER:
                NumRows = int( ThisVar[ VAR_CNT_IND ] )
                TSTyper = int( ThisVar[ VAR_TSTYPE_IND ] )
                ValueList = PyOutList[ VarCnt ]
                OutFID.write("Time, Value \n")
                for ThisList in ValueList:
                    if TSTyper == ELAPSED_TIME:
                        DecimalSeconds = float( ThisList[0].total_seconds() )
                        OutFID.write( "%g," % DecimalSeconds ) 
                    elif TSTyper == CALENDAR_TIME:
                        DateStr = "%s" % ThisList[0].strftime( Echo_Time_Fmt ) 
                        OutFID.write( "%s," % DateStr )
                    OutFID.write("%g \n" % ThisList[1] )
                OutFID.write( "\n" )
            VarCnt = VarCnt + 1
        OutFID.write("\n\n\n")
        # next do the list that will actually go back to GoldSim.
        VarCnt = 0
        OutFID.write( "Sent to GoldSim: \n\n" )
        OutFID.write( "Index, Value \n" )
        # echo out the actual list
        for ThisVar in OutputList:
            OutFID.write("%d, %g \n" % ( (VarCnt + 1), ThisVar ) )
            VarCnt = VarCnt + 1 
    # end of with block file closed.
    return

def CustomCalculations( InputList, NumToReturn ):
    """
    Wrapper function which calls whatever functions are required to do the
    calculations for this custom dll. This wrapper function expects to 
    receive a list, of float values, in the GoldSim dll formats specified
    in the GoldSim manual appendix. It also expects to receive the number of
    indexes in the return list which GoldSim is expecting. 
    
    This function then processes the InputList into the "Python" structure
    format for each variable type defined in IN_VAR_LIST. These "Python" 
    structures are appended to a list, in order corresponding to IN_VAR_LIST,
    and this input list of "Python" structures is passed to custom Python
    code in the CImp module (Custom Implementation module).
    
    This function expects to receive back from the CImp module function, a 
    list of "Python" structures in order and format corresponding to 
    RET_VAR_LIST. It will then take these "Python" structures and create a
    list of float values to send back to CustomPython.pyx where this list
    of floats will be put into the outargs array. The ReturnList length
    is checked against NumToReturn here and in CustomPython.pyx.
    
    It is the user's responsibility to ensure that the the custom 
    implementation in the CImp module can accept the list of Python structures
    corresponding to IN_VAR_LIST and that it returns a list of Python
    structures corresponding to RET_VAR_LIST with the appropriate entries
    so that the GoldSim-structuctured list of float (includes header values)
    will have the required number of return values (NumToReturn).
    
    If DEBUG_LEVEL == 1, this function will echod the inputs and outputs to
    text files for testing and debugging.
        
    Arguments:
    
        InputList = the list of floats which is the input array from GoldSim.
        NumToReturn = the total number of indices to return in the list
                        which goes back to CustomPython.pyx.
    
    Return:
    
        ReturnList = list of floats with NumToReturn indexes which will be
                        written to the output arguments array.
    
    """
    # globals
    global IN_VAR_LIST, RET_VAR_LIST, VAR_TYPE_IND, VAR_CNT_IND
    global TIME_SERIES_EXTRA, VAR_TSTYPE_IND, DEBUG_LEVEL
    # parameters
    FuncName = "CustomCalculations"
    # python variables
    NumOutputVars = len( RET_VAR_LIST ) # the number of input variables.
    CurrentType = ""                    # the type of the current variable.
    VarInList = list()                  # the current variable portion of input
    CurrentIndexes = 0                  # the current number of indexes expected
    StartIndex = 0                      # the starting index for the input.
    InputScalar = 0.0                   # the input scalar
    InputVector = list()                # the input vector
    InputMatrix = list()                # the input matrix
    InputTS = list()                    # the input time series, if needed
    OutputScalar = 0.0                  # the output scalar
    OutputVector = list()               # the output vector
    OutputMatrix = list()               # the output matrix
    Output1D = list()                   # the 1D lookup table output
    Output2D = list()                   # the 1D lookup table output
    OutputTS = list()                   # the output time series, if needed
    NumRows = 0                         # the number of rows if needed
    NumCols = 0                         # the number of columns if needed
    ReturnList = list()                 # the list of return values
    VarIndex = 0                        # the index for the variable working on
    TstLength = 0                       # the testing length for the return
    TstIndexes = list()                 # the indexes for testing
    PyInputList = list()                # inputs in Python list format
    TSTyper = 0                         # the time series type to use
    # start of function.
    # go through the input variable definition list IN_VAR_LIST and the
    # list of input arguments and extract the actual input values for use
    # in the custom python module. There is much stuff here in "stub" format
    # to provide a template for customization.
    TstIndexes.append( 0 )
    for ThisList in IN_VAR_LIST:
        CurrentType = str( ThisList[ VAR_TYPE_IND ] )
        if CurrentType == DBL_TYPER:
            CurrentIndexes = int( ThisList[ VAR_CNT_IND ] )
            VarInList = InputList[ StartIndex:( StartIndex + CurrentIndexes ) ]
            InputScalar = VarInList[0]
            PyInputList.append( InputScalar )
        elif CurrentType == VECTOR_TYPER:
            CurrentIndexes = int( ThisList[ VAR_CNT_IND ] )
            VarInList = InputList[ StartIndex:( StartIndex + CurrentIndexes ) ]
            InputVector = VarInList
            PyInputList.append( InputVector )
        elif CurrentType == MATRIX_TYPER:
            NumRows = int( ThisList[ VAR_CNT_IND ][0] )
            NumCols = int( ThisList[ VAR_CNT_IND ][1] )
            CurrentIndexes = NumRows * NumCols
            VarInList = InputList[ StartIndex:( StartIndex + CurrentIndexes ) ]
            InputMatrix = ConvertInListToMatrix( VarInList, NumRows, NumCols )
            PyInputList.append( InputMatrix )
        elif CurrentType == LUTABLE_1D_TYPER:
            # Lookup table not supported for input
            with open( CImp.LOG_FILE_NAME, 'a', 0 ) as LogFID:
                LogFID.write( "Data type %s not supported for inputs by " \
                              "GoldSim.\n" % CurrentType ) 
            return [-1]
        elif CurrentType == LUTABLE_2D_TYPER:
            # Lookup table not supported for input
            with open( CImp.LOG_FILE_NAME, 'a', 0 ) as LogFID:
                LogFID.write( "Data type %s not supported for inputs by " \
                              "GoldSim.\n" % CurrentType ) 
            return [-1]
        elif CurrentType == TS_TYPER:
            CurrentIndexes = int( TIME_SERIES_EXTRA ) + ( 2 * 
                                            int( ThisList[ VAR_CNT_IND ] ) )
            VarInList = InputList[ StartIndex:( StartIndex + CurrentIndexes ) ]
            InputTS = ConvertInListToTS( VarInList, TIME_SERIES_EXTRA,
                                         ThisList[ VAR_CNT_IND ] )
            PyInputList.append( InputTS )
        else:
            # this is an error for an undefined type.
            with open( CImp.LOG_FILE_NAME, 'a', 0 ) as LogFID:
                LogFID.write( "Found invalid variable type of %s in " \
                              "function %s.\n" % 
                              ( CurrentType, FuncName ) )
            # log file closed
            return [-1]
        # end switch
        StartIndex = StartIndex + CurrentIndexes
        TstIndexes.append( StartIndex )
    # end of the input variable for
    # Input debug 
    if DEBUG_LEVEL == 1:
        InputEcho( InputList, IN_VAR_LIST, TstIndexes, PyInputList )
    # now can call the custom function.
    # in our case know or designed for a single scalar input.
    RetVarList = CImp.MyCustomCalculations( PyInputList )
    # do a check on the returned list
    if len( RetVarList ) != NumOutputVars:
        # this is an error.
        with open( CImp.LOG_FILE_NAME, 'a', 0 ) as LogFID:
            LogFID.write( "Received %d variables back from processing in " \
                              "function %s. Expected %d variables.\n" % 
                              ( len( RetVarList ), FuncName, NumOutputVars) )
        # log file closed
        return [-1]
    # now process the inputs to create a list in return format.
    StartIndex = 0
    for ThisList in RET_VAR_LIST:
        CurrentType = str( ThisList[ VAR_TYPE_IND ] )
        if CurrentType == DBL_TYPER:
            OutputScalar = float( RetVarList[ VarIndex ][ 0 ] )
            ReturnList.append( OutputScalar )
        elif CurrentType == VECTOR_TYPER:
            CurrentIndexes = int( ThisList[ VAR_CNT_IND ] )
            OutputVector = RetVarList[ VarIndex ]
            for ThisValue in OutputVector:
                ReturnList.append( float( ThisValue ) )
        elif CurrentType == MATRIX_TYPER:
            NumRows = int( ThisList[ VAR_CNT_IND ][0] )
            NumCols = int( ThisList[ VAR_CNT_IND ][1] )
            OutputMatrix = RetVarList[ VarIndex ]
            for ThisRow in range( NumRows ):
                for ThisCol in range( NumCols ):
                    ReturnList.append( float( OutputMatrix[ ThisRow ][ ThisCol ] ) )
        elif CurrentType == LUTABLE_1D_TYPER:
            LUNumRet = RetLUTableHeaderCnt( 1, CImp.LOG_FILE_NAME )
            Output1D = CreateLookupList( RetVarList[ VarIndex ], LUNumRet )
            for ThisValue in Output1D:
                ReturnList.append( ThisValue )
        elif CurrentType == LUTABLE_2D_TYPER:
            LUNumRet = RetLUTableHeaderCnt( 2, CImp.LOG_FILE_NAME )
            Output2D = CreateLookupList( RetVarList[ VarIndex ], LUNumRet )
            for ThisValue in Output2D:
                ReturnList.append( ThisValue )
        elif CurrentType == TS_TYPER:
            NumRows = int( ThisList[ VAR_CNT_IND ] )
            TSTyper = int( ThisList[ VAR_TSTYPE_IND ] )
            OutputTS = CreateTSList( RetVarList[ VarIndex ], 1, NumRows, 
                                     TSTyper )
            for ThisValue in OutputTS:
                ReturnList.append( ThisValue )
        else:
            # this is an error for an undefined type.
            with open( CImp.LOG_FILE_NAME, 'a', 0 ) as LogFID:
                LogFID.write( "Found invalid variable type of %s in " \
                              "function %s.\n" % 
                              ( CurrentType, FuncName ) )
            # log file closed
            return [-1]
        # end switch
        VarIndex = VarIndex + 1
    # end of the input variable for
    TstLength = len( ReturnList )
    # some debugging
    if DEBUG_LEVEL == 1:
        OutputEcho( ReturnList, RET_VAR_LIST, RetVarList )
    # check
    if TstLength != NumToReturn:
        # this is an error.
        with open( CImp.LOG_FILE_NAME, 'a', 0 ) as LogFID:
            LogFID.write( "Created return list with wrong length. Return " \
                           "list has length %d. Needs to have length %d.\n" % \
                            ( TstLength, NumToReturn ) )
        # end of with block, file closed.
        return [-1]
    # some debugging.
    # if are here then is good and return the list.
    return ReturnList

def WrapUpStuff( ):
    """
    Pass through wrapper that calls whatever has been defined in the way of
    clean-up in the custom python module. In this case, it just writes a
    final log file entry and then exits.
    """
    CImp.WrapUpLogFile( CImp.LOG_FILE_NAME )
    return

def PythonInitializationError( ):
    """
    Python function to write an error to the log file.
    """
    with open( CImp.LOG_FILE_NAME, 'a', 0 ) as LogFID:
        LogFID.write("Python did not initialize correctly.\n" )
        LogFID.write("This is most likely due to an error in your Python code\n" )
        LogFID.write("which was triggered during the bytecode compilation\n" )
        LogFID.write("step which was triggered by an import statement.\n" )
        LogFID.write("Please use an if __name__ == \"__main__\": block \n" )
        LogFID.write("in your Python module to test and to ensure that it \n" )
        LogFID.write("runs without error.\n" )
    return
#EOF