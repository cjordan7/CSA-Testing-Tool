
import json
import multiprocessing
import os
import pickle
import re
import subprocess

import argparse
from argparse import RawTextHelpFormatter

from runCodeChecker import RunCodeChecker
from sampleReadCSATable import getCWECheckerMapping
from variables import Variables

export = "html"

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
        number = 0
        for i in items:
            if(i in mapping):
                number += 1
                checkers.add(mapping[i])
        returnDictio[key] = (checkers, number)

    return returnDictio


def workFunction(pathCGC):
    codeChecker = RunCodeChecker(export, extraCommands="--file */src/* */include/*")

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


def createCompilationDatabases(mappings):
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(createCompilationDatabasesHelper, mappings)
    pool.close()


def createCompilationDatabases2(mappings):
    baseDir = os.path.dirname(os.path.realpath(__file__))
    pathBuildSH = os.path.join(baseDir, Variables.DATA_FOLDER)
    pathBuildSH = os.path.join(pathBuildSH, "cgcBuild.sh")
    runCodeChecker = RunCodeChecker(export)

    for key, tupl in mappings.items():
        makefilePath = os.path.join(key, "Makefile")

        cbsOnly = ["KPRCA_00024", "KPRCA_00048", "KPRCA_00016",
                   "NRFIN_00006", "YAN01_00009"]

        if(any(i in key for i in cbsOnly)):
            subfolders2 = [f.path for f in os.scandir(key) if "cb" in f.path]

            for subf in subfolders2:
                name = subf.split("/")[-2] + "/" + subf.split("/")[-1]
                print("CGC: Creating compilation database for " + name)
                if("cb" in subf):
                    subprocess.run("bash " + pathBuildSH +
                                   " TargetName cc", shell=True, cwd=subf)
                    runCodeChecker.runInterceptBuild(subf, "make", "")

        else:
            name = os.path.basename(os.path.normpath(key))
            print("CGC: Creating compilation database for " + name)
            subprocess.run("bash " + pathBuildSH +
                           " TargetName cc", shell=True, cwd=key)
            runCodeChecker.runInterceptBuild(key, "make", "")
        f = open(makefilePath)
        f.close

        f = open(makefilePath, "r")
        lines = f.readlines()
        f.close
        for lineN in range(0, len(lines)):
            if("include" in lines[lineN]):
                lines[lineN] = "# " + lines[lineN]


def createCompilationDatabasesHelper(key):
    baseDir = os.path.dirname(os.path.realpath(__file__))
    pathBuildSH = os.path.join(baseDir, Variables.DATA_FOLDER)
    pathBuildSH = os.path.join(pathBuildSH, "cgcBuild.sh")
    runCodeChecker = RunCodeChecker(export)

    makefilePath = os.path.join(key, "Makefile")

    cbsOnly = ["KPRCA_00024", "KPRCA_00048", "KPRCA_00016",
               "NRFIN_00006", "YAN01_00009"]

    if(any(i in key for i in cbsOnly)):
        subfolders2 = [f.path for f in os.scandir(key) if "cb" in f.path]

        for subf in subfolders2:
            name = subf.split("/")[-2] + "/" + subf.split("/")[-1]
            print("CGC: Creating compilation database for " + name)
            if("cb" in subf):
                subprocess.run("bash " + pathBuildSH +
                               " TargetName cc", shell=True, cwd=subf)
                runCodeChecker.runInterceptBuild(subf, "make", "")

    else:
        name = os.path.basename(os.path.normpath(key))
        print("CGC: Creating compilation database for " + name)
        subprocess.run("bash " + pathBuildSH +
                       " TargetName cc", shell=True, cwd=key)
        #runCodeChecker.compileDB(key, "make", "")
        runCodeChecker.runInterceptBuild(key, "make", "")
    #f = open(makefilePath)
    #f.close

    #f = open(makefilePath, "r")
    #lines = f.readlines()
    #f.close
    #for lineN in range(0, len(lines)):
    #    if("include" in lines[lineN]):
    #        lines[lineN] = "# " + lines[lineN]


