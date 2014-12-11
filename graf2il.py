import xml.etree.ElementTree as ET
import sys


filename = sys.argv[1] #get filename for xml-file from command line
print
print 'graf2il - converts a JGrafchart xml-file to Siemens Step 7 awl-file'
print 'Fritz Schimpf, version 0.2'
print
print 'opening file: ', filename
print

# parse XML with ElementTree
tree = ET.parse(filename)
root = tree.getroot()

# create output file and write header. FIX: ask for overwrite
outfilename = filename.partition('.')[0] + '.awl'
outfile = open(outfilename, 'w')
outfile.write ('ORGANIZATION_BLOCK MAIN:OB1\nTITLE=Autogenerated by Graf2il\nBEGIN\n')
#outfile.write ('// *** BEGIN of autogenerated code from graf2il ***\n')

#print 'found input(s):'
digInDict = {}                          #create dictionary for digital Inputs
for din in root.findall('DigitalIn'):
    channel = din.get('channel')    
    name = din.get('name')
    digInDict[name] = channel
#print digInDict
#print
#print 'found output(s):'
digOutDict = {}                          #create dictionary for digital outputs
for dout in root.findall('DigitalOut'):
    channel = dout.get('channel')    
    name = dout.get('name')
    digOutDict[name] = channel
#print digOutDict
print 'found in- and outputs:'
for i in sorted(digInDict):
    print digInDict[i].ljust(5), i
for i in sorted(digOutDict):
    print digOutDict[i].ljust(5), i
print

MDict = {}          # create Dictionary for PLC-Memory-Bits
nextM = 0           # counter for next unused Memory-Bit
stepDict = {}       # create Dictionary for Steps and their IDs
stepNameDict = {}   # create Dictionary for Step IDs and the namestings
nextStep = 0        # Step-counter  
nextNetwork = 1     # Network-counter for output file                         

def mem(n):
    "Generate memory-bit-notation (e.g. M0.0) from number of memory-bit (Mx.y)"
    mBit = (n / 8, n % 8)
    memstring = 'M{0[0]}.{0[1]}'.format(mBit)
    return memstring

#print 'found initial step:'
# Fix: Fehler abfangen: Kein Initial Step / mehrere

stepList = []                                 # create empty list for storing transition data

for initialStep in root.findall('GCInitialStep'):
    name = initialStep.get('name')
    action = initialStep.get('actionText')
    eid = initialStep.get('id')
    #print name, action, eid
    nameString = 'Initial_Step_{0}'.format(name)    # generate name-sring for State
    MDict[nameString] = mem(nextM)                  # add name and M to dictionary

    stepDict[eid] = nextStep                        # add Step-ID to dictionary
    stepNameDict[eid] = nameString                  # add Step name to dictionary

    # new: Add step to stepList    
    thisStep = nextStep, nameString, action, eid, mem(nextM)
    stepList.append(thisStep)

    nextM = nextM + 1
    nextStep = nextStep + 1

#print
print 'found step(s):'
for step in root.findall('GCStep'):
    name = step.get('name')
    action = step.get('actionText')
    eid = step.get('id')
    # print name, action, eid
    nameString = 'Step_{0}_{1}'.format(nextStep, name)    # generate name-sring for State
    MDict[nameString] = mem(nextM)                  # add name and M to dictionary
    stepDict[eid] = nextStep                        # add Step-ID to dictionary 
    stepNameDict[eid] = nameString                  # add Step name to dictionary
    
    # new: Add step to stepList    
    thisStep = nextStep, nameString, action, eid, mem(nextM)
    stepList.append(thisStep)
    
    nextM = nextM + 1
    nextStep = nextStep + 1

for thisStep in stepList:
    n, name, action, eid, memory = thisStep    
    print str(n).ljust(3), memory.ljust(5), name
