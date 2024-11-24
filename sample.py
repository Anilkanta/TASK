import re

# Example input string with multiple formats (static, direct, local, connected)
input_string = """
Codes: L local, C connected, S static, R RIP, M mobile, B BGP
      D EIGRP, EX EIGRP external, O OSPF, N1 OSPF NSSA external type 1, N2
      OSPF NSSA external type 2, IA OSPF inter area
      E1 OSPF external type 1, E2 OSPF external type 2, m OMP
      n NAT, Ni NAT inside, No NAT outside, Nd NAT DIA
      i IS-IS, su IS-IS summary, L1 IS-IS level-1, L2 IS-IS level-2
      ia IS-IS inter area, candidate default, U per-user static route
      H NHRP, G NHRP registered, g NHRP registration summary
      O ODR, P periodic downloaded static   
      route, 1 LISP
      a replicated route, % next hop override, p overrides from PFR
      & replicated local route overrides by connected

Gateway of last resort is 10.176.28.1 to network 0.0.0.0

S*    0.0.0.0/0 [1/0] via 10.176.28.1
        10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
C       10.176.28.0/23 is directly connected, GigabitEthernet0/0/0
L       10.176.28.31/32 is directly connected, GigabitEthernet0/0/0
"""

# Define the regex patterns to match the input data
route_pattern = r"^\s*(?P<RouteType>[A-Za-z\*]+)\s+(?P<Destination>\S+/\d+)\s+\[(?P<Distance>\d+)\s*/\s*(?P<Metric>\d+)\](?:\s+via\s+(?P<NextHop>\S+))?"
# Pattern for directly connected and local routes (C and L lines) with Vlan or Interface info
via_pattern = r"^\s*(?P<RouteType>[A-Za-z])\s+(?P<Destination>\S+/\d+)\s+is\s+(?P<ConnectionType>directly connected),\s+(?:Vlan(?P<Vlan>\S+)|(?P<Interface>\S+))"

# Compile the regex patterns for efficiency
route_re = re.compile(route_pattern)
via_re = re.compile(via_pattern)

# Initialize an empty list to store the results
parsed_data = []

# Track the current routing information
current_route = {}

# Parse the input string to capture route and via data
for line in input_string.splitlines():
    route_match = route_re.match(line)
    if route_match:
        # Parse the destination and mask
        destination = route_match.group('Destination')
        # Exclude the mask part (before the '/'), keep only the IP address
        ip_address, mask = destination.split('/')  # Split IP address and mask

        # Store the route information with the correct IP address (excluding the mask)
        current_route = route_match.groupdict()
        current_route['Destination'] = ip_address  # Update with only the IP address (without the mask)
        current_route['Mask'] = mask  # Add the mask separately

        # If 'NextHop' exists, store it
        if current_route.get('NextHop'):
            current_route['NextHop'] = current_route['NextHop']
        else:
            current_route['NextHop'] = None
        
        # Add the static route to the parsed data list
        parsed_data.append(current_route.copy())  # Add static route immediately
    
    via_match = via_re.match(line)
    if via_match:
        # If we find a via entry, add it to the current route
        current_route.update(via_match.groupdict())

        # For directly connected and local routes (C and L), keep the Mask and add it to the Destination
        if current_route['RouteType'] in ['C', 'L']:
            current_route['Destination'] = via_match.group('Destination')  # Keep the full Destination (IP/Mask format)
        
        # Handle case where destination contains IP/Mask
        res = current_route['Destination'].split('/')
        if len(res) > 1:
            current_route['Destination'] = res[0]
            current_route['Mask'] = res[1]

        # Add the current route to the parsed data list
        parsed_data.append(current_route.copy())  # Copy to avoid reference issues

        # Reset current_route for the next entry
        current_route = {}

# Ensure we add the last route if it exists
if current_route:
    parsed_data.append(current_route)

# Print the results as structured data
for entry in parsed_data:
    print(entry)
