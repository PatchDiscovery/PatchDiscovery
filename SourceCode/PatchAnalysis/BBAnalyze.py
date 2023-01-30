from collections import OrderedDict
from datasketch import MinHashLSHForest, MinHash


def lcs(s1, s2):
    matrix = [[[] for x in range(len(s2))] for x in range(len(s1))]
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                if i == 0 or j == 0:
                    matrix[i][j].append((i, j))
                else:
                    matrix[i][j].extend(matrix[i - 1][j - 1])
                    matrix[i][j].append((i, j))
            else:
                matrix[i][j] = max(matrix[i - 1][j], matrix[i][j - 1], key=len)
    return matrix[-1][-1]


def LCS_ID(s1, s2):
    lcs1 = []
    lcs2 = []
    if (len(s1) > 0) and (len(s2) > 0):
        result = lcs(s1, s2)
        for item in result:
            lcs1.append(item[0])
            lcs2.append(item[1])
    return lcs1, lcs2


def CalIDFScore(AsmList):
    DiffScore = 0
    if (len(AsmList) == 0):
        return 0

    for asm in AsmList:
        print(asm)
        DiffScore += 1

    print()
    return DiffScore


class ID_BB:
    def __init__(self):
        self.InsDict = OrderedDict()
        self.LCSIns = []
        self.DiffIns = []

    def NotLcs(self):
        self.DiffIns = []
        for id, ins in self.InsDict.items():
            if (id not in self.LCSIns):
                self.DiffIns.append(ins)

    def __str__(self):
        return self.InsDict


