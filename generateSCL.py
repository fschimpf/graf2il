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

    outfile.write ('(* File autogenerated by graf2il.py *)\n\n')
    outfile.write ('FUNCTION_BLOCK "{0}"\n'.format(filename.partition('.')[0]))
    outfile.write ('VERSION : 0.1\n\n')

    # create input veriables for block:
    outfile.write ('    VAR_INPUT\n')
    for i in sorted(digInDict):
        outfile.write ('        {0} : Bool; (* attach to {1} *)\n'.format(i, digInDict[i]))
    outfile.write ('    END_VAR\n\n')

    # create output veriables for block:
    outfile.write ('    VAR_OUTPUT\n')
    for i in sorted(digOutDict):
        outfile.write ('        {0} : Bool; (* attach to {1} *)\n'.format(i, digOutDict[i]))
    outfile.write ('    END_VAR\n\n')

    # create variables for states:
    outfile.write ('    VAR\n')
    for thisStep in stepList:
        number, name, action, eid, memory = thisStep    # unpack tuple
        outfile.write ('        {0} : Bool;\n'.format(name))
    
    # create variables for transitions:
    for thisTransition in transitionList:
        nTransition, name, eid, fromStepn, fromStepMem, toStepn, condition, memory = thisTransition  # unpack tuple from List 
        outfile.write ('        {0} : Bool;\n'.format(name))
    outfile.write ('    END_VAR\n\n')

    # start to write program block, transitions
    outfile.write ('BEGIN\n')
    outfile.write ('    (* Transitions *)\n')

    for thisTransition in transitionList:
        nTransition, name, eid, fromStepn, fromStepMem, toStepn, condition, memory = thisTransition  # unpack tuple from List
        conditionVariableName = 'switch_xyz'    # REPLACE!
        fromStepName = 'fromStepName'           # REPLACE! 
        outfile.write ('    IF #{0} AND #{1} THEN\n'.format(fromStepName, conditionVariableName))  
        outfile.write ('        {0} := TRUE;\n'.format(name))
        outfile.write ('    END_IF;\n')      
    outfile.write ('\n')    

    # set initial state
    outfile.write ('    (* Set initial state if none is active *)\n')
    outfile.write ('    IF NOT (')

    nStep = 0
    for thisStep in stepList:
        number, name, action, eid, memory = thisStep    # unpack tuple
        if nStep == 0:      # initial step, do nothing
            a = 1
        elif nStep == 1:    # first step:
            outfile.write ('#{0}'.format(name))            # "#variableName"
        else:
            outfile.write (' OR #{0}'.format(name))      # "OR #variableName" for all other steps
        nStep = nStep + 1

    outfile.write (') THEN\n')      # finish the line
    number, name, action, eid, memory = stepList[0]    # unpack tuple for initial step
    outfile.write ('        #{0} := TRUE;\n'.format(name))
    outfile.write ('    END_IF;\n\n')
 
    # let transitions activate states:
    outfile.write ('    (* Transitions activate steps *)\n')
    for thisTransition in transitionList:
        nTransition, name, eid, fromStepn, fromStepMem, toStepn, condition, memory = thisTransition  # unpack tuple from List
        toStepName = 'toStepName'                       # REPLACE!
        nextTransitionName = 'nextTransitionName'       # REPLACE!
        outfile.write ('    IF (#{0} OR #{1}) AND NOT #{2} THEN\n'.format(name, toStepName, nextTransitionName))
        outfile.write ('        #{0} := TRUE;\n'.format(toStepName))
        outfile.write ('    END_IF;\n')
    outfile.write ('\n')  

    # set outputs:
    def parse_actions (actionstring, outputfile, outDict):
        "parses the action string and writes result into .scl-file. Calls itself recursively."
        inverted = 0
        actionstring = actionstring.strip()    
        separated = actionstring.partition(';')
        action = separated[0].strip()
        remainder = separated[2].strip()    
        separated = action.partition('=')
        output = separated[0].strip()
        setReset = separated[2].strip()
        separated = output.partition(' ')
        if separated[0] == 'S':
            output = separated[2].strip()
            outputChannel = outDict[output]
            if outputChannel[0] == '/':         # channel has to be inverted
                inverted = 1
                outputChannel = outputChannel[1:]     # remove '/' from channel-string

            if setReset == '1':
                if inverted == 0:
                    outputfile.write ('        #{0} := TRUE;\n'.format(output))   #set output
                else:
                    outputfile.write ('        #{0} := FALSE;\n'.format(output))   #reset output
            elif setReset == '0':
                if inverted == 0:
                    outputfile.write ('        #{0} := FALSE;\n'.format(output))   #reset output
                else:
                    outputfile.write ('        #{0} := TRUE;\n'.format(output))   #set output  
            else:
                raise NameError, 'unsupported output value'
        else:
            raise NameError, 'unsupported output action'
        if remainder != '':
            parse_actions (remainder, outputfile, outDict)


    outfile.write ('    (* Set outputs *)\n')
    for thisStep in stepList:
        number, name, action, eid, memory = thisStep    # unpack tuple
        if action.strip() != '':
            outfile.write ('    IF #{0} THEN\n'.format(name))
            parse_actions (action, outfile, digOutDict) # action-string zerlegen und als actions reinschreiben
            outfile.write ('    END_IF;\n')
    outfile.write ('\n') 

        




    # write footer and close file
    outfile.write('END_FUNCTION_BLOCK\n')
    outfile.close()
    print '.scl generated successfully. :-)'
