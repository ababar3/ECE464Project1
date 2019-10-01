from __future__ import print_function
import os
import copy
# FUNCTION: Neatly prints the Circuit Dictionary:
def printCkt(circuit):
    print("INPUT LIST:")
    for x in circuit["INPUTS"][1]:
        print(x + "= ", end='')
        print(circuit[x])

    print("\nOUTPUT LIST:")
    for x in circuit["OUTPUTS"][1]:
        print(x + "= ", end='')
        print(circuit[x])

    print("\nGATE list:")
    for x in circuit["GATES"][1]:
        print(x + "= ", end='')
        print(circuit[x])
    print()


def FaultList(netName):

    #Open circuit file

    netFile = open(netName,'r')

    #Create variables to store data and so to save circuit elements and faults

    inputs = []
    outputs = []
    gates = []
    Faultsl = []
    counter = 0
    #Create a dictionary for the circuit to check the correctness of the circuit.bench file

    circuit = {}

    #print("Input reading")

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

            F = line + "-SA-0"
            counter += 1
            Faultsl.append(F)
            F = line + "-SA-1"
            Faultsl.append(F)
            counter += 1
            continue

        if line[0:6] == "OUTPUT":
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

        F = line + "-SA-0"
        Faultsl.append(F)
        counter += 1
        F = line + "-SA-1"
        Faultsl.append(F)
        counter += 1
        ref_wire = lineSpliced[0]

        lineSpliced = lineSpliced[1].split("(")

        logic = lineSpliced[0].upper
        lineSpliced[1] = lineSpliced[1].replace(")", "")

        terms = lineSpliced[1].split(",")

        for x in terms:

            F = ref_wire + "-IN-" + x + "-SA-0"
            Faultsl.append(F)
            counter += 1
            F = ref_wire + "-IN-" + x + "-SA-1"
            Faultsl.append(F)
            counter += 1
            continue

        terms = ["wire_" + x for x in terms]


        circuit[gateOut] = [logic, terms, False, 'U']
    line = '\n# total faults: %d' %counter
    Faultsl.append(line)
    return Faultsl


def NetReader(netName):
    # Open circuit file

    netFile = open(netName, 'r')

    # Create variables to store data and so to save circuit elements and faults

    inputs = []
    outputs = []
    gates = []
    inputBits = 0
    # Create a dictionary for the circuit to check the correctness of the circuit.bench file

    circuit = {}

    # Circuit read
    for line in netFile:

        if (line == '\n'):
            continue

        if (line[0] == '#'):
            continue

        line = line.replace(" ", "")
        line = line.replace("\n", "")

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
            inputBits += 1
            # add this wire as an entry to the circuit dictionary
            circuit[line] = ["INPUT", line, False, 'U']
            print(circuit[line])
            continue

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

        lineSpliced = lineSpliced[1].split("(")  # splicing the line again at the "("  to get the gate logic
        logic = lineSpliced[0].upper()

        lineSpliced[1] = lineSpliced[1].replace(")", "")
        terms = lineSpliced[1].split(",")  # Splicing the the line again at each comma to the get the gate terminals
        # Turning each term into an integer before putting it into the circuit dictionary
        terms = ["wire_" + x for x in terms]


        # add the gate output wire to the circuit dictionary with the dest as the key
        circuit[gateOut] = [logic, terms, False, 'U']

        circuit["INPUT_WIDTH"] = ["input width:", inputBits]
        circuit["INPUTS"] = ["Input list", inputs]
        circuit["OUTPUTS"] = ["Output list", outputs]
        circuit["GATES"] = ["Gate list", gates]

        #print("\n bookkeeping items in circuit: \n")
        #print(circuit["INPUT_WIDTH"])
        #print(circuit["INPUTS"])
        #print(circuit["OUTPUTS"])
        #print(circuit["GATES"])

    return circuit