print
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
            toStep = link.get('toObject')           # Transition geht zu toStep
            break;
    for link in root.findall('GCLink'):
        toId = link.get('toObject')
        if toId == eid:
            fromStep = link.get('fromObject')       # Transition kommt von fromStep
            break;

    # find Step numbers from IDs
    fromStepn = stepDict[fromStep]
    toStepn =  stepDict[toStep]

    nameString = 'Transition_{0}_{1}'.format(fromStepn, toStepn)    # generate name-sring for Transition
        
    MDict[nameString] = mem(nextM)                       # add name and M to dictionary


    # evaluate condition (so far only support for one condition, check if true)
    condition = digInDict[name]    



    # make new version of transition-list
    thisTransition = nTransition, nameString, eid, fromStepn, toStepn, condition, mem(nextM)     # pack tuple with transition info
    nextM = nextM + 1
    transitionList.append(thisTransition)                            # add new transition to list



    # old..........
    #print nameString, name, condition

    outfile.write ('Network {0} // {1}\n'.format(nextNetwork, nameString))
    nextNetwork = nextNetwork + 1

    fromStepName = stepNameDict[fromStep]   # find namesting of fromStep
    fromStepMem = MDict[fromStepName]       # find Memory-bit of fromStep
    outfile.write ('LD      {0}\n'.format(fromStepMem))
    outfile.write ('A       {0}\n'.format(condition))
    outfile.write ('=       {0}\n'.format(MDict[nameString]))

for thisTransition in transitionList:
    nTransition, name, eid, fromStepn, toStepn, condition, memory = thisTransition
    print str(nTransition).ljust(3), memory.ljust(5), name


print
print 'generating initial condition:'
outfile.write ('Network {0} // Initial condition\n'.format(nextNetwork))
nextNetwork = nextNetwork + 1
nStep = 0
for step in root.findall('GCStep'):
    name = step.get('name')
    eid = step.get('id')    
    stepName = stepNameDict[eid]        # finde namestring of each step
    stepMem = MDict[stepName]           # find Memory-Bit
    if nStep == 0:
        outfile.write ('LDN     {0}\n'.format(stepMem))
    else:
        outfile.write ('AN      {0}\n'.format(stepMem))
    nStep = nStep + 1
for initialStep in root.findall('GCInitialStep'):
    name = initialStep.get('name')
    eid = initialStep.get('id')
    stepName = stepNameDict[eid]        # finde namestring of initial step
    stepMem = MDict[stepName]           # find Memory-Bit
outfile.write ('=       {0}\n'.format(stepMem))
print '... done'
print
print 'generating step activation networks'
"""for transition in root.findall('GCTransition'):
    name = transition.get('actionText')
    eid = transition.get('id')
    
    # find links to steps:    
    for link in root.findall('GCLink'):
        fromId = link.get('fromObject')
        if fromId == eid:
            toStep = link.get('toObject')           # Transition geht zu toStep
            break;
    for link in root.findall('GCLink'):
        toId = link.get('toObject')
        if toId == eid:
            fromStep = link.get('fromObject')       # Transition kommt von fromStep
            break;

    # find Step numbers from IDs
    fromStepn = stepDict[fromStep]
    toStepn =  stepDict[toStep]

    nameString = 'Transition_{0}_{1}'.format(fromStepn, toStepn)    # generate name-sring for Transition

    outfile.write ('Network {0} // {1} activates {2}\n'.format(nextNetwork, nameString, stepNameDict[toStep]))
    nextNetwork = nextNetwork + 1

    toStepName = stepNameDict[toStep]   # find namesting of fromStep
    toStepMem = MDict[toStepName]       # find Memory-bit of fromStep
    outfile.write ('LD      {0}\n'.format(MDict[nameString]))   #LD M_transition
    outfile.write ('O       {0}\n'.format(toStepMem))           # O M_toStep
    
    # find next transition (this transition is pointing to a step which is pointing to a transition again.)
    for link in root.findall('GCLink'):
        fromId = link.get('fromObject')
        if fromId == toStep:                        # vom Step auf den die Transition zeigt...
            nextTran = link.get('toObject')         # to next Transition
            break;
    # now find next step on which nextTran is pointing
    for link in root.findall('GCLink'):
        fromId = link.get('fromObject')
        if fromId == nextTran:                     
            nextNextStep = link.get('toObject')         # to next Step
            break;
    nextNextStepn = stepDict[nextNextStep]    
    nextTranName = 'Transition_{0}_{1}'.format(toStepn, nextNextStepn)    # generate name-sring for State
    nextTranMem = MDict[nextTranName]
    outfile.write ('AN      {0}\n'.format(nextTranMem))         # AN nextTran
    outfile.write ('=       {0}\n'.format(toStepMem))
"""

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
        raise NameError, 'Step index not found' 
    return (returnStep)

