"""
    Copyright 2015 Fritz Schimpf       

    This file is part of graf2il.py.

    graf2il is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    graf2il is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with graf2il.  If not, see <http://www.gnu.org/licenses/>.
"""

def generateSCL(filename, stepList, transitionList, digInDict, digOutDict):

    # create output file and write header. FIX: ask for overwrite:
    outfilename = filename.partition('.')[0] + '.scl'
    outfile = open(outfilename, 'w')

    outfile.write ('FUNCTION_BLOCK "{0}"\n'.format(filename.partition('.')[0]))
    outfile.write ('VERSION : 0.1\n')

    # create input veriables for block:
    outfile.write ('    VAR_INPUT\n')

    outfile.write ('    END_VAR\n')


    # write footer and close file
    outfile.write('END_FUNCTION_BLOCK\n')
    outfile.close()
    print '.scl generated successfully. :-)'
