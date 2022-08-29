from copy import deepcopy as deepcopy
from AnalyzeBinary.PatchAnalyze.Normalize import Normalize2
from AnalyzeBinary.PatchAnalyze.BBAnalyze_Temp import BBAnalyze
from collections import OrderedDict,defaultdict

class Path:
    def __init__(self, BBs):
        self.BBs = BBs
        self.NormList = []
        self.BB_Addrs = []
        self.P = ""

        for bb in self.BBs:
            self.BB_Addrs.append(bb.addr)
            self.NormList.extend(bb.NormList2)
        self.P = "-".join(self.BB_Addrs)

    def __str__(self):
        return self.P

class PathSet:
    def __init__(self):
        self.Paths = []
        self.BBs = []
        self.Ps = set()

    def Add_Path(self, Path):
        self.Paths.append(Path)
        self.BBs.extend(Path.BBs)
        self.BBs = list(set(self.BBs))
        self.Ps.add(Path.P)


def ExtractPath1(NowPath, NowBB, BBs, SameBBList, Path):

    addr = NowBB.addr
    if(NowBB.addr in SameBBList) or (len(NowBB.Subs) == 0) or (NowBB.addr in NowPath):
        NowPath.append(NowBB.addr)
        Path.append(tuple(NowPath))
    else:
        NowPath.append(NowBB.addr)

        for NextBBaddr in NowBB.Subs:
            NewPath = deepcopy(NowPath)
            ExtractPath1(NewPath, BBs[NextBBaddr], BBs, SameBBList, Path)


def InitPath(RestBBs, BBs, SameBBList):
    Paths = []
    for addr, BB in BBs.items():
        addr = BB.addr

        if (addr not in RestBBs):
            if(len(set(BB.Subs).intersection(set(RestBBs))) > 0):
                for NextBBaddr in BB.Subs:
                    if(NextBBaddr in RestBBs):
                        NowPath = []
                        NowPath.append(addr)
                        NowBB = BBs[NextBBaddr]
                        ExtractPath1(NowPath, NowBB, BBs, SameBBList, Paths)

        elif(len(BB.Pres) == 0):
            if (BB.addr in RestBBs):
                if(len(BB.Subs)>0):
                    for NextBBaddr in BB.Subs:
                        NowPath = []
                        NowPath.append(addr)
                        NowBB = BBs[NextBBaddr]
                        ExtractPath1(NowPath, NowBB, BBs, SameBBList, Paths)
                else:
                    NowPath = []
                    NowPath.append(addr)
                    Paths.append(tuple(NowPath))

    TempPaths = {}
    Paths = list(set(Paths))

    for src_p in Paths:
        p = list(src_p)
        # print(p)
        temp = []
        for addr in p:
            if not(addr in SameBBList):
                temp.append(BBs[addr])

        start = None
        end = None

        if(p[0] in SameBBList):
            start = p[0]
            p.remove(p[0])
        elif(len(BBs[p[0]].Pres)==0):
                start = "Start"

        if(p[-1] in SameBBList):
            end = p[-1]
            p.remove(p[-1])
        elif(len(BBs[p[-1]].Subs)==0):
            end = "End"

        if((start, end) not in TempPaths):
            TempPaths[(start, end)] = PathSet()

        TempPaths[(start, end)]. Add_Path(Path(temp))

    return TempPaths

def MatchPath(Paths1, Paths2, SameBBDict):

    PP = {}
    for key in Paths1.keys():
        if(key[0] in SameBBDict):
            start = SameBBDict[key[0]]
        else:
            start = key[0]

        if(key[1] in SameBBDict):
            end = SameBBDict[key[1]]
        else:
            end = key[1]

        if((start, end) in Paths2):
            PP[key] = (start, end)

    return PP

def Equal(Ps1,Ps1_1, Ps2, Ps2_1):
    if(Ps1 == Ps1_1) and (Ps2 == Ps2_1):
        return True
    elif(Ps1_1.issubset(Ps1)) and (Ps2_1.issubset(Ps2)):
        return True
    else:
        return False




