import re
import string
from copy import deepcopy

REGS_X64 = [ "rip", "rax", "eax", "ax", "al", "ah", "rbx", "ebx", "bx", "bl", "bh", "rcx", "ecx", "cx", "cl",
                "ch", "rdx", "edx", "dx", "dl", "dh", "rsi", "esi", "si", "sil", "rdi", "edi", "di", "dil", "rbp", "ebp",
                "bp", "bpl", "rsp", "esp", "sp", "spl", "r8", "r8d", "r8w", "r8b", "r9", "r9d", "r9w", "r9b",
                "r10", "r10d", "r10w", "r10b", "r11", "r11d", "r11w", "r11b", "r12", "r12d", "r12w", "r12b",
                "r13", "r13d", "r13w", "r13b", "r14", "r14d", "r14w", "r14b", "r15", "r15d", "r15w", "r15b"]

REGS_2 = ['rax', 'rcx', 'rdx', 'rbx', 'rsi', 'rdi', 'rsp', 'rbp', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15',
'eax', 'ecx', 'edx', 'ebx', 'esi', 'edi', 'esp', 'ebp', 'r8d', 'r9d', 'r10d', 'r11d', 'r12d', 'r13d', 'r14d', 'r15d',
'ax', 'cx', 'dx', 'bx', 'si', 'di', 'sp', 'bp', 'r8w', 'r9w', 'r10w', 'r11w', 'r12w', 'r13w', 'r14w', 'r15w',
'al', 'cl', 'dl', 'bl', 'sil', 'dil', 'spl', 'bpl', 'r8b', 'r9b', 'r10b', 'r11b', 'r12b', 'r13b', 'r14b', 'r15b']

def Normalize1(BBs):
    # 数据依赖抽象

    for BB_addr, BB in BBs.items():
        BB.NormList1 = []

        for addr, asm in BB.InsDict.items():

            if ("Str:" in asm):
                Operands = asm.split(" ", 1)[1].split(",")

                for oper in Operands:
                    if (oper.startswith("Str:")):
                        if ("Str:" in oper):
                            Tempoper = oper.replace("Str:", "")
                            trantab = str.maketrans({key: None for key in string.punctuation})
                            asm = asm.replace(oper, Tempoper.translate(trantab).lower())

            asm = asm.replace("Lib:", "").replace("Str:", "")

            if (asm.startswith("jmp") or asm.startswith("nop")):
                continue

            if (asm.startswith("j")) and ("," not in asm):
                op = asm.split(" ")[1]
                if (op.startswith("0x")):
                    asm = asm.replace(op, "addr")

                elif(op == "addr"):
                    asm = asm.replace(op, "addr")

                BB.NormList1.append(asm)
                continue
            else:
                if (asm.startswith("call")):
                    op = asm.split(" ")[1]
                    if (op.startswith("UDFunc:")):
                        asm = asm.replace(op, "UDFunc")
                        BB.NormList1.append(asm)
                        continue

            if (" " not in asm):
                BB.NormList1.append(asm)
                continue

            Operands = asm.split(" ", 1)[1].split(",")

            for i in range(0, len(Operands)):
                oper = Operands[i]
                if (oper in REGS_X64) or (oper in REGS_2):
                    Operands[i] = "reg"

                elif ("[" in oper):
                    # men = re.split("\[|\]", oper)[1]
                    # Operands[i] = oper.replace(men, "mem")
                    Operands[i] = "mem"

                elif (oper.startswith("0x") or oper.startswith("-0x")):
                    Operands[i] = "addr"
                    # Operands[i] = "imme"

                elif (oper == "addr"):
                    Operands[i] = "addr"

            temp = asm.split(" ", 1)[0] + " " + (",".join(Operands))
            BB.NormList1.append(temp)

        if(len(BB.NormList1) == 0):
            Label = True
            tempList = []
            for addr, asm in BB.InsDict.items():
                if not(asm.startswith("jmp") or (asm.startswith("nop"))):
                    Label = False
                    break
                if(asm.startswith("jmp")):
                    tempList.append("jmp addr")
                if(asm.startswith("nop")):
                    tempList.append("nop")
            if(Label):
                BB.NormList1 = tempList



def Normalize2(BBs):
    # 无数据依赖抽象

    for BB_addr, BB in BBs.items():
        BB.NormList2 = []

        for addr, asm in BB.InsDict.items():

            if("Str:" in asm):
                Operands = asm.split(" ", 1)[1].split(",")

                for oper in Operands:
                    if(oper.startswith("Str:")):
                        Tempoper = oper.replace("Str:", "")
                        trantab = str.maketrans({key: None for key in string.punctuation})
                        asm = asm.replace(oper, Tempoper.translate(trantab).lower())

            asm = asm.replace("Lib:", "").replace("Str:", "")

            if (asm.startswith("jmp") or asm.startswith("nop")):
                continue

            if (asm.startswith("j")) and ("," not in asm):
                op = asm.split(" ")[1]
                if (op.startswith("0x")):
                    asm = asm.replace(op, "addr")
                elif (op == "addr"):
                    asm = asm.replace(op, "addr")
                BB.NormList2.append(asm)
                continue
            else:
                if (asm.startswith("call")):
                    op = asm.split(" ")[1]
                    if (op.startswith("UDFunc:")):
                        asm = asm.replace(op, "UDFunc")
                        BB.NormList2.append(asm)
                        continue

            if (" " not in asm):
                BB.NormList2.append(asm)
                continue

            Operands = asm.split(" ", 1)[1].split(",")

            for i in range(0, len(Operands)):
                oper = Operands[i]
                if (oper in REGS_X64) or (oper in REGS_2):
                    Operands[i] = "reg"

                elif ("[" in oper):
                    # men = re.split("\[|\]", oper)[1]
                    # Operands[i] = oper.replace(men, "mem")
                    Operands[i] = "mem"

                elif (oper.startswith("0x") or oper.startswith("-0x")):
                    Operands[i] = "addr"
                    # Operands[i] = "imme"
                elif(oper == "addr"):
                    Operands[i] = "addr"


            temp = asm.split(" ", 1)[0] + " " + (",".join(Operands))
            BB.NormList2.append(temp)

        if (len(BB.NormList2) == 0):
            Label = True
            tempList = []
            for addr, asm in BB.InsDict.items():
                if not (asm.startswith("jmp") or (asm.startswith("nop"))):
                    Label = False
                    break
                if (asm.startswith("jmp")):
                    tempList.append("jmp addr")
                if (asm.startswith("nop")):
                    tempList.append("nop")
            if (Label):
                BB.NormList2 = tempList


def Normalize3(BBs):

    for addr, bb in BBs.items():
        TempInsList = deepcopy(bb.InsList)
        bb.InsList = []
        for ins in TempInsList:
            if (ins.startswith("j")) and ("," not in ins):
                op = ins.split(" ")[1]
                if (op.startswith("0x")):
                    ins = ins.replace(op, "addr")
                bb.InsList.append(ins)
            else:
                bb.InsList.append(ins)






