# -*- coding: utf-8 -*-
"""
Python Module: GoldQC.py
Created by: Keiran Hines, RMIT
Creation Date: 14/08/2017
Last Edited: 28/08/2017


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
by combining the GoldQC.py and TestModule.py files
Available at:
https://www.goldsim.com/library/models/featurescapabilities/dllscripts/pythondll/
"""
# ===========================================================================
# imports
import ConfigParser

# Module level globals.
CUSTOM_MODULE_VERSION = 0.5
PHREEQC = None
STEP = 0

VECTOR_TYPE = "1-D Array"  # this is vector
VAR_CNT_IND = 0  # index of count
VAR_TYPE_IND = 1  # index for the type
VAR_DESC_IND = 2  # the index for the description

CONFIG = ConfigParser.ConfigParser()
CONFIG.read("GoldQC.config")
ELEMENTS = eval(CONFIG.get("GoldSim", "elements"))
LOG_FILE_NAME = CONFIG.get("GoldQC", "log_file")
DEBUG_LEVEL = int(CONFIG.get("GoldQC", "debug_level"))
DB_PATH = CONFIG.get("phreeqc", "database")

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
    global CONFIG
    global DB_PATH
    global ELEMENTS
    # local imports
    import datetime
    from comtypes.client import CreateObject
    from Converstions import ELEMENT_SYMBOLS

    debug_string = ''
    with open(LOG_FILE_NAME, 'w', 0) as Log:
        Log.write("Starting GoldQC.py script at %s.\n\n" % datetime.datetime.now().strftime("%x %H:%M"))

    if DEBUG_LEVEL:
        debug_string += str("database path: %s\n" % str(DB_PATH))

    try:
        PHREEQC = CreateObject('IPhreeqcCOM.Object')
    except WindowsError as e:
        debug_string += str("Error Could not find IPhreeqcCOM, are you sure its installed?\n")
        debug_string += str("Error Message: %s\n" % e)
        WriteStringToLog(debug_string)
        return 1

    try:
        PHREEQC.LoadDatabase(DB_PATH)
    except WindowsError as e:
        debug_string += str("Error Could not load database file %s\n" % DB_PATH)
        debug_string += str("Error message: %s" % e)
        WriteStringToLog(debug_string)
        return 1
    for element in ELEMENTS:
        if element in ELEMENT_SYMBOLS:
            ELEMENTS[ELEMENTS.index(element)] = ELEMENT_SYMBOLS[element]

    print ELEMENTS
    debug_string += str("Successfully Started GoldQC.py script at %s.\n\n" %
                        datetime.datetime.now().strftime("%x %H:%M"))
    WriteStringToLog(debug_string)
    return 0


def PyModuleVersion():
    """
    Wrapper function that transfers the version specified in the Specific/
    Custom implementation module back to the dll.
    
    :return:    Version number --- will be cast to a double later
    """
    return CUSTOM_MODULE_VERSION


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


def InputEcho(input_list, var_definition, py_in_list):
    """
    Echos the input to a csv file for debugging when needed.
    
    :param: input_list = the input list from GoldSim external element
    :param: var_definition = the definition from this file for inputs
    :param: py_in_list = the input list of variables in "Python" formats
    """
    # globals
    global VECTOR_TYPE

    # local parameters
    out_file_name = "Echo_Inputs.csv"  # output file name

    # local variables
    var_cnt = 0  # the variable counter

    with open(out_file_name, 'w', 0) as output_file:
        output_file.write("Input variable definition:\n\n")
        output_file.write("Index, Length, Type, Description, Time Series Type \n")
        for this_var in var_definition:
            current_type = str(this_var[VAR_TYPE_IND])
            current_desc = str(this_var[VAR_DESC_IND])
            output_file.write("%d, %d, %s, %s,\n" % (var_cnt + 1, this_var[VAR_CNT_IND],
                                                     current_type, current_desc))
            var_cnt = var_cnt + 1
        output_file.write("\n\n\n")

        # now do the list of in_args
        var_cnt = 0
        output_file.write("GoldSim in_args:\n\n")
        output_file.write("Index, Value \n")
        for this_var in input_list:
            output_file.write("%d, %g \n" % ((var_cnt + 1), this_var))
            var_cnt = var_cnt + 1
        output_file.write("\n\n\n")

        # finally the python formatted list
        var_cnt = 0
        output_file.write("Python-format list of input variables\n\n")
        for this_var in var_definition:
            current_type = str(this_var[VAR_TYPE_IND])
            current_desc = str(this_var[VAR_DESC_IND])
            output_file.write("%d, Type = %s, Desc = %s \n" % ((var_cnt + 1), current_type, current_desc))
            if current_type == VECTOR_TYPE:
                num_rows = int(this_var[VAR_CNT_IND])
                value_list = py_in_list[var_cnt]
                for ThisRow in range(num_rows):
                    output_file.write("%g,\n" % value_list[ThisRow])
                output_file.write("\n")
            var_cnt = var_cnt + 1
    # end of with block file closed.
    return


