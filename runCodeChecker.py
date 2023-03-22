import subprocess


class InterceptBuild():
    @staticmethod
    def getInterceptBuildCommand(command):
        return "intercept-build --override-compiler " + command + " CC=intercept-cc CXX=intercept-c++"


class RunCodeChecker():
    def __init__(self):
        self.codeCheckerLog = "CodeChecker log -o compile_commands.json -b "

        self.interceptBuild = "intercept-build --override-compiler make CC=intercept-cc CXX=intercept-c++"

    def codeCheckerCSAAnalysis(self, goodOrBad, outputPath):
        # Use -d to disable checker class
        return "CodeChecker analyze compile_commands"+ \
            goodOrBad + ".json " +\
            "--ctu -d core -d alpha -d cplusplus -d " +\
            "nullability -d optin -d deadcode -d " +\
            "security -d unix -d valist  -d security.FloatLoopCounter -d " +\
            "security.insecureAPI.UncheckedReturn " +\
            "-d security.insecureAPI.getpw -d " +\
            "security.insecureAPI.gets -d security.insecureAPI.mkstemp -d " +\
            "security.insecureAPI.mktemp -d security.insecureAPI.rand -d " +\
            "security.insecureAPI.vfork " +\
            "--analyzer-config clangsa:unroll-loops=true " +\
            "-o " + outputPath + " --verbose debug "

    def parseOutput(self, path):
        return "CodeChecker parse --export html --output " + path +\
            " ./reports"

    def runDBCommandAndRenameJSON(self, command, path, name):
        # Make clean just in case
        subprocess.run("make clean", shell=True, cwd=path,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)

        subprocess.run(command, shell=True, cwd=path)

        subprocess.run("make clean", shell=True, cwd=path,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)

        # Rename compile_commands.json
        subprocess.run("mv compile_commands.json compile_commands" +
                       name + ".json", shell=True, cwd=path)

    def compileDB(self, path, command, name):
        compileDBCommand = "compiledb -n " + command

        # Create compilation database for CSA
        self.runDBCommandAndRenameJSON(compileDBCommand, path, name)

    def runInterceptBuild(self, path, command, name):
        # TODO: Parse result for potential errors
        interceptBuild = InterceptBuild.getInterceptBuildCommand(command)

        # Create compilation database for CSA
        self.runDBCommandAndRenameJSON(interceptBuild, path, name)

    def runCodeChecker(self, pathIn, reportPath, checkers, goodOrBad):
        enableCheckers = " ".join(["-e " + i for i in checkers])

        subprocess.run(self.codeCheckerCSAAnalysis(goodOrBad, reportPath) +
                       enableCheckers,
                       shell=True, cwd=pathIn)

    def outputInDierectory(self, directory):
        self.parseOutput(directory)
