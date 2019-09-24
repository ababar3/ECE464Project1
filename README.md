# ECE464Project1

%Point 1%
Read the circuit

Compose gate

Find the Fault list (complete one!) -> Go to gate, SA-0/1 for output + output in input SA
                                    -> Same for INPUT
                                    -> Create a counter to know which the number of total fault

%Point 2%
Read the circuit

Create circuit and simulate it -> save outputs of the correct circuit

Read the fault list

Create # bad circuits, each with a different fault of the list
[NOT to simulate all the faults on a single bad circuit for the assumption of a single fault for circuit]

Read the TV (ordered from LSB to MSB)

Test each TV on each faulty circuit  and check if the output is different to the good one or not
Different?
        YES: Fault detected -> flag 1 to be sure it is detected and print good and bad behaviour
        NO: Flag stays 0
 At the end print undetected faults.
