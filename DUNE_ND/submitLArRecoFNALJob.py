# Script to submit a LArReco job to Fermigrid. Used by createLArRecoFNALJobs.py

import os
import platform
import random
import sys

class parameters(object):

    def __init__(self, label, sample, jobName, inFileName,
                 startEvt, endEvt, runtime = '8h', memory = '2000MB'):

        # Physics process label, e.g numu_cc_qe
        self.label = label
        # Sample label
        self.sample = sample
        # Job label
        self.jobName = jobName
        # Pandora input (simulation) file
        self.inFileName = inFileName
        # Start and end event numbers
        self.startEvt = startEvt
        self.endEvt = endEvt
        # Number of events to process
        self.NEvts = self.endEvt - self.startEvt

        # Job runtime
        self.runtime = runtime
        # Job memory requirement (default = 2GB)
        self.memory = memory
        
        # Test area directory
        self.myTestArea = os.getenv('MY_TEST_AREA')

        # LArReco executable settings
        self.recoExe = 'LArReco/bin/PandoraInterface'
        # Xml reco settings file
        self.recoXml = 'LArReco/settings/PandoraSettings_EDepReco_NoGUI.xml'
        # Hit projection method (LArTPC or 3D)
        self.projection = 'LArTPC'
        # LArReco option: Full, AllHitsCR, AllHitsNu, CRRemHitsSliceCR,
        # CRRemHitsSliceNu, AllHitsSliceCR, AllHitsSliceNu
        self.recoOpt = 'AllHitsNu'
        
        # Scratch area for batch jobs:
        self.user = os.getenv('USER')
        self.pandoraName = 'Pandora'
        self.baseJob = '/pnfs/dune/scratch/users/{0}/{1}'.format(self.user, self.pandoraName)
        # Job scratch directory location
        self.jobDir = '{0}/{1}/{1}_{2}_{3}'.format(self.baseJob, self.label, self.sample, self.jobName)
        
        # Name of Pandora install tar ball
        self.pandoraTarName = '{0}Install.tar.gz'.format(self.pandoraName)
        self.pandoraTarFile = '{0}/{1}'.format(self.baseJob, self.pandoraTarName)
        # Required installed packages for LArReco executable (shared libraries & xml files etc.)
        self.pandoraPkgs = ['PandoraSDK', 'LArContent', 'LArMachineLearningData',
                            'PandoraMonitoring', 'edep-sim', 'LArReco']
        
        # Batch machine temporary directory location
        self.batchDir = '$_CONDOR_SCRATCH_DIR'
        
        # Linux operating system version. Following command is deprecated in python 3:
        #self.OSVer ="SL%i"%int(float(platform.linux_distribution()[1]))
        self.OSVer = 'SL7'
        
        
def run(pars):

    print('Base job directory = {0}; label = {1}, sample = {2}'.format(pars.baseJob, pars.label, pars.sample))
    print('jobName = {0}, inFileName = {1}, events = {2} to {3}'.format(pars.jobName, pars.inFileName,
                                                                        pars.startEvt, pars.endEvt))

    print('OSVer = {0}'.format(pars.OSVer))
    
    # Run directory for the job
    print('JobDir = {0}'.format(pars.jobDir))
    if not os.path.exists(pars.jobDir):
        print('Creating {0}'.format(pars.jobDir))
        os.makedirs(pars.jobDir)
        os.chmod(pars.jobDir, 0o0755)
        
    # Create tar file containing Pandora release and copy it to scratch area
    if not os.path.exists(pars.pandoraTarFile):
        print('Creating {0}'.format(pars.pandoraTarFile))
        # List of required install packages
        pgkList = ' '.join([str(pkg) for pkg in pars.pandoraPkgs])
        tarCmd = 'tar -czf {0} -C {1} {2}'.format(pars.pandoraTarFile, pars.myTestArea, pgkList)
        print('tarCmd = {0}'.format(tarCmd))
        os.system(tarCmd)
    else:
        # Tar file has already been created
        print('Using tarball {0}'.format(pars.pandoraTarFile))

    # Now create the script containing the job commands
    jobScript = createJobScript(pars)

    # Finally submit the job; for tests, use --timeout=Xm to stop after X minutes.
    # Majority of jobs should finish within 8 hours and use a max memory of 2GB
    logFile = '{0}/submitJob.log'.format(pars.jobDir)
    jobCmd = 'jobsub_submit.py -N 1 --resource-provides=usage_model=OPPORTUNISTIC ' \
             '--expected-lifetime={0} --OS={1} --group=dune --memory={2} -L {3} ' \
             'file://{4}'.format(pars.runtime, pars.OSVer, pars.memory, logFile, jobScript)
    print('jobCmd = {0}'.format(jobCmd))

    os.system(jobCmd)
    print('DONE\n')


