# docker build -t csatool:csatool . --progress plain

# docker run -v $(pwd)/workdir2:/home/CSA-Testing-Tool/workdir csatool:csatool /bin/bash PREINSTALL_JTS.sh

# docker run csatool:csatool /bin/bash createDocker.sh

python3 parseJulietTestSuite.py -b 111378
