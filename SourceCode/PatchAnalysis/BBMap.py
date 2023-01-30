from copy import deepcopy
from collections import OrderedDict, defaultdict
from AnalyzeBinary.PatchAnalyze.Normalize import Normalize1, Normalize2, Normalize3
from AnalyzeBinary.ReadPickle import ReadPickle


def CheckBB(addr1, addr2, PF, VF, AnchorDict, CheckNum):
    bb1 = PF.BBs[addr1]
    bb2 = VF.BBs[addr2]

    Pres1 = bb1.Pres
    Subs1 = bb1.Subs

    Pres2 = [AnchorDict[pre1] for pre1 in Pres1 if pre1 in AnchorDict]
    Subs2 = [AnchorDict[sub1] for sub1 in Subs1 if sub1 in AnchorDict]

    if CheckNum == 1:
        if (set(Pres1).issubset(set(AnchorDict.keys())) and set(Subs1).issubset(set(AnchorDict.keys()))) and set(
                Pres2) == set(bb2.Pres) and set(Subs2) == set(bb2.Subs):
            return True
        return False

    elif CheckNum == 2:
        if set(Subs1).issubset(set(AnchorDict.keys())) and set(Subs2) == set(bb2.Subs):
            return True
        return False

    elif CheckNum == 3:
        if set(Pres1).issubset(set(AnchorDict.keys())) and set(Pres2) == set(bb2.Pres):
            return True
        return False


def IdentifyEqualBB(addr1, addr2s, PF, VF, AnchorDict, AddAnchorDict):
    True_addr2 = ""
    for addr2 in addr2s:
        if addr2 not in AddAnchorDict.values():

            bb1 = PF.BBs[addr1]
            bb2 = VF.BBs[addr2]

            Pres1 = bb1.Pres
            Subs1 = bb1.Subs

            if set(Pres1).issubset(set(AnchorDict.keys())) and set(Subs1).issubset(set(AnchorDict.keys())):
                if CheckBB(addr1, addr2, PF, VF, AnchorDict, 1):
                    return addr2

            elif set(Pres1).issubset(set(AnchorDict.keys())):
            # elif set(Pres1).issubset(set(AnchorDict.keys())) and set(Subs1).intersection(set(AnchorDict.keys())):

                Pres2 = [AnchorDict[pre1] for pre1 in Pres1]
                if not set(Pres2) == set(bb2.Pres):
                    break

                Subs2 = [AnchorDict[sub1] for sub1 in Subs1 if sub1 in AnchorDict]
                if not set(Subs2).issubset(set(bb2.Subs)):
                    break

                Subs1 = [sub1 for sub1 in Subs1 if sub1 not in AnchorDict]
                Subs2 = [sub2 for sub2 in bb2.Subs if sub2 not in AnchorDict.values()]

                Subs1_Rest = []
                while Subs1:
                    sub1 = Subs1.pop()
                    Label = False

                    for sub2 in Subs2:
                        if PF.BBs[sub1].NormList1 == VF.BBs[sub2].NormList1 \
                                and CheckBB(sub1, sub2, PF, VF, AnchorDict, 2):
                            Label = True
                            Subs2.remove(sub2)
                            break

                    if not Label:
                        Subs1_Rest.append(sub1)

                if not Subs1_Rest:
                    return addr2

            elif set(Subs1).issubset(set(AnchorDict.keys())):
            # elif set(Pres1).intersection(set(AnchorDict.keys())) and set(Subs1).issubset(set(AnchorDict.keys())):
                Subs2 = [AnchorDict[sub1] for sub1 in Subs1]
                if not set(Subs2) == set(bb2.Subs):
                    break

                Pres2 = [AnchorDict[Pre1] for Pre1 in Pres1 if Pre1 in AnchorDict]
                if not set(Pres2).issubset(set(bb2.Pres)):
                    break

                Pres1 = [Pre1 for Pre1 in Pres1 if Pre1 not in AnchorDict]
                Pres2 = [Pre2 for Pre2 in bb2.Pres if Pre2 not in AnchorDict.values()]

                Pres1_Rest = []
                while Pres1:
                    pre1 = Pres1.pop()
                    Label = False

                    for pre2 in Pres2:
                        if PF.BBs[pre1].NormList1 == VF.BBs[pre2].NormList1 \
                                and CheckBB(pre1, pre2, PF, VF, AnchorDict, 3):
                            Label = True
                            Pres2.remove(pre2)
                            break

                    if not Label:
                        Pres1_Rest.append(pre1)

                if not Pres1_Rest:
                    return addr2

    return True_addr2


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
            if not (addr1_1 == addr1):
                if (addr2_1 == addr2):
                    Delete.add(addr1)
                    Delete.add(addr1_1)

    for addr1 in Delete:
        AnchorDict.pop(addr1)

    return AnchorDict


