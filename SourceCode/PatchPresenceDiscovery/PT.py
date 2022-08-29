from AnalyzeBinary.PatchAnalyze.BBMap import BBMap
from AnalyzeBinary.PatchAnalyze.SEAnalyze import SEAnalyze
from AnalyzeBinary.PatchAnalyze.GroupMap import GroupMap
from collections import defaultdict
from AnalyzeBinary.PatchPresenceTest.CalculateSimilarity_temp import CalculateSimilarity


def PT(PF, TF, TestBB1, AddBB1, n, IDF):

    PTSameBBDict, PFRestBBDict, TFRestBBDict = BBMap(PF, TF)

    SEAnalyze(PTSameBBDict, PFRestBBDict, TFRestBBDict)

    print()
    print(10 * "-" + "\033[;33mFunction1 Rest BB\033[0m" + 10 * "-")
    for addr, bb in PFRestBBDict.items():
        print(addr)

    print()
    print(10 * "-" + "\033[;33mFunction2 Rest BB\033[0m" + 10 * "-")
    for addr, bb in TFRestBBDict.items():
        print(addr)
    print()
    print()

    PTDict, PList, TList = GroupMap(PTSameBBDict, PFRestBBDict, TFRestBBDict, PF, TF)

    TestPT = defaultdict(list)

    TestBBs1 = []

    TestRest = []
    for key in TestBB1:
        testbb = PF.BBs[key]
        Label = False
        for group in PTDict.keys():
            if(key in group.BBs):
                TestPT[group].append(testbb)
                Label = True

        if(not Label):
            TestRest.append(testbb)

    for key in AddBB1:
        testbb = PF.BBs[key]
        if(testbb not in TestBBs1):
            Label = False
            for group in PTDict.keys():
                if (key in group.BBs):
                    TestPT[group].append(testbb)
                    Label = True
            if (not Label):
                TestRest.append(testbb)


    for group1 in TestPT:
        PTSameBBDict = CalculateSimilarity(PTDict[group1].BBs, TestPT[group1], TF, PTSameBBDict, IDF)
    TFRestBBDict = {}
    for group2 in TList:
        TFRestBBDict.update(group2.BBs)

    PTSameBBDict = CalculateSimilarity(TFRestBBDict, TestRest,TF, PTSameBBDict, IDF)
    print()
    print()
    return PTSameBBDict




