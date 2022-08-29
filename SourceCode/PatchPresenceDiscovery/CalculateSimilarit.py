from collections import OrderedDict

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

def CalIDFScore(AsmList, IDF):
    IDFScore = 0
    if (len(AsmList) == 0):
        return 0
    # print(IDF)
    for asm in AsmList:
        # print(asm)
        # IDFScore += IDF[asm.split(" ")[0]]
        IDFScore += 1
    # print(IDFScore)
    return IDFScore

# def CalLCSScore(AsmList1, AsmList2, IDF):
#     print(AsmList1)
#     print(AsmList2)
#     if(len(AsmList1)>0) and (len(AsmList2)>0):
#         result = lcs(AsmList1, AsmList2)
#         print(len(AsmList1), len(AsmList2), len(result))
#         return (len(result)*2)/ (len(AsmList1)+len(AsmList2))
#     else:
#         return 0

def CalLCSScore(AsmList1, AsmList2, IDF):
    print(AsmList1)
    print(AsmList2)

    if(len(AsmList1)>0) and (len(AsmList2)>0):
        result = lcs(AsmList1, AsmList2)

        lcsList = []
        for i in result:
            lcsList.append(AsmList1[i[0]])

        print(len(AsmList1), len(AsmList2), len(result))
        return (CalIDFScore(lcsList, IDF)*2)/(CalIDFScore(AsmList1, IDF)+CalIDFScore(AsmList2, IDF))
    else:
        return 0

def Locate(BB2Lists):

    # print(BB2Lists)
    Temp = BB2Lists[0]
    for BB2List in BB2Lists:
        Temp = list(set(BB2List).intersection(set(Temp)))

    if(len(Temp)>0):
        return Temp
    else:
        Temp = BB2Lists[0]
        for BB2List in BB2Lists:
            Temp = list(set(BB2List).union(set(Temp)))
        return Temp


