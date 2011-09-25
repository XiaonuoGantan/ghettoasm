import re

REG_NAMES = [
    'zero', 'ra',
    'v0', 'v1',
    'a0', 'a1', 'a2', 'a3',
    't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9',
    's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9',
]

def signature(sig):
    def decorator(func):
        func.sig = sig
        return func
    return decorator

def signature_to_regexp(signature):
    stuff = {'R': r'\$(\w+)', 'C': r'(\d+)'}
    return re.compile(',\s{0,}'.join(stuff[i] for i in signature))

def signature_to_cast(signature):
    stuff = dict(C=int, R=lambda s: REG_NAMES.index(s) if s in REG_NAMES else int(s))
    return [stuff[i] for i in signature]

def parse_instruction(signature, instruction):
    groups = signature_to_regexp(signature).match(instruction).groups()
    return map(lambda c, o: c(o), signature_to_cast(signature), groups)


class RegisterFile(object):
    def __init__(self):
        self._registers = [0]*len(REG_NAMES)

    def __getitem__(self, i):
        return self._registers[i]

    def __setitem__(self, i, val):
        assert isinstance(val, int)
        if i == 0: return False
        self._registers[i] = val


class Core(object):
    def __init__(self):
        self._pc = 0
        self._stack = list()
        self._registers = RegisterFile()
        self._memory = [0]*655360

    @signature('RRR')
    def inst_add(self, d, s, t):
        self._registers[d] = self._registers[s] + self._registers[t]

    @signature('RRR')
    def inst_sub(self, d, s, t):
        self._registers[d] = self._registers[s] - self._registers[t]

    @signature('RRC')
    def inst_addi(self, t, s, C):
        self._registers[t] = self._registers[s] + C

    @signature('RRR')
    def inst_mult(self, d, s, t):
        self._registers[d] = self._registers[s] * self._registers[t]

    @signature('RRR')
    def inst_div(self, d, s, t):
        self._registers[d] = self._registers[s] / self._registers[t]

    @signature('RRR')
    def inst_mod(self, d, s, t):
        self._registers[d] = self._registers[s] % self._registers[t]

    @signature('RCR')
    def inst_lw(self, t, C, s):
        self._registers[t] = self._memory[self._registers[s] + C]

    @signature('RCR')
    def inst_sw(self, t, C, s):
        self._memory[self._registers[s] + C] = self._registers[t]

    @signature('RRR')
    def inst_and(self, d, s, t):
        self._registers[d] = self._registers[s] & self._registers[t]

    @signature('RRC')
    def inst_andi(self, t, s, C):
        self._registers[t] = self._registers[s] & C

    @signature('RRR')
    def inst_or(self, d, s, t):
        self._registers[d] = self._registers[s] | self._registers[t]

    @signature('RRC')
    def inst_ori(self, t, s, C):
        self._registers[t] = self._registers[s] | C

    @signature('RC')
    def inst_li(self, rd, C):
        self._registers[rd] = C

    @signature('R')
    def inst_stpop(self, rd):
        self._registers[rd] = self._stack.pop()

    @signature('R')
    def inst_stpush(self, rd):
        self._stack.append(self._registers[rd])

    @signature('C')
    def inst_stpushi(self, C):
        self._stack.append(C)

    @signature('C')
    def inst_jal(self, C):
        self._registers[1] = self._pc + 1
        self._pc = C

    @signature('R')
    def inst_pkr(self, r):
        return self._registers[r]

    @signature('C')
    def inst_pkm(self, C):
        return self._memory[C]


class Runtime(object):
    def __init__(self):
        self._core = Core()

    def do_instruction(self, instruction):
        op, rest = instruction.split(' ', 1)
        meth = getattr(self._core, 'inst_%s' % op, None)
        if meth is None: return
        return meth(*parse_instruction(meth.sig, rest))


