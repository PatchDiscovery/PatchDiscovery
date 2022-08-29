from copy import deepcopy
from collections import OrderedDict, defaultdict

def YesNO(BB, SubAddr):
    Yes = list(BB.InsDict.values())[-1].split(" ")[1]

    if (Yes == SubAddr):
        return "Yes"
    else:
        return "No"


def FilterAdd(BB1, BB2s, PF, VF, AnchorDict):
    InsSameAddr =[]
    InsSame = []

    for BB2 in BB2s:
        if BB1.InsList == BB2.InsList:
            InsSameAddr.append(BB2.addr)
            InsSame.append(BB2)

    if not len(InsSameAddr) > 1:
        return InsSameAddr

    BB2s = InsSame

    Filter = []
    for pre1 in BB1.Pres:
        if (pre1 in AnchorDict) and (len(PF.BBs[pre1].Subs) == 2):
            attr = YesNO(PF.BBs[pre1], BB1.addr)

            pre2 = AnchorDict[pre1]

            for BB2 in BB2s:
                if not (YesNO(VF.BBs[pre2], BB2.addr) == attr):
                    Filter.append(BB2)

    if (len(BB1.Subs) == 2):
        for sub1 in BB1.Subs:
            if (sub1 in AnchorDict):
                attr = YesNO(BB1, sub1)

                sub2 = AnchorDict[sub1]
                for BB2 in BB2s:
                    if (BB2 not in Filter):
                        if not (YesNO(BB2, sub2) == attr):
                            Filter.append(BB2)

    Add = []

    for BB2 in BB2s:
        if (BB2 not in Filter):
            Add.append(BB2.addr)

    return Add

def FindBaseAnchor(PF, VF):
    AnchorDict = {}

    # 起始节点
    FindAnchor(AnchorDict, PF.StartBBDict, VF.StartBBDict)
    # 终止节点
    FindAnchor(AnchorDict, PF.EndBBDict, VF.EndBBDict)

    # 库函数
    FindAnchor(AnchorDict, PF.LibBBDict, VF.LibBBDict)
    # 字符串
    FindAnchor(AnchorDict, PF.StrBBDict, VF.StrBBDict)
    # 用户定义函数
    FindAnchor(AnchorDict, PF.UDBBDict, VF.UDBBDict)

    FindAnchor(AnchorDict, PF.nPreBBDict, VF.nPreBBDict)

    FindAnchor(AnchorDict, PF.nSubBBDict, VF.nSubBBDict)

    Delete = set()
    for addr1, addr2 in AnchorDict.items():
        for addr1_1, addr2_1 in AnchorDict.items():
            if not(addr1_1 == addr1):
                if(addr2_1 == addr2):
                    Delete.add(addr1)
                    Delete.add(addr1_1)

    for addr1 in Delete:
        AnchorDict.pop(addr1)

    return AnchorDict

def FindAnchor(AnchorDict, PFBBDict, VFBBDict):
    Anchortemp = {}
    addr1s = []
    addr2s = []

    for addr1, bb1 in PFBBDict.items():
        for addr2, bb2 in VFBBDict.items():

            if (bb2.NormList1 == bb1.NormList1):

                if(addr1 not in addr1s) and (addr2 not in addr2s):
                    Anchortemp[addr1] = addr2
                    addr1s.append(addr1)
                    addr2s.append(addr2)

                elif(addr1 in addr1s) or (addr2 in addr2s):
                    Del = []
                    for a1, a2 in Anchortemp.items():
                        if (a1 == addr1) or (a2 == addr2):
                            Del.append(a1)

                    for a1 in Del:
                        Anchortemp.pop(a1)
    AnchorDict.update(Anchortemp)


def GetRestBBDict(AnchorDict, PFBBDict, VFBBDict):
    for bb1, bb2 in AnchorDict.items():
        if(bb1 in PFBBDict):
            PFBBDict.pop(bb1)

        if(bb2 in VFBBDict):
            VFBBDict.pop(bb2)

    return PFBBDict, VFBBDict

def UpdatePriority(AddAnchorDict, PFRestBBDict, Priority):

    for addr, bb in PFRestBBDict.items():
        if(addr not in Priority):
            Priority[addr] = 0

        if(len(set(bb.Pres).intersection(AddAnchorDict.keys()))>0) or (len(set(bb.Subs).intersection(AddAnchorDict.keys()))>0):
            Pres = bb.Pres
            Subs = bb.Subs

            for pre in Pres:
                if(pre in AddAnchorDict):
                    Priority[addr] = Priority[addr] + 1

            for sub in Subs:
                if(sub in AddAnchorDict):
                    Priority[addr] = Priority[addr] + 1


    Priority = OrderedDict(sorted(Priority.items(), key=lambda item: item[1], reverse=True))
    # print(Priority)
    return Priority


