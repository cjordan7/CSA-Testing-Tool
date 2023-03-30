from runCodeChecker import RunCodeChecker
from variables import Variables
from sampleReadCSATable import getCWECheckerMapping
import os

from itertools import groupby

import json


def readMagmaCWEs():
    print("Magma: Read CWEs")
    baseDir = os.path.dirname(os.path.realpath(__file__))
    pathJTS = os.path.join(baseDir, Variables.DATA_FOLDER, "magmapatchesCWE.txt")

    f = open(pathJTS)
    lines = f.readlines()
    f.close()

    libsCWEs = dict()
    for i in lines:
        k = i.strip("\n").split(":")
        libName = k[1].strip()[0:3]
        if(libName in libsCWEs):
            libsCWEs[libName].append((k[0].strip(), k[1].strip()))
        else:
            libsCWEs[libName] = [(k[0].strip(), k[1].strip())]

    return libsCWEs


def getCheckers(libsCWEs):
    print("Magma: Getting Magma libs, cwes, and checkers mappings")
    checkers = getCWECheckerMapping()
    mappingLibsCheckers = dict()

    findableBugs = dict()
    libs = {"PNG": "libpng",
            "SND": "libsndfile",
            "TIF": "libtiff",
            "XML": "libxml2",
            "LUA": "lua",
            "SSL": "openssl",
            "PHP": "php",
            "PDF": "poppler",
            "SQL": "sqlite3"}
    for lib, o in libsCWEs.items():
        findableCWEs = dict()
        for cwe, patch in o:
            if(cwe in checkers):
                findableCWEs[patch] = checkers[cwe]
                if(libs[lib] not in mappingLibsCheckers):
                    mappingLibsCheckers[libs[lib]] = set()

                mappingLibsCheckers[libs[lib]].add(checkers[cwe])
        findableBugs[libs[lib]] = findableCWEs

    return mappingLibsCheckers, findableBugs


