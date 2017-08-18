# -*- coding: utf-8 -*-
"""
Python Module: GoldQC.py
Created by: Keiran Hines, RMIT
Creation Date: 14/08/2017
Last Edited: 16/08/2017

License: FreeBSD License (reproduced below)

Purpose:

Provides communication between GoldSim and PHREEQC for the purpose of
verifying the chemical balance of a solution. This is linked using the GoldSim
external element and PHREEQC's COM connection (IPHREEQC).
This file was developed by recreating the TestModule.py file provided by GoldSim
Technology Group, as such the licence and copyright for the original file are
listed below.

Original copyright notice.
---------------------------------------------------------------------------------
Python Module: TestModule.py
Created by: Nick Martin, GoldSim Technology Group
Creation Date: 23 May 2015
Last Edited: 25 May 2015
---------------------------------------------------------------------------------

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

# ===========================================================================
# Module level globals.
CUSTOM_MODULE_VERSION = 0.1  # module version --- REQUIRED
LOG_FILE_NAME = "TestLog.txt"  # log file name --- REQUIRED
PHREEQC = None
STEP = 0


# BAD_NAME = "
# ===========================================================================
# functions

def SetStuffUp():
    """
    Required function from CustomModule.py. Does whatever is needed in terms
    of set-up. Here just writes the initial entry to the log file.

    :return: Integer status: 0 = good; 1 = bad
    """
    # globals
    global LOG_FILE_NAME
    global PHREEQC

    # local imports
    import datetime
    with open(LOG_FILE_NAME, 'w', 0) as Log:
        Log.write("Starting GoldQC.py script at %s.\n\n" % datetime.datetime.now().strftime("%x %H:%M"))

    from comtypes.client import CreateObject
    # start of function.
    db_path = "database/phreeqc.dat"
    try:
        PHREEQC = CreateObject('IPhreeqcCOM.Object')
    except Exception:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("Error Could not find IPhreeqcCOM, are you sure its installed?\n")
        return 1
    try:
        PHREEQC.LoadDatabase(db_path)  # TODO Make more generic maybe with a config file.
    except Exception:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("Error Could not load database file %s\n" % db_path)
        return 1
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write("Successfully Started GoldQC.py script at %s.\n\n" % datetime.datetime.now().strftime("%x %H:%M"))
    return 0


def WrapUpLogFile(log_file):
    """
    Required to end off the log file with completion time and any other useful information
    :param log_file:
    :return: None
    """
    # local imports
    import datetime
    with open(log_file, 'a', 0) as Log:
        Log.write("GoldQC.py completed successfully at %s.\n\n" % datetime.datetime.now().strftime("%x %H:%M"))
    return


def MyCustomCalculations(input_list):
    """
    Required to transform the input from GoldSim to a PHREEQC simulation string then transform the result from
    PHREEQC back to GoldSims expected format

    :param
        input_list = a list of the input values/parameters which has come
                    from the GoldSim external element via CustomModule.py.

    :return
        return_list = list of the output values which needs to be in the format
                    expected by CustomModule.py.
    """
    # globals
    global LOG_FILE_NAME
    global STEP

    STEP = STEP + 1
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write('Running step %d\n' % STEP)

    input_string = ('SOLUTION 1\n'
                    '\tunits\tmg/l\n')
    return_list = list()
    # Start of needed items for test purposes only while we wait on getting able to extract the labels from GoldSim
    # =======================================================================================================
    from collections import OrderedDict
    element_symbols = ['Al', 'Ca', 'Mg', 'Na', 'SO4', 'Cl', 'Br']  # Temporary until goldsim info can be collected.
    element_values = input_list[0]
    e_dict = OrderedDict(zip(element_symbols, element_values))
    print e_dict
    # End of needed items for test purposes only while we wait on getting able to extract the labels from GoldSim
    # =======================================================================================================

    # Need to refactor based on final GoldSim inputs
    for element, value in e_dict.iteritems():
        input_string += str('\t' + element + '\t\t' + value + '\n')
    input_string += str('\n SELECTED_OUTPUT\n\t-totals\t')
    for element in e_dict:
        input_string += str(element + ' ')
    input_string += '\n'

    # Input string created, Logging details.
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write('Input on Step %d\n' % STEP)
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write(input_string)

    # calling PHREEQC
    phreeqc_values = process_input(input_string)

    if phreeqc_values is None:
        return 1
    # Processing PHREEQC output to GoldSim format
    headings = list(phreeqc_values[0])[-len(element_values):]
    values = list(phreeqc_values[1])[-len(element_values):]

    # TODO REMOVE THE PRINTS
    print "Values"
    print headings
    print values
    print "End Values"

    # TODO Convert Mol/kgw to mg/l
    return_list.append(values)
    return return_list


def process_input(input_string):
    """
    Runs a selected input string on the PHREEQC connection and returns the output
    :param input_string: input for simulation
    :return: @see Dispatch.getSelectedOutputArray()
    """

    # globals
    global LOG_FILE_NAME

    # local imports
    if not PHREEQC:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("Database is not connected or PHREEQC not running.\n")
            return None
    PHREEQC.RunString(input_string)
    warning = PHREEQC.getWarningString()
    if warning:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write(warning)
    output = PHREEQC.GetSelectedOutputArray()
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write("Output-----------------\n\n")
        for o in output:
            Log.write(str(o))
            Log.write("\n")
        Log.write("End-of-Output----------\n\n")
    return output


def main():
    SetStuffUp()
    test_list = [["0.12", "323", "458", "4.32", "0.34", "1.23", "95.6554"]]
    output = MyCustomCalculations(test_list)
    WrapUpLogFile(LOG_FILE_NAME)
    print output


if __name__ == "__main__":
    main()