def gateCalc(circuit, node):

    # terminal will contain all the input wires of this logic gate (node)
    terminals = list(circuit[node][1])

    # If the node is an Inverter gate output, solve and return the output
    if circuit[node][0] == "NOT":
        if circuit[terminals[0]][3] == '0':
            circuit[node][3] = '1'
        elif circuit[terminals[0]][3] == '1':
            circuit[node][3] = '0'
        elif circuit[terminals[0]][3] == "U":
            circuit[node][3] = "U"
        else:  # Should not be able to come here
            return -1
        return circuit

    # If the node is an AND gate output, solve and return the output
    elif circuit[node][0] == "AND":
        # Initialize the output to 1
        circuit[node][3] = '1'
        # Initialize also a flag that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 0 at any input terminal, AND output is 0. If there is an unknown terminal, mark the flag
        # Otherwise, keep it at 1
        for term in terminals:
            if circuit[term][3] == '0':
                circuit[node][3] = '0'
                break
            if circuit[term][3] == "U":
                unknownTerm = True

        if unknownTerm:
            if circuit[node][3] == '1':
                circuit[node][3] = "U"
        return circuit

    # If the node is a NAND gate output, solve and return the output
    elif circuit[node][0] == "NAND":
        # Initialize the output to 0
        circuit[node][3] = '0'
        # Initialize also a variable that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 0 terminal, NAND changes the output to 1. If there is an unknown terminal, it
        # changes to "U" Otherwise, keep it at 0
        for term in terminals:
            if circuit[term][3] == '0':
                circuit[node][3] = '1'
                break
            if circuit[term][3] == "U":
                unknownTerm = True
                break

        if unknownTerm:
            if circuit[node][3] == '0':
                circuit[node][3] = "U"
        return circuit

    # If the node is an OR gate output, solve and return the output
    elif circuit[node][0] == "OR":
        # Initialize the output to 0
        circuit[node][3] = '0'
        # Initialize also a variable that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 1 terminal, OR changes the output to 1. Otherwise, keep it at 0
        for term in terminals:
            if circuit[term][3] == '1':
                circuit[node][3] = '1'
                break
            if circuit[term][3] == "U":
                unknownTerm = True

        if unknownTerm:
            if circuit[node][3] == '0':
                circuit[node][3] = "U"
        return circuit

    # If the node is an NOR gate output, solve and return the output
    if circuit[node][0] == "NOR":
        # Initialize the output to 1
        circuit[node][3] = '1'
        # Initialize also a variable that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 1 terminal, NOR changes the output to 0. Otherwise, keep it at 1
        for term in terminals:
            if circuit[term][3] == '1':
                circuit[node][3] = '0'
                break
            if circuit[term][3] == "U":
                unknownTerm = True
        if unknownTerm:
            if circuit[node][3] == '1':
                circuit[node][3] = "U"
        return circuit

    # If the node is an XOR gate output, solve and return the output
    if circuit[node][0] == "XOR":
        # Initialize a variable to zero, to count how many 1's in the terms
        count = 0

        # if there are an odd number of terminals, XOR outputs 1. Otherwise, it should output 0
        for term in terminals:
            if circuit[term][3] == '1':
                count += 1  # For each 1 bit, add one count
            if circuit[term][3] == "U":
                circuit[node][3] = "U"
                return circuit

        # check how many 1's we counted
        if count % 2 == 1:  # if more than one 1, we know it's going to be 0.
            circuit[node][3] = '1'
        else:  # Otherwise, the output is equal to how many 1's there are
            circuit[node][3] = '0'
        return circuit

    # If the node is an XNOR gate output, solve and return the output
    elif circuit[node][0] == "XNOR":
        # Initialize a variable to zero, to count how many 1's in the terms
        count = 0

        # if there is a single 1 terminal, XNOR outputs 0. Otherwise, it outputs 1
        for term in terminals:
            if circuit[term][3] == '1':
                count += 1  # For each 1 bit, add one count
            if circuit[term][3] == "U":
                circuit[node][3] = "U"
                return circuit

        # check how many 1's we counted
        if count % 2 == 1:  # if more than one 1, we know it's going to be 0.
            circuit[node][3] = '1'
        else:  # Otherwise, the output is equal to how many 1's there are
            circuit[node][3] = '0'
        return circuit
    elif circuit[node][0] == "BUFF":
        if circuit[terminals[0]][3] == '0':
            circuit[node][3] = '0'
        elif circuit[terminals[0]][3] == '1':
            circuit[node][3] = '1'
        elif circuit[terminals[0]][3] == "U":
            circuit[node][3] = "U"
        else:  # Should not be able to come here
            return -1
        return circuit
    # Error detection... should not be able to get at this point
    return circuit[node][0]

