# TimingEfficiencyRadiographyUtil

Project based on: https://github.com/jjhollar/PPSRun3Utils

### Step 1. prepare the environment:
``` bash
cmsrel CMSSW_15_0_8
```
``` bash
cd CMSSW_15_0_8/src
```
``` bash
cmsenv
```

### Step 2. clone the repo:

Either if you don't want to commit any changes:
``` bash
git clone https://github.com/wisniewskij/TimingEfficiencyRadiographyUtil.git
```
or instead if you want to change something:
``` bash
git clone git@github.com:wisniewskij/TimingEfficiencyRadiographyUtil.git
```

### Step 3. compile the project:

``` bash
scram b
```

``` bash
cd FWLiteTimingEfficiencyRadiography/FWLiteTimingEfficiencyRadiography/bin
```

### Step 4. gather the filepaths of the rootfiles as csv string:
``` bash
find /eos/cms/store/express/Run2025C/StreamALCAPPSExpress/ALCARECO/PPSCalMaxTracks-Express-v1/000/392/959/00000 -type f -print0 | xargs -0 realpath | paste -sd, > InputFiles.txt
```

### Step 5. running the binary:
``` bash
../../../../bin/el9_amd64_gcc12/FWLiteTimingEfficiencyRadiography inputPathsCSV="$(cat InputFiles.txt)" minLS=45 maxLS=1034 outputFile=timingHistograms_Run392959.root pickedBunchesCSV="$(cat leftmost_bx_25ns_2460b_2448_2089_2227_144bpi_20inj.txt)"
```

(The leftmost_bx_25ns_2460b_2448_2089_2227_144bpi_20inj.txt is a file with comma-separated numbers of runs that we care about)



In addition to the aforementioned parameters, the following options can be passed at the command line when running the FWLiteTimingEfficiencyRadiography binary:

minimumToT=[float] This imposes a minimum ToT on the rechits used to fill the efficiency and ToT plots. By default no cut is applied. In order to properly interpret the average ToT plots, a cut of 0 should be applied. minLS=[int] The first LumiSection to process maxLS=[int] The last LumiSection to process outputFile=[string] The output file name can be changed from the default value of "timingHistograms.root" mode=[integer] By default the program uses the collection names from the PPS AlCaReco (mode 1). By setting mode=2, the collection names from the standard PromptReco/AOD will be used instead.

A plotting macro PlotTimingEfficiencies.C gives an example of drawing the output histograms of efficiency, ToT, and radiographies. To use it with the above example, open a ROOT session and do:
``` bash
root
[0] .L PlotTimingEfficiencies.C
[1] PlotTimingEfficiencies("timingHistograms_Run392959.root")
```
For further informations on the source code visit https://github.com/jjhollar/PPSRun3Utils/blob/main/PPSRun3Utils/README_DiamondRadiographiesEfficienices.md
