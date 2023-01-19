Value Filldown AREA (\d+\.\d+\.\d+\.\d+|\d+)
Value Filldown NETMASK (\d+\.\d+\.\d+\.\d+)
Value Filldown ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required DR_IP_Add (\d+\.\d+\.\d+\.\d+)
Value List NEIGHBORING_ROUTER_ID (\d+\.\d+\.\d+\.\d+)

Start
  ^\s+Area:\s*${AREA}
  ^\s+Type\s*: -> Continue.Record
  ^\s+Type\s*:\s*Network
  ^\s+Ls id\s*:\s*${DR_IP_Add}
  ^\s+Adv rtr\s*:\s*${ADV_ROUTER_ID}
  ^\s*Net mask\s*:\s*${NETMASK} 
  ^.*Attached Router\s*${NEIGHBORING_ROUTER_ID}