#Input reader
def inputRead(circuit,line):
    if len(line) < circuit["INPUT_WIDTH"][1]:
        print("Not enough bits")
        return -1

    # Getting the proper number of bits:
    line = line[(len(line) - circuit["INPUT_WIDTH"][1]):(len(line))]

    # Adding the inputs to the dictionary
    # Since the for loop will start at the most significant bit, we start at input width N
    i = circuit["INPUT_WIDTH"][1] - 1
    inputs = list(circuit["INPUTS"][1])
    # dictionary item: [(bool) If accessed, (int) the value of each line, (int) layer number, (str) origin of U value]
    for bitVal in line:
        bitVal = bitVal.upper()  # in the case user input lower-case u
        circuit[inputs[i]][3] = bitVal  # put the bit value as the line value
        circuit[inputs[i]][2] = True  # and make it so that this line is accessed

        # In case the input has an invalid character (i.e. not "0", "1" or "U"), return an error flag
        if bitVal != "0" and bitVal != "1" and bitVal != "U":
            return -2
        i -= 1  # continuing the increments

    return circuit

def FaultReader(line):

    if not "-SA-" in line :
        print("Error in the format")
        return -1

    #This condition allows to accept inputs with a name long no more than 5 characters
    if (len(line) > 10):
        line = line.replace("-SA","")
        line = line.replace("IN-","")
        line = line.split("-")
        flag = 'I'
        line.append(flag)
        fault = line
    else:
        line = line.replace("-SA","")
        line = line.split("-")
        flag = 'S'
        line.append(flag)
        fault = line
    return fault

def good_sim(circuit):
    queue = list(circuit["GATES"][1])
    i = 1

    while True:
        i -= 1
        # If there's no more things in queue, done
        if len(queue) == 0:
            break

        # Remove the first element of the queue and assign it to a variable for us to use
        curr = queue[0]
        queue.remove(curr)

        # initialize a flag, used to check if every terminal has been accessed
        term_has_value = True

        # Check if the terminals have been accessed
        for term in circuit[curr][1]:
            if not circuit[term][2]:
                term_has_value = False
                break

        if term_has_value:
            circuit[curr][2] = True
            circuit = gateCalc(circuit, curr)

            # ERROR Detection if LOGIC does not exist
            if isinstance(circuit, str):
                print(circuit)
                return circuit

            #print("Progress: updating " + curr + " = " + circuit[curr][3] + " as the output of " + circuit[curr][
              #  0] + " for:")
            #for term in circuit[curr][1]:
             #   print(term + " = " + circuit[term][3])


        else:
            # If the terminals have not been accessed yet, append the current node at the end of the queue
            queue.append(curr)

    return circuit

def Fault_Input(circuit, fault):
    Input_check = list(circuit["INPUTS"][1])

    bad_wire = "wire_" + fault[0]

    for line in Input_check:
        if line == bad_wire:
            circuit[line][3] = fault[1]
            break

    return circuit

