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

def generateAWL(filename, stepList, transitionList, digInDict, digOutDict):

    # create output file and write header. FIX: ask for overwrite:
    outfilename = filename.partition('.')[0] + '.awl'
    outfile = open(outfilename, 'w')
    outfile.write ('ORGANIZATION_BLOCK MAIN:OB1\nTITLE=Autogenerated by Graf2il V0.4\nBEGIN\n')

    nextNetwork = 1     # Network-counter for output file  

    # write transition definitions to awl-file: 
    for thisTransition in transitionList:
        nTransition, name, eid, fromStepn, fromStepMem, toStepn, condition, memory = thisTransition  # unpack tuple from List 

        outfile.write ('Network {0} // {1}\n'.format(nextNetwork, name))
        nextNetwork = nextNetwork + 1

        outfile.write ('LD      {0}\n'.format(fromStepMem))           # LD fromStep memory  (e.g. LD M0.0)
        
        # Check if condition is inverted or not. This is remembered by putting '/' as first charcter of condition String
        if condition[0] == '/':          # If inverting input...
            condition = condition[1:]   # Remove first character '/'
            outfile.write ('AN      {0}\n'.format(condition))         # AN condition        (e.g. AN I0.0)
        else:
            outfile.write ('A       {0}\n'.format(condition))         # A condition         (e.g. A I0.0)
        
           
        outfile.write ('=       {0}\n'.format(memory))                # = Mem               (e.g. = M0.1)

   
    # generate initial condition:
    outfile.write ('Network {0} // Initial condition\n'.format(nextNetwork))
    nextNetwork = nextNetwork + 1
    nStep = 0
    for step in stepList:
        if nStep == 0:      # initial step, do nothing
            a = 1
        elif nStep == 1:    # first step:
            outfile.write ('LDN     {0}\n'.format(step[4]))     # LDN step-memory for first step. Mem is in element 4.
        else:
            outfile.write ('AN      {0}\n'.format(step[4]))     # LD for all other steps
        nStep = nStep + 1

    outfile.write ('=       {0}\n'.format(stepList[0][4]))      # = mem of initial step. This is in list-element 0, Mem is in step-element 4.


    # generate step-activation networks:
    def findStepN(n, sList):
        "Find tuple step from unsorted stepList which has index n"
        for step in sList:
            number, name, action, eid, memory = step         
            if number != n:                             # in number we are looking for is not found, ...
                returnStep = []                         # make empty return
            else:
                returnStep = step                       # found, return current step and
                break                                   # exit for-loop
        if returnStep == []:
            raise (NameError, 'Step index not found' )
        return (returnStep)

    def findTransitionsFromStep (n, tList):
        "Find all transitions originating from step n"
        returnTransitions = []              # create empty List for returning result    
        for transition in tList:
            nTr, nameTr, eidTr, fromStepNTr, fromStepMemTr, toStepNTr, PLCInputTr, memoryTr = transition   # unpack current transition
            if fromStepNTr == n:
                returnTransitions.append(transition)    # append current transition if fromStep matches index
        if returnTransitions == []:
            raise (NameError, 'No transition from Step x found.')
        return (returnTransitions)    
        

    for thisTransition in transitionList:
        nTransition, name, eid, fromStepN, fromStepMem, toStepN, PLCInput, memory = thisTransition # unpack info about current transition
        
        toStep = findStepN(toStepN, stepList)   # find info about next Step

        toStepN, toStepName, toStepAction, toStepEid, toStepMemory = toStep # unpack info about toStep

        nextTransitions = findTransitionsFromStep (toStepN, transitionList) # find next Transition(s)


        # write the stuff into awl
        outfile.write ('Network {0} // {1} activates {2}\n'.format(nextNetwork, name, toStepName))
        nextNetwork = nextNetwork + 1    

        outfile.write ('LD      {0}\n'.format(memory))              #LD M_transition
        outfile.write ('O       {0}\n'.format(toStepMemory))        # O M_toStep

        # tricky part: add all following transistions away from toStep as NOTs
        for nextTran in nextTransitions:
            outfile.write ('AN      {0}\n'.format(nextTran[7]))     # AN memory of nextTran (mem is element no. 7)
        outfile.write ('=       {0}\n'.format(toStepMemory))        # network activates next Step 


    # generate output-networks for each step:
    def parse_actions (actionstring, outputfile, outDict):
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
                    outputfile.write ('S       {0}, 1\n'.format(outputChannel))   #set output
                else:
                    outputfile.write ('R       {0}, 1\n'.format(outputChannel))   #reset output
            elif setReset == '0':
                if inverted == 0:
                    outputfile.write ('R       {0}, 1\n'.format(outputChannel))   #reset output
                else:
                    outputfile.write ('S       {0}, 1\n'.format(outputChannel))   #set output  
            else:
                raise (NameError, 'unsupported output value')
        else:
            print ('Error: unsupported output action: ', actionstring)
            print
            raise (NameError, 'unsupported output action')
        if remainder != '':
            parse_actions (remainder, outputfile, outDict)


    for step in stepList:
        n, name, action, eid, memory = step

        if (action.strip() != '') and (action.strip() != ';'):  
            outfile.write ('Network {0} // set outputs for {1}\n'.format(nextNetwork, name))
            nextNetwork = nextNetwork + 1

            outfile.write ('LD      {0}\n'.format(memory))   #LD M_Step
        
            # action-string zerlegen und als actions reinschreiben
            parse_actions (action, outfile, digOutDict)





    # write footer of .awl and close file
    outfile.write('END_ORGANIZATION_BLOCK\nSUBROUTINE_BLOCK SBR_0:SBR0\nTITLE=SUBROUTINE COMMENTS\nBEGIN\nNetwork 1 // Network Title\n// Network Comment\nEND_SUBROUTINE_BLOCK\nINTERRUPT_BLOCK INT_0:INT0\nTITLE=INTERRUPT ROUTINE COMMENTS\nBEGIN\nNetwork 1 // Network Title\n// Network Comment\nEND_INTERRUPT_BLOCK\n')
    outfile.close()
    print ('.awl generated successfully. :-)')

