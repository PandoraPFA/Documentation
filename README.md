# Pandora build instructions / suggestions

As with any multi-library application, there are a number of
different ways in which one can choose to structure and build
your Pandora application.

A few detailed examples are presented below, working with
either the CMake files or the simple Makefiles provided alongside
the Pandora source code.

1. Using CMake and the PandoraPFA metadata package
2. Using CMake for each individual package
3. Using simple Makefiles and the PandoraPFA metadata package
4. Using simple Makefiles for each individual package

This document describes how to build the core Pandora packages
(PandoraSDK and PandoraMonitoring), the library of LAr TPC algorithms
and tools (LArContent) and a simple client application for developing
algorithms in the Pandora LAr TPC standalone environment (LArReco).

If it is at all unclear how to adapt these instructions to your
circumstances, please get in touch: john.marshall AT warwick.ac.uk

## Build notes
1. These instructions have been tested with:
-Scientific Linux CERN SLC release 6.9, gcc 4.9.3, ROOT 6.06.08
-CentOS Linux release 7.5.1804, gcc 6.4.0, ROOT 6.12.04
-macOS Sierra, 10.12.6, Apple LLVM version 8.1.0 (clang-802.0.42), ROOT 6.08.02

2. Please note that some configurations of the LArReco application now require
access to files maintained in the PandoraPFA/LArMachineLearningData repository.
Users requiring these files should clone this repository, checkout the tag 
matching the PANDORA_LAR_CONTENT_VERSION below then add the directory path to
the colon-separated list stored in the FW_SEARCH_PATH environment variable.

3. PandoraMonitoring functionality is optional, but its
usage is assumed throughout the following examples. It is assumed 
that the user has already built ROOT, including the EVE libraries.
The environment variable ROOTSYS is used below and may need to be 
specified/replaced carefully on some systems.

4. c++11 is now mandatory for Pandora packages. Using a version of ROOT built
when demanding a more recent standard may force you to demand a newer
standard when building PandoraMonitoring and LC/LArReco, despite the fact that
these packages themselves only require c++11 support.

5. Using CMake, the user may find that the identified C and C++
compilers revert to the system default compilers. If the intention
is to pick-up alternative compilers, either specify CC and CXX
environment variables or provide the additional CMake arguments:
-DCMAKE_C_COMPILER=/your/cc/path and -DCMAKE_CXX_COMPILER=/your/c++/path

## Recommended library/application versions
Use 'git tag' to check the list of available tags.
Current recommended versions are as defined below:
```
export PANDORA_PFA_VERSION=v03-13-00
export PANDORA_SDK_VERSION=v03-03-02
export PANDORA_MONITORING_VERSION=v03-04-01
export PANDORA_LAR_CONTENT_VERSION=v03_15_00
export PANDORA_LC_CONTENT_VERSION=v03-01-03
export PANDORA_EXAMPLE_CONTENT_VERSION=v03-00-02
export PANDORA_LAR_RECO_VERSION=v03-14-05
export PANDORA_LC_RECO_VERSION=v03-01-03

export MY_TEST_AREA=/path/to/your/test/area
```

## 1. Using CMake and the PandoraPFA metadata package
```
cd $MY_TEST_AREA
git clone https://github.com/PandoraPFA/PandoraPFA.git
cd PandoraPFA
git checkout $PANDORA_PFA_VERSION # select your chosen tag, defining all daughter library tags
mkdir build
cd build
cmake -DCMAKE_MODULE_PATH=$ROOTSYS/etc/cmake -DPANDORA_MONITORING=ON -DPANDORA_EXAMPLE_CONTENT=OFF -DPANDORA_LAR_CONTENT=ON -DPANDORA_LC_CONTENT=OFF ..
make -j4 install

cd $MY_TEST_AREA
git clone https://github.com/PandoraPFA/LArReco.git
cd LArReco
git checkout $PANDORA_LAR_RECO_VERSION
mkdir build
cd build
cmake -DCMAKE_MODULE_PATH="$MY_TEST_AREA/PandoraPFA/cmakemodules;$ROOTSYS/etc/cmake" -DPANDORA_MONITORING=ON -DPandoraSDK_DIR=$MY_TEST_AREA/PandoraPFA/ -DPandoraMonitoring_DIR=$MY_TEST_AREA/PandoraPFA/ -DLArContent_DIR=$MY_TEST_AREA/PandoraPFA/ ..
make -j4 install

$MY_TEST_AREA/LArReco/bin/PandoraInterface -h

./bin/PandoraInterface
    -r RecoOption          (required) [Full, AllHitsCR, AllHitsNu, CRRemHitsSliceCR, CRRemHitsSliceNu, AllHitsSliceCR, AllHitsSliceNu]
    -i Settings            (required) [algorithm description: xml]
    -e EventFileList       (optional) [colon-separated list of files: xml/pndr]
    -g GeometryFile        (optional) [detector geometry description: xml/pndr]
    -n NEventsToProcess    (optional) [no. of events to process]
    -s NEventsToSkip       (optional) [no. of events to skip in first file]
    -p                     (optional) [print status]
    -N                     (optional) [print event numbers]
```
Note: In this configuration, you will need to read in events via e.g. the EventReading
algorithm, configured in the specified settings file.

