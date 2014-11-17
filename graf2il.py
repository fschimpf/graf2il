import xml.etree.ElementTree as ET
import sys

filename = sys.argv[1] #get filename for xml-file from command line
print
print 'graf2il - converts a JGrafchart xml-file to Siemens Step 7 awl-file'
print 'Fritz Schimpf, version 0.1'
print
print 'opening file: ', filename
print

tree = ET.parse(filename)
root = tree.getroot()

print 'found input(s):'
for din in root.findall('DigitalIn'):
    channel = din.get('channel')    
    name = din.get('name')
    print channel, name
print
print 'found output(s):'
for dout in root.findall('DigitalOut'):
    channel = dout.get('channel')    
    name = dout.get('name')
    print channel, name
print
print 'found initial step:'
for initialStep in root.findall('GCInitialStep'):
    name = initialStep.get('name')
    action = initialStep.get('actionText')
    eid = initialStep.get('id')
    print name, action, eid
print
print 'found step(s):'
for step in root.findall('GCStep'):
    name = step.get('name')
    action = step.get('actionText')
    eid = step.get('id')
    print name, action, eid
print
print 'found transition(s):'
for transition in root.findall('GCTransition'):
    name = transition.get('actionText')
    eid = transition.get('id')
    print name, eid
print
print 'found link(s):'
for link in root.findall('GCLink'):
    fromId = link.get('fromObject')
    toId = link.get('toObject')
    print fromId, toId

