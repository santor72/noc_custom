Value Filldown ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Filldown AREA (\d+)
Value Filldown ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required STUB (Stub)
Value SUBNET (\d+\.\d+\.\d+\.\d+)
Value SUBNET_MASK (\d+\.\d+\.\d+\.\d+)
Value METRIC (\d+)

Start
  ^.*Area\s\d+\.\d+\.\d+\.${AREA}
  ^Router\s+[*]?${ROUTER_ID}\s+${ADV_ROUTER_ID}
  ^.*id\s+${SUBNET},\s+data\s+${SUBNET_MASK},\s+Type\s+${STUB}
  ^.*Default metric:\s+${METRIC} -> Record
  ^.*id -> Start

