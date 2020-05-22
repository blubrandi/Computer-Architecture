import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
ST = 0b10000100
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""
    def __init__(self):
        self.reg = [0] * 8
        self.ram = [0] * 256

        self.pc = 0
        self.sp = 7
        self.value = 0
        # self.call = 8
        # self.ret = 9

        self.branch_table = {}
        self.branch_table[HLT] = self.handle_hlt
        self.branch_table[LDI] = self.handle_ldi
        self.branch_table[PRN] = self.handle_prn
        self.branch_table[MUL] = self.handle_mul
        self.branch_table[POP] = self.handle_pop
        self.branch_table[PUSH] = self.handle_push
        self.branch_table[ST] = self.handle_st
        self.branch_table[CALL] = self.handle_call
        self.branch_table[RET] = self.handle_return
        self.branch_table[ADD] = self.handle_add
        self.branch_table[CMP] = self.handle_cmp
        self.branch_table[JMP] = self.handle_jmp
        self.branch_table[JEQ] = self.handle_jeq
        self.branch_table[JNE] = self.handle_jne

    def handle_st(self, pc):
        reg_num = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]
        self.reg[reg_num] = value
        self.pc += 3

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""
        address = 0
        with open(sys.argv[1]) as f:
            for line in f:
                string_val = line.split("#")[0].strip()
                if string_val == '':
                    continue
                v = int(string_val, 2)
                self.ram[address] = v
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":

            if self.reg[reg_a] == self.reg[reg_b]:
                self.E = 1
            else:
                self.E = 0

            if self.reg[reg_a] < self.reg[reg_b]:
                self.L = 1
            else:
                self.L = 0
            
            if self.reg[reg_a] > self.reg[reg_b]:
                self.G = 1
            else: 
                self.G = 0

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

    def handle_push(self, reg_a, reg_b):
        self.reg[self.sp] -= 1
        reg_num = self.ram[self.pc + 1]
        self.value = self.reg[reg_num]
        self.ram[self.reg[self.sp]] = self.value
        self.pc += 2

    def handle_pop(self, reg_a):
        top_of_stack_addr = self.reg[self.sp]
        self.value = self.ram[top_of_stack_addr]
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = self.value
        self.reg[self.sp] += 1
        self.pc += 2

    def handle_hlt(self):
        running = False
        self.pc += 1
        sys.exit()

    def handle_ldi(self, reg_a, reg_b):
        self.reg[reg_a] = reg_b
        self.pc += 3

    def handle_prn(self, reg_a):
        print(self.reg[reg_a])
        self.pc += 2

    def handle_mul(self, reg_a, reg_b):
        self.alu("MUL", reg_a, reg_b)
        self.pc += 3

    def handle_cmp(self, reg_a, reg_b):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("CMP", reg_a, reg_b)
        self.pc += 3

    def handle_call(self, reg_a):
        return_address = self.pc + 2

        self.reg[self.sp] -= 1
        top_of_the_stack_address = self.reg[self.sp]
        self.ram[top_of_the_stack_address] = return_address

        reg_num = self.ram[self.pc + 1]
        subroutine_address = self.reg[reg_num]

        self.pc = subroutine_address

    def handle_return(self):
        top_of_stack_address = self.reg[self.sp]
        return_address = self.ram[top_of_stack_address]
        self.reg[self.sp] += 1

        self.pc = return_address
    
    def handle_add(self, reg_a, reg_b):
        self.alu("ADD", reg_a, reg_b)
        self.pc += 3
    
    def handle_jmp(self, reg_a, reg_b):
        pointer = self.ram_read(self.pc + 1)
        self.pc = self.reg[pointer]
    
    def handle_jeq(self, reg_a, reg_b):
        pointer = self.ram_read(self.pc + 1)
        
        if self.E == 1:
            self.pc = self.reg[pointer]
        else: 
            self.pc += 2
    
    def handle_jne(self, reg_a, reg_b):
        pointer = self.ram_read(self.pc + 1)

        if self.E == 0:
            self.pc = self.reg[pointer]
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        running = True

        while running == True:
            instruction = self.ram_read(self.pc)
            reg_a = self.ram_read(self.pc + 1)
            reg_b = self.ram_read(self.pc + 2)

            if instruction == LDI:
                self.branch_table[instruction](reg_a, reg_b)
            elif instruction == MUL:
                self.branch_table[instruction](reg_a, reg_b)
            elif instruction == PRN:
                self.branch_table[instruction](reg_a)
            elif instruction == PUSH:
                self.branch_table[instruction](reg_a, reg_b)
            elif instruction == POP:
                self.branch_table[instruction](reg_a)
            elif instruction == CALL:
                self.branch_table[instruction](reg_a)
            elif instruction == RET:
                self.branch_table[instruction]()
            elif instruction == ADD:
                self.branch_table[instruction](reg_a, reg_b)
            elif instruction == CMP:
                self.branch_table[instruction](reg_a, reg_b)
            elif instruction == JMP:
                self.branch_table[instruction](reg_a, reg_b)
            elif instruction == JEQ:
                self.branch_table[instruction](reg_a, reg_b)
            elif instruction == JNE:
                self.branch_table[instruction](reg_a, reg_b)
            else:
                self.branch_table[instruction]()

        running = False
        sys.exit()
