#!/usr/bin/perl

use Cwd;

#$lowMass = 0.7; # 0.8; #is a shared lower cutoff for all 3 datas.
#$highMass = 2.5; #2.0; #is the upper cutoff of the thrown data and 3ish is the upper cutoff for the reco/data
#$nBins = 45; #30; #45; because it is kind of small and (2-0.7)/26 = 0.05 which is nice and round

# for the 5tbins, always have 0.8 as the lower bound
$lowMass = 0.7;#0.82;#0.7; # 0.8 for 5 tbins
$highMass = 2.5;#1.98;#2.5; #2.0,2.4,2.6,2.8,2.8
$nBins = 45;#29;#45; #30,40,45,50,50

$fitName = "EtaPi_fit";

# put a limit on the number of data events to process
# gen MC and acc MC smaples are not limited
$maxEvts = 1E9;

$workingDir=getcwd();
print "\n\ncurrent working dir: $workingDir";
print "\n===================================\n";

# these files must exist in the workin directory.  If you don't know how
# to generate them or don't have them, see the documentation in gen_3pi
# the Simulation area of the repository

#$baseGenDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/shared_gen_files/baseFiles/";
#$baseAccDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/3tbins/baseFiles/";
#$baseBkgDir="/d/grid17/ln16/myDSelector/amptools/zMalte_kmatrix/";
#$baseDatDir="/d/grid17/ln16/myDSelector/amptools/zMalte_kmatrix/";
#$baseGenFileName="amptools_flat_gen_2018_8_";
#$baseAccFileName="amptools_flat_2018_8_t0110_e8288_sig_";
#$baseDatFileName="amptools_malte_kmatrix_2018_8_t0110_e8288_tot_";
#$baseBkgFileName="amptools_malte_kmatrix_2018_8_t0110_e8288_sb_";

#$baseGenDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/";
#$baseAccDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/dataDriven_backgrounds/";
#$baseBkgDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/dataDriven_backgrounds/";
#$baseDatDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/dataDriven_backgrounds/";
#$baseDatFileName="DAT_FILE";
#$baseBkgFileName="BKGND_FILE";
#$baseAccFileName="FLAT_SIG_FILE";
#$baseGenFileName="amptools_flat_gen_phase1_";

#$baseGenDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/shared_gen_files/";
#$baseAccDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/5tbins/";
#$baseBkgDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/5tbins/";
#$baseDatDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/5tbins/";
#$baseGenFileName="amptools_flat_gen_phase1_";
#$baseAccFileName="amptools_flat_phase1_t0102_e8288_sig_";
#$baseBkgFileName="amptools_data_phase1_t0102_e8288_sb_";
#$baseDatFileName="amptools_data_phase1_t0102_e8288_tot_";
#
$baseGenDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/shared_gen_files/";
$baseAccDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/t0105_zach_dnp/";#_vh/";
$baseBkgDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/t0105_zach_dnp/";#_vh/";
$baseDatDir="/d/grid17/ln16/myDSelector/amptools/zPhase1_t0103061_e79828890/t0105_zach_dnp/";#_vh/";
$baseGenFileName="amptools_flat_gen_phase1_";
$baseAccFileName="amptools_flat_phase1_t0105_e8288_sig_";
$baseBkgFileName="amptools_data_phase1_t0105_e8288_sb_";
$baseDatFileName="amptools_data_phase1_t0105_e8288_tot_";

@polTags=qw(000 045 090 135 AMO);
print "DATAFILES:\n";
foreach $polTag (@polTags){
    print "$baseDatDir$baseDatFileName$polTag\.root\n";
}
print "------------------\n";

print "BKGNDFILES:\n";
foreach $polTag (@polTags){
    print "$baseBkgDir$baseBkgFileName$polTag.root\n";
}
print "------------------\n";

print "ACCFILES:\n";
foreach $polTag (@polTags){
    print "$baseAccDir$baseAccFileName$polTag.root\n";
}
print "------------------\n";

print "GENFILES:\n";
foreach $polTag (@polTags){
    print "$baseGenDir$baseGenFileName$polTag.root\n";
}
print "------------------\n";


# this file sould be used for partially polarized or unpolarized beam fits

$cfgTempl = "$workingDir/zlm_etapi_bothReflect_bothM_loop.cfg";
#$cfgTempl = "$workingDir/zlm_etapi_bothReflect_bothM.cfg";
#$cfgTempl = "$workingDir/zlm_etapi_bothReflect_bothM_loop_sb0.cfg";

### things below here probably don't need to be modified

# this is where the goodies for the fit will end up
$fitDir = "$workingDir/$fitName/";
print "Output fitDir: $fitDir";
print "\n";
#mkdir $fitDir unless -d $fitDir;
`./ramdisk.sh`;

chdir $fitDir;

print "Changing into $fitDir\n";

# use the split_mass command line tool to divide up the
foreach $polTag (@polTags){
    $fileTag="$baseDatFileName$polTag";
    $dataFile="$fileTag.root";
    print "splitting datatag: $dataFile\n";
    system( "split_mass $baseDatDir$dataFile $fileTag $lowMass $highMass $nBins $maxEvts -T kin:kin" );

    $fileTag="$baseBkgFileName$polTag";
    $dataFile="$fileTag.root";
    print "splitting bkgtag: $dataFile\n";
    system( "split_mass $baseBkgDir$dataFile $fileTag $lowMass $highMass $nBins $maxEvts -T kin:kin" );

    $fileTag="$baseAccFileName$polTag";
    $dataFile="$fileTag.root";
    print "splitting acctag: $dataFile\n";
    system( "split_mass $baseAccDir$dataFile $fileTag $lowMass $highMass $nBins $maxEvts -T kin:kin" );

    $fileTag="$baseGenFileName$polTag";
    $dataFile="$fileTag.root";
    print "splitting gentag: $dataFile\n";
    system( "split_mass $baseGenDir$dataFile $fileTag $lowMass $highMass $nBins $maxEvts -T kin:kin" );
}

# make directories to perform the fits in
for( $i = 0; $i < $nBins; ++$i ){

  mkdir "bin_$i" unless -d "bin_$i";
  
  system( "mv *\_$i.root bin_$i" );

  chdir "bin_$i";

#we are essentially copying fit_etapi_moments.cfg and substituting some variables. CFGOUT is going to be a config file in all of our bins. CFGIN is fit_etapi_moments.cfg. Note how fit_etapi_moments.cfg has these place holders defined (DATAFILE,ACCMCFILE,GENMCFILE ... ). They will get replaced here to fit the bin directory. 
  open( CFGOUT, ">bin_$i-full.cfg" );
  open( CFGIN, $cfgTempl ); 

  while( <CFGIN> ){
    foreach $polTag (@polTags){
        s/DATAFILE_$polTag/$baseDatFileName$polTag\_$i.root/;
        s/BKGNDFILE_$polTag/$baseBkgFileName$polTag\_$i.root/;
        s/ACCMCFILE_$polTag/$baseAccFileName$polTag\_$i.root/;
        s/GENMCFILE_$polTag/$baseGenFileName$polTag\_$i.root/;
        s/NIFILE_$polTag/bin_$i\_$polTag.ni/;
    }

    s/FITNAME/bin_$i/;

    print CFGOUT $_;
  }

  close CFGOUT;
  close CFGIN;
  
  system( "touch param_init.cfg" );

  chdir $fitDir;
}

