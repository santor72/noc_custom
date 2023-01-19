Value Filldown ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Filldown ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required SUBNET (\d+\.\d+\.\d+\.\d+)
Value Required SUBNET_MASK (\d+\.\d+\.\d+\.\d+)
Value Required METRIC_TYPE (\d+)
Value Required METRIC (\d+)
Value Filldown FORWARDING_IP_ADDR (\d+\.\d+\.\d+\.\d+)

Start
  ^.*with Router ID ${ROUTER_ID}
  ^\s+Type\s*:\s*External
  ^\s+Ls id\s*:\s*${SUBNET}
  ^\s+Adv rtr\s*:\s*${ADV_ROUTER_ID} 
  ^\s+Net mask\s*:\s*${SUBNET_MASK}
  ^\s+TOS 0\s*Metric:\s*${METRIC} 
  ^\s+E type\s*:\s*${METRIC_TYPE}
  ^\s+Forwarding Address\s*:\s*${FORWARDING_IP_ADDR} -> Record

