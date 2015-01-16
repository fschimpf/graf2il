def generateSCL(filename, stepList, transitionList, digInDict, digOutDict):

    # create output file and write header. FIX: ask for overwrite:
    outfilename = filename.partition('.')[0] + '.scl'
    outfile = open(outfilename, 'w')
 
    outfile.close()
    print '.scl generated successfully. :-)'
