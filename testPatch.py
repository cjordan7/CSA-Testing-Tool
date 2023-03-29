import os


baseDir = os.path.dirname(os.path.realpath(__file__))
dire = os.path.join(baseDir, "workdir/workdir/magma/targets")
dire = os.path.join(dire, "sqlite3", "patches", "bugs")
subfolders = [f.path for f in os.scandir(dire)]

for i in subfolders:
    f = open(i)
    p = f.readlines()
    f.close()
    for line in range(0, len(p)):
        if("MAGMA_LOG" in p[line]):
            p[line] = p[line][:-2] + "//" + i.split("/")[-1] + p[line][-2:]

    f = open(i, "w")
    f.write("".join(p))
    f.close()
