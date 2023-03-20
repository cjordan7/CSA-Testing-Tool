import json
import os

from variables import Variables

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


def getCFlags(path):
    f = open(path)

    lines = f.readlines()

    for i in lines:
        if("CFLAGS =" in i):
            return i

    return ""


print(getCFlags('/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/workdir/julietTestSuite/julietTestSuite/62640-v1.0.0/Makefile'))


#subfolders = [f.path for f in os.scandir(folder) if f.is_dir()]


# TODO: Change name of file