def FindAnchor(AnchorDict, PFBBDict, VFBBDict):
    for addr1, bb1 in PFBBDict.items():
        # if addr1 == "0x452216" or addr1 == "0x452478":
        #     print()
        addr2s = []

        for addr2, bb2 in VFBBDict.items():
            # temp1 = bb1.NormList1
            # temp2 = bb2.NormList1
            if (bb2.NormList1 == bb1.NormList1):
                addr2s.append(addr2)

        if len(addr2s) == 1:
            AnchorDict[addr1] = addr2s[0]


def GetRestBBDict(AnchorDict, PFBBDict, VFBBDict):
    for bb1, bb2 in AnchorDict.items():
        if (bb1 in PFBBDict):
            PFBBDict.pop(bb1)

        if (bb2 in VFBBDict):
            VFBBDict.pop(bb2)

    return PFBBDict, VFBBDict


def UpdatePriority(AddAnchorDict, PFRestBBDict, Priority):
    for addr, bb in PFRestBBDict.items():
        if (addr not in Priority):
            Priority[addr] = 0

        if (len(set(bb.Pres).intersection(AddAnchorDict.keys())) > 0) or (
                len(set(bb.Subs).intersection(AddAnchorDict.keys())) > 0):
            Pres = bb.Pres
            Subs = bb.Subs

            for pre in Pres:
                if (pre in AddAnchorDict):
                    Priority[addr] = Priority[addr] + 1

            for sub in Subs:
                if (sub in AddAnchorDict):
                    Priority[addr] = Priority[addr] + 1

    Priority = OrderedDict(sorted(Priority.items(), key=lambda item: item[1], reverse=True))
    return Priority

def CountMapBB(addr1, addr2, PF, VF, AnchorDict):

    Pres2 = [pre2 for pre2 in VF.BBs[addr2].Pres if pre2 not in AnchorDict.values()]
    Subs2 = [sub2 for sub2 in VF.BBs[addr2].Subs if sub2 not in AnchorDict.values()]


    Pres1 = [pre1 for pre1 in PF.BBs[addr1].Pres if pre1 not in AnchorDict]
    MapPre = []
    while Pres2:
        pre2 = Pres2.pop()

        for pre1 in Pres1:
            if PF.BBs[pre1].NormList1 == VF.BBs[pre2].NormList1:
                Pres1.remove(pre1)
                MapPre.append(pre2)
                break

    Subs1 = [sub1 for sub1 in PF.BBs[addr1].Subs if sub1 not in AnchorDict]

    MapSub = []

    while Subs2:
        sub2 = Subs2.pop()

        for sub1 in Subs1:
            if PF.BBs[sub1].NormList1 == VF.BBs[sub2].NormList1:
                Subs1.remove(sub1)
                MapSub.append(sub2)
                break


    return len(MapSub) + len(MapPre)



def ChooseAddr1(Addr1s,addr2, PF, VF, AnchorDict):

    Addr1Count = {}
    for addr1 in Addr1s:
        Addr1Count[addr1] = CountMapBB(addr1, addr2, PF, VF,AnchorDict)

    Addr1Count = sorted(Addr1Count.items(), key=lambda x: x[1], reverse=True)

    if Addr1Count[0][1]> Addr1Count[1][1]:
        return Addr1Count[0][0]
    else:
        return False





def CheckAddAnchorDict(AddAnchorDict, AnchorDict, PF, VF):
    Verify = {}
    for addr1, addr2 in AddAnchorDict.items():
        if addr2 in Verify.values():
            continue
        Addr1s = [a1 for a1, a2 in AddAnchorDict.items() if a2 == addr2]

        if len(Addr1s)>1:
            ChooseResult = ChooseAddr1(Addr1s,addr2, PF, VF, AnchorDict)
            if ChooseResult:
                Verify[ChooseResult] = addr2
        else:
            Verify[addr1] = addr2

    return Verify




