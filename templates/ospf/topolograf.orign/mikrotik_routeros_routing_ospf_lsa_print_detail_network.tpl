Value AREA (\S+)
Value ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required NETMASK (\d+\.\d+\.\d+\.\d+|\d+)
Value Filldown DR_IP_Add (\d+\.\d+\.\d+\.\d+)
Value List NEIGHBORING_ROUTER_ID (\d+\.\d+\.\d+\.\d+)

Start
  ^\s+instance= -> Continue.Record
  ^.*area=${AREA} type=network id=${DR_IP_Add}(\s+originator=${ADV_ROUTER_ID})?
  ^\s+originator=${ADV_ROUTER_ID}
  ^\s+netmask=${NETMASK}
  ^\s+routerId=${NEIGHBORING_ROUTER_ID}

