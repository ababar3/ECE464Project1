# Logic Simulator
## Table Contents:
No. | Content 
:---: | :---
**1** | [About](README.md#1-About)
**2** | [Format](README.md#2-Format)
• **2.1** | [○ NetList](README.md#21-NetList)
• **2.2** | [○ Input(.txt)](README.md#22-Input-txt)
**3** | [Error Detection](README.md#3-ERROR-detection)
• **3.1** | [○ Netlist Errors](README.md#31-NetList-Errors)
• **3.2** | [○ Input Errors](README.md#32-Input-Errors)
**4** | [Functions](README.md#4-Functions)
• **4.1** | [○ netRead](README.md#41-netRead)
• **4.2** | [○ gateCalc](README.md#42-gateCalc)
• **4.3** | [○ inputRead](README.md#43-inputRead)
• **4.4** | [○ basic_sim](README.md#44-basic_sim)
_____________
## 1. About:
    Sample code of circuit simulator for Project 0, FAll 2019 UIC class ECE 464: Testing and Reliability of Digital Systems.
    
____________
## 2. Format of files:
    Guidelines on how to format the NetList benchmark and the input.txt files
### 2.1 NetList benchmark (circuit file):
    # Comments are not read by the program
    # No two INPUT, OUTPUT, or GATE calls must be in a single "line of code"
    # VAR_NAME is the name of the variable you want to name that variable
    # LOGIC can be substituted with "AND", "NAND", "OR", "NOR", "XOR", or "XNOR"
    INPUT(VAR_NAME0)
    OUTPUT(VAR_NAME1)
    VAR_NAME1 = NOT(VAR_NAME2)
    VAR_NAME2 = LOGIC(VAR_NAME3, VAR_NAME4, ...)
> __For Example:__

*  __Valid:__

```
# 5 inputs
# 2 outputs
# 7 gates

# INPUTS:
INPUT(a)
INPUT(b)
INPUT(c)
INPUT(d)
INPUT(e)

# OUTPUTS:
OUTPUT(j)
OUTPUT(k)

# GATES:
f = AND(a, c)
g = NAND(c, d)
h = OR(b, g)
i = NOR(g, e)
j = XOR(f, h)
k = XNOR(h, i)
l = NOT(k)
```

*  __Invalid:__

```
# INPUTS:
INPUT(a)
INPUT(b)
INPUT(a) # ERROR: User calls a new input line to an existing line already

# OUTPUTS:
OUTPUT(c)
OUTPUT(d)
OUTPUT(e) # ERROR: User calls a floating output line that is not going to be accessed in the circuit

# GATES:
c = NOT(a)
c = NOT(b) # ERROR: User calls a gate output line with an existing line already
d = ABBA(c) # ERROR: User calls an unknown logic
f = NOT(c) y = OR(f,d) # ERROR: User called 2 or more gates in one single "line of code" 
```

### 2.2 INPUT vectors (.txt)
    # Comments are not read by the program
    # X can be substituted with 1, 0, or U
    # The number of X's must be equal or greater than the number of INPUTS in the NetList
    # for the program to run these INPUTS
    XXXXXXXXXXX
> __For Example:__

```
# VALID OPTIONS:
# 4 bits, with lower-case u
1u01

#5 bits, with upper-case U's
UU111

#8 bits, only 1's and 0's
11001100

# INVALID OPTIONS:
#  Using character's not 1's, 0's nor U's
AAAAAAAA
23452345
10U13
100A1
```

_____________
## 3. ERRORs detected:
    Lists of errors that sim.py detects on user inputs, namely: the circuit benchmark file (netlist) and the input text
    file. 
### 3.1 NetList Errors:
> "NETLIST ERROR: INPUT LINE "wire_VAR_NAME" ALREADY EXISTS PREVIOUSLY IN NETLIST"
    
    Error occurs when user calls a new INPUT that already exists previously on the NetList, preventing 
    a single line hold two or more values

> "NETLIST ERROR: GATE OUTPUT LINE "wire_VAR_NAME" ALREADY EXISTS PREVIOUSLY IN NETLIST"

    Error occurs when user calls a new LOGIC GATE output that already exists previously on the NetList, 
    preventing a single line hold two or more values

> "NETLIST ERROR: LOGIC "LOGIC" DOES NOT EXIST"

    Error occurs when user calls a LOGIC that is not "NOT", "AND", "NAND", "OR", "NOR", "XOR", or "XNOR"

> "NETLIST ERROR: OUTPUT LINE "wire_VAR_NAME" NOT ACCESSED" 

    Error occurs when user calls an OUTPUT line and at the end of the NetList, the OUTPUT line can not have 
    any value due to not being accessed

### 3.2 INPUT Errors:
> "INPUT ERROR: INSUFFICIENT BITS"

    Error occurs when the user's INPUTS has less bits than specified in the NetList. The program will print
    this error in the output.txt and will continue to run the program on the next set of inputs

> "INPUT ERROR: INVALID INPUT VALUE/S"

    Error occurs when the user inputs a value that is not 1, 0, or U

________________
## 4. Functions:
    Descriptions and notes for the functions given in sim.py
### 4.1 netRead:
* **Function that reads in the circuit gate-level netlist/benchmark file, and creates a circuit dictionary to be used
for the rest of the program**
* Variable names are case-sensitive: lower-case letters is not equal to their respective upper-case letters
* Commas (','), Parentheses ('(' and ')'), space (' ') and equal signs ('=') in variable names
would lead to errors the program could not detect
* INPUT() and OUTPUT() variables would be ordered in the order they were called on the NetList, from Least Significant
bit to Most significant bit
    * INPUT() and OUTPUT() can still be put anywhere on the NetList
### 4.2 gateCalc:
* **Function that is called when trying to "*pass through*" a single gate**
* Little error detection, assumes you will have caught every thing before calling this function
* If the logic is NOT and was given more than one terminal, it would only give the NOT output of the first terminal
in the list
### 4.3 inputRead:
* **Function that takes a single series/line of input from the input file, and accordingly updates the circuit
dictionary**
* If the given bits is more than what is needed, the function will use the Least Significant Bit to Most Significant 
Bit/Right-to-left
### 4.4 basic_sim:
* **Function that takes the updated circuit dictionary and runs a simulation on the given values. This function will 
then outputs the result onto the output file**
* The sim.py is used for Python 2, and sim_for_python3.py is used for Python 3. The only difference between
two version is, the function "raw_input()" in sim.py is replaced by the function "input()" for Python 3.
* Every gate called should be used, meaning the user may not call a floating gate or a gate with an 
unspecified/unaccessible terminal. Otherwise, it will cause an infinite loop
* The simulation will *pause* for each "progress." (a gate has been accessed/calculated)
It then asks for the user to press Enter to continue
* The simulation runs through the list of gates to see for any gate that is ready to be calculated, by checking for each
terminal and see if all has a value