def Propagate(AnchorDict, Priority, PFRestBBDict, VFRestBBDict, P_Max, P_Min, PF, VF):
    AddAnchorDict = {}

    Label = True
    if (P_Max == P_Min):
        Label = False

    for addr1, p in Priority.items():
        if (p < P_Max):  # 不考虑优先级低的
            break
        if (p == P_Max):
            if addr1 == "0x4529bb":
                print()
            # print(addr1)
            bb1 = PF.BBs[addr1]

            Pres1 = bb1.Pres
            Subs1 = bb1.Subs

            addr2s_pre = []
            for pre1 in Pres1:
                if (pre1 in AnchorDict):
                    pre2 = AnchorDict[pre1]

                    # subs_pre2 = []
                    # for i in VF.BBs[pre2].Subs:
                    #     if i in VFRestBBDict:
                    #         a = PF.BBs[addr1].NormList1
                    #         b = VF.BBs[i].NormList1
                    #         if PF.BBs[addr1].NormList1 == VF.BBs[i].NormList1:
                    #             subs_pre2.append(i)

                    subs_pre2 = [i for i in VF.BBs[pre2].Subs if
                                 (i in VFRestBBDict) and (PF.BBs[addr1].NormList1 == VF.BBs[i].NormList1)]

                    if (len(addr2s_pre) == 0):
                        addr2s_pre = subs_pre2
                    else:
                        addr2s_pre = list(set(addr2s_pre).intersection(set(subs_pre2)))

            addr2s_sub = []
            for sub1 in Subs1:
                if (sub1 in AnchorDict):
                    sub2 = AnchorDict[sub1]
                    pres_sub2 = [i for i in VF.BBs[sub2].Pres if
                                 (i in VFRestBBDict) and (PF.BBs[addr1].NormList1 == VF.BBs[i].NormList1)]

                    if (len(addr2s_sub) == 0):
                        addr2s_sub = pres_sub2
                    else:
                        addr2s_sub = list(set(addr2s_sub).intersection(set(pres_sub2)))

            addr2s = []
            if (len(addr2s_pre) > 0 and (len(addr2s_sub) > 0)):
                addr2s = list(set(addr2s_pre).intersection(set(addr2s_sub)))
            elif (len(addr2s_pre) > 0):
                addr2s = addr2s_pre
            elif (len(addr2s_sub) > 0):
                addr2s = addr2s_sub

            if len(addr2s) == 1:
                AddAnchorDict[addr1] = addr2s[0]
            else:
                addr2 = IdentifyEqualBB(addr1, addr2s, PF, VF, AnchorDict, AddAnchorDict)
                if addr2:
                    AddAnchorDict[addr1] = addr2


    AddAnchorDict = CheckAddAnchorDict(AddAnchorDict, AnchorDict, PF, VF)
    if (len(AddAnchorDict) > 0):

        for addr1, addr2 in AddAnchorDict.items():
            AnchorDict[addr1] = addr2

            Priority.pop(addr1)
            PFRestBBDict.pop(addr1)
            VFRestBBDict.pop(addr2)
        Priority = UpdatePriority(AddAnchorDict, PFRestBBDict, Priority)
        if (len(Priority) > 0):
            P_Max = Priority[list(Priority.keys())[0]]
            P_Min = Priority[list(Priority.keys())[len(list(Priority.keys())) - 1]]
            Propagate(AnchorDict, Priority, PFRestBBDict, VFRestBBDict, P_Max, P_Min, PF, VF)
    elif (Label):
        for addr, p in Priority.items():
            if (p < P_Max):
                P_Max = p
                break
        if (P_Max > 0) and (len(Priority) > 0):
            P_Min = Priority[list(Priority.keys())[len(list(Priority.keys())) - 1]]
            Propagate(AnchorDict, Priority, PFRestBBDict, VFRestBBDict, P_Max, P_Min, PF, VF)
        else:
            return
    else:
        return