def Propagate(AnchorDict, Priority, PFRestBBDict, VFRestBBDict, P_Max, P_Min, PF, VF):
    # print(P_Max)
    AddAnchorDict = {}
    Used = []

    Label = True
    if(P_Max == P_Min):
        Label = False

    for addr1, p in Priority.items():
        if(p<P_Max): # 不考虑优先级低的
            break
        if(p == P_Max):
            bb1 = PF.BBs[addr1]

            Pres1 = bb1.Pres
            Subs1 = bb1.Subs


            addr2s_pre = []
            for pre1 in Pres1:
                if(pre1 in AnchorDict):
                    pre2 = AnchorDict[pre1]
                    subs_pre2_temp = VF.BBs[pre2].Subs
                    subs_pre2 = [i for i in subs_pre2_temp if i in VFRestBBDict]

                    if(len(addr2s_pre)==0):
                        addr2s_pre = subs_pre2
                    else:
                        addr2s_pre = list(set(addr2s_pre).intersection(set(subs_pre2)))


            addr2s_sub = []
            for sub1 in Subs1:
                if(sub1 in AnchorDict):
                    sub2 = AnchorDict[sub1]
                    # print('\033[33m%s\033[0m' % (sub2))
                    pres_sub2_temp = VF.BBs[sub2].Pres
                    pres_sub2 = [i for i in pres_sub2_temp if i in VFRestBBDict]

                    # print('\033[33m%s\033[0m' % (pres_sub2))

                    if(len(addr2s_sub)==0):
                        addr2s_sub = pres_sub2
                    else:
                        addr2s_sub = list(set(addr2s_sub).intersection(set(pres_sub2)))

            addr2s = []
            if(len(addr2s_pre)>0 and (len(addr2s_sub)>0)):
                addr2s = list(set(addr2s_pre).intersection(set(addr2s_sub)))
            elif(len(addr2s_pre)>0):
                addr2s = addr2s_pre
            elif(len(addr2s_sub)>0):
                addr2s = addr2s_sub

            Add = []
            for addr2 in addr2s:
                if(addr2 in VFRestBBDict):
                    if(PF.BBs[addr1].NormList1 == VF.BBs[addr2].NormList1):
                        Add.append(addr2)

            Add = list(set(Add))

            if (len(Add) > 1):
                Addr1BB = PF.BBs[addr1]
                Addr2BBs = []
                for addr2 in Add:
                    Addr2BBs.append(VF.BBs[addr2])

                Add = FilterAdd(Addr1BB, Addr2BBs, PF, VF, AnchorDict)

            Add = list(set(Add))

            if(len(Add) == 1):
                if(Add[0] in Used):
                    Dela1 = []
                    for a1, a2 in AddAnchorDict.items():
                        if(a2 == Add[0]):
                            Dela1.append(a1)
                    for a1 in Dela1:
                        if(a1 in AddAnchorDict):
                            AddAnchorDict.pop(a1)

                else:
                    Used.append(Add[0])
                    AddAnchorDict[addr1] = Add[0]

    if(len(AddAnchorDict)>0):
        for addr1, addr2 in AddAnchorDict.items():
            AnchorDict[addr1] = addr2

            Priority.pop(addr1)
            PFRestBBDict.pop(addr1)
            VFRestBBDict.pop(addr2)
        Priority = UpdatePriority(AddAnchorDict, PFRestBBDict, Priority)
        if(len(Priority)>0):
            P_Max = Priority[list(Priority.keys())[0]]
            P_Min = Priority[list(Priority.keys())[len(list(Priority.keys())) - 1]]
            Propagate(AnchorDict, Priority, PFRestBBDict, VFRestBBDict, P_Max, P_Min, PF, VF)
    elif(Label):
        for addr, p in Priority.items():
            if (p < P_Max):
                P_Max = p
                break
        if(P_Max>0)and(len(Priority)>0):
            P_Min = Priority[list(Priority.keys())[len(list(Priority.keys())) - 1]]
            Propagate(AnchorDict, Priority, PFRestBBDict, VFRestBBDict, P_Max, P_Min, PF, VF)
        else:
            return
    else:
        return

def AnchorAndPropagate(AnchorDict, PFBBs, VFBBs, PF, VF):
    PFRestBBDict, VFRestBBDict = GetRestBBDict(AnchorDict, deepcopy(PFBBs), deepcopy(VFBBs))

    if(len(PFRestBBDict) == 0) or (len(VFRestBBDict) == 0):
        return AnchorDict, PFRestBBDict, VFRestBBDict

    Priority = UpdatePriority(AnchorDict, PFRestBBDict, {})
    # print(Priority)

    P_Max = Priority[list(Priority.keys())[0]]
    P_Min = Priority[list(Priority.keys())[len(list(Priority.keys())) - 1]]
    Propagate(AnchorDict, Priority, PFRestBBDict, VFRestBBDict, P_Max, P_Min, PF, VF)


    return AnchorDict, PFRestBBDict, VFRestBBDict


