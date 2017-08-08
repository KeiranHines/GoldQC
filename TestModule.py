# -*- coding: utf-8 -*-
"""
Python Module: TestModule.py
Created by: Nick Martin, GoldSim Technology Group
Creation Date: 23 May 2015
Last Edited: 25 May 2015

License: FreeBSD License (reproduced below)

Purpose:

Provides a rudimentary implementation of the CustomPython.dll linkage for
the GoldSim external element. Primarily confirms that pass the various
supported element type values in the right format.

The "required" functions to implement are:

SetStuffUp
WrapUpLogFile
MyCustomCalculations

The "required" parameters are:

CUSTOM_MODULE_VERSION
LOG_FILE_NAME

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
# Module level globals.
CUSTOM_MODULE_VERSION = 0.9         # module version --- REQUIRED
LOG_FILE_NAME = "TestLog.txt"       # log file name --- REQUIRED
#BAD_NAME = "
#===========================================================================
# functions
def SetStuffUp( ):
    """
    Required function from CustomModule.py. Does whatever is needed in terms
    of set-up. Here just writes the initial entry to the log file.
    
    Return:
    
        Integer status: 0 = good; 1 = bad
    
    """
    # globals
    global LOG_FILE_NAME
    # local imports
    import datetime as dt
    # start of function.
    with open( LOG_FILE_NAME, 'w', 0 ) as LogFID:
        LogFID.write( "Start TestModule.py script at %s.\n\n" % 
                        dt.datetime.now().strftime( "%x %H:%M" ) )
    # end of with block, file closed
    return 0

def WrapUpLogFile( LogFileName ):
    """
    Required wrap-up function. Just writes successful end to the log file.
    
    Arguments:
    
        LogFileName = the name for the log file.
    
    Return:
        none
        
    """
    # globals
    global LOG_FILE_NAME
    # local imports
    import datetime as dt
    # start of function.
    with open( LOG_FILE_NAME, 'a', 0 ) as LogFID:
        LogFID.write( "Successful end of TestModule.py script at %s.\n\n" % 
                        dt.datetime.now().strftime( "%x %H:%M" ) )
    # end of with block, file closed
    return

def MakeLookupTableFormat( RowList, ColList, ValueList ):
    """
    Convenience function which makes a "Python" structure lookup table 
    dictionary from the component lists.
    
    Arguments:
    
        RowList = the list of row values
        ColList = the list of column values
        ValueList = the values --- if 1D needs to be len( RowList ). If 2D
                    needs to have nested lists equal to number of rows.
                    Each nested list needs to have number of column items.
    
    Return:
    
        LUDict = the dictionary format of the lookup table.
    
    """
    # globals
    global LOG_FILE_NAME
    # imports
    from CustomModule import LUTABLE_DIMS_KEY, LUTABLE_ROW_KEY 
    from CustomModule import LUTABLE_COL_KEY, LUTABLE_VALUES_KEY
    # local parameters
    FuncName = "MakeLookupTableFormat"
    # local variables
    LUDict = {}             # the lookup table dictionary
    NumRows = 0             # the number of rows
    NumCols = 0             # the number of columns
    # start of function.
    # use ColList to determine the dimension
    NumCols = len( ColList )
    NumRows = len( RowList )
    # can test the number of items in the big value list
    if len( ValueList ) != NumRows:
        # this is an error.
        with open( LOG_FILE_NAME, 'a', 0 ) as LogFID:
            LogFID.write( "The value list in %s does not have the same " \
                            "length as the row list. Value list length %d " \
                            "and row list length %d.\n" % \
                            ( FuncName, len( ValueList ), NumRows ) )
        return LUDict
    if NumCols < 1:
        # this is 1D
        LUDict[ LUTABLE_DIMS_KEY ] = 1
        LUDict[ LUTABLE_ROW_KEY ] = RowList
        LUDict[ LUTABLE_VALUES_KEY ] = ValueList 
    else:
        # this is 2D
        for ThisList in ValueList:
            # check the length
            if len( ThisList ) != NumCols:
                # this is an error.
                with open( LOG_FILE_NAME, 'a', 0 ) as LogFID:
                    LogFID.write( "The nested value list in %s does not " \
                            "have the same number of columns as the column " \
                            "list. Value list columns or values %d and " \
                            "column list length %d.\n" % \
                            ( FuncName, len( ThisList ), NumCols ) )
                return LUDict
            # end of check
        # end of checking for
        LUDict[ LUTABLE_DIMS_KEY ] = 2
        LUDict[ LUTABLE_ROW_KEY ] = RowList
        LUDict[ LUTABLE_COL_KEY ] = ColList
        LUDict[ LUTABLE_VALUES_KEY ] = ValueList
    # return LUDict
    return LUDict

def ConvertElapsedtoCalendar( StartDays, ElapsedList ):
    """
    Convenience function to convert an elapsed time list to a calendar time
    list.
    
    Arguments:
    
        StartDays = decimal start days (this is from the GoldSim start date)
        ElapsedList = the "Python" elapsed time time series structure
    
    Return:
    
        CalendarList = the Elapsed time list converted to calendar time.
        
    """
    # imports
    import datetime as dt
    from CustomModule import GS_START_YEAR, GS_START_MONTH, GS_START_DAY
    from CustomModule import GS_START_HOUR
    # local parameters
    # DateTime version of start of GoldSim Julian epoch
    GSStartDT = dt.datetime( GS_START_YEAR, GS_START_MONTH, GS_START_DAY, 
                             GS_START_HOUR, 0 ) 
    # local variables
    StartDate = GSStartDT + dt.timedelta( StartDays )
    TimeList = list()       # the list to hold the time values
    DateList = list()       # the list to hold the date values
    ValueList = list()      # the value list.
    CalendarList = list()   # the calendar based time series list
    # start of function
    TimeList = [ x[0] for x in ElapsedList ]
    ValueList = [ x[1] for x in ElapsedList ]
    DateList = [ StartDate + x for x in TimeList ]
    # end of for so put the return list together
    CalendarList = [ [x,y] for x,y in zip( DateList, ValueList ) ]
    # return
    return CalendarList

def ConvertCalendarToElapsed( CalendarList ):
    """
    Convenience function to convert a calendar-based time series, "python"
    structure to an elapsed time based time series "python" structure. The
    calendar based tim
    
    Arguments:
        
        CalendarList
        
    Return:
        
        ElapsedList
    
    """
    # local variables
    TimeList = list()       # the list to hold the time values
    DateList = list()       # the list to hold the date values
    ValueList = list()      # the value list.
    ElapsedList = list()    # the elapsed time, time series list    
    # start
    DateList = [ x[0] for x in CalendarList ]
    ValueList = [ x[1] for x in CalendarList ] 
    FirstTime = DateList[0]     # first datetime
    # now create the elapsed times.
    TimeList = [ x - FirstTime for x in DateList ]
    # put the return list together
    ElapsedList = [ [x,y] for x,y in zip( TimeList, ValueList ) ]
    # return
    return ElapsedList

def MyCustomCalculations( PyInputList ):
    """
    Required wrapper function for either completing the custom calculations 
    or for calling other functions and modules to complete these calculations.
    
    Arguments:
    
        PyInputList = a list of the input values/parameters which has come
                        from the GoldSim external element via CustomModule.py.
    
    Return:
    
        ReturnList = list of the output values which needs to be in the format
                        expected by CustomModule.py.
    
    RET_VAR_LIST = [ [ 3, LUTABLE_1D_TYPER, "1D Lookup Table" ],
                 [ [4,4], MATRIX_TYPER, "Matrix" ],
                 [ 12, TS_TYPER, "Elapsed Time Series", ELAPSED_TIME ],
                 [ 1, DBL_TYPER, "Number of Inputs" ],
                 [ 12, TS_TYPER, "Calendar Time Series", CALENDAR_TIME ],
                 [ [4,3], LUTABLE_2D_TYPER, "2D Lookup Table" ],
                 [ 12, VECTOR_TYPER, "Vector" ],
                 [ 1, DBL_TYPER, "Number of Inputs" ] ]
    
    """
    # imports
    from CustomModule import RET_VAR_LIST 
    # local variables
    ReturnList = list()         # the list of return values.
    ListLen = 0                 # the list length
    ReturnLen = 0               # the return length
    ReturnVect = list()         # the return vector
    ReturnCalendar = list()     # the return calendar time, time series
    ReturnElapsed = list()      # the return elapsed time, time series
    #ListCnt = 0                 # the list counter
    # get the list length. This is the last return.
    ListLen = len( PyInputList )
    # this is the return for standalone script block which will only
    # have a list with length 1.
    if ListLen == 1:
        ReturnList.append( [ float( ListLen ) ] )
        return ReturnList
    # if the input list is longer than 1, then keep going for the
    #   example GoldSim model.
    ReturnLen = len( RET_VAR_LIST )
    # Now get the lookup tables ....
    # these are hard coded here.
    RowList = [ 1, 2, 3 ]
    ColList = []
    ValueList = [100.0, 200.0, 300.0 ]
    LUDict1D = MakeLookupTableFormat( RowList, ColList, ValueList )
    # next do the 2D lU table
    RowList = [ 1, 2, 3, 4 ]
    ColList = [ 1, 2, 3 ]
    ValueList = [ [ 1.0, 2.0, 6.0 ],
                  [ 2.0, 4.0, 12.0 ],
                  [ 3.0, 6.0, 18.0 ],
                  [ 4.0, 8.0, 24.0 ] ]
    LUDict2D = MakeLookupTableFormat( RowList, ColList, ValueList )
    # for the matrix to return, add the vector, index 3 as the last row
    # to the input matrix, input 2
    InVector = PyInputList[2]
    InMatrix = PyInputList[1]
    ReturnMat = InMatrix
    ReturnMat.append( InVector )
    # the return vector has 12 indices for the months of the year. The
    # input vector has 4 indices so do 3 of these appended with each one
    # multiplied by the vector multiplier input.
    for ThisIt in range( 3 ):
        for ThisInd in range( len( InVector ) ):
            ReturnVect.append( InVector[ ThisInd ] )
    # now do the time series.
    # use start time to convert the elapsed time to calendar time.
    DecimalStartTime = PyInputList[0]
    OriginalElapsedTime = PyInputList[5]
    ReturnCalendar = ConvertElapsedtoCalendar( DecimalStartTime, 
                                               OriginalElapsedTime )
    # then conver the calendar time to elapsed time and multiply by the
    # time series multiplier input.
    OriginalCalendarTime = PyInputList[4]
    TSMultiply = PyInputList[6]
    ReturnElapsed = ConvertCalendarToElapsed( OriginalCalendarTime )
    ReturnElapsed = [ [ x[0], ( TSMultiply * x[1] ) ] for x in ReturnElapsed ]
    # now have all the components so create the ReturnList by appending in
    # the specified order.
    ReturnList.append( LUDict1D )
    ReturnList.append( ReturnMat )
    ReturnList.append( ReturnElapsed )
    ReturnList.append( [ ListLen ] )
    ReturnList.append( ReturnCalendar )
    ReturnList.append( LUDict2D )
    ReturnList.append( ReturnVect )
    ReturnList.append( [ ReturnLen ] )
    # return
    return ReturnList

# Block to run as standalone script. This can be run from the command line
# using python TestModule.py. This standalone script block provides a good
# way to test your custom implementation. This testing is important because
# need to implement the Python interpreter functions imported from 
# CustomModule without error in order to have the dll work correctly. In
# other words, errors thrown from the Python interpreter will not make it
# back to GoldSim.
# This example standalone block assumes that IN_VAR_LIST has been changed to
# one double type inputs and that RET_VAR_LIST has been changed to one double 
# type output. Need to have MyCustomCalculations return a list which has 
# one item which is a list containing a float value.
if __name__ == "__main__":
    # local imports
    import sys
    from CustomModule import InitialChecks, PyModuleVersion, CalcInputs
    from CustomModule import CalcOutputs, CustomCalculations, WrapUpStuff
    # local variables
    RetStatus1 = 0              # integer return status
    ErrorMsg = ""               # error message.
    ModelVer = 0.0              # the model versions
    NumInputs = 0               # the number of inputs
    NumOutputs = 0              # the number of outputs
    RetList = list()            # the return list
    InList = list()             # testing input list.
    # now do the calculaitons.
    RetStatus1 = InitialChecks()
    if RetStatus1 != 0:
        # this is an error
        ErrorMsg = "Found return status of %d from InitialChecks(). This " \
                    "denotes an error.\n" % RetStatus1
        sys.exit( ErrorMsg )
    # get the model versions
    ModelVer = PyModuleVersion()
    print( "The module version %g.\n" % ModelVer )
    # get the number of inputs and outputs
    NumInputs = CalcInputs()
    NumOutputs = CalcOutputs()
    print( "Number of inputs expected is %d \n" % NumInputs )
    print( "Number of outputs expected is %d \n" % NumOutputs )
    # now do the main part.
    InList.append( 22.5 )
    RetList = CustomCalculations( InList, NumOutputs )
    print( "Return list is %s " % RetList )
    # now do the wrap up.
    WrapUpStuff()
    # now are done
    
# EOF