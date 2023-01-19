Value Filldown ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Filldown PROCESS_ID (\d+)
Value Filldown ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Filldown SUBNET (\d+\.\d+\.\d+\.\d+)
Value Filldown SUBNET_MASK (\d+\.\d+\.\d+\.\d+)
Value Filldown METRIC_TYPE (\d+)
Value Filldown METRIC (\d+)
Value Filldown FORWARDING_IP_ADDR (\d+\.\d+\.\d+\.\d+)


Start
  ^.+\(${ROUTER_ID}\) \(.* ${PROCESS_ID}\)
  ^.*Extern\s+${SUBNET}\s+${ADV_ROUTER_ID}
  ^\s+mask\s+${SUBNET_MASK}
  ^\s+Type:\s+${METRIC_TYPE},\s+Metric: ${METRIC},\s+Fwd addr:\s+${FORWARDING_IP_ADDR} -> Record
  ^.*LS -> Start

EOF