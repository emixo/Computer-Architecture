"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
SP = 7

CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.stack_pointer = 255
        self.ops = {}
        self.ops[LDI] = self.LDI
        self.ops[PRN] = self.PRN
        self.ops[HLT] = self.HLT
        self.ops[MUL] = self.MUL
        self.running = False
        self.ops[POP] = self.POP
        self.ops[PUSH] = self.PUSH
        self.ops[CALL] = self.CALL
        self.ops[RET] = self.RET
        self.ops[ADD] = self.ADD
        self.reg[7] = 0xf4

        self.FL = 0b00000000
        self.ops[CMP] = self.CMP
        self.ops[JMP] = self.JMP
        self.ops[JEQ] = self.JEQ
        self.ops[JNE] = self.JNE

    def LDI(self):
        address = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]
        self.reg[address] = value
        self.pc += 3

    def PRN(self):
        address = self.ram[self.pc + 1]
        output = self.reg[address]
        self.pc += 2
        print(output)

    def MUL(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu('MUL', reg_a, reg_b)
        self.pc += 3

    def HLT(self):
        self.running = False

    def PUSH(self):
        # decrement stack pointer
        print(self.reg, 'REG BEFORE')
        self.reg[7] -= 1

        # get register value
        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num]

        # store it on the stack
        top_of_stack_addr = self.reg[7]
        self.ram[top_of_stack_addr] = value
        print(self.reg, 'REG AFTER')

        self.pc += 2
    
    def POP(self):
        # get value from the top of the stack
        print(self.reg, 'POP BEFORE')
        address_to_pop = self.reg[SP]
        value = self.ram[address_to_pop]

        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = value

        self.reg[SP] += 1
        print(self.reg, 'POP AFTER')
        self.pc += 2

    def CALL(self):
        ret_addr = self.pc + 2
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = ret_addr
        
        reg_num = self.ram[self.pc + 1]
        self.pc = self.reg[reg_num]
        
    def RET(self):
        ret_addr = self.ram[self.reg[SP]]
        self.reg[SP] += 1
        self.pc = ret_addr
    def ADD(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu('ADD', reg_a, reg_b)
        self.pc += 3

    def CMP(self):
        # `FL` bits: `00000LGE`
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        # If they are equal, set the Equal `E` flag to 1
        if reg_a == reg_b:
            self.FL = 0b00000001

        # If reg_a is less than reg_b, set the Less-than `L` flag to 1
        elif reg_a < reg_b:
            self.FL = 0b00000100

        # If reg_a is greater than reg_b, set the Greater-than `G` flag to 1
        elif reg_a > reg_b:
            self.FL = 0b00000010

        self.pc += 3

    def JMP(self):
        # Jump to the address stored in the given register.
        reg_num = self.ram[self.pc + 1]

        addr = self.reg[reg_num]
        # set pc to addr
        self.pc = addr

    def JEQ(self):
        # If `equal` flag is set (true), jump to the address stored in the given register.
        if self.FL & 0b001 == 1:
            # reg_num = self.ram[self.pc + 1]

            # addr = self.reg[reg_num]

            self.pc = self.reg[self.ram[self.pc + 1]]
        else:
            self.pc += 2

    def JNE(self):
        # If `E` flag is clear (false, 0), jump to the address stored in the given register
        if self.FL & 0b1 == 0:
            # reg_num = self.ram[self.pc + 1]

            # addr = self.reg[reg_num]

            self.pc = self.reg[self.ram[self.pc + 1]]
        else:
            self.pc += 2



    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("usage: comp.py progname")
            sys.exit(1)

        try:
            with open('examples/' + sys.argv[1]) as f:
                for line in f:
                    line = line.strip()
                    temp = line.split()

                    if len(temp) == 0:
                        continue

                    if temp[0][0] == '#':
                        continue

                    try:
                        self.ram[address] = int(temp[0], 2)

                    except ValueError:
                        print(f"Invalid number: {temp[0]}")
                        sys.exit(1)


                    address += 1

        except FileNotFoundError:
            print(f"Couldn't open {sys.argv[1]}")
            sys.exit(1)

        if address == 0:
            print("Program was empty!")
            sys.exit(3)

    def ram_read(self, address):
        # print(self.reg[address])
        output = self.ram[address]
        return output

    def ram_write(self, address, value):
         self.ram[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')


    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            ir = self.ram[self.pc]
            self.ops[ir]()

            # if ir == 0b10000010:
            #     reg_num = self.ram[self.pc + 1]
            #     value = self.ram[self.pc + 2]

            #     self.reg[reg_num] = value

            #     self.pc += 3

            # elif ir == 0b01000111:
            #     reg_num = self.ram[self.pc + 1]
            #     print(self.reg[reg_num])

            #     self.pc += 2

            # elif ir == 0b00000001:
            #     running = False
