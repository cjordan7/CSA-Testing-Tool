import argparse
from argparse import RawTextHelpFormatter

import json
import os

from runCodeChecker import RunCodeChecker
from sampleReadCSATable import getCWECheckerMapping
from variables import Variables

import multiprocessing


# This class represent only a bug (CWE) at a precise line of a file
class Bug:
    def __init__(self, cwe, line, internetLink, idN, fileName, isOnlyWindows):
        self.cwe = cwe
        self.line = line
        self.idN = idN
        self.fileName = fileName
        self.isOnlyWindows = isOnlyWindows

        # For debugging
        self.internetLink = internetLink

    # This is only used for sorting the lines in the same file
    def __lt__(self, bug2):
        return self.line < bug2.line

    # Used for debugging
    def __str__(self):
        return "(" + self.idN + ", " + self.cwe + ", " + str(self.line) +\
            ", " + self.fileName + ", " + self.internetLink + ", " + \
            str(self.isOnlyWindows) + ")"

    def __repr__(self):
        return self.__str__()


def getBugsAssociatedWithJulietTestSuite():
    print("JulietTestSuite: Collecting bugs (CWEs, lines, urls) from Juliet Test Suite.")

    print("JulietTestSuite: Reading sarifs.json")
    baseDir = os.path.dirname(os.path.realpath(__file__))
    newPath = os.path.join(baseDir, Variables.DATA_JULIETTESTSUITE_WORKDIR)
    newPath = os.path.join(newPath, "sarifs.json")

    f = open(newPath)
    d = json.load(f)
    f.close()

    bugsMappedInFile = dict()

    for i in range(0, len(d['testCases'])):
        for j in range(0, len(d['testCases'][i]['sarif']['runs'][0]['results'])):
            # CWE number
            cwe = d['testCases'][i]['sarif']['runs'][0]['results'][j]['ruleId']

            # Identifier
            idFile = d['testCases'][i]['identifier']

            # Internet link of bug
            internetLink = d['testCases'][i]['link']

            for k in range(0, len(d['testCases'][i]['sarif']['runs'][0]['results'][j]['locations'])):
                # Url of location of bug. Path to bug
                uri = d['testCases'][i]['sarif']['runs'][0]['results'][j]['locations'][k]['physicalLocation']['artifactLocation']['uri']

                # Check for windows only compatible and ignore them as we are
                # working on Linux and those won't work.
                isOnlyWindows = "_w32_" in uri or "_w32" in uri

                # Start Line of bug
                startLine = d['testCases'][i]['sarif']['runs'][0]['results'][j]['locations'][k]['physicalLocation']['region']['startLine']

                bug = Bug(cwe, startLine, internetLink, idFile, uri, isOnlyWindows)

                if(uri in bugsMappedInFile):
                    bugsMappedInFile[uri].append(bug)
                else:
                    bugsMappedInFile[uri] = [bug]

    return bugsMappedInFile


def getBugsForIds(bugsMappedInFile, idNs):
    returnDict = dict()
    for filePath, bugs in bugsMappedInFile.items():
        if(any(i == bugs[0].idN.split("-")[0] for i in idNs)):
            returnDict[filePath] = bugs

    return returnDict


def addFlagsToFiles(bugsMappedInFile, runIt):
    print("Adding Codechecker flags to each files")
    mappings = getCWECheckerMapping()
    baseDir = os.path.dirname(os.path.realpath(__file__))

    toRun = dict()
    toRunTotal = set()

    for filePath, bugs in bugsMappedInFile.items():
        filename = filePath
        sortedBugs = sorted(bugs, reverse=True)
        if(len(bugs) >= 1):
            array = []
            i = 0
            f = False

            # TODO: create func
            for bug in sortedBugs:
                toRunTotal.add(bug.idN)
                if(bug.cwe in mappings and not bug.isOnlyWindows):
                    if(bug.idN in toRun):
                        toRun[bug.idN].add(mappings[bug.cwe])
                    else:
                        toRun[bug.idN] = set()
                        toRun[bug.idN].add(mappings[bug.cwe])

                    f = True
                    if(len(array) == 0):
                        checkerSet = {mappings[bug.cwe]}
                        array.append((bug.line, checkerSet))
                    else:
                        if(array[i-1][0] == bug.line):
                            array[i-1][1].add(mappings[bug.cwe])
                        else:
                            checkerSet = {mappings[bug.cwe]}
                            array.append((bug.line, checkerSet))

                    i += 1

            # Create the comment:
            # // codechecker_confirmed [checkers] This is a bug."
            if(len(array) >= 1 and runIt):
                newPath = os.path.join(baseDir,
                                       Variables.DATA_JULIETTESTSUITE_WORKDIR)
                newPath = os.path.join(newPath, filename)
                fileToBug = open(newPath)
                lines = fileToBug.readlines()
                fileToBug.close()

                if("// codechecker_confirmed" not in "".join(lines)):
                    for tupl in array:
                        line, checkers = tupl
                        t = ", ".join(checkers)
                        t = "// codechecker_confirmed [" + t + "] This is a bug.\n"

                        if(t != lines[line-1]):
                            lines.insert(line-1, t)

                    tempNewFile = "".join(lines)
                    fileToBug = open(newPath, "w")
                    fileToBug.write(tempNewFile)
                    fileToBug.close()

    print("Finished adding Codechecker flags to each files")
    return toRun, toRunTotal


