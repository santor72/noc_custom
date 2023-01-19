Value Filldown ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Filldown AREA (\S+)
Value Filldown ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required STUB (Transit)
Value Required DR_IP_Addr (\d+\.\d+\.\d+\.\d+)
Value ROUTER_INTERFACE_IP (\d+\.\d+\.\d+\.\d+)
Value Required METRIC (\d+)

Start
  ^.*area=${AREA} type=router id=${ROUTER_ID}( originator=${ADV_ROUTER_ID})?
  ^\s+originator=${ADV_ROUTER_ID}
  ^.*${STUB} (id=)?${DR_IP_Addr} (data=)?${ROUTER_INTERFACE_IP} (metric=)?${METRIC} -> Record
  
EOF