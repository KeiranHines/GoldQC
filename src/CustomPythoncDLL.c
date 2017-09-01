/* 
c language dll: CustomPythoncDLL.c
Created by: Nick Martin, GoldSim Technology Group
Creation Date: 21 May 2015
Last Edited: 6 May 2016

License: FreeBSD License (reproduced below)

Purpose:

This file provides a wrapper which wraps Cython code which then provides
a direct interface to a custom, pure python module.

Python must be installed on this machine so that Python.h can be found by
the compiler. Additionally, the Py_Initialize, initCustomPython and 
Py_Finalize functions are provided by Cython and linkage/compilation of this
file to CustomPython.pyx (and the CustomPython.c and CustomPython.h files
created by Cython).

*/
/*
LICENSE

This source code is available for your use under the FreeBSD License, see:
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
*/

#include <Python.h>
#include "CustomPython.h"

// DLL c language 
extern void __declspec(dllexport) CustomPython ( int methodID, int * status, 
                                                 double * inargs, 
                                                 double * outargs ) {
    // initialize a few c variables that will use later.
    int RetStatus1 = 0;
    int RetStatus2 = 0;
    int RetStatus3 = 0;
    int RetStatus4 = 0;
    double VersionReturn = -1.0;
    int PyStatus = 0;
    // set the status to bad to start.
    *status = XF_FAILURE;
    // The first thing to do is to set up the interaction with the Python
    // interpreter. For documentation of this setup see "Exposing Cython 
    // Code to C" on p. 126 and 127 of Cython: A Guide for Python 
    // Programmers.
    //
    // The Python interpreter will compile the python module (in this case 
    // CustomPython.py) to byte code when the init command ( 
    // initCustomPython() ) is called if this text file is newer than the 
    // corresponding *pyc byte code file. If there are any errors that will 
    // prevent compilation then will have an issue in the first method with
    // arguments which seems to be XF_REP_VERSION.
    //
    // If GoldSim may want to keep this dll loaded do not want to repeatedly
    // initialize python so determine the current status with Py_IsInitialized()
    // where == 0 is false; <> 0 is true. This Py_Initialize() and 
    // Py_Finalize() are available from <Python.h>. The enumeration of the
    // the method identifiers is provided via Cython in "CustomPython.h"
    //
    // continue based on the selected method.
    switch ( methodID ) {
        case XF_INITIALIZE:
            // first initialize the python stuff
            // check tha python is initialized
            PyStatus = Py_IsInitialized();
            // if not then initialize.
            if ( PyStatus == 0 ) {
                Py_Initialize();
                initCustomPython();
            }
            // call function to check for paths and existence of files.
            // update the status if needed.
            RetStatus1 = InitRoutines( );
            if ( RetStatus1 == 1 ) {
                *status = XF_FAILURE_WITH_MSG;
                ReturnErrorMsg( XF_INITIALIZE, outargs );
                // see if need to clean-up python
                PyStatus = Py_IsInitialized();
                if ( PyStatus != 0 ) {
                    Py_Finalize();
                }
            }
            else {
                *status = XF_SUCCESS;
            }
            break;
        case XF_REP_VERSION:
            PyStatus = Py_IsInitialized();
            // first initialize the python stuff
            if ( PyStatus == 0 ) {
                Py_Initialize();
                initCustomPython();
            }
            // call function to get the version from the Python module.
            VersionReturn = ReturnCustomModuleVersion( );
            // the check is set up here with VersionReturn having a 
            // default negative value to catch Python at run time 
            // compilation issues.
            if ( VersionReturn > 0.0 ) {
                outargs[0] = ReturnCustomModuleVersion( );
                *status = XF_SUCCESS;
            }
            else {
                *status = XF_FAILURE_WITH_MSG;
                ReturnErrorMsg( XF_REP_VERSION, outargs );
                // see if need to clean-up python
                PyStatus = Py_IsInitialized();
                if ( PyStatus != 0 ) {
                    Py_Finalize();
                }
            }
            break;
        case XF_REP_ARGUMENTS:
            PyStatus = Py_IsInitialized();
            // first initialize the python stuff
            if ( PyStatus == 0 ) {
                Py_Initialize();
                initCustomPython();
            }
            // custom function to return the arguments and allocate to 
            // the outargs.
            RetStatus3 = NumInputsExpected( ); // number of inputs expected
            if ( RetStatus3 < 0 ) {
                *status = XF_FAILURE_WITH_MSG;
                ReturnErrorMsg( XF_REP_ARGUMENTS, outargs );
            }
            else {
                *status = XF_SUCCESS;
            }
            outargs[0] = (double)RetStatus3; 
            RetStatus4 = NumOutputsToProvide( );
            // check to make sure that have no errors.
            if ( RetStatus4 < 0 ) {
                *status = XF_FAILURE_WITH_MSG;
                ReturnErrorMsg( XF_REP_ARGUMENTS, outargs );
            }
            else {
                *status = XF_SUCCESS;
            }
            outargs[1] = (double)RetStatus4; 
            if ( ( RetStatus3 < 0 ) || ( RetStatus4 < 0 ) ) {
                // see if need to clean-up python
                PyStatus = Py_IsInitialized();
                if ( PyStatus != 0 ) {
                    Py_Finalize();
                }
            }
            break;
        case XF_CALCULATE:
            PyStatus = Py_IsInitialized();
            // first initialize the python stuff
            if ( PyStatus == 0 ) {
                Py_Initialize();
                initCustomPython();
            }
            RetStatus2 = DoCalcsAndReturnValues( inargs, outargs );
            if ( RetStatus2 != 0 ) {
                *status = XF_FAILURE_WITH_MSG;
                ReturnErrorMsg( XF_CALCULATE, outargs );
                // see if need to clean-up python
                PyStatus = Py_IsInitialized();
                if ( PyStatus != 0 ) {
                    Py_Finalize();
                }
            }
            else {
                *status = XF_SUCCESS;
            }
            break;
        case XF_CLEANUP:
            // still need to check the status
            PyStatus = Py_IsInitialized();
            // first initialize the python stuff
            if ( PyStatus == 0 ) {
                Py_Initialize();
                initCustomPython();
            }
            *status = XF_SUCCESS;
            WrapUpSimulation( );
            // now check for de-initialization
            PyStatus = Py_IsInitialized();
            // de-initialize/clean-up if possible
            if ( PyStatus != 0 ) {
                Py_Finalize();
            }
            break;          // 
        default:
            // still need to check the status
            PyStatus = Py_IsInitialized();
            // first initialize the python stuff
            if ( PyStatus == 0 ) {
                Py_Initialize();
                initCustomPython();
            }
            *status = XF_FAILURE_WITH_MSG;
            ReturnErrorMsg( 5, outargs );
            // de-initialize/clean-up if possible
            PyStatus = Py_IsInitialized();
            if ( PyStatus != 0 ) {
                Py_Finalize();
            }
            break;
    }
}

//EOF