def runCodeCheckerStatistics(mappingLibsCheckers, findableBugs):
    codeChecker = RunCodeChecker()
    baseDir = os.path.dirname(os.path.realpath(__file__))

    # TODO: Change!!!
    pathIn = os.path.join(baseDir, "workdir", "magma_libs")
    pathReport = os.path.join(baseDir, Variables.DATA_MAGMA_REPORT_DIR)

    subfolders = [f.path for f in os.scandir(pathIn) if f.is_dir()]

    # TODO ?? Good idea?
    analyzedFiles = dict()
    for sub in subfolders:
        tp = 0
        #tn = 0 # We don't know
        fp = 0
        fn = 0

        bugsFound = set()

        lib = sub.split("/")[-1]
        pathReport2 = os.path.join(pathReport, lib+".json")

        print(pathReport2)

        f = open(pathReport2)
        js = json.load(f)

        print(len(js["reports"]))

        findableBugForLib = findableBugs[lib]
        numberOfBugs = len(findableBugs)
        #l = mappingLibsCheckers[lib]

        for h in js["reports"]:
            temp = []

            for k in h["bug_path_positions"]:
                pathOriginal = k["file"]["original_path"]
                temp.append((k["range"]["start_line"], k["file"]["original_path"]))

                if(pathOriginal not in analyzedFiles):
                    f1 = open(pathOriginal)
                    analyzedFiles[pathOriginal] = f1.readlines()
                    f1.close()

            lines = [key for key, _group in groupby(temp)]
            metadata = dict()

            for k in h["bug_path_events"]:
                fileMeta = k["file"]["original_path"]
                startLine = k["range"]["start_line"]
                message = k["message"]
                print(k["range"])
                print(startLine)
                if(fileMeta not in metadata):
                    metadata[fileMeta] = dict()

                if(startLine == 4739):
                    print(startLine not in metadata[fileMeta])
                if(startLine not in metadata[fileMeta]):
                    if(startLine == 4739):
                        print(startLine not in metadata[fileMeta])
                    metadata[fileMeta][startLine] = [0]
                    print(metadata[fileMeta][startLine])
                    print(metadata[fileMeta])

                metadata[fileMeta][startLine].append(message)
            start = lines[0][0]
            end = lines[0][0]
            i = 0
            #for line, filePath in lines:
            hasFoundBug = False
            print(h["file"])
            print("Start ============================================================================")
            for line, filePath in lines:
                currentFilePath = filePath
                i += 1

                if(i >= len(lines)):
                    break

                if(line in metadata[filePath]):
                    print(metadata[filePath][line])
                    if(any("Entering loop body" in str(k) for k in metadata[filePath][line])):
                        print("f")
                        #start = lines[i][0]
                        end = lines[i][0]
                    elif(any("Assuming the condition" in str(k) for k in metadata[filePath][line])):
                        print("Weird")
                        metadata[filePath][line][0] += 1
                        condition = metadata[filePath][line][0]
                        # TODO: Replace by better check of if
                        if("if" in analyzedFiles[filePath][line-1]):
                            #if("if" in metadata[filePath][line][condition]):
                            start = lines[i][0]
                            end = lines[i][0]
                    elif(any("Calling" in str(k) for k in metadata[filePath][line])):
                        print("Calling")

                        nextFile = lines[i][1]
                        currentFilePath = nextFile
                        if(lines[i][0] in metadata[nextFile] and any("Entered" in str(k) for k in metadata[nextFile][lines[i][0]])):
                            print("Here.......")
                            metadata[filePath][line][0] += 1

                        condition = metadata[filePath][line][0]
                        print(condition > 0)
                        if(condition > 0 and "Calling" in metadata[filePath][line][condition]):
                            print("Here2....")
                            start = lines[i][0]
                            end = lines[i][0]
                        else:
                            end = lines[i][0]
                        # TODO Change file
                    elif(any("Entered" in str(i) for i in metadata[filePath][line])):
                            end = lines[i][0]

                    else:
                        print("Up here")
                        start = lines[i][0]
                        end = lines[i][0]
                else:
                    print("Up here")
                    end = lines[i][0]
                print(analyzedFiles[filePath][line-1])

                if(start <= end):

                    print("----------------------------------------------------")
                    print(str(start) + " " + str(end) + " " + currentFilePath)
                    for m in range(start, end+1):
                        #print(" Quoi: " + str(len(analyzedFiles[filePath])))
                        #print(m-1)
                        readLine = analyzedFiles[currentFilePath][m-1].strip()
                        #print(readLine)
                        if("MAGMA_LOG" in readLine):
                            for bug, checker in findableBugs.items():
                                if(bug in readLine and checker == h["checker_name"]):
                                    bugsFound.add(bug)
                                    hasFoundBug = True
                if(hasFoundBug):
                    break

                    # TODO: Read everything from start to end and check magma_log
                start = end
            if(not hasFoundBug):
                fp += 1

            print(len(findableBugs))
            print(h["checker_name"])
            print(findableBugForLib)

        tp = len(bugsFound)
        fn = len(findableBugs) - len(bugsFound)
        print(tp)
        print(fn)
        print(fp)

        bugsFound = set()


def runCodeChecker(mappingLibsCheckers):
    codeChecker = RunCodeChecker()
    baseDir = os.path.dirname(os.path.realpath(__file__))

    # TODO: Change!!!
    pathIn = os.path.join(baseDir, "workdir", "magma_libs")
    pathReport = os.path.join(baseDir, Variables.DATA_MAGMA_REPORT_DIR)

    subfolders = [f.path for f in os.scandir(pathIn) if f.is_dir()]

    for sub in subfolders:
        lib = sub.split("/")[-1]
        pathReport2 = os.path.join(pathReport, lib)
        checkers = mappingLibsCheckers[lib]
        pathCC = os.path.join(pathIn, lib, "repo")
        print(mappingLibsCheckers[lib])
        checkers = mappingLibsCheckers[lib]
        print(pathReport2)
        codeChecker.runCodeChecker(pathCC, pathReport2, checkers, "")
        raise NotImplementedError


if __name__ == '__main__':
    mappingLibsCheckers, findableBugs = getCheckers(readMagmaCWEs())

    #runCodeChecker(mappingLibsCheckers)
    runCodeCheckerStatistics(mappingLibsCheckers, findableBugs)
    #runCodeCheckerStatistics(m, toRunAndBugs)
