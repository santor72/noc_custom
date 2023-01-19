Value Filldown ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Filldown AREA (\d+\.\d+\.\d+\.\d+|\d+)
Value Filldown ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required STUB (P-2-P)
Value Required NEIGHBORING_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required METRIC (\d+)

Start
  ^.*with Router ID ${ROUTER_ID}
  ^\s+Area: \d+\.\d+\.\d+\.${AREA}
  ^\s+Type\s*:\s*Router
  ^\s+Adv rtr\s*:\s*${ADV_ROUTER_ID}
  ^.*Link ID\s*:\s*${NEIGHBORING_ROUTER_ID} 
  ^\s+Link Type\s*:\s*${STUB}
  ^\s+Metric\s*:\s*${METRIC} -> Record

