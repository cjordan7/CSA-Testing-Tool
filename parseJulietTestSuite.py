import json
import os

from variables import Variables
from sampleReadCSATable import getCWECheckerMapping
from runCodeChecker import RunCodeChecker

import multiprocessing
#from multiprocessing import Pool, multiprocessing

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
    # TODO: replace with workdir/julietTestSuite
    #dirPath = os.getcwd()
    #sarifsPath = os.getcwd()
    #Variables.DATA_JULIETTESTSUITE_WORKDIR
    print("JulietTestSuite: Collecting bugs (CWEs, lines, urls) from Juliet Test Suite.")

    print("JulietTestSuite: Reading sarifs.json")
    baseDir = os.getcwd()
    newPath = os.path.join(baseDir, Variables.DATA_JULIETTESTSUITE_WORKDIR)
    newPath = os.path.join(newPath, "sarifs.json")

    f = open(newPath)
    d = json.load(f)

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


def addFlagsToFiles(bugsMappedInFile):
    print("Adding Codechecker flags to each files")
    mappings = getCWECheckerMapping()
    baseDir = os.getcwd()

    toRun = dict()
    toRunTotal = set()

    for filePath, bugs in bugsMappedInFile.items():
        filename = filePath
        sortedBugs = sorted(bugs, reverse=True)

        if(len(bugs) > 1):
            array = []
            i = 0
            f = False

            # TODO: create func
            for bug in sortedBugs:
                toRunTotal.add(bug.idN)
                if(bug.cwe in mappings and not bug.isOnlyWindows):
                    if(bug.idN in toRun):
                        toRun[bug.idN].append(mappings[bug.cwe])
                    else:
                        toRun[bug.idN] = [mappings[bug.cwe]]

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
            if(len(array) > 1):
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
    baseDir = os.getcwd()
    pathJTS = os.path.join(baseDir, Variables.DATA_JULIETTESTSUITE_WORKDIR)

    print("Creating compilation database for " + idN)
    path = os.path.join(pathJTS, idN)
    addCodeCheckerFlagToCFlags(path + "/Makefile")

    makeGood = 'make build CODE_CHECKER_FLAG=-DOMIT_BAD'
    makeBad = 'make build CODE_CHECKER_FLAG=-DOMIT_GOOD'

    codeChecker.compileDB(path, makeGood, "GOOD")
    codeChecker.compileDB(path, makeBad, "BAD")

    # codeChecker.runInterceptBuild(path, makeGood, "GOOD")
    # codeChecker.runInterceptBuild(path, makeBad, "BAD")


def interceptBuildForJulietTestSuite(toRun):
    print("Run codechecker for juliet test suite")

    print(multiprocessing.cpu_count())

    # for idN in toRun:
    #    workFunction(codeChecker, pathJTS, idN)

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(workFunction, toRun)
    pool.close()


def runCodeChecker(toRun):
    codeChecker = RunCodeChecker()
    baseDir = os.getcwd()
    pathJTS = os.path.join(baseDir, Variables.DATA_JULIETTESTSUITE_WORKDIR)

    for idN in toRun:
        #    workFunction(codeChecker, pathJTS, idN)
        print("Creating compilation database for " + idN)
        path = os.path.join(pathJTS, idN)
        addCodeCheckerFlagToCFlags(path + "/Makefile")

        makeGood = 'make build CODE_CHECKER_FLAG=-DOMIT_BAD'
        makeBad = 'make build CODE_CHECKER_FLAG=-DOMIT_GOOD'

        codeChecker.runCodeChecker(path, makeGood, "GOOD")
        #codeChecker.runCodeChecker(path, makeBad, "BAD")

    raise NotImplementedError


# TODO: Implement command line options. Don't need to always run everything in pipeline...
if __name__ == '__main__':
    bugsMappedInFile = getBugsAssociatedWithJulietTestSuite()
    m, e = addFlagsToFiles(bugsMappedInFile)
    print(m)
    print(len(m))
    print(len(e))
    interceptBuildForJulietTestSuite(m.keys())
    runCodeChecker(m)
