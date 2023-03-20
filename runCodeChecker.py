import subprocess


class InterceptBuild():
    @staticmethod
    def getInterceptBuildCommand(command):
        return "intercept-build --override-compiler " + command + " CC=intercept-cc CXX=intercept-c++"


class RunCodeChecker():
    def __init__(self):
        self.codeCheckerLog = "CodeChecker log -o compile_commands.json -b "

        # Use -d to disable checker class
        self.codeCheckerCSAAnalysis = """CodeChecker analyze compile_commands.json
        --ctu -d core -d alpha -d cplusplus -d nullability -d optin -d deadcode -d
        security -d unix -d valist  -d security.FloatLoopCounter -d
        security.insecureAPI.UncheckedReturn -d security.insecureAPI.getpw -d
        security.insecureAPI.gets -d security.insecureAPI.mkstemp -d
        security.insecureAPI.mktemp -d security.insecureAPI.rand -d
        security.insecureAPI.vfork """

        self.interceptBuild = "intercept-build --override-compiler make CC=intercept-cc CXX=intercept-c++"

    def parseOutput(self, path):
        return "CodeChecker parse --export html --output " + path + " ./reports"

    def runInterceptBuild(self, path, command):
        #result = subprocess.run(self.codeCheckerLog + runCommand, shell=True)

        # TODO: Parse result for potential errors
        #if("debug" in result):
        interceptBuild = InterceptBuild.getInterceptBuildCommand(command)

        # Make clean just in case
        subprocess.run("make clean", shell=True, cwd=path)

        # Create compilation database for CSA
        subprocess.run(interceptBuild, shell=True, cwd=path)

        print(result)

    def runCodeChecker(self, checkers):
        enableCheckers = " ".join(["-e " + i for i in checkers].join(" "))

        subprocess.run(self.codeCheckerCSAAnalysis + enableCheckers, shell=True)

    def outputInDierectory(self, directory):
        self.parseOutput(directory)