def OutputEcho(output_list, var_definition, py_out_list):
    """
    Echo out the outputs for debugging
    
    :param: output_list the output list for the GoldSim external element.
    :param: var_definition the definition from this file for outputs. Should be RET_VAR_LIST
    :param: py_out_list the list of "Python" structures of return values corresponding to RET_VAR_LIST
    """

    # globals
    global VECTOR_TYPE
    # local parameters
    out_file_name = "Echo_Outputs.csv"  # output file name
    # parameters
    # local variables
    var_cnt = 0  # the variable counter
    # now output
    with open(out_file_name, 'w', 0) as OutFID:
        # first output the variable definition from RET_VAR_LIST
        OutFID.write("Output variable definition:\n\n")
        OutFID.write("Index, Length, Type, Description, Time Series Type \n")
        for this_var in var_definition:
            current_type = str(this_var[VAR_TYPE_IND])
            current_desc = str(this_var[VAR_DESC_IND])

            OutFID.write("%d, %d, %s, %s\n" % (var_cnt + 1,
                                               this_var[VAR_CNT_IND], current_type, current_desc))
            var_cnt = var_cnt + 1
        OutFID.write("\n\n\n")
        # next do the Python structures returned from CImp
        var_cnt = 0
        OutFID.write("Python-format list of Output variables\n\n")
        for this_var in var_definition:
            current_type = str(this_var[VAR_TYPE_IND])
            current_desc = str(this_var[VAR_DESC_IND])
            OutFID.write("%d, Type = %s, Desc = %s \n" %
                         ((var_cnt + 1), current_type, current_desc))
            if current_type == VECTOR_TYPE:
                num_rows = int(this_var[VAR_CNT_IND])
                value_list = py_out_list[var_cnt]
                for ThisRow in range(num_rows):
                    OutFID.write("%g,\n" % value_list[ThisRow])
                OutFID.write("\n")
            var_cnt = var_cnt + 1
        OutFID.write("\n\n\n")
        # next do the list that will actually go back to GoldSim.
        var_cnt = 0
        OutFID.write("Sent to GoldSim: \n\n")
        OutFID.write("Index, Value \n")
        # echo out the actual list
        for this_var in output_list:
            OutFID.write("%d, %g \n" % ((var_cnt + 1), this_var))
            var_cnt = var_cnt + 1
    # end of with block file closed.
    return


