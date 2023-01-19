Value Filldown ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required SUBNET (\d+\.\d+\.\d+\.\d+)
Value Required SUBNET_MASK (\d+\.\d+\.\d+\.\d+)
Value Required METRIC_TYPE (\d+)
Value Required METRIC (\d+)
Value Filldown FORWARDING_IP_ADDR (\d+\.\d+\.\d+\.\d+)

Start  
  ^.*type=as-external id=${SUBNET}(\s+originator=${ADV_ROUTER_ID})?
  ^\s+originator=${ADV_ROUTER_ID}
  ^\s+netmask=${SUBNET_MASK}
  ^\s+forwarding-address=${FORWARDING_IP_ADDR}
  ^\s+metric=${METRIC}
  ^\s+type${METRIC_TYPE} -> Record

