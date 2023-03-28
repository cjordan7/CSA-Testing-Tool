import multiprocessing
import os
import re
import subprocess

import argparse
from argparse import RawTextHelpFormatter

from runCodeChecker import RunCodeChecker
from sampleReadCSATable import getCWECheckerMapping
from variables import Variables


def getCWEs():
    fileCWEsMapped = dict()
    print("CGC: Collecting bugs (CWEs, lines, urls) from Juliet Test Suite.")

    baseDir = os.path.dirname(os.path.realpath(__file__))
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


def writeToFileCQE_Challenges():
    dictio = getCWEs()
    mapping = getCWECheckerMapping()

    cbsOnly = ["KPRCA_00024", "KPRCA_00048", "KPRCA_00016",
               "NRFIN_00006", "YAN01_00009"]

    suffixes = [".c", ".cc", ".h"]
    for key, items in dictio.items():
        t = True

        checkers = set()
        for i in items:
            if(i in mapping):
                checkers.add(mapping[i])

        # The folder only contains vulnerabilites CSA can't detect
        if(len(checkers) == 0):
            continue

        subfolders = []

        subfolders_LIBs = [f.path for f in os.scandir(key) if "lib" in f.path]

        for i in subfolders_LIBs:
            subfolders += [f.path for f in os.scandir(i)]

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

                        for lineToChange in linesToChange:
                            splitted.insert(lineToChange+1, "#ifndef PATCHED\n" +
                                            check + "\n#endif")

                    f = open(subfolderPath, "w")
                    f.write("\n".join(splitted))
                    f.close()


def getMappings():
    dictio = getCWEs()
    mapping = getCWECheckerMapping()
    returnDictio = dict()

    for key, items in dictio.items():
        checkers = set()
        for i in items:
            if(i in mapping):
                checkers.add(mapping[i])
        returnDictio[key] = checkers

    return returnDictio


def workFunction(pathCGC):
    codeChecker = RunCodeChecker()

    path = os.path.join(pathCGC)

    print("Creating compilation database (bad) for " + path.split(os.sep)[-1])

    codeChecker.compileDB(path, "PATCHED")
    codeChecker.compileDB(path, "")

    # codeChecker.runInterceptBuild(path, makeGood, "GOOD")
    # codeChecker.runInterceptBuild(path, makeBad, "BAD")


def interceptBuildForJulietTestSuite(toRun):
    print("Run codechecker for juliet test suite")

    # TODO: Remove?
    # for idN in toRun:
    #    workFunction(codeChecker, pathJTS, idN)

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(workFunction, toRun)
    pool.close()


def applyPatch():
    baseDir = os.path.dirname(os.path.realpath(__file__))
    print(baseDir)
    pathCGC = os.path.join(baseDir, Variables.DATA_CGC_WORKDIR)

    pathPatch = os.path.join(baseDir, Variables.CGC_PATCH_PATH)

    subprocess.run("git checkout -- . ", shell=True, cwd=pathCGC)
    subprocess.run("git clean -fd", shell=True, cwd=pathCGC)
    subprocess.run("git apply " + pathPatch, shell=True, cwd=pathCGC)


def getBugsForIds(mappings, idNs):
    returnDict = dict()
    for filePath, bugs in mappings.items():
        if(any(i == filePath.split("/")[-1] for i in idNs)):
            returnDict[filePath] = bugs

    return returnDict


def updateMakefile(mappings):
    print(mappings)
    baseDir = os.path.dirname(os.path.realpath(__file__))
    pathBuildSH = os.path.join(baseDir, Variables.DATA_FOLDER)
    pathBuildSH = os.path.join(pathBuildSH, "cgcBuild.sh")
    runCodeChecker = RunCodeChecker()

    for key, checkers in mappings.items():
        makefilePath = os.path.join(key, "Makefile")

        cbsOnly = ["KPRCA_00024", "KPRCA_00048", "KPRCA_00016",
                   "NRFIN_00006", "YAN01_00009"]

        if(any(i in key for i in cbsOnly)):
            subfolders2 = [f.path for f in os.scandir(key) if "cb" in f.path]

            for subf in subfolders2:
                print(subf)
                if("cb" in subf):
                    subprocess.run("bash " + pathBuildSH +
                                   " TargetName cc", shell=True, cwd=subf)
                    runCodeChecker.compileDB(subf, "make", "")

        else:
            subprocess.run("bash " + pathBuildSH +
                           " TargetName cc", shell=True, cwd=key)
            runCodeChecker.compileDB(subf, "make", "")
            runCodeChecker.runCodeChecker(key, pathOutGood, checkers, "reports")

        f = open(makefilePath)
        f.close

        f = open(makefilePath, "r")
        lines = f.readlines()
        f.close
        for lineN in range(0, len(lines)):
            if("include" in lines[lineN]):
                lines[lineN] = "# " + lines[lineN]

        #f = open(makefilePath, "w")
        #f.write("".join(lines))
        #f.close
        #raise NotImplementedError


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="parseJulietTestSuite",
                                     description="Parse and run the " +
                                     "Clang Static Analyzer for the " +
                                     "Juliet Test Suite: " +
                                     "(Juliet C/C++ 1.3.1 with extra " +
                                     "support - https://samate.nist.gov" +
                                     "/SARD/test-suites/116).\n\n" +
                                     "By default everything is ran " +
                                     "(creation of compilation database " +
                                     "and running the codechecker)\n\n" +
                                     "If you only want to run a few steps, " +
                                     "then check the option below.",
                                     epilog="Happy analysis!",
                                     formatter_class=RawTextHelpFormatter)

    parser.add_argument("-o", action="store_true",
                        help="write codechecker flags to the test files. " +
                        "This has to be run once for the CSA analysis " +
                        "to correctly work.")

    parser.add_argument("-i", action="store_true",
                        help="run interceptBuild to create the " +
                        "compilation database for each tests. -o " +
                        "has to be used prior to the call of this flag.")

    parser.add_argument("-b", nargs='+',
                        help="run the corresponding bug ids. " +
                        "For example: -b KPRCA_00048 NRFIN_00042")

    parser.add_argument("-s", action="store_true",
                        help="run statistics. " +
                        "For example: -s KPRCA_00048 NRFIN_00042")

    args = parser.parse_args()
    mappings = {}
    if(args.b is not None):
        mappings = getBugsForIds(getMappings(), args.b)
    else:
        mappings = getMappings()

    print(mappings)

    applyPatch()
    updateMakefile(mappings)