def CustomCalculations(input_list, num_return):
    """
    Handles conversion from GoldSim format to Python style list. The function then passes the input to
    MyCustomCalculations for processing to IPhreeqc format before being ran in PHREEQC and passed back
    with conversions from PHREEQC to Python to GoldSim.

    If DEBUG_LEVEL == 1, this function will echo'd the inputs and outputs to
    text files for testing and debugging.
        
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
    current_indexes = 0

    tst_indexes.append(0)
    for ThisList in IN_VAR_LIST:
        current_type = str(ThisList[VAR_TYPE_IND])
        if current_type == VECTOR_TYPE:
            current_indexes = int(ThisList[VAR_CNT_IND])
            var_in_list = input_list[start_index:(start_index + current_indexes)]
            input_vector = var_in_list
            py_input_list.append(input_vector)
        # end switch
        start_index = start_index + current_indexes
        tst_indexes.append(start_index)

    if DEBUG_LEVEL == 1:
        InputEcho(input_list, IN_VAR_LIST, py_input_list)

    ret_var_list = MyCustomCalculations(py_input_list)

    if len(ret_var_list) != num_output_vars:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write("Received %d variables back from processing in "
                      "function CustomCalculations. Expected %d variables.\n" %
                      (len(ret_var_list), num_output_vars))
        return [-1]
    return_list = ret_var_list[0]

    if DEBUG_LEVEL:
        # noinspection PyTypeChecker
        OutputEcho(return_list, RET_VAR_LIST, ret_var_list)

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
    # local imports
    import datetime
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write("GoldQC.py completed successfully at %s.\n\n" % datetime.datetime.now().strftime("%x %H:%M"))
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

    WriteStringToLog(debug_string)
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
    global STEP
    global DEBUG_LEVEL

    import re
    from collections import OrderedDict
    from Converstions import MOLAR_MASS_LIST

    debug_string = ''

    if DEBUG_LEVEL:
        debug_string += str("Starting step %d\n" % STEP)
    element_values = input_list[0]

    if DEBUG_LEVEL:
        debug_string += str("Element Symbols: %s\n" % str(ELEMENTS))
        debug_string += str("Element Values:  %s\n" % str(element_values))
    input_string = ('SOLUTION %d\n'
                    '\tunits\tmg/l\n'
                    '\twater\t\t1\n' % STEP)
    element_dict = OrderedDict(zip(ELEMENTS, element_values))

    # Need to refactor based on final GoldSim inputs
    for element, value in element_dict.iteritems():
        input_string += str('\t' + element + '\t\t' + str(value) + '\n')

    input_string += str('EQUILIBRIUM_PHASES\n\tGypsum\t0\t0\n')

    # ---------------------------------------------------------------------------------
    # TOTALS MODE
    input_string += str('SELECTED_OUTPUT\n\t-totals ')
    for element in element_dict:
        input_string += str(element + ' ')
    # ---------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------
    # USER_PUNCH MODE
    # input_string += str('SELECTED_OUTPUT\nUSER_PUNCH\n\t-headings ')
    # for element in element_dict:
    #     input_string += str(element + ' ')
    # input_string += '\n-start\n'
    #
    # i = 1
    # for element in element_dict:
    #     input_string += str('\t' + str(i) + '0\tPUNCH TOT(\"' + element + '\") * ' + str(MOLAR_MASS_LIST[element]) +
    #                         ' * 1000\n')
    #     i += 1
    # input_string += '-end\n'
    # ----------------------------------------------------------------------------------
    input_string += '\nEND\n'

    # Input string created, Logging details.
    if DEBUG_LEVEL:
        debug_string += str('Input on Step %d\n' % STEP)
        debug_string += str(input_string)

    # calling PHREEQC
    phreeqc_values = process_input(input_string)

    if phreeqc_values is None:
        WriteStringToLog(debug_string)
        STEP += 1
        return [-2]

    # Processing PHREEQC output to GoldSim format
    headings = list(phreeqc_values[0])[-len(element_values):]
    values = list(phreeqc_values[2])[-len(element_values):]
    react = list(phreeqc_values[2])[-len(element_values):]

    if DEBUG_LEVEL:
        debug_string += str("headings : %s\n" % str(headings))
        debug_string += str("values   : %s\n" % str(values))
        debug_string += str("react(eq): %s\n" % str(react))

    # Converting mol/kgw to mg/l ONLY NEEDED IN TOTALS MODE
    i = 0
    while i < len(headings):
        headings[i] = re.sub('\(mol/kgw\)$', '', headings[i])
        values[i] = float(values[i] * MOLAR_MASS_LIST[headings[i]] * 1000.0)
        i += 1

    # Formatting values into GoldSim required format
    return_list = list()
    return_list.append(values)
    if DEBUG_LEVEL:
        debug_string += str("return list: " + str(return_list) + "\n\n")
        WriteStringToLog(debug_string)

    STEP += 1
    return return_list


def process_input(input_string):
    """
    Runs a selected input string on the PHREEQC connection and returns the output
    :param input_string: input for simulation
    :return: @see Dispatch.getSelectedOutputArray()
    """

    # globals
    global LOG_FILE_NAME
    global PHREEQC
    global STEP
    global DB_PATH

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
    # noinspection PyBroadException
    PHREEQC.OutputStringOn = True
    try:
        PHREEQC.RunString(input_string)
    except Exception:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write(str('Error at step %d: \n' % STEP))
            error = PHREEQC.GetErrorString()
            if error:
                Log.write(error)
                return None
    warning = PHREEQC.GetWarningString()  # TODO Investigate passing warning back to GoldSim
    if warning:
        with open(LOG_FILE_NAME, 'a', 0) as Log:
            Log.write(str('Warning at step %d: \n' % STEP))
            Log.write(warning)
    output = PHREEQC.GetSelectedOutputArray()
    # with open("out.txt", 'a', 0) as debug:
    #     debug.write(PHREEQC.GetOutputString().encode('utf8', 'replace'))
    return output


def WriteStringToLog(string):
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write(string)


def main():
    status = InitialChecks()
    if status:
        exit(status)
    test_list = [["0.12", "323", "458", "4.32", "0.34", "1.23", "95.6554"], 200.0]
    output = MyCustomCalculations(test_list)
    print output
    test_list2 = [["0.13", "343", "4438", "34232", "0.33244", "1.2343", "95.6532454"], 200.0]
    output = MyCustomCalculations(test_list2)
    print output
    WrapUpStuff()


if __name__ == "__main__":
    main()