def findTransitionsFromStep (n, tList):
    "Find all transitions originating from step n"
    returnTransitions = []              # create empty List for returning result    
    for transition in tList:
        nTr, nameTr, eidTr, fromStepNTr, toStepNTr, PLCInputTr, memoryTr = transition   # unpack current transition
        if fromStepNTr == n:
            returnTransitions.append(transition)    # append current transition if fromStep matches index
    if returnTransitions == []:
        raise NameError, 'No transition from Step x found.'
    return (returnTransitions)    
    

for thisTransition in transitionList:
    nTransition, name, eid, fromStepN, toStepN, PLCInput, memory = thisTransition # unpack info about current transition
    
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
        outfile.write ('AN      {0}\n'.format(nextTran[6]))     # AN memory of nextTran (mem is element no. 6)
    outfile.write ('=       {0}\n'.format(toStepMemory))        # network activates next Step


print '... done'
print

print 'generating output networks'
def parse_actions (actionstring, outputfile, outDict):
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
        #print output, setReset
        if setReset == '1':
            outputfile.write ('S       {0}, 1\n'.format(outDict[output]))   #set output
        elif setReset == '0':
            outputfile.write ('R       {0}, 1\n'.format(outDict[output]))   #reset output
        else:
            raise NameError, 'unsupported output value'
    else:
        raise NameError, 'unsupported output action'
    if remainder != '':
        parse_actions (remainder, outputfile, outDict)


nextStep = 0
for initialStep in root.findall('GCInitialStep'):
    name = initialStep.get('name')
    action = initialStep.get('actionText')
    eid = initialStep.get('id')
    nameString = 'Initial_Step_{0}'.format(name)    # generate name-sring for State

    if action != '':  
        outfile.write ('Network {0} // set outputs for {1}\n'.format(nextNetwork, nameString))
        nextNetwork = nextNetwork + 1

        outfile.write ('LD      {0}\n'.format(MDict[nameString]))   #LD M_Step
        nextStep = nextStep + 1
    
        # action-string zerlegen und als actions reinschreiben
        parse_actions (action, outfile, digOutDict)

    
for step in root.findall('GCStep'):
    name = step.get('name')
    action = step.get('actionText').strip()
    eid = step.get('id')
    nameString = 'Step_{0}_{1}'.format(nextStep, name)    # generate name-sring for State

    if action != '':  
        outfile.write ('Network {0} // set outputs for {1}\n'.format(nextNetwork, nameString))
        nextNetwork = nextNetwork + 1

        outfile.write ('LD      {0}\n'.format(MDict[nameString]))   #LD M_Step
        nextStep = nextStep + 1
    
        # action-string zerlegen und als actions reinschreiben
        parse_actions (action, outfile, digOutDict)

print '... done'

print
print 'Created memory list:'
for i in sorted(MDict):
    print i.ljust(30), MDict[i]
print


#outfile.write ('// *** END of autogenerated code from graf2il ***\n')
outfile.write('END_ORGANIZATION_BLOCK\nSUBROUTINE_BLOCK SBR_0:SBR0\nTITLE=SUBROUTINE COMMENTS\nBEGIN\nNetwork 1 // Network Title\n// Network Comment\nEND_SUBROUTINE_BLOCK\nINTERRUPT_BLOCK INT_0:INT0\nTITLE=INTERRUPT ROUTINE COMMENTS\nBEGIN\nNetwork 1 // Network Title\n// Network Comment\nEND_INTERRUPT_BLOCK\n')
outfile.close()
print 'finished successfully :-)'