def AnchorAndPropagate(AnchorDict, PFBBs, VFBBs, PF, VF):
    PFRestBBDict, VFRestBBDict = GetRestBBDict(AnchorDict, deepcopy(PFBBs), deepcopy(VFBBs))

    if (len(PFRestBBDict) == 0) or (len(VFRestBBDict) == 0):
        return AnchorDict, PFRestBBDict, VFRestBBDict

    Priority = UpdatePriority(AnchorDict, PFRestBBDict, {})

    P_Max = Priority[list(Priority.keys())[0]]
    P_Min = Priority[list(Priority.keys())[len(list(Priority.keys())) - 1]]
    Propagate(AnchorDict, Priority, PFRestBBDict, VFRestBBDict, P_Max, P_Min, PF, VF)

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

    print(10 * "-" + "\033[;33mMatch BB\033[0m" + 10 * "-")
    for addr1 in PF.BBs.keys():
        if (addr1 in AnchorDict):
            print(addr1, AnchorDict[addr1])
        else:
            print(addr1)

    print(10 * "-" + "\033[;33mPF Rest BB\033[0m" + 10 * "-")
    for addr, BB in PFRestBBDict.items():
        print(BB)

    print(10 * "-" + "\033[;33mVF Rest BB\033[0m" + 10 * "-")
    for addr, BB in VFRestBBDict.items():
        print(BB)
    # print(VFRestBBDict)
    return AnchorDict, PFRestBBDict, VFRestBBDict


def LastCheck(AnchorDict, PFRestBBDict, VFRestBBDict, PF, VF):
    AddAnchorDict = {}
    TempBBPairDict = defaultdict(list)

    for addr1, addr2 in AnchorDict.items():
        bb1 = PF.BBs[addr1]
        bb2 = VF.BBs[addr2]

        Prepre1s = []
        for pre1 in bb1.Pres:
            if (pre1 not in AnchorDict) and (pre1 in PF.BBs):
                for prepre1 in PF.BBs[pre1].Pres:
                    if (prepre1 not in AnchorDict) and (prepre1 in PFRestBBDict):
                        Prepre1s.append(prepre1)
        Prepre1s = list(set(Prepre1s))

        Prepre2s = []
        for pre2 in bb2.Pres:
            if (pre2 not in list(AnchorDict.values())) and (pre2 in VF.BBs):
                for prepre2 in VF.BBs[pre2].Pres:
                    if (prepre2 not in list(AnchorDict.values())) and (prepre2 in VFRestBBDict):
                        Prepre2s.append(prepre2)

        Prepre2s = list(set(Prepre2s))
        for prepre1 in Prepre1s:
            for prepre2 in Prepre2s:
                if (PF.BBs[prepre1].NormList1 == VF.BBs[prepre2].NormList1):
                    TempBBPairDict[prepre1].append(prepre2)

        Subsub1s = []
        for sub1 in bb1.Subs:
            if (sub1 not in AnchorDict) and (sub1 in PF.BBs):
                for subsub1 in PF.BBs[sub1].Subs:
                    if (subsub1 not in AnchorDict) and (subsub1 in PFRestBBDict):
                        Subsub1s.append(subsub1)
        Subsub1s = list(set(Subsub1s))

        Subsub2s = []
        for sub2 in bb2.Subs:
            if (sub2 not in list(AnchorDict.values())) and (sub2 in VF.BBs):
                for subsub2 in VF.BBs[sub2].Subs:
                    if (subsub2 not in list(AnchorDict.values())) and (subsub2 in VFRestBBDict):
                        Subsub2s.append(subsub2)
        Subsub2s = list(set(Subsub2s))

        for subsub1 in Subsub1s:
            for subsub2 in Subsub2s:
                if (subsub1 not in AnchorDict) and (subsub2 not in list(AnchorDict.items())):
                    if (PF.BBs[subsub1].NormList1 == VF.BBs[subsub2].NormList1):
                        TempBBPairDict[subsub1].append(subsub2)

    for addr1, addr2s in TempBBPairDict.items():
        addr2s = list(set(addr2s))
        if (len(addr2s) == 1):
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

    for addr1, bb1 in PFRestBBDict.items():
        addr2s = []
        for addr2, bb2 in VFRestBBDict.items():
            if (bb1.InsList == bb2.InsList):
                addr2s.append(addr2)

        if (len(addr2s) == 1):
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
