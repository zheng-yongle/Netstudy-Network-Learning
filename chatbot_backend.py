    @staticmethod
    def parse_subnet_request(query):
        """Parse natural language subnet request"""
        # Pattern: "with X.X.X.X, give me the addressing plan for Y subnets and Z hosts per subnet"
        ip_pattern = r'\d+\.\d+\.\d+\.\d+'
        subnets_pattern = r'(\d+)\s+subnets?'  # Changed: added 's?' to match both subnet and subnets
        hosts_pattern = r'(\d+)\s+hosts?'      # Changed: added 's?' to match both host and hosts
        
        ip_match = re.search(ip_pattern, query)
        subnets_match = re.search(subnets_pattern, query, re.IGNORECASE)
        hosts_match = re.search(hosts_pattern, query, re.IGNORECASE)
        
        if ip_match and subnets_match and hosts_match:
            return {
                'network': ip_match.group(),
                'num_subnets': int(subnets_match.group(1)),
                'hosts_per_subnet': int(hosts_match.group(1))
            }
        return None
