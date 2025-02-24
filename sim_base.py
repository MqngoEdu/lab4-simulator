def get_bits(number, idx1, idx2):
    """Returns the bits of number between idx1 and idx2 as an integer"""
    if idx1 > idx2:
        low, num = idx2, idx1-idx2
    else:
        low, num = idx1, idx2-idx1
    return (number >> low) & ((1 << num)-1)


def execute(instruction, oldPC):
    """Handles a single instruction, returning the new PC"""
    global M, R
    
    # to do: add instructions here

    b = get_bits(instruction, 0, 2)
    a = get_bits(instruction, 2, 4)
    icode = get_bits(instruction, 4, 7)
    reserve_bit = get_bits(instruction, 7, 8)

    print(f'\n{a = }, {b = }, {icode = }, {reserve_bit = }\n')

    if reserve_bit == 1 and icode != 0:
        return oldPC
    elif reserve_bit == 1 and icode == 0:
        match b:
            case 0: 
                rsp -= 1
                M[rsp] = R[a]
            case 1:
                R[a] = R[rsp]
                rsp += 1
            case 2:
                M[rsp] = oldPC + 2
                oldPC = M[oldPC + 1]
                return
            case 3:
                oldPC = M[rsp]

    match icode:
        case 0: R[a] = R[b]
        case 1: R[a] += R[b]
        case 2: R[a] &= R[b]
        case 3: R[a] = M[R[b]]
        case 4: M[R[b]] = R[a]
        case 5:
            match b:
                case 0: R[a] = ~R[a]
                case 1: R[a] = -R[a]
                case 2: R[a] = not R[a]
                case 3: R[a] = oldPC
        case 6:
            match b:
                case 0: R[a] = M[oldPC + 1]
                case 1: R[a] += M[oldPC + 1]
                case 2: R[a] &= M[oldPC + 1]
                case 3: R[a] = M[M[oldPC +1]]
            return oldPC + 2
        case 7:
            if R[a] == 0 or R[a] >= 0x80:
               return R[b]
    
    return oldPC + 1



# initialize memory and registers
R = [0 for i in range(4)]
M = [0 for i in range(256)]

rsp = 0xFF # new!

# initialize control registers; do not modify these directly
_ir = 0
_pc = 0


def cycle():
    """Implement one clock cycle"""
    global M, R, _pc, _ir
    
    # execute
    _ir = M[_pc]
    _pc = execute(_ir, _pc)
    
    # enforce the fixed-length nature of values
    for i in range(len(R)): R[i] &= 0b11111111
    for i in range(len(M)): M[i] &= 0b11111111
    _pc &= 0b11111111
    

def showState():
    """Displays all processor state to command line"""
    print('-'*40)
    print('last instruction = 0b{:08b} (0x{:02x})'.format(_ir, _ir))
    for i in range(4):
        print('Register {:02b} = 0b{:08b} (0x{:02x})'.format(i, R[i], R[i]))
    print('next PC = 0b{:08b} (0x{:02x})'.format(_pc, _pc))
    print('//////////////////////// Memory \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')
    for i in range(0, 256, 16):
        print('0x{:02x}-{:02x}'.format(i, i+15), end=': ')
        for j in range(16):
            print('{:02x}'.format(M[i+j]), end=' ')
        print()
        if not any(M[i+j:]):
            break
    print('-'*40)


if __name__ == '__main__':
    import sys, os.path
    
    if len(sys.argv) <= 1:
        print('USAGE: python', sys.argv[0], 'memory.txt\n    where memory.txt is a set of bytes in hex')
        print('USAGE: python', sys.argv[0], 'byte [byte, byte, ...]\n    where the bytes are in hex and will be loaded into memory before running')
        quit()
    
    if os.path.exists(sys.argv[1]):
        with open(sys.argv[1]) as f:
            i = 0
            for b in f.read().split():
                M[i] = int(b, 16)
                i += 1
    else:
        i = 0
        for b in sys.argv[1:]:
            M[i] = int(b, 16)
            i += 1
    
    showState()
    while True:
        n = input('Take how many steps (0 to exit, default 1)? ')
        try:
            n = int(n)
        except:
            n = 1
        if n <= 0: break
        for i in range(n):
            cycle()
            showState()
