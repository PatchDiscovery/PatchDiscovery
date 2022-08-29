from bingraphvis.angr import *
import os

def ImportBinary(binary):
    p = angr.Project(binary, load_options={'auto_load_libs': False})
    cfg = p.analyses.CFG(normalize=True)
    Project_Vex = AngrVex(p)
    Project_Asm = AngrAsm(p)
    f = cfg.kb.functions
    return p, Project_Vex, Project_Asm, f

