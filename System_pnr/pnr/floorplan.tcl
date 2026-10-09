

################################ Variables ####################################

set NUM_SCAN_CHAINS 4
set load_fp 0
set top_module SYS_TOP

########### Define Aspect Ratio (Length/Width) of Digital Macro  ############

if {$load_fp == 0} {

	if {$NUM_SCAN_CHAINS == 4} {
              floorPlan -d 240.47 160.47 6.0 6.0 6.0 6.0
	} elseif {$NUM_SCAN_CHAINS == 5} {
              floorPlan -d 240.47 200.47 6.0 6.0 6.0 6.0
	} elseif {$NUM_SCAN_CHAINS == 6} {
              floorPlan -d 240.47 220.47 6.0 6.0 6.0 6.0
        }


} else {

loadFPlan ./$top_module.fp

}


