import argparse
from argparse import RawTextHelpFormatter

from runCodeChecker import RunCodeChecker
from variables import Variables
from sampleReadCSATable import getCWECheckerMapping
import os

import subprocess

from collections import OrderedDict
from itertools import groupby

import json


def addCommentsToPatches():
    baseDir = os.path.dirname(os.path.realpath(__file__))

    dire = os.path.join(baseDir, Variables.DATA_MAGMA_WORKDIR, "targets")
    direSub = [f.path for f in os.scandir(dire)]

    listPatchesPath = OrderedDict()
    for lib in direSub:
        subfolders = [f.path for f in os.scandir(os.path.join(lib, "patches", "bugs"))]

        listPatchesPath[lib] = []
        for i in subfolders:
            listPatchesPath[lib].append(i)
            f = open(i)
            p = f.readlines()
            f.close()
            for line in range(0, len(p)):
                if("MAGMA_LOG" in p[line]):
                    p[line] = p[line][:-2] + "//" + i.split("/")[-1] + p[line][-2:]

            f = open(i, "w")
            f.write("".join(p))
            f.close()

    return listPatchesPath


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

    findableBugs = OrderedDict()
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
    #codeChecker = RunCodeChecker()
    baseDir = os.path.dirname(os.path.realpath(__file__))

    # TODO: Change!!!
    pathIn = os.path.join(baseDir, "workdir", "magma_libs")
    pathReport = os.path.join(baseDir, Variables.DATA_MAGMA_REPORT_DIR)

    subfolders = [f.path for f in os.scandir(pathIn) if f.is_dir()]

    analyzedFiles = dict()
    for sub in subfolders:
        tp = 0
        #tn = 0 # We don't know
        fp = 0
        fn = 0

        bugsFound = set()

        lib = sub.split("/")[-1]
        pathReport2 = os.path.join(pathReport, lib+".json")

        f = open(pathReport2)
        js = json.load(f)

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
                if(fileMeta not in metadata):
                    metadata[fileMeta] = dict()

                if(startLine not in metadata[fileMeta]):
                    metadata[fileMeta][startLine] = [0]

                metadata[fileMeta][startLine].append(message)
            start = lines[0][0]
            end = lines[0][0]
            i = 0
            #for line, filePath in lines:
            hasFoundBug = False
            for line, filePath in lines:
                currentFilePath = filePath
                i += 1

                if(i >= len(lines)):
                    break

                if(line in metadata[filePath]):
                    if(any("Entering loop body" in str(k) for k in metadata[filePath][line])):
                        #start = lines[i][0]
                        end = lines[i][0]
                    elif(any("Assuming the condition" in str(k) for k in metadata[filePath][line])):
                        metadata[filePath][line][0] += 1
                        condition = metadata[filePath][line][0]
                        # TODO: Replace by better check of if
                        if("if" in analyzedFiles[filePath][line-1]):
                            #if("if" in metadata[filePath][line][condition]):
                            start = lines[i][0]
                            end = lines[i][0]
                    elif(any("Calling" in str(k) for k in metadata[filePath][line])):
                        nextFile = lines[i][1]
                        currentFilePath = nextFile
                        if(lines[i][0] in metadata[nextFile] and any("Entered" in str(k) for k in metadata[nextFile][lines[i][0]])):
                            metadata[filePath][line][0] += 1

                        condition = metadata[filePath][line][0]
                        if(condition > 0 and "Calling" in metadata[filePath][line][condition]):
                            start = lines[i][0]
                            end = lines[i][0]
                        else:
                            end = lines[i][0]
                        # TODO Change file
                    elif(any("Entered" in str(i) for i in metadata[filePath][line])):
                            end = lines[i][0]
                    else:
                        start = lines[i][0]
                        end = lines[i][0]
                else:
                    end = lines[i][0]
                print(analyzedFiles[filePath][line-1])

                if(start <= end):
                    for m in range(start, end+1):
                        readLine = analyzedFiles[currentFilePath][m-1].strip()
                        if("MAGMA_LOG" in readLine):
                            for bug, checker in findableBugs.items():
                                if(bug in readLine and checker == h["checker_name"]):
                                    bugsFound.add(bug)
                                    hasFoundBug = True
                if(hasFoundBug):
                    break
                start = end
            if(not hasFoundBug):
                fp += 1

        tp = len(bugsFound)
        fn = len(findableBugs) - len(bugsFound)
        print(tp)
        print(fn)
        print(fp)

        bugsFound = set()


