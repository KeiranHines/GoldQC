# -*- coding: utf-8 -*-
"""
Python Module: GoldQC.py
Created by: Keiran Hines, RMIT
Creation Date: 14/08/2017

Copyright 2017, Keiran Hines
This file is part of GoldQC.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* The name of the author may not be used to endorse or promote products
  derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

Purpose:

Provides communication between GoldSim and PHREEQC for the purpose of
verifying the chemical balance of a solution. This is linked using the GoldSim
external element and PHREEQC's COM connection (IPHREEQC).
This file was developed using the guide created by GoldSim Technologies Group
by combining the ideas of CustomPython.py and TestModule.py available at:
https://www.goldsim.com/library/models/featurescapabilities/dllscripts/pythondll/
"""
# ===========================================================================
import datetime
import re
from ConfigParser import ConfigParser, NoOptionError, NoSectionError
from collections import OrderedDict

from comtypes.client import CreateObject
from prettytable import PrettyTable

from Converstions import ELEMENT_SYMBOLS, MOLAR_MASS_LIST

# Module level globals.
GOLDQC_VERSION = 0.9
PHREEQC = None
STEP = 0
ERRORS = 0
WARNINGS = 0
PHREEQC_SPECS = ''
EQ_PHASES = ''
TOTALS = ''
LOG_FILE_NAME = 'logFile.txt'
DB_PATH = None
DEBUG_LEVEL = 0
SUPPRESS_WARNINGS = False

# PHREEQC variables to be populated by parseConfig
ELEMENTS = []
PH = 7
PE = 4
REDOX = 'pe'
TEMP = 25
CHARGE = None
EQ_OPTIONS = [["Gypsum", 0, 0]]

# GoldSim specific constants and variables
VECTOR_TYPE = "1-D Array"  # this is vector
VAR_CNT_IND = 0  # index of count
VAR_TYPE_IND = 1  # index for the type
VAR_DESC_IND = 2  # the index for the description
IN_VAR_LIST = None
RET_VAR_LIST = None


def parseConfig():
    """
    Helper function to parse the config file GoldQC.config. This function will read the config file and set the global
    variables accordingly.

    :return: None
    """
    global LOG_FILE_NAME, DB_PATH, DEBUG_LEVEL, SUPPRESS_WARNINGS
    global ELEMENTS, PH, PE, REDOX, TEMP, CHARGE, EQ_OPTIONS
    global IN_VAR_LIST, RET_VAR_LIST
    # Parsing config file and sanitising configuration variables
    config = ConfigParser()
    conf_check = config.read("GoldQC.config")
    if not len(conf_check):
        raise Exception("Error: Config file GoldQC.Config could not be read")

    try:
        ELEMENTS = config.get("GoldSim", "elements")
        if not ELEMENTS:
            exit("Error elements not specified")
        else:
            ELEMENTS = eval(ELEMENTS)
    except SyntaxError:
        exit("Error parsing elements in config: potentially missing ]")
    except NameError:
        exit("Error parsing elements in config: a non-string object was encountered")
    except NoOptionError:
        exit("Error Elements are not specified.")
    if not all(isinstance(item, str) for item in ELEMENTS):
        exit("Error an element listed in the config is not in string format (double or single quotes)")
    try:
        DB_PATH = config.get("phreeqc", "database")
    except NoSectionError:
        exit("Error no database file specified.")
    try:
        LOG_FILE_NAME = config.get("GoldQC", "log_file")
    except (NoOptionError, ValueError, NoSectionError):
        LOG_FILE_NAME = 'GoldQC.log'
    try:
        DEBUG_LEVEL = int(config.get("GoldQC", "debug_level"))
    except (ValueError, NoOptionError, NoSectionError):
        DEBUG_LEVEL = 0
    try:
        t = config.get("GoldQC", "suppress_warnings")
        if t:
            SUPPRESS_WARNINGS = eval(t)
            if not isinstance(SUPPRESS_WARNINGS, bool):
                SUPPRESS_WARNINGS = False
        else:
            SUPPRESS_WARNINGS = False
    except NoOptionError:
        SUPPRESS_WARNINGS = False
    try:
        PH = config.get("phreeqc", "pH")
        if not PH:
            PH = '7'
    except NoOptionError:
        PH = 7
    try:
        PE = config.get("phreeqc", "pe")
        if not PE:
            PE = '4'
    except NoOptionError:
        PE = 4
    try:
        REDOX = config.get("phreeqc", "redox")
        if not REDOX:
            REDOX = 'pe'
        else:
            REDOX = eval(REDOX)
    except NoOptionError:
        REDOX = 'pe'
    try:
        TEMP = config.get("phreeqc", "temp")
        if not TEMP:
            TEMP = '25'
    except NoOptionError:
        TEMP = 25
    try:
        CHARGE = config.get("phreeqc", "charge")
        if not CHARGE:
            CHARGE = None
        else:
            CHARGE = eval(CHARGE)
    except NoOptionError:
        CHARGE = None
    try:
        t = config.get("phreeqc", "equilibrium_phases")
        if t:
            EQ_OPTIONS = eval(t)
    except NoOptionError:
        EQ_OPTIONS = [["Gypsum", 0, 0]]
    except SyntaxError:
        exit("Error parsing elements in config: potentially missing ]")
    except NameError:
        exit("Error parsing elements in config: a non-string object was encountered")

    IN_VAR_LIST = [[len(ELEMENTS), VECTOR_TYPE, "inputVector"]]
    RET_VAR_LIST = [[len(ELEMENTS), VECTOR_TYPE, "outputVector"]]


