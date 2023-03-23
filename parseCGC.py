import argparse
from argparse import RawTextHelpFormatter

import json
import os


import subprocess

from sampleReadCSATable import getCWECheckerMapping
from variables import Variables
import re

import pathlib


import webbrowser



def getCWEs():
    fileCWEsMapped = dict()
    print("CGC: Collecting bugs (CWEs, lines, urls) from Juliet Test Suite.")

    baseDir = os.getcwd()
    newPath = os.path.join(baseDir, Variables.DATA_CGC_WORKDIR)
    newPath = os.path.join(newPath, "cqe-challenges")
    folder = newPath

    subfolders = [f.path for f in os.scandir(folder) if f.is_dir()]

    for i in subfolders:
        path1 = os.path.join(i, "README.md")
        f = open(path1)
        a = f.read()
        cwes = re.findall(r'CWE-\d+', a)
        fileCWEsMapped[i] = cwes
        f.close()

    return fileCWEsMapped


def writeToFile():
    dictio = getCWEs()
    mapping = getCWECheckerMapping()

    cbsOnly = ["KPRCA_00024", "KPRCA_00048", "KPRCA_00016", "NRFIN_00006", "YAN01_00009"]

    emacsRun2 = 0
    emacsRun = 0

    alreadyRan = ["/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00034/src/main.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/NRFIN_00008/src/actions.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/NRFIN_00030/src/rxtx.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/NRFIN_00030/src/fishyxml.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00014/src/edit_dives.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00014/src/download_dive.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00033/src/lsimp.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00022/src/ui.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/NRFIN_00039/src/service.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/NRFIN_00001/src/joke.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00025/src/fpti_image_data.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00025/src/tbir_image_data.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00002/src/main.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00051/src/student.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00051/src/read.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00040/lib/new_printf.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00040/src/print_recipe.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00040/src/get_instructions.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00040/src/find_recipe.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00024/src/bst.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00023/src/dive.cc",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/NRFIN_00007/lib/libmixology.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/NRFIN_00038/lib/md5.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/NRFIN_00038/src/service.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00015/lib/printf.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00015/src/planetParsers.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00015/src/countyParsers.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00015/src/countryParsers.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00015/src/genericParsers.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00015/src/cityParsers.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00032/src/atree.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00012/src/service.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/NRFIN_00036/src/map.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/NRFIN_00009/src/service.h",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/NRFIN_00009/src/service.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00035/src/main.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00041/src/message.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00050/lib/realloc.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00050/src/vault.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/YAN01_00007/src/main.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/YAN01_00009/cb_3/src/newsletter.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/YAN01_00009/cb_2/src/walkthrough.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/YAN01_00012/src/main.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00044/src/main.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00043/src/main.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00017/src/main.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/NRFIN_00014/src/multipass.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/NRFIN_00014/src/account.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00028/src/eval.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00030/src/packet.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/KPRCA_00010/src/uwfc.c",
"/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/cgc/cqe-challenges/CROMU_00008/src/expression_parser.c"]

    emacsRun2 = len(alreadyRan)
    suffixes = [".c", ".cc", ".h"]
    for key, items in dictio.items():
        t = True

        checkers = set()
        for i in items:
            if(i in mapping):
                checkers.append(mapping[i])

        # The folder only contains vulnerabilites CSA can't detect
        if(len(checkers) == 0):
            continue

        subfolders = []

        subfolders_LIBs = [f.path for f in os.scandir(key) if "lib" in f.path]

        for i in subfolders_LIBs:
            subfolders += [f.path for f in os.scandir(i)]

        # TODO: Find better way to do it!!
        #for i in cbsOnly:
        #    if(i in key):
        if(any(i in key for i in cbsOnly)):
            subfolders2 = [f.path for f in os.scandir(key) if "cb" in f.path]
            t = False

        if(t):
            newPath = os.path.join(key, "src")
            subfolders += [f.path for f in os.scandir(newPath)]
        else:
            for j in subfolders2:
                newPath = os.path.join(j, "src")
                subfolders += [f.path for f in os.scandir(newPath)]

        patchExists = False
        for subfolderPath in subfolders:
            check = ""
            if(any(i in subfolderPath for i in suffixes)):
                f = open(subfolderPath)
                lines = f.read()
                f.close()
                if("PATCHED" in lines):
                    linesToChange = []
                    stackMacros = []
                    splitted = lines.split("\n")

                    temp = False
                    for line in range(0, len(splitted)):
                        if("#ifdef PATCHED" in splitted[line]):
                            temp = True
                            stackMacros.append("#ifdef PATCHED")
                        elif("#ifndef PATCHED" in splitted[line]):
                            stackMacros.append("#ifndef PATCHED")
                            linesToChange.append(line)
                        elif("#if PATCHED" in splitted[line]):
                            temp = True
                            stackMacros.append("#if PATCHED")
                        elif("#else" in splitted[line] and len(stackMacros) >= 1):
                            if("#ifdef PATCHED" in stackMacros[-1] or
                               "#if PATCHED" in stackMacros[-1]):
                                if(temp):
                                    temp = False

                                linesToChange.append(line)

                        elif("#endif" in splitted[line] and len(stackMacros) >= 1):
                            if("PATCHED" in stackMacros[-1]):
                                if(temp):
                                    linesToChange.append(line)
                                    temp = False

                                stackMacros.pop()

                    linesToChange = sorted(linesToChange, reverse=True)

                    if("// codechecker_confirmed" not in "".join(splitted)):
                        check = ""
                        check = ", ".join(checkers)
                        check = "// codechecker_confirmed [" + check + "] This is a bug."
                        #print(check)

                        for lineToChange in linesToChange:
                            splitted.insert(lineToChange+1, "#ifndef PATCHED\n" +
                                            check + "\n#endif")

                    if(subfolderPath not in alreadyRan):
                        subprocess.run("open -a Emacs " + subfolderPath, shell=True)
                        print(subfolderPath)

                        emacsRun += 1
                        emacsRun2 += 1
                        f = open(subfolderPath, "w")
                        f.write("\n".join(splitted))
                        f.close()

                        if(emacsRun == 4):
                            input1 = input()
                            emacsRun = 0
                            print(input1)
                print(emacsRun2)

writeToFile()
