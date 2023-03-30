# docker build -t csatool:csatool . --progress plain

# docker run -v $(pwd)/workdir2:/home/CSA-Testing-Tool/workdir csatool:csatool /bin/bash PREINSTALL_JTS.sh

# docker run -v $(pwd)/reports:/home/CSA-Testing-Tool/reports csatool:csatool /bin/bash createDocker.sh


# docker run csatool:csatool /bin/bash creagsgdteDocker.sh

python3 parseMagma.py
