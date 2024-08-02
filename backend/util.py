import re

IPV4_PATTERN = r'(?:\d{1,3}\.){3}\d{1,3}'

PLAYER_LOG_PATTERN = r'(\S*)\[/' + IPV4_PATTERN + r':.{5}\]'
PLAYER_JOIN_PATTERN = r'(\S*) joined the game'
PLAYER_LEAVE_PATTERN = r'(\S*) left the game'

def didPlayerJoin(line) -> bool:
    line = getTextAfterTags(line)
    match = re.search(PLAYER_JOIN_PATTERN, line)
    if match:
        return match.group(1)
    return None

def didPlayerLeave(line):
    line = getTextAfterTags(line)
    match = re.search(PLAYER_LEAVE_PATTERN, line)
    if match:
        return match.group(1)
    return None

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

def getConsoleTags(text):
    in_tag = False
    current_tag = ""
    tags = []
    for c in text:
        if c == "[":
            in_tag = True
        elif c == "]":
            in_tag = False
            tags.append(current_tag)
            current_tag = ""
        elif in_tag:
            current_tag += c
        elif c != " ":
            break
    return tags

def getTextAfterTags(text):
    in_tag = False
    x = 0
    for i, c in enumerate(text):
        if c == "[":
            in_tag = True
        elif c == "]":
            in_tag = False
        elif in_tag:
            pass
        elif c == ":":
            x = i
            break
        elif c == " ":
            pass
        else:
            return text
    return text[x+2:]