# We want to either omit the good code or the bad code for each test suites.
# To do this we can use -DOMIT_GOOD or -DOMIT_BAD flags, but we need to set them out.
# We could either change the Makefile, or we get the CFLAGS
# and add our own -Dvar.
def addCodeCheckerFlagToCFlags(path):
    f = open(path, "r")

    lines = f.readlines()
    f.close()

    for i in range(0, len(lines)):
        if("FLAGS" in lines[i] and
           "CFLAGS" not in lines[i] and
           "LDFLAGS" not in lines[i]):
            print(lines[i])

    CODE_CHECKER_FLAG = "CODE_CHECKER_FLAG"
    for i in range(0, len(lines)):
        if("CFLAGS =" in lines[i] and
           # Don't add the variable if it is already there
           CODE_CHECKER_FLAG not in lines[i]):
            lines[i] = lines[i].strip("\n") + " $(" + CODE_CHECKER_FLAG + ")\n"
            break

    f = open(path, "w")
    f.write("".join(lines))
    f.close()


def workFunction(idN):
    codeChecker = RunCodeChecker()
    baseDir = os.path.dirname(os.path.realpath(__file__))
    pathJTS = os.path.join(baseDir, Variables.DATA_JULIETTESTSUITE_WORKDIR)

    print("Creating compilation database (good) for " + idN)
    path = os.path.join(pathJTS, idN)

    print("Creating compilation database (bad) for " + idN)
    addCodeCheckerFlagToCFlags(path + "/Makefile")

    makeGood = 'make build CODE_CHECKER_FLAG=-DOMIT_BAD'
    makeBad = 'make build CODE_CHECKER_FLAG=-DOMIT_GOOD'

    codeChecker.compileDB(path, makeGood, "GOOD")
    codeChecker.compileDB(path, makeBad, "BAD")

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


def runCodeCheckerStatistics(m):
    print("")
    raise NotImplementedError


def runCodeChecker(toRun):
    codeChecker = RunCodeChecker()
    baseDir = os.path.dirname(os.path.realpath(__file__))
    pathJTS = os.path.join(baseDir, Variables.DATA_JULIETTESTSUITE_WORKDIR)

    reportPath = os.path.join(baseDir,
                              Variables.DATA_JULIETTESTSUITE_REPORT_DIR)

    for idN, checkers in toRun.items():
        pathIn = os.path.join(pathJTS, idN)
        pathOut = os.path.join(reportPath, idN)
        pathOutGood = os.path.join(pathOut, "GOOD")

        print("Running codechecker analysis (good) for " + idN)
        codeChecker.runCodeChecker(pathIn, pathOutGood, checkers, "GOOD")

        pathOutBad = os.path.join(pathOut, "BAD")
        print("Running codechecker analysis (bad) for " + idN)
        codeChecker.runCodeChecker(pathIn, pathOutBad, checkers, "BAD")


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
                        "For example: -b 111378 111866.")

    parser.add_argument("-s", action="store_true",
                        help="run statistics. " +
                        "For example: -b 111378 111866.")

    args = parser.parse_args()

    bugsMappedInFile = getBugsAssociatedWithJulietTestSuite()

    if(args.b is not None):
        bugsMappedInFile = getBugsForIds(bugsMappedInFile, args.b)

    if(not args.o and not args.i and not args.r):
        m, e = addFlagsToFiles(bugsMappedInFile, True)
        interceptBuildForJulietTestSuite(m.keys())
        runCodeChecker(m)
        runCodeCheckerStatistics(m)
        exit(0)

    m, e = addFlagsToFiles(bugsMappedInFile, args.o)

    if(args.i):
        interceptBuildForJulietTestSuite(m.keys())

    if(args.r):
        runCodeChecker(m)

    if(args.s):
        runCodeCheckerStatistics(m)