def BBRank(PFRestBBDict, VFRestBBDict, SameBBDict, PFBBs, VFBBs, IDF):

    RankBB1 = {}
    RankBB12 = {}
    RankBB2 = {}

    AddBB1 = []
    DelBB2 = []
    BBPair = {}


    PPaths = InitPath(PFRestBBDict, PFBBs, list(SameBBDict.keys()))
    VPaths = InitPath(VFRestBBDict, VFBBs, list(SameBBDict.values()))


    PP = MatchPath(PPaths, VPaths, SameBBDict)

    print(50 * "-")
    for key1, key2 in PP.items():
        print(key1, key2)

        for P1 in PPaths[key1].Paths:
            print(P1)
        print()

        for P2 in VPaths[key2].Paths:
            print(P2)

        print()
        print()

    for key1 in PPaths.keys():
        if (key1 not in PP):
            if (key1[0] in PFBBs) and (key1[1] in PFBBs) and (key1[0] in SameBBDict) and (key1[1] in SameBBDict):
                start1 = key1[0]
                end1 = key1[1]

                start2 = SameBBDict[start1]
                end2 = SameBBDict[end1]

                for key2 in VPaths.keys():
                    if (key2 not in PP.values()):
                        if(start2 == key2[0]) or(end2 == key2[1]):
                            if(key2[0] in VFBBs) and (key2[1] in VFBBs):
                                if(start2 == key2[0]):
                                    if(PFBBs[end1].NormList1 == VFBBs[key2[1]].NormList1):
                                        PP[key1] = key2
                                        break
                                if(end2 == key2[1]):
                                    if (PFBBs[start1].NormList1 == VFBBs[key2[0]].NormList1):
                                        PP[key1] = key2
                                        break


    # print("Rest Path1")
    # for key1 in PPaths:
    #
    #     if(key1 not in PP):
    #         print(key1)
    #         for P1 in PPaths[key1].Paths:
    #             print(P1)
    #         print()
    # print(10*"-")
    # print("Rest Path2")
    # for key2 in VPaths:
    #
    #     if(key2 not in PP.values()):
    #         print(key2)
    #         for P2 in VPaths[key2].Paths:
    #             print(P2)
    #     print()

    Remove = {}
    RemoveDict = defaultdict(list)

    print()
    for key1, key2 in PP.items():
        if (key1 in Remove):
            continue
        for key1_1, key2_1 in PP.items():
            if (key1_1 in Remove) or (key1_1 == key1):
                continue
            if(Equal(PPaths[key1].Ps,PPaths[key1_1].Ps, VPaths[key2].Ps, VPaths[key2].Ps)):
                print(key1, key2)
                print(key1_1, key2_1)
                print()
                Remove[key1_1] = key2_1
                RemoveDict[key1].append(key1_1)

    # for key, value in RemoveDict.items():
    #     print(key, value)

    for key1 in Remove:
        PP.pop(key1)


    Merge = {}
    for key in PPaths:
        start = key[0]

        if (start in SameBBDict):
            bb1 = PFBBs[start]
            bb2 = VFBBs[SameBBDict[start]]
            if (len(bb1.Subs) > 2) and (bb1.InsList[-1].startswith("jmp")) and (len(bb2.Subs)>2) \
                    and (bb2.InsList[-1].startswith("jmp")):
                Merge[start] = SameBBDict[start]

    for start1, start2 in Merge.items():
        key1 = ""
        key2 = ""
        Label = False
        for key1_temp in PPaths:
            if(Label):
                break
            if(start1 == key1_temp[0]) and (key1_temp in PP):
                for key2_temp in VPaths:
                    if(start2 == key2_temp[0]) and (key2_temp == PP[key1_temp]):
                        key1 = key1_temp
                        key2 = key2_temp
                        Label = True
                        break


        PMerge = []
        VMerge = []
        if(len(key1)>0) and (len(key2)>0):
            for key in PPaths:
                if (not (key == key1)) and (key[0] == start1):
                    PPaths[key1].Paths.extend(PPaths[key].Paths)

                    PPaths[key1].BBs.extend(PPaths[key].BBs)
                    PPaths[key1].BBs = list(set(PPaths[key1].BBs))

                    PPaths[key1].Ps.union(PPaths[key].Ps)
                    PMerge.append(key)

            for key in VPaths:
                if (not (key == key2)) and (key[0] == start2):
                    VPaths[key2].Paths.extend(VPaths[key].Paths)

                    VPaths[key2].BBs.extend(VPaths[key].BBs)
                    VPaths[key2].BBs = list(set(VPaths[key].BBs))

                    VPaths[key2].Ps.union(VPaths[key].Ps)
                    VMerge.append(key)

        print("Merge", (key1, key2))
        for key in PMerge:
            print(key)
            PPaths.pop(key)
            if(key in PP):
                PP.pop(key)
        print()
        for key in VMerge:
            VPaths.pop(key)
            print(key)
        print()
        print()
        print()




    print(50 * "-")
    for key1, key2 in PP.items():
        print(key1, key2)

        for P1 in PPaths[key1].Paths:
            print(P1)
        print()

        for P2 in VPaths[key2].Paths:
            print(P2)

        print()
        print()

    print()
    print(50 * "-")

    print()

    TempRankBB1, RankBB12, TempRankBB2, BBPair, AddBB1, DelBB2 = BBAnalyze(PP, PPaths, VPaths, PFRestBBDict, VFRestBBDict,
                                                                   RankBB1, RankBB12, RankBB2, AddBB1, DelBB2, BBPair,
                                                                   IDF)
    TempAddBB1 = []
    for add1 in AddBB1:
        bb1 = PFBBs[add1]
        if not(len(bb1.Subs) == 0 or len(bb1.Pres) == 0):
            label = True
            if(label):
                TempAddBB1.append(add1)

    AddBB1 = TempAddBB1

    RankBB1 = {}
    RankBB2 = {}

    for addr1, value in TempRankBB1.items():
        if(value>=0):
            RankBB1[addr1] = value

    for addr2, value in TempRankBB2.items():
        if(value >= 0):
            RankBB2[addr2] = value

    if(len(RankBB1) == len(RankBB2)):
        Label = True
        for i in range(0, len(RankBB1)):
            addr1 = list(RankBB1.keys())[i]
            value1 = RankBB1[addr1]

            addr2 = list(RankBB2.keys())[i]
            value2 = RankBB2[addr2]

            if(value1 == value2):
                if (PFBBs[addr1].NormList1 == VFBBs[addr2].NormList1):
                    Pre2s = []
                    for pre in PFBBs[addr1].Pres:
                        if(pre in SameBBDict):
                            Pre2s.append(SameBBDict[pre])
                    Sub2s = []
                    for sub in PFBBs[addr1].Subs:
                        if(sub in SameBBDict):
                            Sub2s.append(SameBBDict[sub])

                    Pres = set(Pre2s).intersection(set(VFBBs[addr2].Pres))
                    Subs = set(Sub2s).intersection(set(VFBBs[addr2].Subs))
                    if not(len(Pres)>0 or len(Subs)>0):
                        Label = False
                        break
                else:
                    Label = False
                    break
            else:
                Label = False
                break

        if(Label):
            RankBB1 = OrderedDict()
            RankBB2 = OrderedDict()


    RankBB1 = OrderedDict(sorted(RankBB1.items(), key=lambda item: item[1], reverse=True))
    RankBB2 = OrderedDict(sorted(RankBB2.items(), key=lambda item: item[1], reverse=True))

    return RankBB1, RankBB12, RankBB2, AddBB1, DelBB2, BBPair







