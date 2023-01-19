Value Filldown ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Filldown AREA (\d+)
Value Filldown ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required STUB (TransNet)
Value Required DR_IP_Addr (\d+\.\d+\.\d+\.\d+)
Value ROUTER_INTERFACE_IP (\d+\.\d+\.\d+\.\d+)
Value Required METRIC (\d+)

Start
  ^.*with Router ID ${ROUTER_ID}
  ^\s+Area: \d+\.\d+\.\d+\.${AREA}
  ^\s+Type\s*:\s*Router
  ^\s+Adv rtr\s*:\s*${ADV_ROUTER_ID}
  ^.*Link ID\s*:\s*${DR_IP_Addr} 
  ^.*Data\s*:\s*${ROUTER_INTERFACE_IP} 
  ^\s+Link Type\s*:\s*${STUB}
  ^\s+Metric\s*:\s*${METRIC} -> Record