def InitialChecks():
    """
        Required function; starts up the Iphreeqc module and initialises the logfile.

        :return: Integer status: 0 = good; 1 = bad
    """
    # globals
    global LOG_FILE_NAME
    global PHREEQC
    global DEBUG_LEVEL
    global DB_PATH, ELEMENTS, PHREEQC_SPECS, EQ_PHASES, TOTALS

    debug_string = ''
    with open(LOG_FILE_NAME, 'w') as Log:
        Log.write("Starting GoldQC.py script at %s.\n\n" % datetime.datetime.now().strftime("%x %H:%M"))
    if DEBUG_LEVEL:
        debug_string += "database path: %s\n" % str(DB_PATH)

    try:
        PHREEQC = CreateObject('IPhreeqcCOM.Object')
    except WindowsError as e:
        debug_string += "Error Could not find IPhreeqcCOM, are you sure its installed?\n" \
                        "Error Message: %s\n" % e
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write(debug_string)
        return 1

    try:
        PHREEQC.LoadDatabase(DB_PATH)
    except WindowsError as e:
        debug_string += "Error Could not load database file %s\n" \
                        "Error message: %s" % (DB_PATH, e)
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write(debug_string)
        return 1
    for element in ELEMENTS:
        if element in ELEMENT_SYMBOLS:
            ELEMENTS[ELEMENTS.index(element)] = ELEMENT_SYMBOLS[element]
    PHREEQC_SPECS = ('\ttemp\t\t%s\n\tpH\t\t\t%s\n\tpe\t\t\t%s\n\tredox\t\t%s\n' % (TEMP, PH, PE, REDOX))
    EQ_PHASES = 'EQUILIBRIUM_PHASES\n%s' % "".join(['\t%s\t%s\t%s\n' % (e[0], e[1], e[2]) for e in EQ_OPTIONS])
    TOTALS = "".join(['%s ' % s for s in ELEMENTS])
    debug_string += "Successfully Started GoldQC.py script at %s.\n\n" % \
                    datetime.datetime.now().strftime("%x %H:%M")
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write(debug_string)
    return 0


def PyModuleVersion():
    """
    Wrapper function that transfers the version specified in the Specific/
    Custom implementation module back to the dll.
    
    :return:    Version number --- will be cast to a double later
    """
    return GOLDQC_VERSION


def CalcInputs():
    """
    Returns the number of elements as specified by the elements config.
    This should match the number of inputs from GoldSim.
    
    :return:    Number of inputs expected. -1 is an error
    """
    return len(ELEMENTS)


def CalcOutputs():
    """
    Returns the number of elements as specified by the elements config.
    This should match the size of the vector GoldSim is expected to be returned.

    :return:    Number of outputs expected. -1 is an error
    """
    return len(ELEMENTS)


