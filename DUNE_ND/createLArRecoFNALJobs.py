# Creates a shell script that can be run to submit Fermigrid LArReco jobs,
# using submitLArRecoFNALJob.py for each individual job

import os
import ROOT
import sys

def run(label, nSamples, nEvtJob):

    # Grid jobs can't access the "/dune/data/users" areas, so use pnfs scratch
    user = os.getenv('USER')
    dataDir = '/pnfs/dune/scratch/users/{0}/EDepSimFiles/{1}'.format(user, label)
    print('Data directory = {0}'.format(dataDir))

    # Data file label, e.g. LArEDepSim_numu_cc_qe
    dataName = 'LArEDepSim_{0}'.format(label)

    for iS in range(1, nSamples+1):

        sampleName = '{0}_{1}'.format(dataName, iS)
        print('sampleName = {0}'.format(sampleName))

        # Find the number of generated events in the sample data file
        dataFileName = '{0}/{1}.root'.format(dataDir, sampleName)
        rootFile = ROOT.TFile.Open(dataFileName, 'read')
        N = 0
        if rootFile is not None:
            events = rootFile.Get('EDepSimEvents')
            if events is not None:
                N = events.GetEntries()

        print('Number of events in {0} = {1}'.format(dataFileName, N))
        # Set the end event remainder for the final job
        remainder = N%nEvtJob
        print('Event remainder = {0}'.format(remainder))

        if N == 0:
            print('Zero events. Skipping')
            continue

        # Number of jobs required to process sample events
        nJobs = int((N/nEvtJob))
        if N%nEvtJob != 0:
            nJobs += 1
        print('Number of jobs = {0} for nEvtJobs = {1}'.format(nJobs, nEvtJob))

        runFileName = 'runLArRecoJobs_{0}_sample{1}.sh'.format(label, iS)
        runFile = open(runFileName, 'w')

        for iJ in range(nJobs):
            startEvt = nEvtJob*iJ
            endEvt = nEvtJob*(iJ + 1)
            if iJ == nJobs-1 and remainder > 0:
                endEvt = remainder + startEvt
            jobInt = iJ + 1
            # Submit required job
            line = 'python submitLArRecoFNALJob.py {0} sample{1} job{2} {3} {4} ' \
                   '{5}\n'.format(label, iS, jobInt, dataFileName, startEvt, endEvt)
            runFile.write(line)
            # Wait a few seconds before submitting the next one
            runFile.write('sleep 2\n')

        runFile.close()
        print('Writing job submission script {0}'.format(runFileName))

    
if __name__ == '__main__':

    # Main sample name label, e.g. numu_all or numu_cc_qe
    label = 'numu_all'
    # Number of event samples (edep-sim rooTracker files)
    nSamples = 10
    # Number of reco events per job
    nEvtJob = 100

    nArg = len(os.sys.argv)
    if nArg > 1:
        label = os.sys.argv[1]
    if nArg > 2:
        nSamples = int(os.sys.argv[2])
    if nArg > 3:
        nEvtJob = int(os.sys.argv[3])

    run(label, nSamples, nEvtJob)
