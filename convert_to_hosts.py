import requests
import re

def is_valid_domain(domain):
    # Define a regex pattern for validating domain names
    pattern = re.compile(r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,})+$')
    return bool(pattern.match(domain))

def fix_domain(domain):
    # Basic domain fixing logic
    # Remove unwanted characters and ensure the domain follows standard rules
    # Replace multiple consecutive hyphens or periods with a single one
    domain = re.sub(r'[-.]+', '.', domain)
    domain = domain.strip('-')  # Remove leading/trailing hyphens

    # If it still doesn't match, return None
    return domain if is_valid_domain(domain) else None

def convert_to_hosts(urls, hosts_file):
    unique_domains = set()  # Use a set to store unique domains

    for url in urls:
        # Fetch the content of the ad-blocking filter file from the URL
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
        except requests.RequestException as e:
            print(f"Failed to retrieve the ad filter list from {url}: {e}")
            continue

        # Read the content of the filter list
        lines = response.text.splitlines()

        # Check if the content is already in hosts format
        if any(line.startswith('0.0.0.0 ') for line in lines):
            # Add entries directly from hosts formatted content
            for line in lines:
                line = line.strip()
                if line.startswith('0.0.0.0 '):
                    domain = line.split(' ')[1]
                    if is_valid_domain(domain):
                        unique_domains.add(domain)
                    else:
                        fixed_domain = fix_domain(domain)
                        if fixed_domain:
                            unique_domains.add(fixed_domain)
            continue  # Move to the next URL if it's already in hosts format

        # Process entries not in hosts format
        for line in lines:
            line = line.strip()
            
            # Skip comment lines, whitelist rules (starting with @@), and advanced filters ($)
            if line.startswith('!') or line.startswith('@@') or "$" in line:
                continue
            
            # Handle domain blocking rules (||domain.com^)
            if line.startswith('||'):
                # Extract the domain and clean up unwanted characters
                domain = re.split(r'[/$^]', line.split('||')[1])[0]
                fixed_domain = fix_domain(domain)
                if fixed_domain:
                    unique_domains.add(fixed_domain)
            
            # Handle basic URL blocking (http:// or https://)
            elif line.startswith('http://') or line.startswith('https://'):
                domain = re.split(r'[/$^]', line.split('//')[1])[0]
                fixed_domain = fix_domain(domain)
                if fixed_domain:
                    unique_domains.add(fixed_domain)

            # Skip element hiding rules (e.g., ##.ads)
            elif '##' in line or '#@#' in line:
                continue

    # Write unique domains to the hosts file
    with open(hosts_file, 'w') as outfile:
        for domain in unique_domains:
            outfile.write(f"0.0.0.0 {domain}\n")

    print(f"Hosts file has been created at {hosts_file}")

# List of URLs to convert to hosts format
urls = [
    'https://raw.githubusercontent.com/hoshsadiq/adblock-nocoin-list/refs/heads/master/hosts.txt',
    'https://easylist-downloads.adblockplus.org/easylistspanish.txt',
    'https://easylist-downloads.adblockplus.org/abp-filters-anti-cv.txt',
    'https://filters.adavoid.org/ultimate-privacy-filter.txt',
    'https://filters.adavoid.org/ultimate-security-filter.txt'
]

# Call the function with the list of URLs and output file path
convert_to_hosts(urls, 'hosts.txt')
