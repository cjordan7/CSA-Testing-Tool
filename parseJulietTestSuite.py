import json
import multiprocessing
import os
import pickle

import argparse
from argparse import RawTextHelpFormatter

from runCodeChecker import RunCodeChecker
from sampleReadCSATable import getCWECheckerMapping
from variables import Variables

export = "json"


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
    print("JTS: Collecting bugs (CWEs, lines, urls) from Juliet Test Suite.")
    print("JTS: Reading sarifs.json")
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
    temp = [a[0].idN.split("-")[0] for a in bugsMappedInFile.values()]
    diff = set(idNs).difference(temp)
    if(len(diff) > 0):
        raise Exception("ID(s): " + " ".join(diff) + " don't belong" +
                        " to the Juliet Test Suite. Check for correctness.")

    for filePath, bugs in bugsMappedInFile.items():
        if(any(i == bugs[0].idN.split("-")[0] for i in idNs)):
            returnDict[filePath] = bugs

    return returnDict


def addFlagsToFiles(bugsMappedInFile, runIt):
    print("JTS: Adding Codechecker flags to each files")
    mappings = getCWECheckerMapping()
    baseDir = os.path.dirname(os.path.realpath(__file__))

    toRunAndBugs = dict()
    toRun = dict()
    toRunTotal = set()

    for filePath, bugs in bugsMappedInFile.items():
        filename = filePath
        sortedBugs = sorted(bugs, reverse=True)
        if(len(bugs) >= 1):
            array = []
            i = 0
            f = False

            for bug in sortedBugs:
                toRunTotal.add(bug.idN)
                if(bug.cwe in mappings and not bug.isOnlyWindows):
                    if(bug.idN in toRun):
                        toRun[bug.idN].add(mappings[bug.cwe])
                        toRunAndBugs[bug.idN] += 1
                    else:
                        toRun[bug.idN] = set()

                        toRun[bug.idN].add(mappings[bug.cwe])
                        toRunAndBugs[bug.idN] = 1

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
                print("JTS: Writing codechecker flag to " + bug.idN)
                newPath = os.path.join(baseDir,
                                       Variables.DATA_JULIETTESTSUITE_WORKDIR)
                newPath = os.path.join(newPath, filename)
                fileToBug = open(newPath)
                lines = fileToBug.readlines()
                fileToBug.close()

                if(len(lines) == 0):
                    print("WARNING: Empty file " + newPath)

                if("// codechecker_confirmed" not in "".join(lines) and
                   len(lines) > 0):
                    tempCheckers = ""
                    for tupl in array:
                        line, checkers = tupl
                        t = ", ".join(checkers)
                        tempCheckers += t
                        t = "// codechecker_confirmed [" + t + "] This is a bug.\n"

                        if(t != lines[line-1]):
                            lines.insert(line-1, t)

                    lines2 = []
                    temp = False
                    for i in range(0, len(lines)):
                        # Append before line
                        if(i < len(lines) - 1 and "unix.Malloc" in tempCheckers and
                           "free" in lines[i]):
                            lines2.append("// codechecker_confirmed [" +
                                          "unix.Malloc" + "] This is a bug.\n")

                        # Append before line
                        if(i < len(lines) - 1 and "core.NullDereference" in tempCheckers and
                           "printIntLine" in lines[i]):
                            lines2.append("// codechecker_confirmed [" +
                                          "core.NullDereference" + "] " +
                                          "This is a bug.\n")

                        if("unix.Malloc" in tempCheckers and "#endif /* OMITBAD */" in lines[i]):
                            temp = False

                        if("unix.Malloc" in tempCheckers and "#ifndef OMITBAD" in lines[i]):
                            temp = True

                        if(temp and "}" in lines[i]):
                            lines2.append("// codechecker_confirmed [" +
                                          "unix.Malloc" + "] This is a bug.\n")

                        lines2.append(lines[i])
                        if(i < len(lines) - 1 and "/* POTENTIAL FLAW" in lines[i] and
                           "// codechecker_confirmed" not in lines[i+1]):
                            lines2.append("// codechecker_confirmed [" +
                                          tempCheckers + "] This is a bug.\n")

                    tempNewFile = "".join(lines2)
                    fileToBug = open(newPath, "w")
                    fileToBug.write(tempNewFile)
                    fileToBug.close()

    print("JTS: Finished adding Codechecker flags to each files")
    return toRun, toRunTotal, toRunAndBugs


