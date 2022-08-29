from AnalyzeBinary.PatchAnalyze.Normalize import Normalize1, Normalize2
from AnalyzeBinary.PatchPresenceTest.PT import PT
import csv
from AnalyzeBinary.PatchAnalyze.BBMap import BBMap
from AnalyzeBinary.PatchAnalyze.SEAnalyze import SEAnalyze

from AnalyzeBinary.PatchPresenceTest.CalculateSimilarity_temp import CalSim




IdfFile = "/Users/xuxi/XX-Study/Study-Now/Dataset/PatchDataset/Dataset/IDF.csv"

def ReadIdf(IdfFile):
    IDF = {}
    with open(IdfFile, 'r', encoding='utf-8') as f:
        Rows = csv.reader(f)

        for row in Rows:
            IDF[row[0]] = float(row[1])
            # print(row[0])

        f.close()
    return IDF

def CheckAddBB(PF, VF, TF, PVSameBBDict, PTSameBBDict, VTSameBBDict,  AddBB1, n, IDF):
    for addbb in AddBB1:
        Pres2 = []
        for pre1 in PF.BBs[addbb].Pres:
            if(pre1 in PVSameBBDict):
                if(PVSameBBDict[pre1] in VTSameBBDict):
                    Pres2.append(PVSameBBDict[pre1])
        Subs2 = []
        for sub1 in PF.BBs[addbb].Subs:
            if(sub1 in PVSameBBDict):
                if(PVSameBBDict[sub1] in VTSameBBDict):
                    Subs2.append(PVSameBBDict[sub1])

        if(len(Pres2)>0) and (len(Subs2)>0):
            for pre2 in Pres2:
                for sub2 in VF.BBs[pre2].Subs:
                    if(sub2 in Subs2):
                        pre3 = VTSameBBDict[pre2]
                        sub3 = VTSameBBDict[sub2]
                        addr3s = list(set(TF.BBs[pre3].Subs).intersection(set(TF.BBs[sub3].Pres)))
                        if(len(addr3s) == 0):
                            return False
                        else:
                            TempLabel = False
                            for addr3 in addr3s:
                                if(TF.BBs[addr3].NormList1 == PF.BBs[addbb].NormList1):
                                    TempLabel = True
                            if(not TempLabel):
                                return TempLabel
    return True
def PatchPresenceTest_main(PF, VF, TF, SameBBDict, RankBB1, RankBB12, RankBB2, AddBB1, DelBB2, BBPair, n):
    IDF = ReadIdf(IdfFile)

    Normalize1(TF.BBs)
    Normalize2(TF.BBs)

    VTSameBBDict, VFRestBBDict, TFRestBBDict = BBMap(VF, TF)
    SEAnalyze(VTSameBBDict, VFRestBBDict, TFRestBBDict)

    print(len(TF.BBs), len(VF.BBs), len(VTSameBBDict))
    if(len(TF.BBs) == len(VF.BBs) == len(VTSameBBDict)):
        print("Same VF")
        TestResult = "Vulnerability"
        return TestResult

    PTSameBBDict, PFRestBBDict, TFRestBBDict = BBMap(PF, TF)
    SEAnalyze(PTSameBBDict, PFRestBBDict, TFRestBBDict)

    print(len(TF.BBs), len(PF.BBs), len(PTSameBBDict))
    if(len(TF.BBs) == len(PF.BBs) == len(PTSameBBDict)):
        print("Same PF")
        TestResult = "Patch"
        return TestResult

    if(len(RankBB2) == 0):
        if not CheckAddBB(PF, VF, TF, SameBBDict, PTSameBBDict, VTSameBBDict, AddBB1, n, IDF):
            print("CheckAddBB False")
            TestResult = "Vulnerability"
            return TestResult


    TestBB1 = []
    TempAddBB1 = []
    for key, value in RankBB1.items():
        if(len(TestBB1) < n) and (value > -1):
            TestBB1.append(key)
            if(key in AddBB1):
                TempAddBB1.append(key)

    AddBB1 = TempAddBB1

    PTSameBBDict = PT(PF, TF, TestBB1, AddBB1, n, IDF)
    print(PTSameBBDict)


    if(len(AddBB1)>0):
        print("AddBB")

        NotAdd = []
        for bb in AddBB1:
            if(bb not in PTSameBBDict):
                NotAdd.append(bb)
                print(bb, "")
            else:
                print(bb, PTSameBBDict[bb])

        if(len(NotAdd) > 0):
            TestResult = "Vulnerability"
            return TestResult

    TestBB2 = []
    for key, value in RankBB2.items():
        if (len(TestBB2) < n) and (value > -1):
            TestBB2.append(key)
    VTSameBBDict = PT(VF, TF, TestBB2, [], n, IDF)
    print()
    print("RankBB1", RankBB1)
    print("RankBB2", RankBB2)
    print(10 * "-" + "Similarity Calculation 1" + 10 * "-")
    Sim1 = CalSim(TestBB1, PTSameBBDict, PF, TF, IDF, RankBB1)
    print(10 * "-" + "Similarity Calculation 2" + 10 * "-")
    Sim2 = CalSim(TestBB2, VTSameBBDict, VF, TF, IDF, RankBB2)
    print("Sim1 = %s, Sim2 = %s" % (Sim1, Sim2))


    if (Sim1 > Sim2):
        TestResult = "Patch"
    else:
        TestResult = "Vulnerability"

    print("TestResult = %s " % (TestResult))

    print(len(PTSameBBDict))
    print(len(VTSameBBDict))

    return TestResult