def CalculateSimilarity(TFGroupBBs, TestBBs, TF, SameBBDict, IDF):
    outputlist = []
    for testbb  in  TestBBs:
        outputlist.append(testbb.addr)
    print("-".join(outputlist))

    outputlist = []
    for bb_addr in TFGroupBBs:
        outputlist.append(bb_addr)
    print("-".join(outputlist))


    if(len(TestBBs) == 0):
        return SameBBDict

    LocateSimDict = {}
    SimDict = {}

    for testbb in TestBBs:

        print()
        print("testbb_addr = %s "%(testbb.addr))

        testbb_addr = testbb.addr
        testbb_NormList2 = testbb.NormList2
        # if(testbb_addr == "0x42335c"):
        #     print()

        TempSimDict = {}

        if(testbb_addr in SameBBDict):
            Tempdict = {}
            Tempdict[TF.BBs[SameBBDict[testbb_addr]]] = 1
            LocateSimDict[testbb] = Tempdict
            print(testbb_addr, SameBBDict[testbb_addr], 1)
            continue
        elif(len(testbb.Pres) == 0):
            for bb_addr, bb in TF.StartBBDict.items():
                sim = CalLCSScore(testbb.NormList2, bb.NormList2, IDF)
                TempSimDict[bb] = sim
                print(testbb_addr, bb.addr, sim)
                TempSimDict = OrderedDict(sorted(TempSimDict.items(), key=lambda item: item[1], reverse=True))
                LocateSimDict[testbb] = TempSimDict
            continue
        elif(len(testbb.Subs) == 0):
            for bb_addr, bb in TF.EndBBDict.items():
                sim = CalLCSScore(testbb.NormList2, bb.NormList2, IDF)
                TempSimDict[bb] = sim
                print(testbb_addr, bb.addr, sim)
                # print()
                TempSimDict = OrderedDict(sorted(TempSimDict.items(), key=lambda item: item[1], reverse=True))
                LocateSimDict[testbb] = TempSimDict
            continue
        # elif(len(testbb.LibList)>0):
        #     for bb_addr, bb in TF.LibBBDict.items():
        #         if(len(set(testbb.LibList).intersection(set(bb.LibList)))>0):
        #             if bb_addr not in list(SameBBDict.values()):
        #                 sim = CalLCSScore(testbb.NormList2, bb.NormList2, IDF)
        #                 TempSimDict[bb] = sim
        #                 print(testbb_addr, bb.addr, sim)
        #         # print()
        #         TempSimDict = OrderedDict(sorted(TempSimDict.items(), key=lambda item: item[1], reverse=True))
        #         LocateSimDict[testbb] = TempSimDict
        #     continue
        # elif (len(testbb.StrList) > 0):
        #     for bb_addr, bb in TF.StrBBDict.items():
        #         if (len(bb.StrList) > 0):
        #             if bb_addr not in list(SameBBDict.values()):
        #                 sim = CalLCSScore(testbb.NormList2, bb.NormList2, IDF)
        #                 TempSimDict[bb] = sim
        #                 print(testbb_addr, bb.addr, sim)
        #         # print()
        #         TempSimDict = OrderedDict(sorted(TempSimDict.items(), key=lambda item: item[1], reverse=True))
        #         LocateSimDict[testbb] = TempSimDict
        #     continue
        # elif (len(testbb.UDList) > 0):
        #     for bb_addr, bb in TF.UDBBDict.items():
        #         if (len(bb.UDList) > 0):
        #             if bb_addr not in list(SameBBDict.values()):
        #                 sim = CalLCSScore(testbb.NormList2, bb.NormList2, IDF)
        #                 TempSimDict[bb] = sim
        #                 print(testbb_addr, bb.addr, sim)
        #         # print()
        #         TempSimDict = OrderedDict(sorted(TempSimDict.items(), key=lambda item: item[1], reverse=True))
        #         LocateSimDict[testbb] = TempSimDict
        #     continue

        SameSubs = list(set(testbb.Subs).intersection(set(SameBBDict.keys())))
        SamePres = list(set(testbb.Pres).intersection(set(SameBBDict.keys())))

        TempBB2s_Sub = []
        for sub1 in SameSubs:
            sub2 = SameBBDict[sub1]
            Temp = TF.BBs[sub2].Pres
            TempBB2s_Sub.append(TF.BBs[sub2].Pres)

        if(len(TempBB2s_Sub)>0):

            BB2s_Sub = Locate(TempBB2s_Sub)
        else:
            BB2s_Sub = []


        TempBB2s_Pre = []

        for pre1 in SamePres:
            pre2 = SameBBDict[pre1]
            Temp = TF.BBs[pre2].Subs
            TempBB2s_Pre.append(TF.BBs[pre2].Subs)

        if(len(TempBB2s_Pre)>0):
            BB2s_Pre = Locate(TempBB2s_Pre)
        else:
            BB2s_Pre = []

        Temp = []

        Temp.append(BB2s_Sub)
        Temp.append(BB2s_Pre)

        BB2s = Locate(Temp)

        Del = []
        for bb_addr in BB2s:
            if bb_addr in list(SameBBDict.values()):
                Del.append(bb_addr)

        for bb_addr in Del:
            BB2s.remove(bb_addr)

        if(len(BB2s)>0):

            for bb_addr in BB2s:
                # print(bb_addr)

                bb = TF.BBs[bb_addr]
                # print(bb.NormList2)

                if(bb_addr in list(SameBBDict.values())):
                    continue

                bb__NormList2 = TF.BBs[bb_addr].NormList2

                sim = CalLCSScore(testbb.NormList2, bb.NormList2, IDF)
                # print()
                # print(bb.NormList2)
                # print()
                TempSimDict[bb] = sim
                print(testbb_addr, bb.addr, sim)
                # print()

                TempSimDict = OrderedDict(sorted(TempSimDict.items(), key=lambda item: item[1], reverse=True))

                LocateSimDict[testbb] = TempSimDict
                # MaxSimDict[testbb] = (list(TempSimDict.keys())[0], TempSimDict[list(TempSimDict.keys())[0]])

        else:
            for bb_addr, bb in TF.BBs.items():
                # print(bb_addr)
                # print(bb.NormList2)

                bb_NormList2 = bb.NormList2

                if (bb_addr in list(SameBBDict.values()))or (bb_addr not in TFGroupBBs):
                    continue

                sim = CalLCSScore(testbb.NormList2, bb.NormList2, IDF)

                # print()
                # print(bb.NormList2)
                # print()
                TempSimDict[bb] = sim
                print(testbb_addr, bb.addr, sim)
                # print()

                TempSimDict = OrderedDict(sorted(TempSimDict.items(), key=lambda item: item[1], reverse=True))
                SimDict[testbb] = TempSimDict
                # MaxSimDict[testbb] = (list(TempSimDict.keys())[0], TempSimDict[list(TempSimDict.keys())[0]])

    LocateMaxSimDict = MatchMaxScore(LocateSimDict)

    for testbb in LocateMaxSimDict:
        Maxbb = LocateMaxSimDict[testbb][0]
        print(testbb.addr, Maxbb.addr)
        SameBBDict[testbb.addr] = Maxbb.addr

        for testbb_2, TempSimDict in SimDict.items():
            if not(testbb_2 == testbb):
                if(Maxbb in TempSimDict):
                    TempSimDict.pop(Maxbb)
    MaxSimDict = MatchMaxScore(SimDict)

    print()
    for testbb in MaxSimDict:

        Maxbb = MaxSimDict[testbb][0]
        print(testbb.addr, Maxbb.addr)
        SameBBDict[testbb.addr] = Maxbb.addr
    return SameBBDict