# We want to either omit the good code or the bad code for each test suites.
# To do this we can use -DOMIT_GOOD or -DOMIT_BAD flags, but we need to set them out.
# We could either change the Makefile, or we get the CFLAGS
# and add our own -Dvar.
def addCodeCheckerFlagToCFlags(path):
    f = open(path, "r")

    lines = f.readlines()
    f.close()

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
    codeChecker = RunCodeChecker(export)
    baseDir = os.path.dirname(os.path.realpath(__file__))
    pathJTS = os.path.join(baseDir, Variables.DATA_JULIETTESTSUITE_WORKDIR)

    print("JTS: Creating compilation database (good) for " + idN)
    path = os.path.join(pathJTS, idN)

    print("JTS: Creating compilation database (bad) for " + idN)
    addCodeCheckerFlagToCFlags(path + "/Makefile")

    makeGood = 'make build CODE_CHECKER_FLAG=-DOMITBAD'
    makeBad = 'make build CODE_CHECKER_FLAG=-DOMITGOOD'

    codeChecker.compileDB(path, makeGood, "GOOD")
    codeChecker.compileDB(path, makeBad, "BAD")


def interceptBuildForJulietTestSuite(toRun):
    print("JTS: Run codechecker for juliet test suite.")

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(workFunction, toRun)
    pool.close()


def callCodeCheckerStatistics(toRun, toRunAndBugs):
    baseDir = os.path.dirname(os.path.realpath(__file__))
    reportPath = os.path.join(baseDir,
                              Variables.DATA_JULIETTESTSUITE_REPORT_DIR)

    rates = dict()

    for idN, checkers in toRun.items():
        print("JTS: Statistics for " + str(idN))
        pathOut = os.path.join(reportPath, idN)

        pathOutG = os.path.join(pathOut, "GOOD.json")
        pathOutB = os.path.join(pathOut, "BAD.json")

        tp = 0
        tn = 0
        fp = 0
        fn = 0

        f = open(pathOutB)
        d = json.load(f)
        print(len(d["reports"]))
        f.close()

        fn = toRunAndBugs[idN]
        for i in d["reports"]:
            if("CWE" not in i):
                # We only take into account files which have bugs and flaws
                continue

            if(i["checker_name"] not in checkers):
                continue

            if(i["review_status"] == "confirmed"):
                tp += 1
                fn -= 1
            else:
                fp += 1

        f = open(pathOutG)
        d = json.load(f)
        print(len(d["reports"]))
        f.close()

        tn = toRunAndBugs[idN]

        fn += len(d["reports"])
        tn = tn - fn
        if(tn < 0):
            tn = 0.0

        array = [checkers]

        array.append([tp, tn, fp, fn, tp/(tp+fn) if(tp+fn != 0) else 0,
                      tn/(tn+fp) if(tn+fp != 0) else 0,
                      fn/(fn+tp) if(fn+tp != 0) else 0,
                      fp/(fp+tn) if(fp+tn != 0) else 0])

        rates[idN] = array

    with open('ratesJTS.pickle', 'wb') as handle:
        pickle.dump(rates, handle, protocol=pickle.HIGHEST_PROTOCOL)


def readPickle():
    with open('ratesJTS.pickle', 'rb') as handle:
        b = pickle.load(handle)

    tp = 0
    tn = 0
    fp = 0
    fn = 0
    array = []

    temp = 0
    print(len(b))
    for idN, j in b.items():
        tp += j[1][0]
        tn += j[1][1]
        fp += j[1][2]
        fn += j[1][3]

        if(j[1][0] == 0 and j[1][1] > 0 and j[1][2] == 0 and j[1][3] > 0):
            temp += 1

    array.append([round(tp/(tp+fn), 3), round(tn/(tn+fp), 3),
                  round(fn/(fn+tp), 3), round(fp/(fp+tn), 3),
                  int(tp), int(tn), int(fp), int(fn)])

    print("Fu... " + str(temp))

    print(array)


