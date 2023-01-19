Value Filldown ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Filldown AREA (\d+)
Value Filldown ADV_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value Required STUB (PointToPoint)
Value NEIGHBORING_ROUTER_ID (\d+\.\d+\.\d+\.\d+)
Value ROUTER_INTERFACE_IP (\d+\.\d+\.\d+\.\d+)
Value METRIC (\d+)

Start
  ^.*Area\s\d+\.\d+\.\d+\.${AREA}
  ^Router\s+[*]?${ROUTER_ID}\s+${ADV_ROUTER_ID}
  ^.*id\s+${NEIGHBORING_ROUTER_ID},\s+data\s+${ROUTER_INTERFACE_IP},\s+Type\s+${STUB}
  ^.*Default metric:\s+${METRIC} -> Record
  ^.*id -> Start

Tag
  ^.*LS Type: Router Links -> Next.Clearall
  ^\s -> Start

EOF