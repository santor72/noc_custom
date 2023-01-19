Value Filldown ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Filldown AREA (\d+\.\d+\.\d+\.\d+|\d+)
Value Filldown ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required STUB (StubNet)
Value Required SUBNET (\d+\.\d+\.\d+\.\d+)
Value Required SUBNET_MASK (\d+\.\d+\.\d+\.\d+)
Value Required METRIC (\d+)

Start
  ^.*with Router ID ${ROUTER_ID}
  ^\s+Area: \d+\.\d+\.\d+\.${AREA}
  ^\s+Type\s*:\s*Router
  ^\s+Adv rtr\s*:\s*${ADV_ROUTER_ID}
  ^.*Link ID\s*:\s*${SUBNET} 
  ^.*Data\s*:\s*${SUBNET_MASK} 
  ^\s+Link Type\s*:\s*${STUB}
  ^\s+Metric\s*:\s*${METRIC} -> Record