def CustomCalculations(input_list, num_return):
    """
    Handles conversion from GoldSim format to Python style list. The function then passes the input to
    MyCustomCalculations for processing to IPhreeqc format before being ran in PHREEQC and passed back
    with conversions from PHREEQC to Python to GoldSim.

    :param: input_list the list of floats which is the input array from GoldSim.
    :param: num_return the total number of indices to return in the list which goes back to CustomPython.pyx.
    
    :return: return_list list of floats with NumToReturn indexes which will be written to the output arguments array.
    """
    # globals
    global IN_VAR_LIST, RET_VAR_LIST, VAR_TYPE_IND, VAR_CNT_IND
    global DEBUG_LEVEL

    num_output_vars = len(RET_VAR_LIST)  # the number of input variables.
    start_index = 0  # the starting index for the input.
    tst_indexes = list()  # the indexes for testing
    py_input_list = list()  # inputs in Python list format

    tst_indexes.append(0)
    current_indexes = int(IN_VAR_LIST[0][VAR_CNT_IND])
    var_in_list = input_list[start_index:(start_index + current_indexes)]
    input_vector = var_in_list
    py_input_list.append(input_vector)
    start_index = start_index + current_indexes
    tst_indexes.append(start_index)

    ret_var_list = MyCustomCalculations(py_input_list)
    if not isinstance(ret_var_list, list):
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("ERROR")
        return -1
    if len(ret_var_list) != num_output_vars:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("Received %d variables back from processing in "
                      "function CustomCalculations. Expected %d variables.\n" %
                      (len(ret_var_list), num_output_vars))
        return [-1]
    return_list = ret_var_list[0]

    # noinspection PyTypeChecker
    if len(return_list) != num_return:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            # noinspection PyTypeChecker
            Log.write("Created return list with wrong length. Return "
                      "list has length %d. Needs to have length %d.\n" %
                      (len(return_list), num_return))
        return [-1]
    return return_list


def WrapUpStuff():
    """
    Required to end off the log file with completion time and any other useful information
    :return: None
    """

    global ERRORS, WARNINGS
    # local imports
    if ERRORS:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("Error: GoldQC enocunterd some error(s). Please check the log")
        exit(-1)
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        if WARNINGS:
            Log.write("GoldQC completed successfully but with warnings at %s.\n" %
                      datetime.datetime.now().strftime("%x %H:%M"))
        else:
            Log.write("GoldQC completed successfully at %s.\n" % datetime.datetime.now().strftime("%x %H:%M"))
    return


def PythonInitializationError():
    """
    Python function to write an error to the log file.
    """
    debug_string = str("Python did not initialize correctly.\n")
    debug_string += str("This is most likely due to an error in your Python code\n")
    debug_string += str("which was triggered during the bytecode compilation\n")
    debug_string += str("step which was triggered by an import statement.\n")
    debug_string += str("Please use an if __name__ == \"__main__\": block \n")
    debug_string += str("in your Python module to test and to ensure that it \n")
    debug_string += str("runs without error.\n")

    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write(debug_string)
    return


