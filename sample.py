# Let's create a textfsm template for the user, as it appears they want a file to be provided.

template_content = """
Value ROUTE_PROTOCOL (\S+)      # Protocol like OSPF, RIP, etc.
Value NETWORK     (\S+)         # Network address (e.g., 192.168.1.0)
Value MASK        (\S+)         # Subnet mask (e.g., 255.255.255.0)
Value NEXT_HOP    (\S+)         # Next-hop address (e.g., 192.168.1.1)
Value INTERFACE   (\S+)         # Interface name (e.g., GigabitEthernet0/1)
Value DISTANCE    (\d+)         # Administrative distance (e.g., 110)

Start
  ^Routing entry for ${NETWORK}.*               -> Record
  ^  Routing Protocol is ${ROUTE_PROTOCOL}       -> Record
  ^  Next hop address is ${NEXT_HOP} via ${INTERFACE},.* -> Record
  ^   via ${INTERFACE}.*${MASK}.*               -> Record
  ^${NETWORK}.*Distance ${DISTANCE}.*           -> Record

EOF
"""
output = []
# Save the template content to a .template file
template_path = '/mnt/data/show_ip_route.template'

# Write the template content to the file
with open(template_path) as template_file:
    template = textfsm.TextFSM(template_file)


fsm_results = template.ParseText(output)
for result in fsm_results:
    d ={}
    route_protocol, network, mask, next_hop, interface, distance = result
    output.extend([
        d['route_protocol'] =route_protocol
        d['network'] = network
        d['mask'] = mask
        d['distance'] = distance
        d['next_hop'] = next_hop
        d['interface'] = interface
        ]
    )