def createJobScript(pars):

    jobScript = '{0}/{1}_{2}.sh'.format(pars.jobDir, pars.sample, pars.jobName)
    print('Creating job script {0}'.format(jobScript))
    if os.path.exists(jobScript):
        os.remove(jobScript)
    jobFile = open(jobScript, 'w')

    # Setup job environment
    jobFile.write('#!/bin/bash\n')
    jobFile.write('date\n')
    jobFile.write('source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh\n')
    jobFile.write('setup ifdhc\n')
    
    # For libxxhash.so
    jobFile.write('setup dune_oslibs v1_0_0\n')
    # Compiler
    jobFile.write('setup gcc v8_2_0\n')
    # ROOT
    jobFile.write('setup root v6_18_04d -q e19:prof\n')
    # Geant4 (for edep-sim)
    jobFile.write('setup geant4 v4_10_6_p01c -q e19:prof\n')
    
    # Limit ifdh copying attempts to avoid stalled jobs
    jobFile.write('export IFDH_CP_MAXRETRIES=0\n')

    # Print working directory
    jobFile.write('echo Batch dir is {0}\n'.format(pars.batchDir))
    
    # Copy Pandora release tarball from pnfs scratch area to batch machine local area
    batchTarFile = '{0}/{1}'.format(pars.batchDir, pars.pandoraTarName)
    jobFile.write('ifdh cp {0} {1}\n'.format(pars.pandoraTarFile, batchTarFile))
    jobFile.write('tar -xzf {0} -C {1}\n\n'.format(batchTarFile, pars.batchDir))

    # Specify edep-sim header file location for LArReco executable (for ROOT-based shared-libraries)
    edepSimHDir = '$_CONDOR_SCRATCH_DIR/edep-sim/install/include/EDepSim'
    jobFile.write('export ROOT_INCLUDE_PATH={0}:$ROOT_INCLUDE_PATH\n'.format(edepSimHDir))
    
    # LD_LIBRARY_PATH for shared libraries needed for LArReco executable
    libPath1 = '$_CONDOR_SCRATCH_DIR/PandoraSDK/lib'
    libPath2 = '$_CONDOR_SCRATCH_DIR/LArContent/lib'
    libPath3 = '$_CONDOR_SCRATCH_DIR/PandoraMonitoring/lib'
    libPath4 = '$_CONDOR_SCRATCH_DIR/edep-sim/install/lib'
    jobFile.write('export LD_LIBRARY_PATH={0}:{1}:{2}:{3}:$LD_LIBRARY_PATH\n'.format(libPath1, libPath2,
                                                                                     libPath3, libPath4))
    # Location of Pandora algorithm parameter files
    FWSPath1 = '$_CONDOR_SCRATCH_DIR/LArMachineLearningData'
    FWSPath2 = '$_CONDOR_SCRATCH_DIR/LArReco/settings'
    jobFile.write('export FW_SEARCH_PATH={0}:{1}\n'.format(FWSPath1, FWSPath2))

    # Copy edep-sim rooTracker inputFile to local batch dir
    jobFile.write('ifdh cp -D {0} $_CONDOR_SCRATCH_DIR\n'.format(pars.inFileName))

    # Print directory contents to check presence of directories and inputFile
    jobFile.write('ls -lrta {0}\n\n'.format(pars.batchDir))

    # LArReco run command; "-N" prints event numbers. Use "-h" for help options.
    # Can also add extra arguments: "-c X" for MIP calib cut = X (default = 0.3) and
    # "-m X" to set max number of merged voxels per event (default = -1, all voxels)
    fileName = pars.inFileName.split('/')[-1]
    runCmd = './{0} -i {1} -j {2} -N -s {3} -n {4} -r {5} ' \
             '-e {6}\n'.format(pars.recoExe, pars.recoXml, pars.projection,
                               pars.startEvt, pars.NEvts, pars.recoOpt, fileName)
    
    jobFile.write('cd {0}\n'.format(pars.batchDir))
    jobFile.write(runCmd)

    # List all output to make sure everything was generated OK
    jobFile.write('ls -lrt {0}\n\n'.format(pars.batchDir))

    # Copy Validation.root file from batch node to pnfs user scratch area.
    # Note that the file will not be copied if it already exists!
    jobFile.write('ifdh cp -D Validation.root {0}\n'.format(pars.jobDir))
    
    # End the job
    jobFile.write('echo Copied Validation.root to {0}\n'.format(pars.jobDir))
    jobFile.write('date\n')
    jobFile.write('exit 0\n')
    
    jobFile.close()

    # Make job script executable
    os.chmod(jobScript, 0o0644)

    return jobScript
    
    
if __name__ == '__main__':

    # Physics label
    label = 'numu_all'
    # Sample name
    sample = 'sample1'
    # Job name
    jobName = 'job1'
    # Sample ROOT simulation file
    inFileName = 'numu_all.root'
    # Job number
    jobInt = 1
    # Start and end event range
    startEvt = 0
    endEvt = 100
    # Expected job runtime 8hrs
    runtime = '8h'
    # Maximum job memory
    memory = '2000MB'
    
    nArg = len(os.sys.argv)
    if nArg > 1:
        label = os.sys.argv[1]
    if nArg > 2:
        sample = os.sys.argv[2]
    if nArg > 3:
        jobName = os.sys.argv[3]
    if nArg > 4:
        inFileName = os.sys.argv[4]
    if nArg > 5:
        startEvt = int(os.sys.argv[5])
    if nArg > 6:
        endEvt = int(os.sys.argv[6])
    # Expected job runtime: e.g. "8h" for 8 hours
    if nArg > 7:
        runtime = os.sys.argv[7]
    # Max job memory: default = "2000MB" for 2GB
    if nArg > 8:
        memory = os.sys.argv[8]

    pars = parameters(label, sample, jobName, inFileName,
                      startEvt, endEvt, runtime, memory)
    run(pars)
