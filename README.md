PatchDiscovery: Patch Presence Test for Identifying Binary Vulnerabilities Based on Key Basic Blocks

The Source Code and the dataset can all be downloaded from releases[https://github.com/PatchDiscovery/PatchDiscovery/releases].

The source code is structured in the following way:
1.	Preprocessing：PatchDiscovery preprocesses each input binary function (i.e., VF, PF and TF) by distilling each function’s semantics into a CFG and applying
instruction normalization and simplification to deal with the syntax gaps on instructions. 
2.	PatchAnalysis: PatchDiscovery identifies the scope of patch in PF and the scope of vulnerability in VF and selects the key basic blocks in PF and VF as their signatures for patch presence discovery, respectively.
3.	PatchPresenceDscovery：PatchDiscovery determines whether a TF has been patched or not.

The dataset is structured in the following way:
1.  Bin:the compiled binaries 
2. _config.csv : There are four parts in the file, which are CVE id , the last vulnerable version , the first patched version , involved functions in order.
3. _func.csv : All involved functions in _config.cvs.
4. _version.csv : All binary versions to be analyzed.
5. gt.csv : optional , you can mark V and P for functions in target binary as ground truth.


The ComparisonWithBinXray is structured in the following way:
1. Effectiveness and Resilience Comparison.pdf: The results of experiments of Effectiveness and Resilience Comparison between PatchDiscovery and BinXray.