def createCompilationDatabases(mappingLibsCheckers, libsPatches, findableBugs):
    codeChecker = RunCodeChecker()
    baseDir = os.path.dirname(os.path.realpath(__file__))
    pathIn = os.path.join(baseDir, "workdir", "magma_libs")
    pathReport = os.path.join(baseDir, Variables.DATA_MAGMA_REPORT_DIR)

    pathIn = os.path.join(baseDir, "workdir", "magma_libs")
    pathReport = os.path.join(baseDir, Variables.DATA_MAGMA_REPORT_DIR)

    compilationMake = {"libpng": "make libpng16.la",
                       "libsndfile": "make",
                       "libtiff": "make",
                       "libxml2": "make all",
                       "lua": "make liblua.a lua",
                       "php": "make",
                       "poppler": "make poppler poppler-cpp pdfimages pdftoppm",
                       "openssl": 'make LDCMD="$CXX $CXXFLAGS"',
                       "sqlite3": "make all sqlite3.c"}
    for lib, patches in libsPatches.items():
        libName = lib.split("/")[-1]
        findableBugsLib = findableBugs[libName]

        pathReport2 = os.path.join(pathReport, libName)
        pathCC = os.path.join(pathIn, libName, "repo")
        command = compilationMake[libName]
        for patch in patches:
            patchName = patch.split("/")[-1][0:-6]

            if(patchName in findableBugsLib):
                print("Magma: Creating database for " + libName + " " + patchName)
                e = subprocess.run("git apply " + patch, shell=True,
                                   cwd=pathCC,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                if(e.returncode == 0):
                    codeChecker.compileDB(pathCC, command, patchName)

                    # patchName = f.split("/")[-1].split(".")[0][-6:]
                    checkers = findableBugs[libName]
                    checker = checkers[patchName]

                    # TODO:...
                    codeChecker.runCodeChecker(pathCC, pathReport2,
                                               [checker],
                                               patchName)
                    subprocess.run("git apply -R " + patch, shell=True,
                                   cwd=pathCC)#,

                #stdout=subprocess.DEVNULL,
                #stderr=subprocess.DEVNULL)
                #stdout=subprocess.DEVNULL,
                #stderr=subprocess.DEVNULL)


def runCodeChecker(mappingLibsCheckers):
    codeChecker = RunCodeChecker()
    baseDir = os.path.dirname(os.path.realpath(__file__))

    pathIn = os.path.join(baseDir, "workdir", "magma_libs")
    pathReport = os.path.join(baseDir, Variables.DATA_MAGMA_REPORT_DIR)

    subfolders = [f.path for f in os.scandir(pathIn) if f.is_dir()]

    for sub in subfolders:
        lib = sub.split("/")[-1]
        pathReport2 = os.path.join(pathReport, lib)
        checkers = mappingLibsCheckers[lib]
        pathCC = os.path.join(pathIn, lib, "repo")
        for f in os.listdir(pathCC):
            if f.startswith("compile_command"):
                checkers = mappingLibsCheckers[lib]
                patchName = f.split("/")[-1].split(".")[0][-6:]
                checker = checkers[f.split("/")[-1].split(".")[0][-6:]]
                pathCCPatch = os.path.join(pathIn, lib, "repo", patchName)
                codeChecker.runCodeChecker(pathCCPatch, pathReport2, [checker],
                                           patchName)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="parseMagma",
                                     description="Parse and run the " +
                                     "Clang Static Analyzer for " +
                                     "Magma Libraries. " +
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
                        help="run statistics. " +
                        "Ignore already ran reports")

    args = parser.parse_args()

    mappingLibsCheckers, findableBugs = getCheckers(readMagmaCWEs())

    if(not args.o and not args.i and not args.r and not args.s):
        libsPatches = addCommentsToPatches()
        createCompilationDatabases(mappingLibsCheckers, libsPatches, findableBugs)
        #runCodeChecker(findableBugs)
        #runCodeCheckerStatistics(mappingLibsCheckers, findableBugs)
        exit(0)

    if(args.i):
        libsPatches = addCommentsToPatches()
        createCompilationDatabases(mappingLibsCheckers, libsPatches, findableBugs)

    #if(args.r):
        #runCodeChecker(findableBugs)

    #if(args.s):
        #runCodeCheckerStatistics(m, toRunAndBugs)
        #readPickle()