def MyCustomCalculations(input_list):
    """
    Required to transform the input from GoldSim to a PHREEQC simulation string then transform the result from
    PHREEQC back to GoldSims expected format

    :param: input_list A list of the input values/parameters from the GoldSim

    :return: return_list A list of the output values which needs to be in the format expected by RET_VAR_LIST
    """

    # globals
    global LOG_FILE_NAME
    global STEP, PHREEQC_SPECS, EQ_PHASES, CHARGE
    global DEBUG_LEVEL
    global ERRORS

    debug_string = ''

    if DEBUG_LEVEL:
        debug_string += "Step %d\n" % STEP
    element_values = input_list[0]

    if DEBUG_LEVEL:
        debug_string += "Input Values:\n"
        table = PrettyTable(["Element"] + ELEMENTS)
        table.add_row(["Value"] + element_values)
        debug_string += '%s\n\n' % table

    # Creating input string for input to PHREEQC
    items = OrderedDict(zip(ELEMENTS, element_values))
    if CHARGE in ELEMENTS:
        items[CHARGE] = "%s\tcharge" % items[CHARGE]
    if CHARGE not in ELEMENTS and CHARGE:
        items.update({CHARGE: '0\tcharge'})
    input_string = 'SOLUTION %d\n\tunits\t\tmg/l\n\tdensity\t\t1\n\t-water\t\t1\n' \
                   '%s%s%sSELECTED_OUTPUT\n\t-water\t\ttrue\n\t-totals %s\nEND\n\n' % \
                   (STEP, PHREEQC_SPECS,
                    "".join(['\t%s\t\t\t%s\n' % (element, value) for element, value in items.items()]),
                    EQ_PHASES, TOTALS)

    # Input string created, Logging details.
    if DEBUG_LEVEL > 1:
        debug_string += input_string

    # calling PHREEQC
    phreeqc_values = process_input(input_string)

    # Confirming PHREEQC did not return an error.
    if phreeqc_values is None or not phreeqc_values:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write(debug_string)
        STEP += 1
        ERRORS = 1
        return -1

    # Processing PHREEQC output to GoldSim format
    headings = list(phreeqc_values[0])[-len(element_values):]
    values = list(phreeqc_values[2])[-len(element_values):]
    water = list(phreeqc_values[2])[-len(element_values) - 1]
    raw_values = list(values)
    # Converting mol/kgw to mg/l ONLY NEEDED IN TOTALS MODE
    i = 0
    while i < len(headings):
        headings[i] = re.sub('\(mol/kgw\)$', '', headings[i])
        values[i] = float(values[i] * MOLAR_MASS_LIST[headings[i]] * 1000.0 * float(1 / water))
        i += 1

    # Formatting values into GoldSim required format
    return_list = list()
    return_list.append(values)
    if DEBUG_LEVEL:
        debug_string += "Output Values:\n"
        table = PrettyTable(["Element"] + headings)
        table.add_row(["mg/l"] + raw_values)
        table.add_row(["mol/kg"] + values)
        debug_string += '%s\n\n' % table
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write(debug_string)

    STEP += 1
    return return_list


def process_input(input_string):
    """
    Runs a selected input string on the PHREEQC connection and returns the output

    :param input_string: input for simulation

    :return: @see Dispatch.getSelectedOutputArray()
    """

    # globals
    global LOG_FILE_NAME, PHREEQC, STEP, DB_PATH, ERRORS, WARNINGS, SUPPRESS_WARNINGS

    from comtypes.client import CreateObject

    if not PHREEQC:
        try:
            PHREEQC = CreateObject('IPhreeqcCOM.Object')
            PHREEQC.LoadDatabase(DB_PATH)
        except WindowsError as e:
            with open(LOG_FILE_NAME, 'a', 0) as Log:
                Log.write("Error restarting PHreeqc connection\n")
                Log.write(str(e))
                Log.write("Database is not connected or PHREEQC not running.\n")
        return None
    # PHREEQC.OutputStringOn = True
    # noinspection PyBroadException
    try:
        PHREEQC.RunString(input_string)
    except Exception:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write(str('Error at step %d: \n' % STEP))
            phreeqc_error = PHREEQC.GetErrorString()
            if phreeqc_error:
                ERRORS = 1
                Log.write(phreeqc_error)
    warning = PHREEQC.GetWarningString()  # TODO Investigate passing warning back to GoldSim
    if warning:
        WARNINGS = 1
        if not SUPPRESS_WARNINGS or DEBUG_LEVEL:
            with open(LOG_FILE_NAME, 'a', 0) as Log:
                Log.write('Warning at step %d: \n' % STEP)
                Log.write(warning)
    output = PHREEQC.GetSelectedOutputArray()
    # with open("out.txt", 'a', 0) as debug:
    #     debug.write(PHREEQC.GetOutputString().encode('utf8', 'replace'))
    return output


def main():
    status = InitialChecks()
    if status:
        exit(status)
    global ELEMENTS, ERRORS
    ELEMENTS = ['Al', 'Ca', 'Mg', 'Na', 'S(6)', 'Cl', 'Br']
    test_list = [["0.12", "323", "458", "4.32", "0.34", "1.23", "95.6554"]]
    output = MyCustomCalculations(test_list)
    if output and not ERRORS:
        print "Success! Everything is setup and ready to use"
    else:
        print "Error: Something went wrong. Check the log."
    WrapUpStuff()


# Calling parseConfig as file is loaded to avoid error with GoldSim requiring number of inputs and outputs
parseConfig()

if __name__ == "__main__":
    main()
