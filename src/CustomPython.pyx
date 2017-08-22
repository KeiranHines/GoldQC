# -*- coding: utf-8 -*-
"""
Cython Module: CustomPython.pyx
Created by: Nick Martin, GoldSim Technology Group
Creation Date: 21 May 2015
Last Edited: 15 June 2015

License: FreeBSD License (reproduced below)

Purpose:

This is a Cython file. Cython is "an optimising static compiler for both the
Python programming language and the extended Cython programming language
(based on Pyrex). It makes writing C extensions for Python as easy as Python
itself." Additional Cython information including the documentation is 
availabe from http://cython.org/.

This Cython file provides linkage from c-language dll CustomPython.dll to a
pure Python custom model. This Cython module relies on the pure, Python
accessory module GoldQC.py.

For this Cython file do not use a *.pxd file. The header (.h) file will
not be created correctly for c for this with the *.pxd file.

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
#======================================================================
# Global enumerations, useful for C-style implementations
# cython will create a CustomPython.h and CustomPython.c file from this
# file. These two files are compiled with CustomPythoncDLL.c to create
# the CustomPython.dll.

"""
XFMethodID - identifies the method types, used to identify the phase of the
simulation that is currently in progress.

XF_INITIALIZE:0 - Called after DLL is loaded and before each realization.
XF_CALCULATE:1 - Called during the simulation, each time the inputs change.
XF_REP_VERSION:2 - Called after DLL load to report the external fcn version 
                        number.
XF_REP_ARGUMENTS:3 - Called after DLL load to report the number of input and 
                        output # arguments.
XF_CLEANUP:99 - Called before the DLL is unloaded.
"""
ctypedef public enum XFMethodID:
    XF_PYCOMPILE_ERR = -9
    XF_INITIALIZE = 0
    XF_CALCULATE = 1
    XF_REP_VERSION = 2
    XF_REP_ARGUMENTS = 3
    XF_CLEANUP = 99

"""
XFStatusID - identifies the return codes for external functions.

XF_SUCCESS:0 = Call completed successfully.
XF_CLEANUP_NOW:99 = Call was successful, but GoldSim should clean up and 
                        unload the DLL immediately.
XF_FAILURE:1 = Failure (no error information returned).
XF_FAILURE_WITH_MSG:-1 = Failure, with DLL-supplied error message available. 
                            Address of error message is returned in the first 
                            element of the output arguments array.
XF_INCREASE_MEMORY:-2 = Failed because the memory allocated for output 
                        arguments is too small. GoldSim will increase the 
                        size of the output argument array and try again.
