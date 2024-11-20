import re

# Example input string with multiple formats (static, direct, via next-hop)
input_string = """
0.0.0.0/0, ubest/mbest: 1/0
*via 10.168.2.1, [1/0], 3w3d, static
10.168.2.0/23, ubest/mbest: 1/0, attached
*via 10.168.2.4, Vlan1000, [1/0], 3w3d, direct
10.168.2.4/32, ubest/mbest: 1/0, attached
*via 10.168.2.4, Vlan1000, [1/0], 3w3d, local
"""

# Define the regex patterns to match the input data
route_pattern = r"(?P<Destination>\S+/\d+),\s+ubest/mbest:\s+(?P<Distance>\d+)/(?P<Metric>\d+)(?:, attached)?"
via_pattern = r"\*via\s+(?P<NextHop>\S+),\s*(?:Vlan(?P<Vlan>\S+),\s*)?\[(?P<DistanceMetric>\d+/\d+)\],\s*(?P<AdditionalInfo>[\w, ]+)"

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
        ip_address = destination.split('/')[0]

        # Store the route information with the correct IP address (excluding the mask)
        current_route = route_match.groupdict()
        current_route['Destination'] = ip_address  # Update with only the IP address (without the mask)

    via_match = via_re.match(line)
    if via_match:
        # If we find a via entry, add it to the current route
        current_route.update(via_match.groupdict())

        # Add the current route to the parsed data list
        parsed_data.append(current_route)

        # Reset current_route for the next entry
        current_route = {}

# Ensure we add the last route if it exists
if current_route:
    parsed_data.append(current_route)

# Print the results as structured data
for entry in parsed_data:
    print(entry)