# def CalSim(TestBB, SameBBDict, PF, TF, IDF, RankBB1):
#     Sim = 0
#     if(len(TestBB) == 0):
#         return 0
#
#     All = 0
#     Count = 0
#
#     for bb1_addr in TestBB:
#         All += RankBB1[bb1_addr]
#         Count += len(PF.BBs[bb1_addr].NormList2)
#
#
#     for bb1_addr in TestBB:
#         print()
#         print("-----%s-------"%(bb1_addr))
#
#         bb1 = PF.BBs[bb1_addr]
#         w = RankBB1[bb1_addr]
#
#         if(bb1_addr in SameBBDict) :
#             TFbb_addr = SameBBDict[bb1_addr]
#             TFbb = TF.BBs[TFbb_addr]
#             s = CalLCSScore(bb1.NormList2, TFbb.NormList2, IDF)
#             print(bb1_addr, TFbb_addr, s)
#             if(All == 0):
#                 w= len(PF.BBs[bb1_addr].NormList2)
#                 Sim += (s*w)/Count
#             else:
#                 Sim += (s*w)/All
#
#     return Sim


def CalSim(TestBB, SameBBDict, PF, TF, IDF, RankBB1):
    Sim = 0
    if (len(TestBB) == 0):
        return 0
    All = 0

    for bb1_addr in TestBB:
        print(bb1_addr, PF.BBs[bb1_addr].NormList2)
        # All += CalIDFScore(PF.BBs[bb1_addr].NormList2, IDF)
        All += RankBB1[bb1_addr]


    if(All == 0):
        return 0

    for bb1_addr in TestBB:
        print()
        print("-----%s-------" % (bb1_addr))

        bb1 = PF.BBs[bb1_addr]
        # w = CalIDFScore(PF.BBs[bb1_addr].NormList2, IDF)
        w = RankBB1[bb1_addr]

        if (bb1_addr in SameBBDict):
            TFbb_addr = SameBBDict[bb1_addr]
            TFbb = TF.BBs[TFbb_addr]
            s = CalLCSScore(bb1.NormList2, TFbb.NormList2, IDF)
            print(bb1_addr, TFbb_addr, s)
            Sim += (s * w) / All

    return Sim

# def MatchMaxScore(SimDict):
#
#     MaxSimDict = {}
#
#     print(SimDict)
#     for NowTestBB1, value in SimDict.items():
#         if(len(value) == 0):
#             continue
#         temp1 = NowTestBB1.addr
#         MaxSimBB2 = list(SimDict[NowTestBB1].keys())[0]
#         temp2 = MaxSimBB2.addr
#         MaxSimScore = SimDict[NowTestBB1][MaxSimBB2]
#         MaxSimDict[NowTestBB1] = (MaxSimBB2, MaxSimScore)
#         print((NowTestBB1.addr, MaxSimBB2.addr, MaxSimScore))
#
#     return MaxSimDict


def MatchMaxScore(SimDict):

    TestBBs = list(SimDict.keys())
    MaxSimDict = {}
    while (len(TestBBs) > 0) :

        NowTestBB1 = TestBBs.pop()

        if(len(SimDict[NowTestBB1].keys())==0):
            continue

        # print(SimDict[NowTestBB1].keys())
        MaxSimBB2 = list(SimDict[NowTestBB1].keys())[0]
        MaxSimScore = SimDict[NowTestBB1][MaxSimBB2]
        Label = True

        for CmpTestBB in SimDict:
            if not (CmpTestBB == NowTestBB1):
                if (MaxSimBB2 in SimDict[CmpTestBB]):
                    tempScore = SimDict[CmpTestBB][MaxSimBB2]
                    if (MaxSimScore < tempScore):
                        Label = False

        if (Label):
            MaxSimDict[NowTestBB1] = (MaxSimBB2, MaxSimScore)
            print((NowTestBB1.addr, MaxSimBB2.addr, MaxSimScore))
            SimDict.pop(NowTestBB1)

            for TestBB in SimDict:
                if (MaxSimBB2 in SimDict[TestBB]):
                    SimDict[TestBB].pop(MaxSimBB2)
        else:
            TestBBs.insert(0,  NowTestBB1)

    return MaxSimDict


