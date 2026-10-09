#######################################################
#                                                     #
#  Encounter Command Logging File                     #
#  Created on Sun Aug 18 21:12:16 2024                #
#                                                     #
#######################################################

#@(#)CDS: First Encounter v08.10-p004_1 (32bit) 11/04/2008 14:34 (Linux 2.6)
#@(#)CDS: NanoRoute v08.10-p008 NR081027-0018/USR58-UB (database version 2.30, 67.1.1) {superthreading v1.11}
#@(#)CDS: CeltIC v08.10-p002_1 (32bit) 10/23/2008 22:04:14 (Linux 2.6.9-67.0.10.ELsmp)
#@(#)CDS: CTE v08.10-p016_1 (32bit) Oct 26 2008 15:11:51 (Linux 2.6.9-67.0.10.ELsmp)
#@(#)CDS: CPE v08.10-p009

setUIVar rda_Input ui_topcell SYS_TOP
setUIVar rda_Input ui_netlist /home/ahesham/Projects/System_pnr/DFT/netlists/SYS_TOP.v
setUIVar rda_Input ui_timelib,min /home/ahesham/Projects/System_pnr/std_cells/libs/scmetro_tsmc_cl013g_rvt_ff_1p32v_m40c.lib
setUIVar rda_Input ui_timelib,max /home/ahesham/Projects/System_pnr/std_cells/libs/scmetro_tsmc_cl013g_rvt_ss_1p08v_125c.lib
setUIVar rda_Input ui_timelib /home/ahesham/Projects/System_pnr/std_cells/libs/scmetro_tsmc_cl013g_rvt_tt_1p2v_25c.lib
setUIVar rda_Input ui_leffile {/home/ahesham/Projects/System_pnr/std_cells/lef/tsmc13fsg_7lm_tech.lef /home/ahesham/Projects/System_pnr/std_cells/lef/tsmc13_m_macros.lef /home/ahesham/Projects/System_pnr/pnr/import/SYS_TOP.lef}
setUIVar rda_Input ui_captbl_file /home/ahesham/Projects/System_pnr/std_cells/captables/tsmc13fsg.capTbl
setUIVar rda_Input ui_timingcon_file /home/ahesham/Projects/System_pnr/DFT/sdc/SYS_TOP.sdc
setUIVar rda_Input ui_pwrnet VDD
setUIVar rda_Input ui_gndnet VSS
commitConfig
create_library_set -name min_library -timing "../std_cells/libs/scmetro_tsmc_cl013g_rvt_ff_1p32v_m40c.lib"
create_library_set -name max_library -timing "../std_cells/libs/scmetro_tsmc_cl013g_rvt_ss_1p08v_125c.lib"
create_library_set -name typ_library -timing "../std_cells/libs/scmetro_tsmc_cl013g_rvt_tt_1p2v_25c.lib"
create_constraint_mode -name func_mode -sdc_files {../DFT/sdc/SYS_TOP_func.sdc}
create_constraint_mode -name scan_mode -sdc_files {../DFT/sdc/SYS_TOP_scan.sdc}
create_constraint_mode -name capture_mode -sdc_files {../DFT/sdc/SYS_TOP_capture.sdc}
create_rc_corner -name RCcorner -cap_table "../std_cells/captables/tsmc13fsg.capTbl"
create_delay_corner -name min_corner -library_set min_library -rc_corner RCcorner
create_delay_corner -name max_corner -library_set max_library -rc_corner RCcorner
create_analysis_view -name setup1_analysis_view -delay_corner max_corner -constraint_mode func_mode
create_analysis_view -name hold1_analysis_view  -delay_corner min_corner -constraint_mode func_mode
create_analysis_view -name setup2_analysis_view -delay_corner max_corner -constraint_mode scan_mode
create_analysis_view -name hold2_analysis_view  -delay_corner min_corner -constraint_mode scan_mode
create_analysis_view -name setup3_analysis_view -delay_corner max_corner -constraint_mode capture_mode
create_analysis_view -name hold3_analysis_view  -delay_corner min_corner -constraint_mode capture_mode
set_analysis_view -setup {setup1_analysis_view setup2_analysis_view setup3_analysis_view} -hold {hold1_analysis_view hold2_analysis_view hold3_analysis_view}
floorPlan -d 240.47 160.47 4.0 4.0 4.0 4.0
addRing -spacing_bottom 0.5 -width_left 1 -width_bottom 1 -width_top 1 -spacing_top 0.5 -layer_bottom METAL5 -center 1 -stacked_via_top_layer METAL7 -width_right 1 -around core -jog_distance 0.205 -offset_bottom 0.205 -layer_top METAL5 -threshold 0.205 -offset_left 0.205 -spacing_right 0.5 -spacing_left 0.5 -offset_right 0.205 -offset_top 0.205 -layer_right METAL6 -nets {VSS VDD } -stacked_via_bottom_layer METAL1 -layer_left METAL6
addStripe -block_ring_top_layer_limit METAL7 -max_same_layer_jog_length 0.8 -padcore_ring_bottom_layer_limit METAL5 -set_to_set_distance 60 -stacked_via_top_layer METAL7 -padcore_ring_top_layer_limit METAL7 -spacing 0.5 -merge_stripes_value 0.205 -layer METAL6 -block_ring_bottom_layer_limit METAL5 -width 1 -nets {VSS VDD } -stacked_via_bottom_layer METAL1
selectWire 5.6000 0.8000 6.6000 159.5900 6 VDD
selectWire 4.1000 2.3000 5.1000 158.0900 6 VSS
deleteSelectedFromFPlan
sroute -connect { blockPin padPin padRing corePin floatingStripe } -layerChangeRange { 1 6 } -blockPinTarget { nearestRingStripe nearestTarget } -padPinPortConnect { allPort oneGeom } -checkAlignedSecondaryPin 1 -blockPin useLef -allowJogging 1 -crossoverViaBottomLayer 1 -allowLayerChange 1 -targetViaTopLayer 7 -crossoverViaTopLayer 7 -targetViaBottomLayer 1 -nets { VSS VDD }
placeDesign -inPlaceOpt -prePlaceOpt
addTieHiLo -cell TIELOM -prefix LTIE
addTieHiLo -cell TIEHIM -prefix HTIE
globalNetConnect VDD -type pgpin -pin VDD -inst *
globalNetConnect VSS -type pgpin -pin VSS -inst *
clockDesign -genSpecOnly Clock.ctstch
clockDesign -specFile Clock.ctstch -outDir clock_report -fixedInstBeforeCTS
clearClockDomains
setClockDomains -all
timeDesign -postCTS -hold -pathReports -slackReports -numPaths 50 -prefix SYS_TOP_postCTS -outDir timingReports
optDesign -postCTS -hold
optDesign -postCTS -hold -incr
optDesign -postCTS -hold -incr
setDrawView fplan
setDrawView place
setDrawView fplan
setDrawView ameba
setDrawView fplan
panPage 0 1
panPage -1 0
panPage 0 1
panPage 1 0
panPage 1 0
panPage 0 -1
panPage 0 -1
panPage -1 0
panPage 0 -1
panPage 0 -1
panPage 0 1
panPage -1 0
panPage 0 1
panPage 0 1
panPage 1 0
panPage 0 -1
panPage 0 -1
panPage 0 -1
panPage 0 1
panPage -1 0
panPage 0 -1
panPage 0 1
panPage 0 1
panPage 0 1
panPage 0 1
panPage 1 0
panPage 0 -1
panPage 1 0
panPage 0 1
panPage 0 -1
panPage 0 -1
panPage -1 0
panPage 1 0
panPage -1 0
panPage 0 1
panPage 1 0
panPage 0 -1
panPage -1 0
panPage -1 0
panPage -1 0
panPage 1 0
setDrawView fplan
setDrawView ameba
zoomBox -11.232 148.853 155.956 85.023
panPage 0 -1
panPage 0 -1
panPage 0 1
panPage 1 0
panPage -1 0
zoomBox -4.154 78.380 89.681 45.242
zoomBox -1.325 75.925 87.815 51.007
panPage 0 -1
panPage 0 -1
panPage 0 1
panPage 0 1
panPage 0 1
panPage 0 1
panPage 0 -1
panPage 1 0
panPage 1 0
panPage 0 -1
panPage 0 -1
panPage 0 1
zoomBox 245.289 72.072 202.234 39.823
selectObject Module U7
deselectAll
windowSelect -23.753 103.926 78.868 60.472
deselectAll
zoomBox 279.444 122.585 117.412 44.023
zoomBox 248.526 99.858 119.156 82.157
panPage -1 0
panPage 1 0
selectObject Module U8
panPage -1 0
panPage 1 0
panPage -1 0
panPage 1 0
panCenter 256.119 96.898
zoomBox 95.317 106.872 150.309 73.238
zoomBox 113.341 100.323 139.490 78.805
setDrawView fplan
setDrawView fplan
deselectAll
selectInst U8/U0_TLATNCAX12M
setDrawView fplan
setDrawView fplan
setDrawView ameba
setDrawView place
deselectAll
selectWire 119.4150 90.7150 145.8550 90.9150 3 {REGFILE_RdData[5]}
deselectAll
selectInst U8/U0_TLATNCAX12M
deselectAll
zoomBox 134.952 94.740 115.599 88.889
verifyGeometry -noMinArea
zoomBox -43.884 152.045 266.187 2.533
