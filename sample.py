import re

# Example input string with multiple formats (static, direct, local, connected)
input_string = """
S* 0.0.0.0/0 [1/0] via 10.88.2.1 
      10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
C 10.88.2.0/23 is directly connected, Vlan1000
L 10.88.2.220/32 is directly connected, Vlan1000
"""

# Define the regex patterns to match the input data, adjusted for new formats

# Pattern for static or via routes (S* lines) with a distance/metric and a next-hop
route_pattern = r"^\s*(?P<RouteType>[CSL\*]+)\s+(?P<Destination>\S+/\d+)\s+\[(?P<Distance>\d+)\s*/\s*(?P<Metric>\d+)\](?:\s+via\s+(?P<NextHop>\S+))?"

# Pattern for directly connected and local routes (C and L lines) with Vlan info
via_pattern = r"^\s*(?P<RouteType>[CSL])\s+(?P<Destination>\S+/\d+)\s+is\s+(?P<ConnectionType>directly connected),\s+Vlan(?P<Vlan>\S+)"

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
        ip_address, mask = destination.split('/')  # Split IP address and mask

        # Store the route information with the correct IP address (excluding the mask in the destination field)
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
        # If we find a via entry (directly connected or local route), update the route information
        current_route.update(via_match.groupdict())

        # For directly connected and local routes (C and L), keep the Mask and add it to the Destination
        if current_route['RouteType'] in ['C', 'L']:
            current_route['Destination'] = via_match.group('Destination')  # Keep the full Destination (IP/Mask format)
            # No need to remove Mask for C and L routes; it's already part of the Destination
        res = current_route['Destination'].split('/')
        if len(res)>1:
            current_route['Destination']=res[0]
            current_route['Mask']=res[1]
        # Add the current route to the parsed data list
        parsed_data.append(current_route.copy())  # Copy the current_route to avoid reference issues

        # Reset current_route for the next entry
        current_route = {}

# Ensure we add the last route if it exists (important for cases where we end with a via route)
if current_route:
    parsed_data.append(current_route)

# Print the results as structured data
for entry in parsed_data:
    print(entry)
