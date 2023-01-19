Value Filldown ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Filldown AREA (\S+)
Value Filldown ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required STUB (Point-To-Point)
Value Required NEIGHBORING_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required METRIC (\d+)

Start
  ^.*area=${AREA} type=router id=${ROUTER_ID}( originator=${ADV_ROUTER_ID})?
  ^\s+originator=${ADV_ROUTER_ID}
  ^\s+${STUB} (id=)?${NEIGHBORING_ROUTER_ID} (data=)?\d+\.\d+\.\d+\.\d+ (metric=)?${METRIC} -> Record

