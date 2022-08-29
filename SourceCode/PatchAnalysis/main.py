from AnalyzeBinary.PatchAnalyze.Normalize import Normalize1, Normalize2, Normalize3
from AnalyzeBinary.PatchAnalyze.BBMap import BBMap
from AnalyzeBinary.PatchAnalyze.BBRank import BBRank
from AnalyzeBinary.PatchAnalyze.SEAnalyze import SEAnalyze
import csv
from collections import OrderedDict

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

def PatchAnalyze_Main(PF, VF):

    AnalyzeLabel = True

    Normalize1(PF.BBs)
    Normalize2(PF.BBs)
    Normalize3(PF.BBs)


    Normalize1(VF.BBs)
    Normalize2(VF.BBs)
    Normalize3(VF.BBs)

    # Basic Block Mapping
    SameBBDict, PFRestBBDict, VFRestBBDict = BBMap(PF, VF)

    SEAnalyze(SameBBDict, PFRestBBDict, VFRestBBDict)

    print(len(PF.BBs), len(VF.BBs))

    print()
    print(10 * "-" + "\033[;33mFunction1 Rest BB\033[0m" + 10 * "-")
    for addr, bb in PFRestBBDict.items():
        print(addr)

    print()
    print(10 * "-" + "\033[;33mFunction2 Rest BB\033[0m" + 10 * "-")
    for addr, bb in VFRestBBDict.items():
        print(addr)
    print()
    print()

    print(len(PFRestBBDict), len(VFRestBBDict))


    if (len(PFRestBBDict) == 0) and (len(VFRestBBDict) == 0):
        return {}, {},{}, [], [],{}, SameBBDict, False

    IDF = ReadIdf(IdfFile)

    RankBB1,RankBB12, RankBB2, AddBB1, DelBB2, BBPair = BBRank(PFRestBBDict, VFRestBBDict, SameBBDict, PF.BBs, VF.BBs, IDF)

    print()

    print(10*"-"+"Patch Analyze Result"+10*"-")
    print()
    print('\033[31mRankBB1\033[0m', RankBB1)
    print('\033[31mAddBB1\033[0m', AddBB1)
    print('\033[31mRankBB2\033[0m', RankBB2)
    print('\033[31mDelBB2\033[0m', DelBB2)

    if(len(RankBB1) == len(RankBB2) == 0):
        AnalyzeLabel = False

    return RankBB1, RankBB12, RankBB2, AddBB1, DelBB2, BBPair, SameBBDict, AnalyzeLabel