def LastCheck(AnchorDict, PFRestBBDict, VFRestBBDict, PF, VF):
    AddAnchorDict = {}
    TempBBPairDict = defaultdict(list)

    for addr1, addr2 in AnchorDict.items():
        bb1 = PF.BBs[addr1]
        bb2 = VF.BBs[addr2]

        Prepre1s = []
        for pre1 in bb1.Pres:
            if(pre1 not in AnchorDict) and (pre1 in PF.BBs):
                for prepre1 in PF.BBs[pre1].Pres:
                    if(prepre1 not in AnchorDict) and (prepre1 in PFRestBBDict):
                        Prepre1s.append(prepre1)
        Prepre1s = list(set(Prepre1s))

        Prepre2s = []
        for pre2 in bb2.Pres:
            if(pre2 not in list(AnchorDict.values())) and (pre2 in VF.BBs):
                for prepre2 in VF.BBs[pre2].Pres:
                    if(prepre2 not in list(AnchorDict.values())) and (prepre2 in VFRestBBDict):
                        Prepre2s.append(prepre2)

        Prepre2s = list(set(Prepre2s))
        for prepre1 in Prepre1s:
            for prepre2 in Prepre2s:
                if(PF.BBs[prepre1].NormList1 == VF.BBs[prepre2].NormList1):
                    TempBBPairDict[prepre1].append(prepre2)


        Subsub1s = []
        for sub1 in bb1.Subs:
            if(sub1 not in AnchorDict) and (sub1 in PF.BBs):
                for subsub1 in PF.BBs[sub1].Subs:
                    if(subsub1 not in AnchorDict) and (subsub1 in PFRestBBDict):
                        Subsub1s.append(subsub1)
        Subsub1s = list(set(Subsub1s))

        Subsub2s = []
        for sub2 in bb2.Subs:
            if(sub2 not in list(AnchorDict.values())) and (sub2 in VF.BBs):
                for subsub2 in VF.BBs[sub2].Subs:
                    if(subsub2 not in list(AnchorDict.values())) and (subsub2 in VFRestBBDict):
                        Subsub2s.append(subsub2)
        Subsub2s = list(set(Subsub2s))

        for subsub1 in Subsub1s:
            for subsub2 in Subsub2s:
                if(subsub1 not in AnchorDict) and (subsub2 not in list(AnchorDict.items())):
                    if (PF.BBs[subsub1].NormList1 == VF.BBs[subsub2].NormList1):
                        TempBBPairDict[subsub1].append(subsub2)



    for addr1, addr2s in TempBBPairDict.items():
        addr2s = list(set(addr2s))
        if(len(addr2s)==1):
            AddAnchorDict[addr1] = addr2s[0]

    TempAddAnchorDict = {}
    for addr1, addr2 in AddAnchorDict.items():
        Label = True
        for key, value in  AddAnchorDict.items():
            if not(key == addr1):
                if(addr2 == value):
                    Label = False
                    break

        if(Label):
            TempAddAnchorDict[addr1] = addr2
            AnchorDict[addr1] = addr2

    if(len(TempAddAnchorDict.keys())>0):
        AnchorDict, PFRestBBDict, VFRestBBDict = AnchorAndPropagate(AnchorDict, PFRestBBDict, VFRestBBDict, PF, VF)

    for addr1, bb1 in PFRestBBDict.items():
        addr2s = []
        for addr2, bb2 in VFRestBBDict.items():
            if(bb1.InsList == bb2.InsList):
                addr2s.append(addr2)

        if(len(addr2s) == 1):
            AddAnchorDict[addr1] = addr2s[0]

    TempAddAnchorDict = {}
    for addr1, addr2 in AddAnchorDict.items():
        Label = True
        for key, value in AddAnchorDict.items():
            if not (key == addr1):
                if (addr2 == value):
                    Label = False
                    break

        if (Label):
            TempAddAnchorDict[addr1] = addr2
            AnchorDict[addr1] = addr2

    if (len(TempAddAnchorDict.keys()) > 0):
        AnchorDict, PFRestBBDict, VFRestBBDict = AnchorAndPropagate(AnchorDict, PFRestBBDict, VFRestBBDict, PF, VF)

    return AnchorDict, PFRestBBDict, VFRestBBDict


def BBMap(PF, VF):

    print(10 * "-" + "\033[;33mFind Base Anchor\033[0m" + 10 * "-")
    AnchorDict = FindBaseAnchor(PF, VF)


    for addr1, addr2 in AnchorDict.items():
        print(addr1, addr2)
    print()

    AnchorDict, PFRestBBDict, VFRestBBDict = AnchorAndPropagate(AnchorDict, PF.BBs, VF.BBs, PF, VF)

    print(10 * "-" + "\033[;33mLast Check\033[0m" + 10 * "-")
    AnchorDict, PFRestBBDict, VFRestBBDict = LastCheck(AnchorDict, PFRestBBDict, VFRestBBDict, PF, VF)
    print()

    print(10*"-" + "\033[;33mMatch BB\033[0m" + 10*"-")
    for addr1 in PF.BBs.keys():
        if(addr1 in AnchorDict):
            print(addr1, AnchorDict[addr1])
        else:
            print(addr1)


    return AnchorDict, PFRestBBDict, VFRestBBDict,