def filterIds():
    baseDir = os.path.dirname(os.path.realpath(__file__))
    pathJTS = os.path.join(baseDir, Variables.DATA_JULIETTESTSUITE_REPORT_DIR)
    subfolders = [f.path for f in os.scandir(pathJTS) if f.is_dir()]

    filtered = set()
    for i in subfolders:
        newPath = os.path.join(i, "reports_htmlBAD")
        newPath2 = os.path.join(i, "reports_htmlGOOD")
        if(os.path.isdir(newPath) and os.path.isdir(newPath2)):
            filtered.add(i.split("/")[-1])

    return filtered


def callCodeChecker3(toRun):
    codeChecker = RunCodeChecker(export)
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
        codeChecker.convertJSON(pathOut, "GOOD")

        pathOutBad = os.path.join(pathOut, "BAD")
        print("Running codechecker analysis (bad) for " + idN)
        codeChecker.runCodeChecker(pathIn, pathOutBad, checkers, "BAD")
        codeChecker.convertJSON(pathOut, "BAD")


def callCodeChecker(toRun):
    temp = [e + (export,) for e in toRun.items()]

    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    pool.starmap(callCodeCheckerHelper, temp)
    pool.close()


def callCodeCheckerHelper(idN, checkers, export):
    codeChecker = RunCodeChecker(export, extraCommands="--file *CWE*")
    baseDir = os.path.dirname(os.path.realpath(__file__))
    pathJTS = os.path.join(baseDir, Variables.DATA_JULIETTESTSUITE_WORKDIR)

    reportPath = os.path.join(baseDir,
                              Variables.DATA_JULIETTESTSUITE_REPORT_DIR)

    pathIn = os.path.join(pathJTS, idN)
    pathOut = os.path.join(reportPath, idN)
    pathOutGood = os.path.join(pathOut, "GOOD")

    pathEGraph = os.path.join(baseDir, Variables.DATA_FOLDER, "codeCheckerEGraph.txt")
    f = open(pathEGraph, "w")
    f.write("-Xclang -analyzer-dump-egraph=graphGOOD.dot")
    f.close()

    print("Running codechecker analysis (good) for " + idN)
    codeChecker.runCodeChecker(pathIn, pathOutGood, checkers, "GOOD")
    codeChecker.convertTo(pathOut, "GOOD")

    pathOutBad = os.path.join(pathOut, "BAD")
    print("Running codechecker analysis (bad) for " + idN)

    f = open(pathEGraph, "w")
    f.write("-Xclang -analyzer-dump-egraph=graphBAD.dot")
    f.close()

    codeChecker.runCodeChecker(pathIn, pathOutBad, checkers, "BAD")
    codeChecker.convertTo(pathOut, "BAD")


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
                        "For example: -b 240782 111866")

    parser.add_argument("-s", action="store_true",
                        help="run statistics. " +
                        "For example: -s 240782 111866")

    parser.add_argument("--ignore", action="store_true",
                        help="Ignore already ran reports")

    parser.add_argument("--output",
                        help="Output reports in format." +
                        "For example: --output html or --output json")

    args = parser.parse_args()
    if(args.output is not None and (args.output == "html" or args.output == "json")):
        export = args.output

    bugsMappedInFile = getBugsAssociatedWithJulietTestSuite()
    if(args.b is not None):
        bugsMappedInFile = getBugsForIds(bugsMappedInFile, args.b)

    if(not args.o and not args.i and not args.r and not args.s):
        m, e, toRunAndBugs = addFlagsToFiles(bugsMappedInFile, True)

        if(args.ignore is not None):
            for k in filterIds():
                m.pop(k, None)

        interceptBuildForJulietTestSuite(m.keys())
        callCodeChecker(m)

        if(export == "json"):
            callCodeCheckerStatistics(m, toRunAndBugs)
            readPickle()
        exit(0)

    m, e, toRunAndBugs = addFlagsToFiles(bugsMappedInFile, args.o)

    if(args.ignore is not None):
        for k in filterIds():
            m.pop(k, None)

    if(args.i):
        interceptBuildForJulietTestSuite(m.keys())

    if(args.r):
        callCodeChecker(m)

    if(args.s and export == "json"):
        callCodeCheckerStatistics(m, toRunAndBugs)
        readPickle()