# def BBAnalyze(PVKey, PPath, VPath, PFRestBBDict, VFRestBBDict, RankBB1, RankBB12, RankBB2, AddBB1, DelBB2,BBPair, IDF):
def BBAnalyze(PVKey, PPath, VPath, PFRestBBDict, VFRestBBDict, RankBB1, RankBB12, RankBB2, AddBB1, DelBB2, BBPair):
    for key1, key2 in PVKey.items():

        print()
        print('\033[31m%s, %s\033[0m' % (key1, key2))

        # Path1s = deepcopy(PPath[key1].Paths)
        # Path2s = deepcopy(VPath[key2].Paths)
        Path1s = PPath[key1].Paths
        Path2s = VPath[key2].Paths

        PP = {}

        print()
        print(10 * "-" + "build MinHashLSHForest" + 10 * "-")
        forest = MinHashLSHForest(num_perm=128)
        for i in range(0, len(Path2s)):
            # print(i, len(Path2s))
            Path2 = Path2s[i]
            m2 = MinHash(num_perm=128)

            for ins in Path2.NormList:
                m2.update(ins.encode('utf8'))
            forest.add(i, m2)
        forest.index()

        print()
        print(10 * "-" + "query" + 10 * "-")
        count = 0
        for Path1 in Path1s:
            count += 1
            print(count, len(Path1s))
            m1 = MinHash(num_perm=128)
            for ins in Path1.NormList:
                m1.update(ins.encode('utf8'))

            TopId = forest.query(m1, 1)
            if (len(TopId) > 0):
                PP[Path1] = Path2s[TopId[0]]

        print()
        for Path1, Path2 in PP.items():

            if (True):
                BB1_Used = []
                BB2_Used = []

                BB_temp1 = {}

                # print('\033[33m%s, %s\033[0m' % (Path1, Path2))
                lcs1, lcs2 = LCS_ID(Path1.NormList, Path2.NormList)

                print(len(Path1.NormList), len(Path2.NormList))

                print(lcs1)
                print(lcs2)

                BB1s = {}
                asm_id = 0
                for bb in Path1.BBs:
                    temp = ID_BB()
                    for asm in bb.NormList2:
                        temp.InsDict[asm_id] = asm
                        asm_id += 1
                    BB1s[bb.addr] = temp

                BB2s = {}
                asm_id = 0
                for bb in Path2.BBs:
                    temp = ID_BB()
                    for asm in bb.NormList2:
                        temp.InsDict[asm_id] = asm
                        asm_id += 1
                    BB2s[bb.addr] = temp

                for lcs_id in range(0, len(lcs1)):
                    lcs1_id = lcs1[lcs_id]
                    lcs2_id = lcs2[lcs_id]

                    for addr1, BB1 in BB1s.items():
                        if (lcs1_id in BB1.InsDict):
                            BB1.LCSIns.append(lcs1_id)
                            if (addr1 not in BB1_Used):
                                BB1_Used.append(addr1)
                            if (addr1 not in BB_temp1):
                                BB_temp1[addr1] = []

                            for addr2, BB2 in BB2s.items():
                                if (lcs2_id in BB2.InsDict):
                                    BB2.LCSIns.append(lcs2_id)
                                    if (addr2 not in BB2_Used):
                                        BB2_Used.append(addr2)

                                    if (addr2 not in BB_temp1[addr1]):
                                        BB_temp1[addr1].append(addr2)

                                    break
                            break

                NewBBRank1 = {}
                OriginBBRank1 = {}
                UpdateBBRank1 = {}
                SumBBRank1 = sum(RankBB1.values())

                for addr1 in BB1_Used:
                    BB1 = BB1s[addr1]
                    BB1.NotLcs()
                    IDFDiffScore = CalIDFScore(BB1.DiffIns)
                    NewBBRank1[addr1] = IDFDiffScore

                    if not (len(BB1.DiffIns) == len(BB1.InsDict)):
                        if (addr1 in AddBB1):
                            AddBB1.remove(addr1)

                    if (addr1 not in RankBB1):
                        RankBB1[addr1] = IDFDiffScore
                        UpdateBBRank1[addr1] = IDFDiffScore

                        for addr2 in BB_temp1[addr1]:
                            BB2 = BB2s[addr2]
                            BB2.NotLcs()
                            RankBB12[addr2] = CalIDFScore(BB2.DiffIns)

                        BBPair[addr1] = BB_temp1[addr1]

                        if len(BB1.DiffIns) == len(BB1.InsDict):
                            AddBB1.append(addr1)
                    else:
                        OriginBBRank1[addr1] = RankBB1[addr1]
                        UpdateBBRank1[addr1] = RankBB1[addr1]
                        RankBB1[addr1] = min(RankBB1[addr1], IDFDiffScore)

                        if (RankBB1[addr1] > IDFDiffScore):
                            for addr2 in BB_temp1[addr1]:
                                BB2 = BB2s[addr2]
                                BB2.NotLcs()
                                RankBB12[addr2] = CalIDFScore(BB2.DiffIns)

                            BBPair[addr1] = BB_temp1[addr1]

                if sum(RankBB1.values()) == 0:
                    if sum(OriginBBRank1.values()) == SumBBRank1 and sum(NewBBRank1.values()) == 0:
                        RankBB1.update(OriginBBRank1)

                NewBBRank2 = {}
                OriginBBRank2 = {}
                UpdateBBRank2 = {}
                SumBBRank2 = sum(RankBB2.values())

                for addr2 in BB2_Used:
                    # if addr2 == '0x41a550':
                    #     print()
                    BB2 = BB2s[addr2]
                    BB2.NotLcs()
                    IDFDiffScore = CalIDFScore(BB2.DiffIns)
                    NewBBRank2[addr2] = IDFDiffScore

                    if not (len(BB2.DiffIns) == len(BB2.InsDict)):
                        if (addr2 in DelBB2):
                            DelBB2.remove(addr2)

                    if (addr2 not in RankBB2):
                        UpdateBBRank2[addr2] = IDFDiffScore
                        RankBB2[addr2] = IDFDiffScore
                        if len(BB2.DiffIns) == len(BB2.InsDict):
                            DelBB2.append(addr2)
                    else:
                        OriginBBRank2[addr2] = RankBB2[addr2]
                        UpdateBBRank2[addr2] = RankBB2[addr2]
                        RankBB2[addr2] = min(RankBB2[addr2], IDFDiffScore)

                if sum(RankBB2.values()) == 0:
                    if sum(OriginBBRank2.values()) == SumBBRank2 and sum(NewBBRank2.values()) == 0:
                        RankBB2.update(OriginBBRank2)


                print(RankBB1)
                print(RankBB2)

    print("Rest 1")
    for addr, bb in PFRestBBDict.items():

        if (bb.addr not in RankBB1):
            print(bb.addr)
            RankBB1[bb.addr] = CalIDFScore(bb.NormList2)
            AddBB1.append(bb.addr)

    print("Rest 2")
    for addr, bb in VFRestBBDict.items():
        if (bb.addr not in RankBB2):
            print(bb.addr)
            RankBB2[bb.addr] = CalIDFScore(bb.NormList2)
            DelBB2.append(bb.addr)

    AddBB1 = list(set(AddBB1))
    DelBB2 = list(set(DelBB2))
    print(RankBB1)
    print(RankBB2)

    for addr1, diffscore in RankBB1.items():
        if (diffscore == 0):
            if (addr1 in BBPair):
                if (len(BBPair[addr1]) == 1):
                    addr2 = BBPair[addr1][0]
                    if (RankBB12[addr2] == 0) and (PFRestBBDict[addr1].NormList2 == VFRestBBDict[addr2].NormList2):
                        RankBB1[addr1] = -1
                        RankBB2[addr2] = -1

    if sum(RankBB1.values()) == 0:
        addr1_list = list(RankBB1.keys())
        for addr1 in addr1_list:
            if addr1 in BBPair:
                addr2s = BBPair[addr1]
                for addr2 in addr2s:
                    RankBB1[addr1] += RankBB2[addr2]

    if sum(RankBB2.values()) == 0:
        addr2_list = list(RankBB2.keys())
        for addr2 in addr2_list:
            for addr1, addr2s in BBPair.items():
                if addr2 in addr2s:
                    RankBB2[addr2] = RankBB1[addr1]


    RankBB1 = OrderedDict(sorted(RankBB1.items(), key=lambda item: item[1], reverse=True))
    RankBB12 = OrderedDict(sorted(RankBB12.items(), key=lambda item: item[1], reverse=True))
    RankBB2 = OrderedDict(sorted(RankBB2.items(), key=lambda item: item[1], reverse=True))
    print("Rank1", RankBB1)
    print("Rank2", RankBB2)
    print("BBPair", BBPair)

    AddBB1 = list(set(AddBB1))
    DelBB2 = list(set(DelBB2))

    return RankBB1, RankBB12, RankBB2, BBPair, AddBB1, DelBB2
