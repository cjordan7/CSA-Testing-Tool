import os
from variables import Variables


def getCWECheckerMapping():
    print("Getting CWE - checkers mappings")
    csaTableMapped = dict()
    baseDir = os.path.dirname(os.path.realpath(__file__))
    pathCSACheckers = os.path.join(baseDir, Variables.CSA_CHECKERS_PATH)
    csaTable = open(pathCSACheckers, "r")
    csaTableLines = csaTable.readlines()

    for line in csaTableLines:
        k = line.strip().split(":")
        if(len(k) > 1):
            l0 = k[0].strip()
            l1 = k[1].strip()

            cwes = list(map(str.strip, l0.split(",")))
            for i in cwes:
                csaTableMapped[i] = l1

    return csaTableMapped
