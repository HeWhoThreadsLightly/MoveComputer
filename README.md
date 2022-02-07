# MoveComputer
Move only computer inspired by NASA command module computer and movfuscator
Made in logisim evolution
![image](https://user-images.githubusercontent.com/39104806/152760829-7f9c1a7c-fdfd-4bb8-8555-798f017d84a8.png)

Move core runs unconditional* move instructions all other parts of the cpu is memmory maped ALU+registers, program counter, io, stack frame.
Components have conditional behaviours tex jump registers are conditonaly loded to the program pointer if a non zero value is written to 0x27.
*Two instructions move A -> B and load littral to B register

Built a assembler abusing pythons eval for pre assembly functionality.
Move computer currently has collatzconjecture loded in to rom.

TODO
- Implement physicly taged virtualy indexed lest resently acessed cache
- Extend data path from 8 bits to 32 bits
- Extend internal cpu adress buss from 8 bits to 12, 65% of cpu memory is maped 
- Inderect moves
- Causality zones and out of order execution

