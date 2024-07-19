import re

IPV4_PATTERN = r'(?:\d{1,3}\.){3}\d{1,3}'

PLAYER_LOG_PATTERN = r'\S*\[/' + IPV4_PATTERN + r':.{5}\]'

def didPlayerJoin(line) -> bool:
    matches = re.findall(PLAYER_LOG_PATTERN, line)
    if len(matches) == 1:
        return True
    return False

def hideIPIfPlayerJoined(line):
    matches = re.findall(PLAYER_LOG_PATTERN, line)
    if len(matches) == 1:
        match = hideIPAddresses(line)
        return match
    else:
        return line

def hideIPAddresses(text):
    # Define the regex pattern for an IPv4 address
    IPV4_PATTERN = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

    # Find all matches in the text
    matches = re.findall(IPV4_PATTERN, text)
    
    # Function to replace IP addresses with '*'
    def replace_ip(match):
        ip = match.group(0)
        # Check if IP falls within valid range before replacing
        parts = ip.split('.')
        if all(0 <= int(part) <= 255 for part in parts):
            return "***.***.***.***"
        else:
            return ip

    # Replace IPs in the text using the defined function
    replaced_text = re.sub(IPV4_PATTERN, replace_ip, text)

    return replaced_text
