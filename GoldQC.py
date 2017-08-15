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
CUSTOM_MODULE_VERSION = 0.1         # module version --- REQUIRED
LOG_FILE_NAME = "TestLog.txt"       # log file name --- REQUIRED
PHREEQC = None
STEP = 0
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
    global PHREEQC

    # local imports
    import datetime
    with open(LOG_FILE_NAME, 'w', 0) as Log:
        Log.write("Starting GoldQC.py script at %s.\n\n" % datetime.datetime.now().strftime("%x %H:%M"))
    import pythoncom, pywintypes
    from win32com.client import Dispatch

    # start of function.
    db_path = "database/phreeqc.dat"
    try:
        PHREEQC = Dispatch('IPhreeqcCOM.Object')
    except pythoncom.ole_error:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("Error Could not find IPhreeqcCOM, are you sure its installed?\n")
        return 1
    try:
        PHREEQC.LoadDatabase(db_path) # TODO Make more generic maybe with a config file.
    except pywintypes.com_error:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("Error Could not load database file %s\n" % db_path)
        return 1
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write("Successfully Started GoldQC.py script at %s.\n\n" % datetime.datetime.now().strftime("%x %H:%M"))
    return 0

def WrapUpLogFile( LogFileName ):
    """
    Required to end off the log file
    :param logfilename: the name of the logfile
    :return: None
    """
    #globals
    global LOG_FILE_NAME

    #local imports
    import datetime
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write("GoldQC.py completed successfully at %s.\n\n" % datetime.datetime.now().strftime("%x %H:%M"))
    return

def MyCustomCalculations(input):
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
    #globals
    global LOG_FILE_NAME
    global STEP
    STEP = STEP + 1
    # imports
    from CustomModule import RET_VAR_LIST
    INPUT_STRING = """
        SOLUTION 1
        END
        INCREMENTAL_REACTIONS
        REACTION
        \tNaCl 1.0
        \t0 60*0.1 moles
        EQUILIBRIUM_PHASES
        \tGypsum
        USE solution 1
        SELECTED_OUTPUT
        \t-reset false
        \t-total Na S(6)
        \t-step true
        \t-high_precision true
        END"""
    ReturnList = list()
    listLen = len(input)
    vector = input[0]
    with open(LOG_FILE_NAME, 'a',0) as Log:
        Log.write("Input on Step %d\n" %STEP)
    with open(LOG_FILE_NAME, 'a',0) as Log:
        for i in vector:
            Log.write(str(i) + '\n')
        return ReturnList


def process_input(input_string):
    """
    Runs a selected input string on the PHREEQC connection and returns the output
    :param input_string: input for simulation
    :return: @see Dispatch.getSelectedOutputArray()
    """

    #globals
    global LOG_FILE_NAME

    #local imports
    from Exceptions import DatabaseNotConnectedException
    if not PHREEQC:
        raise DatabaseNotConnectedException("PHREEQC database not connected")
        return
    PHREEQC.RunString(input_string)
    output = PHREEQC.GetSelectedOutputArray()
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write("Output-----------------\n\n")
        for o in output:
            Log.write(str(o))
            Log.write("\n")
        Log.write("End-of-Output----------\n\n")
    return output


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
    SetStuffUp()
    t = list()
    MyCustomCalculations(t)
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