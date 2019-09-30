from __future__ import print_function
import os

def FaultList(netName):

    #Open circuit file & read it

    netFile = open(netName,'r')

    #Create variables to store data and so to save circuit elements and faults
    #empty lits 

    inputs = []
    outputs = []
    gates = []
    faultList = []
    faults = 0
    #Create a dictionary for the circuit to check the correctness of the circuit.bench file

    circuit = {}
    #It will return a list of lines in file. 
    #We can iterate over that list and strip() the new line character then print the line i.e
    
    #Circuit read
    for line in netFile:

        if (line == '\n'):
            continue

        if(line[0] == '#'):
            continue

        line = line.replace(" ","")
        line = line.replace("\n","")

        if (line[0:5] == "INPUT"):
            
            line = line.replace("INPUT", "")
            line = line.replace("(", "")
            line = line.replace(")", "")

            # Format the variable name to wire_*VAR_NAME*
            line = "wire_" + line

            # Error detection: line being made already exists
            if line in circuit:
                msg = "NETLIST ERROR: INPUT LINE \"" + line + "\" ALREADY EXISTS PREVIOUSLY IN NETLIST"
                print(msg + "\n")
                return msg

            # Appending to the inputs array and update the inputBits
            inputs.append(line)
            # add this wire as an entry to the circuit dictionary
            circuit[line] = ["INPUT", line, False, 'U']

            line = line.replace("wire_","")

            newLine = line + "-SA-0"
            faultList.append(newLine)
            line4 = line + "-SA-1"
            faultList.append(line4)
            faults += 2
            continue


        print(inputs)
        if line[0:6] == "OUTPUT":
            
            # Removing everything but the numbers
            line = line.replace("OUTPUT", "")
            line = line.replace("(", "")
            line = line.replace(")", "")

            # Appending to the output array[
            outputs.append("wire_" + line)
            continue

        lineSpliced = line.split("=")  # splicing the line at the equals sign to get the gate output wire

        gateOut = "wire_" + lineSpliced[0]
        if gateOut in circuit:
            msg = "NETLIST ERROR: GATE OUTPUT LINE \"" + gateOut + "\" ALREADY EXISTS PREVIOUSLY IN NETLIST"
            print(msg + "\n")
            return msg

            # Appending the dest name to the gate list
        gates.append(gateOut)

        line = lineSpliced[0]

        line2 = line + "-SA-0"
        faultList.append(line2)
        line2 = line + "-SA-1"
        faultList.append(line2)
        faults += 2
        index = lineSpliced[0]

        lineSpliced = lineSpliced[1].split("(")

        logic = lineSpliced[0].upper
        lineSpliced[1] = lineSpliced[1].replace(")", "")

        terms = lineSpliced[1].split(",")

        i = 0

        while(i<len(terms)):   # Used while loop here that run until terms length where term has the variable that come after "-IN-" .
            line3 = index + "-IN-" + str(terms[i]) + "-SA-0"
            faultList.append(line3)
            line3 = index + "-IN-" + str(terms[i]) + "-SA-1"
            faultList.append(line3)
            faults += 2
            i = i + 1
            continue

        terms = ["wire_" + x for x in terms]

        # add the gate output wire to the circuit dictionary with the dest as the key
        circuit[gateOut] = [logic, terms, False, 'U']
    line = '\n# total faults: %d' % faults
    faultList.append(line)
    return faultList

def main():

    print("Full fault list generator\n")

    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in

    while True:
        cktFile = "circuit.bench"
        print("\n Read circuit benchmark file: use " + cktFile + "?" + " Enter to accept or type filename: ")
        userInput = input()
        if userInput == "":
            break
        else:
            cktFile = os.path.join(script_dir, userInput)
            if not os.path.isfile(cktFile):
                print("File does not exist. \n")
            else:
                break

    print("Detection possible faults...\n")

    faultList = FaultList(cktFile)

    print(faultList)

    while True:
        outputName = "f_list.txt"
        print("\n Write output file: use " + outputName + "?" + " Enter to accept or type filename: ")
        userInput = input()
        if userInput == "":
            break
        else:
            outputName = os.path.join(script_dir, userInput)
            break

    outputFile = open(outputName, 'w')
    outputFile.write("# circuit.bench \n# full SSA list\n\n")

    for line in faultList:
        outputFile.write("%s\n" % line)

    outputFile.close()

if __name__ == "__main__":
    main()