## 2. Using CMake for each individual package
```
cd $MY_TEST_AREA
git clone https://github.com/PandoraPFA/PandoraPFA.git # still need this for the CMake modules
cd PandoraPFA
git checkout $PANDORA_PFA_VERSION

cd $MY_TEST_AREA
git clone https://github.com/PandoraPFA/PandoraSDK.git
cd PandoraSDK
git checkout $PANDORA_SDK_VERSION # now need to select all package tags manually
mkdir build
cd build
cmake -DCMAKE_MODULE_PATH=$MY_TEST_AREA/PandoraPFA/cmakemodules ..
make -j4 install

cd $MY_TEST_AREA
git clone https://github.com/PandoraPFA/PandoraMonitoring.git
cd PandoraMonitoring
git checkout $PANDORA_MONITORING_VERSION
mkdir build
cd build
cmake -DCMAKE_MODULE_PATH="$MY_TEST_AREA/PandoraPFA/cmakemodules;$ROOTSYS/etc/cmake" -DPandoraSDK_DIR=$MY_TEST_AREA/PandoraSDK ..
make -j4 install

cd $MY_TEST_AREA
wget http://bitbucket.org/eigen/eigen/get/3.3.3.tar.gz
tar -xf 3.3.3.tar.gz
mv eigen-eigen-67e894c6cd8f Eigen3
cd Eigen3
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=$MY_TEST_AREA/Eigen3/ ..
make -j4 install

cd $MY_TEST_AREA
git clone https://github.com/PandoraPFA/LArContent.git
cd LArContent
git checkout $PANDORA_LAR_CONTENT_VERSION
mkdir build
cd build
cmake -DCMAKE_MODULE_PATH="$MY_TEST_AREA/PandoraPFA/cmakemodules;$ROOTSYS/etc/cmake" -DPANDORA_MONITORING=ON -DPandoraSDK_DIR=$MY_TEST_AREA/PandoraSDK -DPandoraMonitoring_DIR=$MY_TEST_AREA/PandoraMonitoring -DEigen3_DIR=$MY_TEST_AREA/Eigen3/share/eigen3/cmake/ ..
make -j4 install

cd $MY_TEST_AREA
git clone https://github.com/PandoraPFA/LArReco.git
cd LArReco
git checkout $PANDORA_LAR_RECO_VERSION
mkdir build
cd build
cmake -DCMAKE_MODULE_PATH="$MY_TEST_AREA/PandoraPFA/cmakemodules;$ROOTSYS/etc/cmake" -DPANDORA_MONITORING=ON -DPandoraSDK_DIR=$MY_TEST_AREA/PandoraSDK/ -DPandoraMonitoring_DIR=$MY_TEST_AREA/PandoraMonitoring/ -DLArContent_DIR=$MY_TEST_AREA/LArContent/ ..
make -j4 install

$MY_TEST_AREA/LArReco/bin/PandoraInterface -h # as for example 1.
```
## 3. Using simple Makefiles and the PandoraPFA metadata package
```
cd $MY_TEST_AREA
git clone https://github.com/PandoraPFA/PandoraPFA.git
cd PandoraPFA
git checkout $PANDORA_PFA_VERSION

cd $MY_TEST_AREA/PandoraPFA
git clone https://github.com/PandoraPFA/PandoraSDK.git PandoraSDK
cd PandoraSDK
git checkout $PANDORA_SDK_VERSION # without cmake, need to select all package tags manually

cd $MY_TEST_AREA/PandoraPFA
git clone https://github.com/PandoraPFA/PandoraMonitoring.git PandoraMonitoring
cd PandoraMonitoring
git checkout $PANDORA_MONITORING_VERSION

cd $MY_TEST_AREA/PandoraPFA
wget http://bitbucket.org/eigen/eigen/get/3.3.3.tar.gz
tar -xf 3.3.3.tar.gz
mv eigen-eigen-67e894c6cd8f Eigen3

cd $MY_TEST_AREA/PandoraPFA
git clone https://github.com/PandoraPFA/LArContent.git LArContent
cd LArContent
git checkout $PANDORA_LAR_CONTENT_VERSION

cd $MY_TEST_AREA/PandoraPFA
mkdir include lib
make -j4 MONITORING=1 PANDORA_DIR=$MY_TEST_AREA/PandoraPFA
make install MONITORING=1 PANDORA_DIR=$MY_TEST_AREA/PandoraPFA INCLUDE_TARGET=$MY_TEST_AREA/PandoraPFA/include # optional

cd $MY_TEST_AREA
git clone https://github.com/PandoraPFA/LArReco.git
cd LArReco
git checkout $PANDORA_LAR_RECO_VERSION
mkdir bin
make -j4 MONITORING=1 PROJECT_DIR=$MY_TEST_AREA/LArReco PANDORA_DIR=$MY_TEST_AREA/PandoraPFA

export LD_LIBRARY_PATH=$MY_TEST_AREA/PandoraPFA/lib:$LD_LIBRARY_PATH

$MY_TEST_AREA/LArReco/bin/PandoraInterface -h # as for example 1.
```
## 4. Using simple Makefiles for each individual package
```
cd $MY_TEST_AREA
mkdir lib
export LD_LIBRARY_PATH=$MY_TEST_AREA/lib:$LD_LIBRARY_PATH

git clone https://github.com/PandoraPFA/PandoraSDK.git PandoraSDK
cd PandoraSDK
git checkout $PANDORA_SDK_VERSION # without cmake, need to select all package tags manually
mkdir lib
make -j4 PROJECT_DIR=$MY_TEST_AREA/PandoraSDK
make install PROJECT_DIR=$MY_TEST_AREA/PandoraSDK LIB_TARGET=$MY_TEST_AREA/lib

cd $MY_TEST_AREA
git clone https://github.com/PandoraPFA/PandoraMonitoring.git
cd PandoraMonitoring
git checkout $PANDORA_MONITORING_VERSION
mkdir lib
make -j4 MONITORING=1 PROJECT_DIR=$MY_TEST_AREA/PandoraMonitoring PANDORA_DIR=$MY_TEST_AREA
make install MONITORING=1 PROJECT_DIR=$MY_TEST_AREA/PandoraMonitoring PANDORA_DIR=$MY_TEST_AREA LIB_TARGET=$MY_TEST_AREA/lib

cd $MY_TEST_AREA
wget http://bitbucket.org/eigen/eigen/get/3.3.3.tar.gz
tar -xf 3.3.3.tar.gz
mv eigen-eigen-67e894c6cd8f Eigen3

cd $MY_TEST_AREA
git clone https://github.com/PandoraPFA/LArContent.git
cd LArContent
git checkout $PANDORA_LAR_CONTENT_VERSION
mkdir lib
make -j4 MONITORING=1 PROJECT_DIR=$MY_TEST_AREA/LArContent PANDORA_DIR=$MY_TEST_AREA EIGEN_INC=$MY_TEST_AREA/Eigen3/
make install MONITORING=1 PROJECT_DIR=$MY_TEST_AREA/LArContent PANDORA_DIR=$MY_TEST_AREA LIB_TARGET=$MY_TEST_AREA/lib

cd $MY_TEST_AREA
git clone https://github.com/PandoraPFA/LArReco.git
cd LArReco
git checkout $PANDORA_LAR_RECO_VERSION
mkdir bin
make -j4 MONITORING=1 PROJECT_DIR=$MY_TEST_AREA/LArReco PANDORA_DIR=$MY_TEST_AREA

$MY_TEST_AREA/LArReco/bin/PandoraInterface -h # as for example 1.
```
