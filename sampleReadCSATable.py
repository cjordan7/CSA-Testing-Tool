

def getCWECheckerMapping():
    csaTableMapped = dict()
    csaTable = open("data/csaCheckers.txt", "r")
    csaTableLines = csaTable.readlines()

    for line in csaTableLines:
        l = line.strip().split(":")
        if(len(l) > 1):
            l0 = l[0].strip()
            l1 = l[1].strip()

            cwes = list(map(str.strip, l0.split(",")))
            for i in cwes:
                csaTableMapped[i] = l1

        if(len(l) > 2):
            # TODO: Something better
            print("Problem")

    return csaTableMapped