"""

ctypedef public enum XFStatusID:
    XF_SUCCESS = 0
    XF_FAILURE = 1
    XF_CLEANUP_NOW = 99
    XF_FAILURE_WITH_MSG = -1
    XF_INCREASE_MEMORY = -2

#======================================================================
# python string objects which have our error message. Note that these are all
# defined to have a length of 80 characters.
pyMSG_INIT = "Error in CustomPython DLL in the INITIALIZATION action. " \
                "See the log file.      "
pyMSG_CALC = "Error in CustomPython DLL in the CALCULATION action. " \
                "See the log file.         "
pyMSG_RVER = "Error in CustomPython DLL in VER. REPORT action; check " \
                "Python code compilation."
pyMSG_RARG = "Error in CustomPython DLL in the ARGUMENTS REPORT action. " \
                "See the log file.    "
pyMSG_CLUP = "Error in CustomPython DLL in the CLEAN UP action. " \
                "See the log file.            "
pyMSG_EDEF = "Error in CustomPython DLL. Unsupported action type given to " \
                "DLL interface.     "
pyMSG_PyCOMP = "Error in Python compilation. Please check your Python code " \
                "in imported modules."

#======================================================================
# external declaration to bring in the C code message copy function from 
# the GoldSim documenation
cdef extern from "ErrorRelay.h":
    void CopyMsgToOutputs(const char* sMsg, double* outargs) 

#======================================================================
# Cython cdef functions
# the error handling function
# Utility method used to simplify sending an error message to GoldSim
cdef public void ReturnErrorMsg( int MessageID, double * outargs ):
    """
    Function which passes the correct error message to the c language function
    for populating the output arguments array in the correct way. Note that
    are doing a python string to byte string conversion and then using this
    byte string to create a pointer to a c array of characters.
    
    Arguments:
    
        MessageID = integer which defines which message to use
        outargs = the pointer to the start of the cdef character array
        
    """
    # local declarations
    # local python variables
    pybMSG_INIT = pyMSG_INIT.encode( 'UTF-8' )
    pybMSG_CALC = pyMSG_CALC.encode( 'UTF-8' )
    pybMSG_RVER = pyMSG_RVER.encode( 'UTF-8' )
    pybMSG_RARG = pyMSG_RARG.encode( 'UTF-8' )
    pybMSG_CLUP = pyMSG_CLUP.encode( 'UTF-8' )
    pybMSG_EDEF = pyMSG_EDEF.encode( 'UTF-8' )
    pybMSG_PyCOMP = pyMSG_PyCOMP.encode( 'UTF-8' )
    # local c variables
    cdef char* cMSG_INIT = pybMSG_INIT
    cdef char* cMSG_CALC = pybMSG_CALC
    cdef char* cMSG_RVER = pybMSG_RVER
    cdef char* cMSG_RARG = pybMSG_RARG
    cdef char* cMSG_CLUP = pybMSG_CLUP
    cdef char* cMSG_EDEF = pybMSG_EDEF
    cdef char* cMSG_PyCOMP = pybMSG_PyCOMP
    # now determine which one to use based on the status
    if MessageID == XF_INITIALIZE:
        CopyMsgToOutputs( cMSG_INIT, outargs )
    elif MessageID == XF_CALCULATE:
        CopyMsgToOutputs( cMSG_CALC, outargs )
    elif MessageID == XF_REP_VERSION:
        CopyMsgToOutputs( cMSG_RVER, outargs )
    elif MessageID == XF_REP_ARGUMENTS:
        CopyMsgToOutputs( cMSG_RARG, outargs )
    elif MessageID == XF_CLEANUP:
        CopyMsgToOutputs( cMSG_CLUP, outargs )
    elif MessageID == XF_PYCOMPILE_ERR:
        CopyMsgToOutputs( cMSG_PyCOMP, outargs )
    else:
        CopyMsgToOutputs( cMSG_EDEF, outargs )
    # now return
    return

# the initialization function
cdef public int InitRoutines( ):
    """
    Wrapper function that calls the python initialization routines that we 
    need. Returns an integer status which is used by the DLL to determine
    how to proceed.
    
    Return:
    
        cdef int IntStatus
    
    """
    # local imports
    from GoldQC import InitialChecks
    # local variables
    # c variables
    cdef int IntStatus = 0
    # now are ready to call our functions
    IntStatus = InitialChecks()
    if IntStatus == 1:
        # this is an error
        return IntStatus
    # should be good.
    return IntStatus

# function to return the module version.
cdef public double ReturnCustomModuleVersion( ):
    """
    Convenience function to return the custom Python module version.
    Requires that CUSTOM_MODULE_VERSION be assigned a float in 
    In the specific Python implementation module.
    
    Returns:
    
        cdef double VersionNumber
    
    """
    # local imports (only Python imports)
    from GoldQC import PyModuleVersion
    # c variable declarations.
    cdef double VersionNumber = PyModuleVersion()
    # now return
    return VersionNumber

# return the number of inputs expected
cdef public int NumInputsExpected( ):
    """
    Wrapper function that returns the number of inputs expected.
    
    Return:
    
        cdef int NumInputs
    
    """
    # local imports
    from GoldQC import CalcInputs
    # c variable declarations
    cdef int RetInputs = 0          # the number of inputs returned.
    # start of function
    RetInputs = CalcInputs()
    # now return
    return RetInputs

# return the number of outputs expected.
cdef public int NumOutputsToProvide( ):
    """
    Wrapper function that returns the number of outputs to provide.
    
    Return:
    
        cdef int RetOutputs
    
    """
    # local imports
    from GoldQC import CalcOutputs
     # c variable declarations
    cdef int RetOutputs = 0          # the number of inputs returned.
    # start of function
    RetOutputs = CalcOutputs()
    # now return
    return RetOutputs
    
# wrap up for the simulation
cdef public void WrapUpSimulation( ):
    """
    Wrapper function that calls whatever is needed for the simulation wrap-up.
    In this case, call a Python convenience function to make one last log
    entry.
    
    """
    # local imports
    from GoldQC import WrapUpStuff
    # call the function.
    WrapUpStuff( )
    # now return
    return

# now this is the function that actually does calculations and returns values
cdef public int DoCalcsAndReturnValues( double * inargs, double * outargs ):
    """
    Function that provides the calculation interface between the DLL and
    Python. This function determines the size of the inputs and of the 
    outputs. It then calls a custom Python function to do the calculations with
    the inputs. At this point, only a single input value is supported. 
    The called Python function "CustomCalculations" needs to return a
    Python list of float values of the correct size for the output array.
    
    Arguments:
    
        inargs = the pointer to the input arguments array
        outargs = the pointer to the output values array.
    
    Return:
    
        Integer status - 1 = error; 0 = good
    
    """
    # local imports
    from copy import deepcopy
    from GoldQC import CustomCalculations
    # local variables
    # Python variables 
    PyIntRetNum = int( 0 )                  # the return number
    InputList = list()              # the list of input values.
    PassList = list()               # list of input floats
    PyThisVal = float( 0.0 )        # Python version of this value.
    # c variables
    cdef int ExpectInN = 0      # the expected number of input parameters
    cdef int ThisInd = 0        # current index.
    cdef int ExpectRetN = 0     # the expected number returned from Python
    cdef double ThisValue = 0.0     # value to return from Python list.
    # start of function
    # determine the number of inputs and outputs that are in the passed
    # double arrays.
    ExpectInN = NumInputsExpected( )
    ExpectRetN = NumOutputsToProvide( )
    PyIntRetNum = int( ExpectRetN )
    # check to make sure that are both > 0.
    if ( ExpectInN < 0 ) or ( ExpectRetN < 0 ):
        # this is an error.
        return 1
    # now get the full input list
    for ThisInd in range( ExpectInN ):
        ThisValue = inargs[ ThisInd ]
        PyThisVal = float( ThisValue )
        InputList.append( deepcopy( PyThisVal ) )
    # all of the input arguments have now been copied to a Python list which
    # is a list of Python floats --- ie doubles.
    # probably would not need to copy but want to ensure that these values
    # are not modified.
    RetList = CustomCalculations( InputList, PyIntRetNum )
    # one final check on the return list length.
    if len( RetList ) != ExpectRetN:
        # this is also an error.
        return 1
    # if are here then assign the returned list to outargs.
    for ThisInd in range( ExpectRetN ):
        ThisValue = <double>RetList[ThisInd]
        outargs[ThisInd] = ThisValue
    # now are done so return a successful result.
    return 0

# wrap up for the simulation
cdef public void PyCompileError( ):
    """
    Wrapper function that calls whatever there is a Python initialization or
    compilation error. It writes an entry to the log file.
    
    """
    # local imports
    from GoldQC import PythonInitializationError
    # call the function.
    PythonInitializationError( )
    # now return
    return
#EOF