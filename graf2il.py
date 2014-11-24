import xml.etree.ElementTree as ET
import sys


filename = sys.argv[1] #get filename for xml-file from command line
print
print 'graf2il - converts a JGrafchart xml-file to Siemens Step 7 awl-file'
print 'Fritz Schimpf, version 0.1'
print
print 'opening file: ', filename
print

# parse XML with ElementTree
tree = ET.parse(filename)
root = tree.getroot()

# create output file and write header. FIX: ask for overwrite
outfile = open('testoutput.awl', 'w')
outfile.write ('ORGANIZATION_BLOCK MAIN:OB1\nTITLE=Autogenerated by Graph2IL\nBEGIN\n')
#outfile.write ('// *** BEGIN of autogenerated code from graf2il ***\n')

print 'found input(s):'
digInDict = {}                          #create dictionary for digital Inputs
for din in root.findall('DigitalIn'):
    channel = din.get('channel')    
    name = din.get('name')
    digInDict[name] = channel
print digInDict
print
print 'found output(s):'
digOutDict = {}                          #create dictionary for digital outputs
for dout in root.findall('DigitalOut'):
    channel = dout.get('channel')    
    name = dout.get('name')
    digOutDict[name] = channel
print digOutDict
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

print 'found initial step:'
# Fix: Fehler abfangen: Kein Initial Step / mehrere
for initialStep in root.findall('GCInitialStep'):
    name = initialStep.get('name')
    action = initialStep.get('actionText')
    eid = initialStep.get('id')
    print name, action, eid
    nameString = 'Initial_Step_{0}'.format(name)    # generate name-sring for State
    MDict[nameString] = mem(nextM)                  # add name and M to dictionary
    nextM = nextM + 1
    stepDict[eid] = nextStep                        # add Step-ID to dictionary
    stepNameDict[eid] = nameString                  # add Step name to dictionary
    nextStep = nextStep + 1
print
print 'found step(s):'
for step in root.findall('GCStep'):
    name = step.get('name')
    action = step.get('actionText')
    eid = step.get('id')
    print name, action, eid
    nameString = 'Step_{0}_{1}'.format(nextStep, name)    # generate name-sring for State
    MDict[nameString] = mem(nextM)                  # add name and M to dictionary
    nextM = nextM + 1
    stepDict[eid] = nextStep                        # add Step-ID to dictionary 
    stepNameDict[eid] = nameString                  # add Step name to dictionary
    nextStep = nextStep + 1
print
print 'Translating transitions:'
for transition in root.findall('GCTransition'):
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

    nameString = 'Transition_{0}_{1}'.format(fromStepn, toStepn)    # generate name-sring for State
    MDict[nameString] = mem(nextM)                       # add name and M to dictionary
    nextM = nextM + 1

    # evaluate condition (so far only support for one condition, check if true)
    condition = digInDict[name]    

    print nameString, name, condition

    outfile.write ('Network {0} // {1}\n'.format(nextNetwork, nameString))
    nextNetwork = nextNetwork + 1

    fromStepName = stepNameDict[fromStep]   # find namesting of fromStep
    fromStepMem = MDict[fromStepName]       # find Memory-bit of fromStep
    outfile.write ('LD      {0}\n'.format(fromStepMem))
    outfile.write ('A       {0}\n'.format(condition))
    outfile.write ('=       {0}\n'.format(MDict[nameString]))
print '... done'
print
print 'Translating initial condition: '
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
print 'Created memory list:'
print MDict
print


#outfile.write ('// *** END of autogenerated code from graf2il ***\n')
outfile.write('END_ORGANIZATION_BLOCK\nSUBROUTINE_BLOCK SBR_0:SBR0\nTITLE=SUBROUTINE COMMENTS\nBEGIN\nNetwork 1 // Network Title\n// Network Comment\nEND_SUBROUTINE_BLOCK\nINTERRUPT_BLOCK INT_0:INT0\nTITLE=INTERRUPT ROUTINE COMMENTS\nBEGIN\nNetwork 1 // Network Title\n// Network Comment\nEND_INTERRUPT_BLOCK\n')
outfile.close()

