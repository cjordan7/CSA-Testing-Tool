import multiprocessing
import os
import re
import subprocess

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

    subprocess.run("git apply " + pathPatch, shell=True, cwd=pathCGC)


def testMakefile(mappings):
    for key, checkers in mappings.items():
        makefilePath = os.path.join(key, "Makefile")

        f = open(makefilePath)
        print(f.read())
        f.close


print(testMakefile(getMappings()))

applyPatch()
