import subprocess
import os

from variables import Variables


class InterceptBuild():
    @staticmethod
    def getInterceptBuildCommand(command):
        return "intercept-build --override-compiler " + command + " CC=intercept-cc CXX=intercept-c++"


class RunCodeChecker():
    def __init__(self, export="json", extraCommands=""):
        self.export = export
        self.extraCommands = extraCommands
        self.codeCheckerLog = "CodeChecker log -o compile_commands.json -b "
        self.interceptBuild = "intercept-build --override-compiler make CC=intercept-cc CXX=intercept-c++"

    def codeCheckerCSAAnalysis(self, CBextraName, outputPath):
        baseDir = os.path.dirname(os.path.realpath(__file__))
        pathEGraph = os.path.join(baseDir, Variables.DATA_FOLDER, "codeCheckerEGraph.txt")

        return "CodeChecker analyze compile_commands" + \
            CBextraName + ".json " +\
            " --ctu -d alpha -d cplusplus -d " +\
            "nullability -d optin -d deadcode -d " +\
            "security -d unix -d valist  -d security.FloatLoopCounter -d " +\
            "security.insecureAPI.UncheckedReturn " +\
            "-d security.insecureAPI.getpw -d " +\
            "security.insecureAPI.gets -d security.insecureAPI.mkstemp -d " +\
            "security.insecureAPI.mktemp -d security.insecureAPI.rand -d " +\
            "security.insecureAPI.vfork " +\
            "--analyzer-config clangsa:unroll-loops=true " +\
            "clangsa:widen-loops=true clangsa:cfg-loopexit=true clangsa:z3=on " +\
            "--analyzers clangsa " +\
            "--saargs " + pathEGraph + " " +\
            "-o " + outputPath + " " + self.extraCommands + " -e alpha.security.taint " #" --quiet "

    def parseOutput(self, path):
        return "CodeChecker parse --quiet --export html --output " + path +\
            " ./reports"

    def runDBCommandAndRenameOutput(self, command, path, name):
        subprocess.run(command, shell=True, cwd=path,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)

        # Rename compile_commands.json
        subprocess.run("mv compile_commands.json compile_commands" +
                       name + ".json", shell=True, cwd=path)

    def compileDB(self, path, command, name):
        compileDBCommand = "compiledb -n " + command

        # Create compilation database for CSA
        self.runDBCommandAndRenameOutput(compileDBCommand, path, name)

    def runInterceptBuild(self, path, command, name):
        interceptBuild = InterceptBuild.getInterceptBuildCommand(command)

        # Create compilation database for CSA
        self.runDBCommandAndRenameOutput(interceptBuild, path, name)

    def runCodeChecker(self, pathIn, reportPath, checkers, CBextraName):
        enableCheckers = " ".join(["-e " + i for i in checkers])

        subprocess.run(self.codeCheckerCSAAnalysis(CBextraName, reportPath) +
                       enableCheckers,
                       shell=True, cwd=pathIn)

    def convertTo(self, reportPath, extraName):
        outputName = "_report"
        if(self.export == "json"):
            outputName = ".json"

        subprocess.run("CodeChecker parse --export " + self.export +
                       " --output " + "./" + extraName + outputName + " ./" +
                       extraName, shell=True, cwd=reportPath)

    def convertJSON(self, reportPath, extraName):
        self.convertTo(reportPath, extraName)

    def outputInDierectory(self, directory):
        self.parseOutput(directory)
