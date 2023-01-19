Value Filldown AREA (\d+)
Value Filldown ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Filldown NETMASK (\d+\.\d+\.\d+\.\d+)
Value Required DR_IP_Add (\d+\.\d+\.\d+\.\d+)
Value List NEIGHBORING_ROUTER_ID (\d+\.\d+\.\d+\.\d+)

Start
  ^.*Area\s\d+\.\d+\.\d+\.${AREA}
  ^Network -> Continue.Record
  ^Network\s+[*]?${DR_IP_Add}\s+${ADV_ROUTER_ID}
  ^.*mask ${NETMASK} 
  ^.*attached router ${NEIGHBORING_ROUTER_ID}
  ^Network\s+ -> Start

Tag
  ^\s -> Start