def runCodeChecker(mappings):
    # print(mappings)
    baseDir = os.path.dirname(os.path.realpath(__file__))
    runCodeChecker = RunCodeChecker(export)
    cbsOnly = ["KPRCA_00024", "KPRCA_00048", "KPRCA_00016",
               "NRFIN_00006", "YAN01_00009"]

    pathReport = os.path.join(baseDir, Variables.DATA_CGC_REPORT_DIR)

    for key, tupl in mappings.items():
        checkers = tupl[0]
        if(any(i in key for i in cbsOnly)):
            subfolders2 = [f.path for f in os.scandir(key) if "cb" in f.path]

            for subf in subfolders2:
                name = subf.split("/")[-2] + "_" + subf.split("/")[-1]
                pathReport2 = os.path.join(pathReport, name)
                if(len(checkers) != 0):
                    print("CGC: Run codechecker for " + name)
                    runCodeChecker.runCodeChecker(subf, pathReport2, checkers, "")
                    runCodeChecker.convertTo(pathReport, name)
        else:
            name = os.path.basename(os.path.normpath(key))
            pathReport2 = os.path.join(pathReport, name)
            if(len(checkers) != 0):
                print("CGC: Run codechecker for " + name)
                runCodeChecker.runCodeChecker(key, pathReport2, checkers, "")
                runCodeChecker.convertTo(pathReport, name)


def runCodeCheckerStatistics(mappings):
    baseDir = os.path.dirname(os.path.realpath(__file__))
    reportPath = os.path.join(baseDir,
                              Variables.DATA_CGC_REPORT_DIR)

    rates = dict()

    cbsOnly = ["KPRCA_00024", "KPRCA_00048", "KPRCA_00016",
               "NRFIN_00006", "YAN01_00009"]
    for idN, tupl in mappings.items():
        checkers = tupl[1]
        name = idN.split("/")[-1]
        if(any(i in idN for i in cbsOnly)):
            name = idN.split("/")[-2] + "_" + name
        name += ".json"
        pathOut = os.path.join(reportPath, name)
        print(pathOut)
        print(idN)
        print("JTS: Statistics for " + name)
        print(name)
        tp = 0
        tn = 0
        fp = 0
        fn = 0

        if(not os.path.isfile(pathOut)):
            continue
        f = open(pathOut)
        d = json.load(f)
        print(len(d["reports"]))
        f.close()

        fn = len(d["reports"]) + tupl[1]

        for i in d["reports"]:
            if(i["review_status"] == "confirmed"):
                tp += 1
                fn -= 1
                print("euhh")
            else:
                fp += 1

        array = [checkers]
        # TODO: Check this out
        array.append([tp, tn, fp, fn,
                      round(tp/(tp+fn), 3),
                      round(fn/(fn+tp), 3),
                      round(fp/(tp+tn+fp+fn), 3)])

        rates[idN] = array

    with open('ratesCGC.pickle', 'wb') as handle:
        pickle.dump(rates, handle, protocol=pickle.HIGHEST_PROTOCOL)


def readPickle():
    with open('ratesCGC.pickle', 'rb') as handle:
        b = pickle.load(handle)

    tp = 0
    tn = 0
    fp = 0
    fn = 0
    array = []
    for idN, j in b.items():
        tp += j[1][0]
        tn += j[1][1]
        fp += j[1][2]
        fn += j[1][3]

    array.append([round(tp/(tp+fn), 3),
                  round(fn/(fn+tp), 3),
                  round(fp/(tp+tn+fp+fn), 3),
                  int(tp), int(tn), int(fp), int(fn)])

    print(array)


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

    parser.add_argument("-r", action="store_true",
                        help="run codechecker analysis (CSA analysis) " +
                        "for each tests. " +
                        "-i has to have been called prior for " +
                        "this to work individually")

    parser.add_argument("-b", nargs='+',
                        help="run the corresponding bug ids. " +
                        "For example: -b KPRCA_00048 NRFIN_00042")

    parser.add_argument("-s", action="store_true",
                        help="run statistics. " +
                        "For example: -s KPRCA_00048 NRFIN_00042")

    parser.add_argument("--output",
                        help="Output reports in format." +
                        "For example: --output html or --output json")

    args = parser.parse_args()

    mappings = {}
    if(args.output is not None and (args.output == "html" or args.output == "json")):
        #RunCodeChecker.export = args.output
        export = args.output

    if(args.b is not None):
        mappings = getBugsForIds(getMappings(), args.b)
    else:
        mappings = getMappings()

    if(not args.o and not args.i and not args.r and not args.s):
        applyPatch()
        createCompilationDatabases(mappings)
        runCodeChecker(mappings)
        exit(0)

    if(args.i):
        applyPatch()
        createCompilationDatabases(mappings)

    if(args.r):
        runCodeChecker(mappings)

    if(args.s):
        runCodeCheckerStatistics(mappings)
        readPickle()