def bad_sim(circuit,fault):
    queue = list(circuit["GATES"][1])
    out_wire = ""
    while True:
        flag = False
        # If there's no more things in queue, done

        if len(queue) == 0:
            break

        if fault[2] == 'S':
            bad_wire = "wire_" + fault[0]
        elif fault[3] == 'I':
            bad_wire = "wire_" + fault[1]
            out_wire = "wire_" + fault[0]
        else:
            print("Error in the fault format")
            return -1
        # Remove the first element of the queue and assign it to a variable for us to use

        curr = queue[0]
        queue.remove(curr)

        if (bad_wire == curr) and (fault[2] == 'S'):
            circuit[curr][3] = fault[1]
            circuit[curr][2] = True
            #print(circuit)
        else:
            if (bad_wire in circuit[curr][1]) and (out_wire == curr):
                flag = True
                Corr_Input = circuit[bad_wire][3]
                circuit[bad_wire][3] = fault[2]

            term_has_value = True

                # Check if the terminals have been accessed
            for term in circuit[curr][1]:
                # wire presence check
                if not circuit[term][2]:
                    term_has_value = False
                    break

            if term_has_value:

                circuit[curr][2] = True

                circuit = gateCalc(circuit, curr)

                # ERROR Detection if LOGIC does not exist
                if isinstance(circuit, str):
                    print(circuit)
                    return circuit

                if flag == True:
                    circuit[bad_wire][3] = Corr_Input
                    flag = False

                #print("Progress: updating " + curr + " = " + circuit[curr][3] + " as the output of " + circuit[curr][
                 #       0] + " for:")
                #for term in circuit[curr][1]:
                 #   print(term + " = " + circuit[term][3])


                # If the terminals have not been accessed yet, append the current node at the end of the queue
            else:
                queue.append(curr)

    return circuit

