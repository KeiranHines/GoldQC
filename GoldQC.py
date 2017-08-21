# -*- coding: utf-8 -*-
"""
Python Module: GoldQC.py
Created by: Keiran Hines, RMIT
Creation Date: 14/08/2017
Last Edited: 21/08/2017


Copyright 2017, Keiran Hines
This file is part of GoldQC.

GoldQC is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

GoldQC is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with GoldQC.  If not, see <http://www.gnu.org/licenses/>.

Purpose:

Provides communication between GoldSim and PHREEQC for the purpose of
verifying the chemical balance of a solution. This is linked using the GoldSim
external element and PHREEQC's COM connection (IPHREEQC).
This file was developed using the guide created by GoldSim Technologies Group
Available at:
https://www.goldsim.com/library/models/featurescapabilities/dllscripts/pythondll/
4
"""

# Module level globals.
CUSTOM_MODULE_VERSION = 0.1
LOG_FILE_NAME = "TestLog.txt"
PHREEQC = None
STEP = 0


def SetStuffUp():
    """
    Required function from CustomModule.py provided by GoldSim Technologies Group.
    Starts up the Iphreeqc module and initialises the logfile.

    :return: Integer status: 0 = good; 1 = bad
    """
    # globals
    global LOG_FILE_NAME
    global PHREEQC

    # local imports
    import datetime
    import ConfigParser
    from comtypes.client import CreateObject
    from CustomModule import DEBUG_LEVEL

    with open(LOG_FILE_NAME, 'w', 0) as Log:
        Log.write("Starting GoldQC.py script at %s.\n\n" % datetime.datetime.now().strftime("%x %H:%M"))

    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    db_path = config.get("phreeqc", "database")
    if DEBUG_LEVEL:
        with open(LOG_FILE_NAME, 'w', 0) as Log:
            Log.write("database path: %s\n" % str(db_path))

    try:
        PHREEQC = CreateObject('IPhreeqcCOM.Object')
    except WindowsError as e:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("Error Could not find IPhreeqcCOM, are you sure its installed?\n")
            Log.write("Error Message: %s\n" % e)
        return 1

    try:
        PHREEQC.LoadDatabase(db_path)
    except WindowsError as e:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("Error Could not load database file %s\n" % db_path)
            Log.write("Error message: %s" % e)
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

    import ConfigParser
    from collections import OrderedDict
    from CustomModule import DEBUG_LEVEL

    STEP = STEP + 1
    if DEBUG_LEVEL:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("Starting Step %d\n" % STEP)

    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    element_symbols = config.get("GoldSim", "elements")
    element_symbols = eval(element_symbols)
    element_values = input_list[0]

    if DEBUG_LEVEL:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("Element Symbols: %s\n" % str(element_symbols))
            Log.write("Element Values:  %s\n" % str(element_values))
    input_string = ('SOLUTION 1\n'
                    '\tunits\tmg/l\n')

    e_dict = OrderedDict(zip(element_symbols, element_values))
    print e_dict
    if DEBUG_LEVEL:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write(str(e_dict) + "\n")

    # Need to refactor based on final GoldSim inputs
    for element, value in e_dict.iteritems():
        input_string += str('\t' + element + '\t\t' + str(value) + '\n')
    input_string += str('\n SELECTED_OUTPUT\n\t-totals\t')
    for element in e_dict:
        input_string += str(element + ' ')
    input_string += '\n'

    # Input string created, Logging details.
    if DEBUG_LEVEL:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write('Input on Step %d\n' % STEP)
            Log.write(input_string)

    # calling PHREEQC
    phreeqc_values = process_input(input_string)

    if phreeqc_values is None:
        return 1
    # Processing PHREEQC output to GoldSim format
    headings = list(phreeqc_values[0])[-len(element_values):]
    values = list(phreeqc_values[1])[-len(element_values):]


    # TODO Convert Mol/kgw to mg/l
    return_list = list()
    return_list.append(values)
    if DEBUG_LEVEL:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("return list: " + str(return_list) + "\n")
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
    #TODO handle warning items properly
    return output


def main():
    status = SetStuffUp()
    if status:
        exit(status)
    test_list = [["0.12", "323", "458", "4.32", "0.34", "1.23", "95.6554"]]
    output = MyCustomCalculations(test_list)
    WrapUpLogFile(LOG_FILE_NAME)
    print output


if __name__ == "__main__":
    main()
