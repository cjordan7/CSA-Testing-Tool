import subprocess
import os

from variables import Variables

export = "html"


class InterceptBuild():
    @staticmethod
    def getInterceptBuildCommand(command):
        return "intercept-build --override-compiler " + command + " CC=intercept-cc CXX=intercept-c++"


class RunCodeChecker():
    def __init__(self, export, extraCommands=""):
        self.export = export
        self.extraCommands = extraCommands
        self.codeCheckerLog = "CodeChecker log -o compile_commands.json -b "
        self.interceptBuild = "intercept-build --override-compiler make CC=intercept-cc CXX=intercept-c++"

    # TODO: Remove
    def codeCheckerCSAAnalysis(self, CBextraName, outputPath):
        # Use -d to disable checker class
        baseDir = os.path.dirname(os.path.realpath(__file__))
        pathEGraph = os.path.join(baseDir, Variables.DATA_FOLDER, "codeCheckerEGraph.txt")

        return "CodeChecker analyze compile_commands" + \
            CBextraName + ".json " +\
            "--analyzers clangsa  --ctu " +\
            "--analyzer-config clangsa:unroll-loops=true " +\
            "clangsa:widen-loops=true clangsa:cfg-loopexit=true --z3 on " +\
            "--saargs " + pathEGraph + " " +\
            "-o " + outputPath + " " + self.extraCommands + " --verbose debug -e alpha.security.taint " #" --quiet "

    # TODO: Reinstore to : `codeCheckerCSAAnalysis`
    def codeCheckerCSAAnalysis2(self, CBextraName, outputPath):
        # Use -d to disable checker class
        baseDir = os.path.dirname(os.path.realpath(__file__))
        pathEGraph = os.path.join(baseDir, Variables.DATA_FOLDER, "codeCheckerEGraph.txt")

        return "CodeChecker analyze compile_commands" + \
            CBextraName + ".json " +\
            "--analyzers clangsa  --ctu -d core -d alpha -d cplusplus -d " +\
            "nullability -d optin -d deadcode -d " +\
            "security -d unix -d valist  -d security.FloatLoopCounter -d " +\
            "security.insecureAPI.UncheckedReturn " +\
            "-d security.insecureAPI.getpw -d " +\
            "security.insecureAPI.gets -d security.insecureAPI.mkstemp -d " +\
            "security.insecureAPI.mktemp -d security.insecureAPI.rand -d " +\
            "security.insecureAPI.vfork " +\
            "--analyzer-config clangsa:unroll-loops=true " +\
            "clangsa:widen-loops=true clangsa:cfg-loopexit=true --z3 on " +\
            "--saargs " + pathEGraph + " " +\
            "-o " + outputPath + " " + self.extraCommands + " --verbose debug -e alpha.security.taint " #" --quiet "

    def parseOutput(self, path):
        return "CodeChecker parse --quiet --export html --output " + path +\
            " ./reports"

    def runDBCommandAndRenameJSON(self, command, path, name):
        # Make clean just in case
        #subprocess.run("make clean", shell=True, cwd=path,
        #               stdout=subprocess.DEVNULL,
        #               stderr=subprocess.DEVNULL)

        subprocess.run(command, shell=True, cwd=path,
                       stdout=subprocess.DEVNULL)#,
                       #stderr=subprocess.DEVNULL)

        #subprocess.run("make clean", shell=True, cwd=path,
        #               stdout=subprocess.DEVNULL,
        #               stderr=subprocess.DEVNULL)

        # Rename compile_commands.json
        subprocess.run("mv compile_commands.json compile_commands" +
                       name + ".json", shell=True, cwd=path)

    def compileDB(self, path, command, name):
        compileDBCommand = "compiledb -n " + command

        # Create compilation database for CSA
        self.runDBCommandAndRenameJSON(compileDBCommand, path, name)

    def runInterceptBuild(self, path, command, name):
        interceptBuild = InterceptBuild.getInterceptBuildCommand(command)

        # Create compilation database for CSA
        self.runDBCommandAndRenameJSON(interceptBuild, path, name)

    def runCodeChecker(self, pathIn, reportPath, checkers, CBextraName):
        enableCheckers = " ".join(["-e " + i for i in checkers])
        print(self.codeCheckerCSAAnalysis(CBextraName, reportPath) + enableCheckers)
        #raise NotImplementedError
        subprocess.run(self.codeCheckerCSAAnalysis(CBextraName, reportPath) +
                       enableCheckers,
                       shell=True, cwd=pathIn)

    def convertTo(self, reportPath, extraName):
        # TODO Replace by enum
        # TODO: Redirect output to nothing
        # TODO: Export json

        outputName = "_report"
        if(self.export == "json"):
            outputName = ".json"

        print("Here ========================")
        print(self.export)
        subprocess.run("CodeChecker parse --export " + self.export +
                       " --output " + "./" + extraName + outputName + " ./" +
                       extraName, shell=True, cwd=reportPath)

    def convertJSON(self, reportPath, extraName):
        self.convertTo(reportPath, extraName)
        #TODO: Redirect output to nothing
        #TODO: Export json
        #subprocess.run("CodeChecker parse --export json --output " +
        #               "./" + extraName + ".json ./" + extraName,
        #               shell=True, cwd=reportPath)

    def outputInDierectory(self, directory):
        self.parseOutput(directory)