#main function
def main():
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

    circuit = NetReader(cktFile) #Reading the circuit.bench
    print("\n Finished processing benchmark file and built netlist dictionary: \n")

    print(circuit)

    NewCircuit = copy.deepcopy(circuit) #circuit dictionary is given a new variable NewCircuit

    while True:
        inputName = "input.txt" #for test vector
        FaultName = "f_list.txt" #for faults to be tested
        print("\n Read input vector file: use " + inputName + "?" + " Enter to accept or type filename: ")
        userInput = input()

        if userInput == "": #if user hits enter input.txt file would be read else it would take input of filename
            break
        else:
            inputName = os.path.join(script_dir, userInput)
            if not os.path.isfile(inputName):
                print("File does not exist. \n")
                return
            else:
                break

    print("\n Do you want to use the full fault list? Enter to accept, type no to select your fault list:")
    userInput = input()
    if userInput == "":
        Faultsl = FaultList(cktFile) #Faultsl has the benchmark file now.

        with open(FaultName, 'w') as filehandle: #Writing the faults from circuit benchmark file.
            for line in Faultsl:
                filehandle.write("%s\n" % line)
            filehandle.close()


    while True:
        print("\n Read fault file: use " + FaultName + "?" + " Enter to accept or type filename(if you want the full fault list please press enter): ") #fault file that gets read is here
        userInput = input()
        if userInput == "": # if user hits enter it automatically reads f_list.txt
            break
        else:
            FaultName = os.path.join(script_dir, userInput)
            if not os.path.isfile(FaultName):
                print("File does not exist. \n")
            else:
                break




        # Select output file, default is output.txt
    while True:
        outputName = "output.txt" #output file
        print("\n Write output file: use " + outputName + "?" + " Enter to accept or type filename: ")
        userInput = input()
        if userInput == "":
            break
        else:
            outputName = os.path.join(script_dir, userInput) #takes the name of file user wants to input
            break

    inputFile = open(inputName,"r") #each input and output is initialized after being finally read dynamically
    inputFault = open(FaultName,"r")
    outputFile = open(outputName,"w")

    faultList = [] #List created for all faults

    undetected = [] #List createed for undetected faults

    fault = [] #List created for faults that are detected.

    good_output = []
    i = 0
    outputFile.write("#fault sim result\n")
    outputFile.write("#input: circuit\n")
    outputFile.write("#input: " + inputName + "\n") # Headers for output files
    outputFile.write("#input: " + FaultName + "\n")
    outputFile.write("\n")

    faultList = inputFault.readlines() # Each fault is read and stored in list
    faultList = [x.strip() for x in faultList] # To get the leading and trailing characters eg: A-SA-0 it return 'A' '0'

    print("Simulation begins")
    for line in inputFile:  #for each test vector in the tv input file "The outer For Loop"
        output = ""
        if (line == "\n"):
            continue
        if (line[0] == "#"):
            continue

        line = line.replace("\n", "")

        j = 0
        bad_output = []

        circuit = inputRead(circuit,line) #reads the circuit
        circuit = good_sim(circuit) #circuit runs through the good simulator
        RequiredFault = []
        for y in circuit["OUTPUTS"][1]: #Checking the outputs of goods simulator
            if not circuit[y][2]:
                output[i] = "NETLIST ERROR: OUTPUT LINE \"" + y + "\" NOT ACCESSED"
                break
            output = str(circuit[y][3]) + output #output is stored in variable output
        good_output.append(output) #output gets appended to good_output list here.
        print("Output of the good circuit:" + good_output[i] + "\n")
        outputFile.write("\ntv%d = %s ->  %s \n" %(i+1, line, good_output[i])) #for comparing later, printing the good simulator outputs
        outputFile.write("detected:\n")


        iteration = 0

        while iteration < len(faultList): #iterating the loop until the length of lines in faultList text file
            aux_output = ""
            circuit = inputRead(circuit, line) #the circuit is read here
            if (faultList[iteration] == ""): #if fault line is empty continue to next line
                iteration += 1
                continue
            if "#" in faultList[iteration]: #if fault line has a comment continue to next line
                iteration += 1
                continue

            if "-SA-" in faultList[iteration]: #checks if "-SA- is in faultlist line
                RequiredFault.append(faultList[iteration]) #stores that faultList line in a list called Required Fault
                fault = FaultReader(faultList[iteration]) #Reads the fault and returns the neccessary characters needed for fault
                print("This is the simulation with the fault #: %d" %(j+1))
                print(fault)
                iteration += 1
                j += 1
            else:
                print("Error in file format, line that is no comment and no fault.")
                return -1

            circuit = Fault_Input(circuit,fault) # new line is read by the circuit which has the updated fault list
            circuit = bad_sim(circuit, fault) #fault line ran by bad simulator

            for y in circuit["OUTPUTS"][1]: #checks the outputs of cricuit with faults
                if not circuit[y][2]:
                    output = "NETLIST ERROR: OUTPUT LINE \"" + y + "\" NOT ACCESSED"
                    break
                aux_output = str(circuit[y][3]) + aux_output

            bad_output.append(aux_output) #this output gets stored in bad_ouput list

            if (bad_output[j-1] == good_output[i]): #compares bad and good output and if they are same it mean it was undetected
                if i<1:
                    undetected.append(RequiredFault[j-1]) # add fault to undetected list
            else:
                if RequiredFault[j-1] in undetected:
                    undetected.remove(RequiredFault[j-1]) # remove undetected if not equals

            circuit = copy.deepcopy(NewCircuit) # used deepcopy to copy NewCircuit back to circuit



        #print(RequiredFault)
        #print(bad_output)
        #print(good_output)

        while (i < len(good_output)):
            k = j

            while (k>0):

                if (bad_output[j-k-1] != good_output[i]):
                    outputFile.write("%s: %s -> %s\n" %(RequiredFault[j-k-1],line, bad_output[j-k-1]))
                    k -= 1
                else:
                    k -= 1
            i += 1


    print(undetected) #prints undetected list

    unFaults = len(undetected)
    detected = j-unFaults #to calculate the number detected we subtract total - undetected
    outputFile.write("\nTotal detected faults: %d\n" %detected)
    outputFile.write("\nundetected faults: %d\n" %unFaults)
    for x in undetected:
        outputFile.write(x + "\n")

    percentage = detected/j*100 #calculates percentage
    outputFile.write("\nfault coverage: %d/%d = %d" %(detected, j, percentage))
    outputFile.write('%')
    outputFile.close()

if __name__ == "__main__":
    main()