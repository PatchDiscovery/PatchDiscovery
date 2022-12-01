Here are the details.

Table I- IV shows the full confusion matrices for these totals (TP, TN, FP, FN) and derived summarized precision/recall/F1/accuracy from these.

Table V-VIII shows the comparison results between PatchDiscovery and BinXray. We use bold to highlight the higher performance.

Figure I shows the choice of our selection of parameter N. 

BinXray-freetype.csv shows the testing results of applying BinXray on freetype.
In our replication of BinXray, we found many cases that BinXray can only print error messages such as “NA too much diff” (these are excluded in our comparison). BinXray fails when the total number of the changed basic blocks in patched functions/vulnerable functions and the boundary basic blocks of the changed ones is greater than 40.(i.e., if len(G.nodes()) > 40: print "too much diff" [https://sites.google.com/view/submission-for-issta-2020]). For example, 
BinXray-freetype.csv has shown 255 functions in total 754 functions print the above error.
