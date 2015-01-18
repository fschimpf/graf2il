"""    
    graf2il.py copyright 2015 Fritz Schimpf    

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import xml.etree.ElementTree as ET
import sys
from generateAWL import generateAWL
from generateSCL import generateSCL 

def main():
    filename = sys.argv[1]      # get filename for xml-file from command line
    outputType = sys.argv[2]    # get type of desired output from command line. Valid: "awl" for S7-200 and "scl" for S7-1200
    print
    print 'graf2il - converts a JGrafchart xml-file to Siemens Step 7 awl-file'
    print 'Fritz Schimpf, version 0.3'
    print
    print 'opening file: ', filename
    print 'output-type: ', outputType
    print


    # parse XML with ElementTree
    tree = ET.parse(filename)
    root = tree.getroot()


    # Find digital input- and output-definitions and create dictionaries
    digInDict = {}                          #create dictionary for digital Inputs
    for din in root.findall('DigitalIn'):   # Look for normal inputs
        channel = din.get('channel')    
        name = din.get('name')
        digInDict[name] = channel

    for din in root.findall('DigitalIn1'):  # Look for inverting inputs
        channel = '/' + din.get('channel')  # put / in front of input-channel for remembering that it has to be inverting  
        name = din.get('name')        
        digInDict[name] = channel

    digOutDict = {}                          #create dictionary for digital outputs
    for dout in root.findall('DigitalOut'):  # Look for normal outputs
        channel = dout.get('channel')    
        name = dout.get('name')
        digOutDict[name] = channel

    for dout in root.findall('DigitalOut1'): # Look for inverted outputs
        channel = '/' + dout.get('channel')  # put / in front of input-channel for remembering that it has to be inverted  
        name = dout.get('name')
        digOutDict[name] = channel

    print 'found in- and outputs:'
    for i in sorted(digInDict):
        print digInDict[i].ljust(5), i
    for i in sorted(digOutDict):
        print digOutDict[i].ljust(5), i
    print


    # Parse sequence-Steps from XML and store them in stepList

    def mem(n):
        "Generate memory-bit-notation (e.g. M0.0) from number of memory-bit (Mx.y)"
        mBit = (n / 8, n % 8)
        memstring = 'M{0[0]}.{0[1]}'.format(mBit)
        return memstring

    nextM = 0           # counter for next unused Memory-Bit
    nextStep = 0        # Step-counter  

    print 'found step(s):'
    stepList = []                                 # create empty list for storing transition data

    for initialStep in root.findall('GCInitialStep'):
        name = initialStep.get('name')
        action = initialStep.get('actionText')
        eid = initialStep.get('id')
        nameString = 'Initial_Step_{0}'.format(name)    # generate name-sring for State

        # Add step to stepList    
        thisStep = nextStep, nameString, action, eid, mem(nextM)
        stepList.append(thisStep)

        nextM = nextM + 1
        nextStep = nextStep + 1

    for step in root.findall('GCStep'):
        name = step.get('name')
        action = step.get('actionText')
        eid = step.get('id')
        nameString = 'Step_{0}_{1}'.format(nextStep, name)    # generate name-sring for State
         
        # Add step to stepList    
        thisStep = nextStep, nameString, action, eid, mem(nextM)
        stepList.append(thisStep)
        
        nextM = nextM + 1
        nextStep = nextStep + 1

    for thisStep in stepList:
        n, name, action, eid, memory = thisStep    
        print str(n).ljust(3), memory.ljust(5), name
    print


    def findStepEid(eid, sList):
        "Find step with ID-String eid from unsorted stepList"
        for step in sList:
            number, name, action, stepEid, memory = step         
            if stepEid != eid:                          # id we are looking for is not found, ...
                returnStep = []                         # make empty return
            else:
                returnStep = step                       # found, return current step and
                break                                   # exit for-loop
        if returnStep == []:
            raise NameError, 'Step-id not found in stepList' 
        return (returnStep)


    # Parse Transitions from XML and store them in transitionList
    print 'found transitions:'
    nTransition = 0                                     # counter for Transitions
    transitionList = []                                 # create empty list for storing transition data
    for transition in root.findall('GCTransition'):
        nTransition = nTransition + 1
        name = transition.get('actionText')
        eid = transition.get('id')
        
        # find links to steps:    
        for link in root.findall('GCLink'):
            fromId = link.get('fromObject')
            if fromId == eid:
                toStepEid = link.get('toObject')           # Transition geht zu toStep
                break;
        for link in root.findall('GCLink'):
            toId = link.get('toObject')
            if toId == eid:
                fromStepEid = link.get('fromObject')       # Transition kommt von fromStep
                break;

        # find Step numbers from IDs
        fromStep = findStepEid(fromStepEid, stepList)     # find step with right id  
        fromStepn = fromStep[0]                           # step-number is in element 0 of tuple
        fromStepMem = fromStep[4]                         # step-memory-location is in element 4 of tuple  

        toStep = findStepEid(toStepEid, stepList)     # find step with right id  
        toStepn = toStep[0]                           # step-number is in element 0 of tuple  

        nameString = 'Transition_{0}_{1}'.format(fromStepn, toStepn)    # generate name-sring for Transition
            
        # evaluate condition (so far only support for one condition, check if true)
        condition = digInDict[name]



        thisTransition = nTransition, nameString, eid, fromStepn, fromStepMem, toStepn, condition, mem(nextM)     # pack tuple with transition info
        transitionList.append(thisTransition)                            # add new transition to list

        nextM = nextM + 1   # Next unused Memory-Location + 1        

    # Print transition list
    for thisTransition in transitionList:
        nTransition, name, eid, fromStepn, fromStepMem, toStepn, condition, memory = thisTransition
        print str(nTransition).ljust(3), memory.ljust(5), name

    print '... parsing XML done'

    print
    print 'Created memory list:'
    for step in stepList:
        print step[4].ljust(5), step[1]
    for transition in transitionList:
        print transition[6].ljust(5), transition[1]

    print

    if outputType == 'awl':
        print 'Generating .awl'
        generateAWL(filename, stepList, transitionList, digInDict, digOutDict)
    elif outputType == 'scl':
        print 'Generating .scl'
        generateSCL(filename, stepList, transitionList, digInDict, digOutDict)
    else:
        print 'No valid output type selected. No output file created. Valid types are: awl, scl'


if __name__ == '__main__':  
    main()

