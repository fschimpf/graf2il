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
