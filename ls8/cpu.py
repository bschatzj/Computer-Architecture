"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    commands = {
        "HLT": 0b01,
        "LDI": 0b10000010,
        "PRN": 0b01000111,
        "MUL": 0b10100010,
        "PUSH": 0b01000101,
        "POP": 0b01000110
    }

    commands_inverted = {
        0b01: "HLT",
        0b10000010: "LDI",
        0b01000111: "PRN",
        0b10100010: "MUL",
        0b01000101: "PUSH",
        0b01000110: "POP"
    }

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 
        self.reg = [0] * 8
        self.reg[7] = 0xf4
        self.pc = 0
        self.branch_table = {
            "HLT": self.HLT,
            "LDI": self.LDI,
            "PRN": self.PRN,
            "MUL": self.MUL,
            "PUSH": self.PUSH,
            "POP": self.POP
        }

    def load(self, program):
        """Load a program into memory."""
        address = 0
        try: 
            with open(program) as p:
                for instruction in p:
                    instruction = instruction.strip().split("#")[0]
                    if instruction != "":
                        self.ram_write(address, int(instruction, 2))
                        address += 1

        except Exception:
            raise ValueError("Invalid file path.")

    def ram_read(self, address): 
        try: 
            return self.ram[address]
        except IndexError:
            raise ValueError("The address of value  " + str(address) +  " isn't a valid location in memory")
    
    def ram_write(self, address, value):
        self.ram[address] = value
        return value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

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

        print()

    def HLT(self):
        self.pc += 1
        sys.exit(0) 

    def LDI(self):
        self.reg[self.ram[self.pc + 1]] = self.ram[self.pc + 2]
        self.pc += 3
    
    def PRN(self):
        print(self.reg[self.ram[self.pc + 1]])
        self.pc += 2
    
    def MUL(self):
        self.alu("MUL", self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3

    def PUSH(self):
        # The seventh register is dedicated to keeping track of the stack pointer
        SP = 7
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = self.reg[self.ram[self.pc + 1]]

        self.pc += 2
    
    def POP(self):
        # The seventh register is dedicated to keeping track of the stack pointer
        SP = 7 
        self.reg[self.ram[self.pc + 1]] = self.ram[self.reg[SP]]
        self.reg[SP] += 1

        self.pc += 2

    def run(self):
        """Run the CPU."""
        IR = None
        while IR != self.commands["HLT"]:
            IR = self.ram_read(self.pc)

            if IR in self.commands_inverted:
                self.branch_table[self.commands_inverted[IR]]()
            else:
                raise Exception(f"Invalid Command: {IR}")
        
        # Reset the program counter
        self.pc = 0