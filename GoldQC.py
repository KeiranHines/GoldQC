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

    def process_input(self, input_string):
        """
        Runs a selected input string on the database and returns the output
        :param input_string: input for simulation
        :return: @see Dispatch.getSelectedOutputArray()
        """
        if not self.dbase:
            raise DatabaseNotConnectedException("PHREEQC database not connected")
            return
        self.dbase.RunString(input_string)

        components = self.dbase.GetComponentList()
        # selected_output = self.make_selected_output(components)
        # print(selected_output)
        # i = self.dbase.RunString(selected_output)
        print self.dbase.RowCount
        output = self.dbase.GetSelectedOutputArray()
        return output

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