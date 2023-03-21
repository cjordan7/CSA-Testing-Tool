
# Install unzip
sudo apt-get install unzip

# Install curl
sudo apt install curl

# Download Juliet Test Suite
curl --url https://samate.nist.gov/SARD/downloads/test-suites/2022-08-11-juliet-c-cplusplus-v1-3-1-with-extra-support.zip --output JulietTestSuite.zip

unzip JulietTestSuite.zip -d workdir/julietTestSuite

rm JulietTestSuite.zip
