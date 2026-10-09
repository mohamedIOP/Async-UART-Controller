
################################ Variables ####################################
set route_0_optimze_1 1

########### Global/Detialed Routing ############
set max_m_layer 6

if {$route_0_optimze_1 == 0} {
setNanoRouteMode -quiet -routeTopRoutingLayer $max_m_layer
routeDesign -globalDetail -viaOpt -wireOpt

} else {

#  Engineering Change Order (ECO) is the process of introducing a minimal localized change to a gate-level netlist or physical layout to fix a bug, improve performance
refinePlace -preserveRouting
setNanoRouteMode -routeWithEco true
routeDesign -globalDetail -viaOpt -wireOpt

}

