# remove semantic equivalence

def Test(AsmList1, AsmList2):
    if not(len(AsmList1) == len(AsmList2)):
        return False

    length = len(AsmList1)
    for i in range(0, length - 1):
        if not (AsmList1[i] == AsmList2[i]):
            return False
    if(AsmList1[-1] == AsmList2[-1]):
        return False

    if (AsmList1[-1].startswith("j")) and (AsmList2[-1].startswith("j")):
        Mnem1 = AsmList1[-1].split(" ")[0]
        Mnem2 = AsmList2[-1].split(" ")[0]

        if(Mnem1 == Mnem2):
            return False


        if(Mnem1.replace("n", "") == Mnem2.replace("n", "")):
            return True
        else:
            return False
    else:
        return False

def YesNo(BB1, BB2):
    Mnem1 = BB1.NormList1[-1].split(" ")[0]

    Yes1 = list(BB1.InsDict.values())[-1].split(" ")[1]

    for i in range(0, len(BB1.Subs)):
        if (str(BB1.Subs[i]) == Yes1):
            Yes1 = BB1.Subs[i]

        else:
            No1 = BB1.Subs[i]

    Mnem2 = BB2.NormList1[-1].split(" ")[0]

    Yes2 = list(BB2.InsDict.values())[-1].split(" ")[1]

    for i in range(0, len(BB2.Subs)):
        if (str(BB2.Subs[i]) == Yes2):
            Yes2 = BB2.Subs[i]

        else:
            No2 = BB2.Subs[i]

    if ("n" in Mnem1):
        Yes1, No1 = No1, Yes1

    if ("n" in Mnem2):
        Yes2, No2 = No2, Yes2

    return Yes1, No1, Yes2, No2

def RemoveJmp(AsmList):
    TempAsmList = []
    length = len(AsmList)
    for i in range(0, length - 1):
        TempAsmList.append(AsmList[i])


def MeetSE(bb, SameBBList):
    Label = False
    if(len(bb.Subs) == 2):
        if(bb.NormList1[-1].startswith("j")):
            SubLabel = False
            for sub in bb.Subs:
                if(sub in SameBBList):
                    SubLabel = True

            return SubLabel

    return Label


def SEAnalyze(SameBBDict, PFRestBBDict, VFRestBBDict):
    print()
    print(10 * "-" + "\033[;33mSemantic Equivalence Check\033[0m" + 10 * "-")

    AddSameBBDict = {}
    for addr1, bb1 in PFRestBBDict.items():
        if(addr1 == "0x43decd"):
            print()
        if (MeetSE(bb1, list(SameBBDict.keys()))):

            EqualBBs = []
            for addr2, bb2 in VFRestBBDict.items():
                if(MeetSE(bb2, list(SameBBDict.values()))) and (len(bb1.NormList1) == len(bb2.NormList1)):
                    if(Test(bb1.NormList1, bb2.NormList1)):
                            PatchYes, PatchNo, VulneYes, VulneNo = YesNo(bb1, bb2)

                            if (PatchYes in SameBBDict) and (PatchNo in SameBBDict):
                                if (SameBBDict[PatchYes] == VulneYes) and (SameBBDict[PatchNo] == VulneNo):
                                    EqualBBs.append(addr2)

                            elif(PatchYes in SameBBDict):
                                if (SameBBDict[PatchYes] == VulneYes):
                                    EqualBBs.append(addr2)

                            elif(PatchNo in SameBBDict):
                                if(SameBBDict[PatchNo] == VulneNo):
                                    EqualBBs.append(addr2)

            if(len(EqualBBs)==1):

                print(addr1, EqualBBs[0])
                SameBBDict[addr1] = EqualBBs[0]
                AddSameBBDict[addr1] = EqualBBs[0]

    for addr1, addr2 in AddSameBBDict.items():
        if(addr1 in PFRestBBDict):
            PFRestBBDict.pop(addr1)
        if(addr2 in VFRestBBDict):
            VFRestBBDict.pop(addr2)









































if __name__ == "__main__":
    funcname = "_bfd_generic_read_minisymbols"
    funcname1 = "_bfd_coff_generic_relocate_section"
    binaryName = "addr2line"
    opti = "O0"

    Patch_Version = "2.32"
    Vul_Version = "2.31"

    PickleFolder = "/Users/xuxi/XX-Study/Study-Now/Dataset/PatchDataset/binutils-bin/V%s/gcc-4.8.4/Pickle/%s/%s" % (
        Patch_Version, opti, binaryName)

    Func1_temp = ReadPickle(PickleFolder, funcname)

    PickleFolder = "/Users/xuxi/XX-Study/Study-Now/Dataset/PatchDataset/binutils-bin/V%s/gcc-4.8.4/Pickle/%s/%s" % (
        Vul_Version, opti, binaryName)
    Func2_temp = ReadPickle(PickleFolder, funcname)
    AnalyzePatch(Func1_temp, Func2_temp)








