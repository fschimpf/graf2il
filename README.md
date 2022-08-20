# graf2il

graf2il is a python script for translating a .xml-file created with JGrafchart (http://www.control.lth.se/grafchart/) to an instruction list (.awl)-file. The .awl-file can be imported into Siemens' Step7.

The toolchain consisting JGrafchart and graf2il makes it possible to program control sequences for the S7-200 PLCs in a graphical way.

Update: SCL is supported as second target language. This makes it possible to generate source files which can be imported into TIA portal. The sequence can then be integrated into the project as a function block.


## Usage for S7-200
1. Create a control graph in JGrafchart.
2. Use the Compile-Button in JGrafchart to find any errors.
3. Save the project as an .xml-file
4. Invoke graf2il: python graf2il.py "your-control-sequence.xml" awl
5. graf2il creates the file "your-control-sequence.awl"
6. Start Step7, create a new project for any S7-200 PLC.
7. Go to File-Import and choose the file "your-control-sequence.awl"
8. Download the program to the PLC and test...


## Usage for TIA portal (e.g. S7-1200)
1. Create a control graph in JGrafchart.
2. Use the Compile-Button in JGrafchart to find any errors.
3. Save the project as an .xml-file
4. Invoke graf2il: python graf2il.py "your-control-sequence.xml" scl
5. graf2il creates the file "your-control-sequence.scl"
6. Start TIA portal, create a new project.
7. Go to "External Source Files" and add the created "your-control-sequence.scl"
8. Right click on "your-control-sequence.scl" and select "Generate blocks from source".
9. Drag the newly created block into your program and connect the inputs and outputs.
10. Download the program to the PLC and test...


## Limitations / usage of the JGrafchart-blocks
graf2il does not support the whole Grafchart-language. From JGrafchart only the following blocks are supported:
- digital input
- digital input (inverse logic)
- digital output
- digital output (inverse logic)
- initial step
- step
- transition

Input and output blocks:
- Use input and output blocks for assigning variable names to PLC inputs or outputs.
- Example: Take a block "Digital Input", replace the 0 in "Chan: 0" by the desired PLC-input, e.g. "I0.0". Replace DIn by your desired variable name, e.g. InputButton1
- All inputs and outputs used in the program have to be defined by digital input or output blocks. 

Step actions can only be
- "S yourOutput = 1;" for setting an output
- or "S yourOutput = 0;" for resetting an output.
- "yourOutput" has to be defined by an output or inverting output block.
- it is possible to have more than one action per step.

Transitions:
- Conditions can be inputs defined in the blocks digital input and digital input (inverse logic).
- Conditions in transitions can only be checked for TRUE.
- If a condition had to be checked for FALSE, use a digital input (inverse logic) to invert the condition.


## Tested with
- JGrafchart 2.6.1
- Python 2.7.6
- V4.0 Step7 MicroWIN SP7
- PLC: S7-200 CPU 224 and CPU 222

## Copyright
    
Copyright 2015 Fritz Schimpf

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
