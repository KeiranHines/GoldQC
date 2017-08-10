"""
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
"""
import os, sys
import pythoncom,pywintypes
from win32com.client import Dispatch
from Exceptions import DatabaseNotConnectedException
import datetime

# Module level globals.
CUSTOM_MODULE_VERSION = 0.1         # module version --- REQUIRED
LOG_FILE_NAME = "TestLog.txt"       # log file name --- REQUIRED
PHREEQC = None


def SetStuffUp():
    """
    Required function for Linkage.py to link the GoldSim technologies package an IPHREEQC COM connection
    :return:
        Integer: 0 = good; 1 = something went wrong
    """
    global PHREEQC
    global LOG_FILE_NAME
    db_path = "database/phreeqc.dat"
    with open(LOG_FILE_NAME, 'w', 0) as Log:
        try:
            PHREEQC = Dispatch('IPhreeqcCOM.Object')
        except pythoncom.ole_error:
            Log.write("Error Could not find IPhreeqcCOM, are you sure its installed?\n")
            return 1
        try:
            PHREEQC.LoadDatabase(db_path) # TODO Make more generic maybe with a config file.
        except pywintypes.com_error:
            Log.write("Error Could not load database file %s\n" % db_path)
            return 1
        Log.write("Starting GoldQC.py script at %s.\n\n" % datetime.datetime.now().strftime("%x %H:%M"))
    return 0

def WrapUpLogFile(logfilename):
    """
    Required to end off the log file
    :param logfilename: the name of the logfile
    :return: None
    """

    global LOG_FILE_NAME
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write("GoldQC.py completed successfully at %s.\n\n" % datetime.datetime.now().strftime("%x %H:%M"))
    return

def MyCustomCalculations(PyInputList):
    """
    Required function for completing the PHREEQC side of the calculations first processes the input from GoldSim into
    a PHREEQC input/SelectedOutput string then calls process_input to have it processed by PHREEQC
    :param PyInputList: a list of values provided from GoldSim for processing
    :return: RET_VAR_LIST list of output values in the form GoldSim Expects them to be returned.
    """
    #imports
    from CustomModule import RET_VAR_LIST



def process_input(input_string):
    """
    Runs a selected input string on the PHREEQC connection and returns the output
    :param input_string: input for simulation
    :return: @see Dispatch.getSelectedOutputArray()
    """

    if not PHREEQC:
        raise DatabaseNotConnectedException("PHREEQC database not connected")
        return
    PHREEQC.RunString(input_string)
    output = PHREEQC.GetSelectedOutputArray()
    with open(LOG_FILE_NAME, 'a', 0) as Log:
        Log.write("Output-----------------\n\n")
        Log.write(output)
        Log.write("End-of-Output----------\n\n")
    return output

class IPhreeqcConnection:

    def __init__(self):
        self.dbase = None

    def connect_database(self, db_path):
        """
        Loads the PHREEQC COM connection and connects PHREEQC to the requested database file.
        :param db_path:
        """
        try:
            self.dbase = Dispatch('IPhreeqcCOM.Object')
        except pythoncom.ole_error:
            sys.stderr.write("Error Could not find IPhreeqcCOM, are you sure its installed?\n")
            exit(1)
        try:
            self.dbase.LoadDatabase(db_path)
        except pywintypes.com_error:
            sys.stderr.write("Error Could not load database file %s\n"%(db_path))
            exit(1)

    @staticmethod
    def make_selected_output(components):
        """
       Build SELECTED_OUTPUT data block to retrieve only important information from the PHREEQC calculation
       :param components The list of components from the database input. @see IPHreeqc.COM GetComponentList()

       """
        headings = "-headings    cb    H    O    "
        headings += '\t'.join(components)
        selected_output = """
               SELECTED_OUTPUT
                   -reset false
               USER_PUNCH
               """
        selected_output += headings + "\n"
        # charge balance, H, and O
        code = '10 w = TOT("water")\n'
        code += '20 PUNCH CHARGE_BALANCE, TOTMOLE("H"), TOTMOLE("O")\n'
        # All other elements
        lino = 30
        for component in components:
            code += '%d PUNCH w*TOT(\"%s\")\n' % (lino, component)
            lino += 10
        selected_output += code
        return selected_output


if __name__ == '__main__':
    # TESTING ONLY TODO REMOVE
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
    iphreeqc = IPhreeqcConnection()
    try:
        iphreeqc.connect_database("database/phreeqc.dat")
    except OSError as e:
        print e
    results = iphreeqc.process_input(INPUT_STRING) #Update to read from IPHREEQC database
    heading = ''
    for r in results[0]:
        heading += r + "\t"
    print heading
    for r in results[1:]:
        line = ''
        for i in r:
            line += str(i) + "\t"
        print line