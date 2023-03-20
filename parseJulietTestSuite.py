import json
import os

from variables import Variables
from sampleReadCSATable import getCWECheckerMapping

from runCodeChecker import RunCodeChecker


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
    f = open('/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/julietTestSuite/julietTestSuite/sarifs.json')
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
                isOnlyWindows = "_w32_" in uri

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
    base_dir = os.getcwd()
    print(base_dir)
    for filePath, bugs in bugsMappedInFile.items():
        filename = filePath

        # TODO: Replace that path with variable
        newPath = os.path.join(base_dir, "workdir/julietTestSuite/julietTestSuite")
        newPath = os.path.join(newPath, filename)
        f = open(newPath)
        #lines = f.readlines()
        sortedBugs = sorted(bugs, reverse=True)

        if(len(bugs) > 1):
            lines = f.readlines()
            array = []
            i = 0
            f = False
            # TODO: create func
            for bug in sortedBugs:
                if(bug.cwe in mappings):
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
            for tupl in array:
                line, checkers = tupl
                t = ", ".join(checkers)
                t = "// codechecker_confirmed [" + t + "] This is a bug."


            # TODO: Read and insert in files


# We want to either omit the good code or the bad code for each test suites.
# To do this we can use -DOMIT_GOOD or -DOMIT_BAD flags, but we need to set them out.
# We could either change the Makefile, or we get the CFLAGS and add our own -Dvar.
def getCFlags(path):
    f = open(path)

    lines = f.readlines()

    for i in lines:
        if("CFLAGS =" in i):
            return i

    return "CFLAGS ="


def runCodeChecker(bugsMappedInFile):
    print("Run codechecker for juliet test suite")
    codeChecker = RunCodeChecker()

    # TODO: for each that aren't windows only makefile
    codeChecker.runInterceptBuild("/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/data/julietTestSuite/64340-v1.0.0", "make build")


m = getBugsAssociatedWithJulietTestSuite()

#addFlagsToFiles)

runCodeChecker(m)

#print(getCFlags('/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/julietTestSuite/julietTestSuite/62640-v1.0.0/Makefile'))


#subfolders = [f.path for f in os.scandir(folder) if f.is_dir()]


# TODO: Change name of file
