Value Filldown ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Filldown AREA (\S+)
Value Filldown ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required STUB (Stub)
Value Required SUBNET (\d+\.\d+\.\d+\.\d+)
Value Required SUBNET_MASK (\d+\.\d+\.\d+\.\d+)
Value Required METRIC (\d+)

Start
  ^.*area=${AREA} type=router id=${ROUTER_ID}( originator=${ADV_ROUTER_ID})?
  ^\s+originator=${ADV_ROUTER_ID}
  ^.*${STUB} (id=)?${SUBNET} (data=)?${SUBNET_MASK} (metric=)?${METRIC} -> Record
  
EOF