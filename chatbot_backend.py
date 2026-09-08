"""
Network Learning Chatbot Backend
Designed to help students learn networking and computer maintenance concepts
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import json
import re
import ipaddress
import math

app = Flask(__name__)
CORS(app)

# ==================== SUBNETTING CALCULATOR ====================

class SubnettingCalculator:
    """Calculates subnet information for given network and requirements"""
    
    @staticmethod
    def parse_subnet_request(query):
        """Parse natural language subnet request"""
        # Pattern: "with X.X.X.X, give me the addressing plan for Y subnets and Z hosts per subnet"
        ip_pattern = r'\d+\.\d+\.\d+\.\d+'
        subnets_pattern = r'(\d+)\s+subnet'
        hosts_pattern = r'(\d+)\s+host'
        
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
    
    @staticmethod
    def calculate_addressing_plan(network_str, num_subnets, hosts_per_subnet):
        """Calculate complete addressing plan for subnets"""
        try:
            # Parse the network address
            network = ipaddress.IPv4Network(network_str, strict=False)
            
            # Calculate bits needed for hosts
            host_bits_needed = math.ceil(math.log2(hosts_per_subnet + 2))  # +2 for network and broadcast
            
            # Calculate bits needed for subnets
            subnet_bits_needed = math.ceil(math.log2(num_subnets))
            
            # Calculate new prefix length
            original_prefix = network.prefixlen
            new_prefix = original_prefix + subnet_bits_needed
            
            if new_prefix > 32 - host_bits_needed:
                return {
                    'error': f"Cannot create {num_subnets} subnets with {hosts_per_subnet} hosts each in {network_str}"
                }
            
            # Generate subnets
            subnets = list(network.subnets(new_prefix=new_prefix))
            
            if len(subnets) < num_subnets:
                subnets = subnets[:num_subnets]
            else:
                subnets = subnets[:num_subnets]
            
            # Build addressing plan
            addressing_plan = []
            for idx, subnet in enumerate(subnets):
                subnet_info = {
                    'subnet_number': idx + 1,
                    'network_address': str(subnet.network_address),
                    'subnet_mask': str(subnet.netmask),
                    'cidr_notation': str(subnet),
                    'broadcast_address': str(subnet.broadcast_address),
                    'first_usable_ip': str(list(subnet.hosts())[0]) if len(list(subnet.hosts())) > 0 else "N/A",
                    'last_usable_ip': str(list(subnet.hosts())[-1]) if len(list(subnet.hosts())) > 0 else "N/A",
                    'total_usable_hosts': len(list(subnet.hosts()))
                }
                addressing_plan.append(subnet_info)
            
            return {
                'success': True,
                'original_network': str(network),
                'calculation_summary': {
                    'host_bits_needed': host_bits_needed,
                    'subnet_bits_needed': subnet_bits_needed,
                    'original_prefix': original_prefix,
                    'new_prefix': new_prefix,
                    'total_subnets_available': len(subnets)
                },
                'addressing_plan': addressing_plan
            }
        
        except Exception as e:
            return {
                'error': f"Error calculating subnets: {str(e)}"
            }

# ==================== KNOWLEDGE BASE ====================
# Comprehensive networking and computer maintenance knowledge base
KNOWLEDGE_BASE = {
    "networking_fundamentals": {
        "topics": ["OSI model", "TCP/IP", "protocols", "network layers"],
        "content": {
            "osi_model": {
                "description": "The OSI (Open Systems Interconnection) model has 7 layers that describe how network communication works",
                "layers": {
                    "Layer 1": "Physical Layer - Cables, signals, hardware (hubs, repeaters)",
                    "Layer 2": "Data Link Layer - MAC addresses, switches, frames (IEEE 802.3)",
                    "Layer 3": "Network Layer - IP addresses, routers, packets, routing",
                    "Layer 4": "Transport Layer - TCP/UDP, ports, reliability",
                    "Layer 5": "Session Layer - Session management, synchronization",
                    "Layer 6": "Presentation Layer - Encryption, compression, formatting",
                    "Layer 7": "Application Layer - HTTP, FTP, SMTP, DNS, SSH"
                },
                "study_tip": "Remember: Please Do Not Throw Sausage Pizza Away!"
            },
            "tcp_udp": {
                "TCP": "Connection-oriented, reliable, ordered delivery, slower, used for email/web",
                "UDP": "Connectionless, fast, unreliable, no ordering guarantee, used for streaming/gaming",
                "study_tip": "Use TCP when reliability matters, UDP when speed matters"
            }
        }
    },
    
    "subnetting": {
        "topics": ["CIDR notation", "subnet mask", "IP addressing", "host calculation"],
        "content": {
            "basics": "Subnetting divides large networks into smaller, manageable subnets to reduce traffic and improve security",
            "example": {
                "network": "192.168.1.0/24",
                "explanation": "/24 means 24 bits for network, 8 bits for hosts. Can support 256 addresses (0-255), 254 usable (excluding network and broadcast)"
            },
            "common_masks": {
                "/24": "255.255.255.0 - 256 addresses (254 usable)",
                "/25": "255.255.255.128 - 128 addresses (126 usable)",
                "/26": "255.255.255.192 - 64 addresses (62 usable)",
                "/27": "255.255.255.224 - 32 addresses (30 usable)",
                "/28": "255.255.255.240 - 16 addresses (14 usable)",
                "/29": "255.255.255.248 - 8 addresses (6 usable)",
                "/30": "255.255.255.252 - 4 addresses (2 usable) - Perfect for router links!"
            },
            "calculation_steps": [
                "Identify the network address and CIDR notation",
                "Calculate host bits = 32 - CIDR",
                "Number of hosts = 2^(host bits)",
                "Usable hosts = Total hosts - 2 (network and broadcast)"
            ],
            "study_tip": "Practice with different CIDR notations. The /30 is commonly used for WAN links!"
        }
    },
    
    "network_devices": {
        "topics": ["switch", "router", "hub", "modem", "firewall"],
        "content": {
            "switch": {
                "layer": "Layer 2 (Data Link)",
                "function": "Forwards data frames based on MAC addresses",
                "key_feature": "Learning bridge - builds MAC address table",
                "advantage": "Reduces collision domain, improves bandwidth efficiency",
                "vs_hub": "Switch is intelligent, Hub just repeats"
            },
            "router": {
                "layer": "Layer 3 (Network)",
                "function": "Routes packets between different networks using IP addresses",
                "key_feature": "Uses routing tables to determine best path",
                "ports": "WAN (wide area) and LAN (local area) ports",
                "important": "Default gateway for network devices"
            },
            "firewall": {
                "function": "Filters traffic based on rules, blocks unauthorized access",
                "types": ["Hardware firewall (network level)", "Software firewall (host level)"],
                "stateful_inspection": "Remembers connection states and allows related return traffic"
            },
            "modem": {
                "full_name": "Modulator-Demodulator",
                "function": "Converts ISP signal (analog) to digital data for your network",
                "common_types": ["Cable modem (DOCSIS)", "DSL modem", "Fiber modem"]
            },
            "study_tip": "Switch = Layer 2 (MAC), Router = Layer 3 (IP). This is crucial!"
        }
    },
    
    "bios_uefi": {
        "topics": ["BIOS", "UEFI", "CMOS", "firmware", "boot"],
        "content": {
            "bios_basics": {
                "full_name": "Basic Input/Output System",
                "function": "Initializes hardware before OS loads",
                "boot_process": ["Power On Self Test (POST)", "Load bootloader from MBR", "Pass control to OS"]
            },
            "uefi": {
                "full_name": "Unified Extensible Firmware Interface",
                "advantages": "Supports larger drives (>2TB), faster boot, graphical interface",
                "boot_files": "Uses GPT (GUID Partition Table) instead of MBR",
                "modern": "UEFI is the modern standard replacing BIOS"
            },
            "cmos": {
                "full_name": "Complementary Metal-Oxide-Semiconductor",
                "function": "Stores BIOS settings and system time",
                "power": "Powered by a small CR2032 battery",
                "reset": "Removing battery resets BIOS to defaults (forgot password fix!)"
            },
            "important": "POST failure beep codes help diagnose problems",
            "study_tip": "BIOS = Old firmware, UEFI = New standard. CMOS = Settings storage + battery"
        }
    },
    
    "raid": {
        "topics": ["RAID 0", "RAID 1", "RAID 5", "RAID 6", "storage"],
        "content": {
            "raid_0": {
                "name": "Striping",
                "speed": "Fast - data split across drives",
                "redundancy": "NONE - single drive failure = total data loss",
                "use_case": "Caching, temporary files, performance critical non-critical data",
                "warning": "NOT for important data!"
            },
            "raid_1": {
                "name": "Mirroring",
                "redundancy": "Full - drives are exact copies",
                "capacity": "50% efficiency (2 drives, use 1)",
                "use_case": "Critical data that needs backup",
                "recovery": "Can recover from any single drive failure"
            },
            "raid_5": {
                "name": "Striping with Parity",
                "drives_needed": "Minimum 3",
                "efficiency": "(n-1)/n where n = number of drives. 3 drives = 66% usable",
                "redundancy": "Survives 1 drive failure",
                "recovery": "Automatic reconstruction using parity",
                "use_case": "Most common for servers and NAS"
            },
            "raid_6": {
                "name": "Dual Parity",
                "drives_needed": "Minimum 4",
                "redundancy": "Survives 2 drive failures simultaneously",
                "efficiency": "(n-2)/n",
                "use_case": "Large arrays where rebuild time is critical"
            },
            "parity_concept": "Mathematical calculation that allows recovery of lost data",
            "study_tip": "RAID ≠ Backup! RAID protects against drive failure, not data deletion or malware"
        }
    },
    
    "network_security": {
        "topics": ["firewall", "VPN", "encryption", "authentication", "ports"],
        "content": {
            "common_ports": {
                "20": "FTP Data",
                "21": "FTP Control",
                "22": "SSH (Secure Shell)",
                "23": "Telnet (insecure, use SSH)",
                "25": "SMTP (Email sending)",
                "53": "DNS (Domain resolution)",
                "80": "HTTP (Web)",
                "110": "POP3 (Email retrieval)",
                "143": "IMAP (Email)",
                "443": "HTTPS (Secure Web)",
                "3306": "MySQL Database",
                "3389": "RDP (Remote Desktop)",
                "study_tip": "Remember: 80=HTTP, 443=HTTPS, 22=SSH, 53=DNS"
            },
            "encryption": "Scrambles data so only intended recipient can read it (symmetric and asymmetric)",
            "vpn": "Creates encrypted tunnel for secure remote access to networks",
            "firewall_rules": "Stateless (checks each packet) vs Stateful (tracks connection state)"
        }
    },
    
    "network_troubleshooting": {
        "topics": ["ping", "tracert", "ipconfig", "netstat", "tools"],
        "content": {
            "ping": {
                "command": "ping [IP/hostname]",
                "function": "Tests connectivity using ICMP echo requests",
                "common_use": "Verify host is reachable, measure latency",
                "output": "Shows RTT (Round Trip Time) in milliseconds"
            },
            "tracert": {
                "full_name": "Traceroute (Linux) / Tracert (Windows)",
                "function": "Shows path packets take to destination",
                "useful_for": "Finding where connection fails, identifying slow hops",
                "shows": "Each router (hop) on the path with latency"
            },
            "ipconfig": {
                "windows_command": "ipconfig /all",
                "shows": "IP address, subnet mask, gateway, DNS, MAC address",
                "renew_dns": "ipconfig /release and ipconfig /renew for DHCP reset"
            },
            "netstat": {
                "windows": "netstat -ano",
                "linux": "netstat -tuln or ss -tuln",
                "shows": "Active connections, listening ports, protocol statistics",
                "useful": "Find what application uses what port"
            },
            "study_tip": "Troubleshooting sequence: Ping → Check IP Config → Tracert → Check Firewall Rules"
        }
    },
    
    "ip_addressing": {
        "topics": ["IPv4", "IPv6", "DHCP", "static IP", "classes"],
        "content": {
            "ipv4": {
                "format": "4 octets (0-255.0-255.0-255.0-255)",
                "total_addresses": "2^32 = 4.3 billion",
                "classes": {
                    "Class A": "1.0.0.0 - 126.255.255.255 (16M hosts each)",
                    "Class B": "128.0.0.0 - 191.255.255.255 (64K hosts each)",
                    "Class C": "192.0.0.0 - 223.255.255.255 (256 hosts each)"
                }
            },
            "private_ranges": {
                "Class A": "10.0.0.0/8",
                "Class B": "172.16.0.0/12",
                "Class C": "192.168.0.0/16",
                "note": "These are NOT routable on public internet"
            },
            "dhcp": "Automatically assigns IP addresses, reduces manual configuration",
            "static_ip": "Manually configured, doesn't change, good for servers",
            "study_tip": "Always use private IP ranges for internal networks!"
        }
    },
    
    "computer_maintenance": {
        "topics": ["cleaning", "temperatures", "power", "disk", "updates"],
        "content": {
            "thermal_management": {
                "cpu_normal": "30-45°C idle, up to 90°C under load (varies by processor)",
                "gpu_normal": "30-50°C idle, 65-85°C under load",
                "overheating_causes": ["Dust buildup", "Broken fans", "Dry thermal paste", "Poor ventilation"],
                "solution": "Clean heatsink and fans, reapply thermal paste if needed"
            },
            "disk_maintenance": {
                "ssd": "No defragmentation needed, use TRIM command for optimization",
                "hdd": "Defragmentation helps (Windows does this automatically)",
                "space": "Keep 10-15% free space for optimal performance",
                "health": "Use S.M.A.R.T. tools to check disk status"
            },
            "power_supply": {
                "wattage": "Should be 30-50% above total system requirements",
                "signs_of_failure": ["Random crashes", "Fan noise", "Burning smell", "Immediate shutdown"],
                "important": "Never ignore power supply problems - can damage components"
            },
            "cleaning": {
                "frequency": "Every 3-6 months depending on environment",
                "equipment": ["Compressed air", "Soft brush", "Anti-static wrist strap"],
                "avoid": "Don't touch components directly, avoid liquids"
            },
            "study_tip": "Good maintenance extends hardware life and prevents unexpected failures"
        }
    },
    
    "lab_preparation": {
        "topics": ["practice", "scenarios", "common_mistakes", "tips"],
        "content": {
            "common_mistakes": [
                "Forgetting to calculate broadcast address (last address in subnet)",
                "Confusing MAC address (Layer 2) with IP address (Layer 3)",
                "Not understanding that switches work on Layer 2, routers on Layer 3",
                "Mixing up TCP (reliable) with UDP (fast)",
                "Not checking physical connections before troubleshooting software"
            ],
            "lab_tips": [
                "Always verify your network topology first",
                "Test connectivity step by step (ping → tracert → firewall check)",
                "Document your configuration before changes",
                "Use correct terminology (e.g., 'VLAN' not 'virtual network')",
                "Check port numbers and protocols match configuration"
            ],
            "practice_scenarios": [
                "Design subnetting for a company with 5 departments",
                "Troubleshoot why computer can't access external website",
                "Configure basic firewall rules for security",
                "Plan RAID configuration for file server",
                "Setup DHCP server for classroom network"
            ]
        }
    }
}


class ChatbotResponse:
    """Manages chatbot responses with educational context"""
    
    def __init__(self):
        self.conversation_history = []
        self.user_skill_level = "beginner"
        self.calculator = SubnettingCalculator()
    
    def find_relevant_topics(self, query):
        """Find relevant topics from knowledge base"""
        query_lower = query.lower()
        relevant = []
        
        for category, data in KNOWLEDGE_BASE.items():
            if "topics" in data:
                for topic in data["topics"]:
                    if topic.lower() in query_lower:
                        relevant.append((category, topic))
        
        return relevant
    
    def generate_response(self, user_query):
        """Generate an educational response based on user query"""
        # Check for subnetting calculation request
        if "subnet" in user_query.lower() and any(word in user_query.lower() for word in ["host", "subnets", "addressing"]):
            subnet_request = self.calculator.parse_subnet_request(user_query)
            if subnet_request:
                result = self.calculator.calculate_addressing_plan(
                    subnet_request['network'],
                    subnet_request['num_subnets'],
                    subnet_request['hosts_per_subnet']
                )
                if 'success' in result:
                    return self.format_subnet_response(result)
                else:
                    return f"❌ {result['error']}"
        
        # Default knowledge base lookup
        relevant_topics = self.find_relevant_topics(user_query)
        
        if not relevant_topics:
            return self.generate_not_found_response(user_query)
        
        responses = []
        category, topic = relevant_topics[0]
        category_data = KNOWLEDGE_BASE[category]
        
        # Build response with educational context
        response = f"**Topic: {topic.title()}**\n\n"
        
        if "content" in category_data:
            content = category_data["content"]
            
            # Add relevant content based on query and topic
            for key, value in content.items():
                if key.lower() in user_query.lower() or topic.lower() in key.lower():
                    response += self.format_content(key, value)
        
        if any("study_tip" in str(v).lower() for v in category_data["content"].values()):
            response += "\n💡 **Study Tip:** Review the flashcards and practice problems related to this topic!\n"
        
        return response
    
    def format_subnet_response(self, result):
        """Format subnet calculation response"""
        response = f"**📊 Subnetting Calculation Results**\n\n"
        response += f"**Original Network:** {result['original_network']}\n\n"
        
        summary = result['calculation_summary']
        response += f"**Calculation Summary:**\n"
        response += f"  - Host bits needed: {summary['host_bits_needed']}\n"
        response += f"  - Subnet bits needed: {summary['subnet_bits_needed']}\n"
        response += f"  - Original prefix: /{summary['original_prefix']}\n"
        response += f"  - New prefix: /{summary['new_prefix']}\n"
        response += f"  - Total subnets available: {summary['total_subnets_available']}\n\n"
        
        response += f"**Detailed Addressing Plan:**\n"
        for subnet in result['addressing_plan']:
            response += f"\n**Subnet {subnet['subnet_number']}** ({subnet['cidr_notation']})\n"
            response += f"  - Network Address: {subnet['network_address']}\n"
            response += f"  - Subnet Mask: {subnet['subnet_mask']}\n"
            response += f"  - First Usable IP: {subnet['first_usable_ip']}\n"
            response += f"  - Last Usable IP: {subnet['last_usable_ip']}\n"
            response += f"  - Broadcast Address: {subnet['broadcast_address']}\n"
            response += f"  - Total Usable Hosts: {subnet['total_usable_hosts']}\n"
        
        return response
    
    def format_content(self, key, value):
        """Format content for display"""
        if isinstance(value, dict):
            formatted = f"\n**{key.replace('_', ' ').title()}:**\n"
            for k, v in value.items():
                if isinstance(v, dict):
                    formatted += f"  - {k}: {json.dumps(v, indent=2)}\n"
                else:
                    formatted += f"  - {k}: {v}\n"
            return formatted
        elif isinstance(value, list):
            formatted = f"\n**{key.replace('_', ' ').title()}:**\n"
            for item in value:
                formatted += f"  - {item}\n"
            return formatted
        else:
            return f"\n**{key.replace('_', ' ').title()}:** {value}\n"
    
    def generate_not_found_response(self, query):
        """Generate helpful response when topic not found"""
        return (
            f"I don't have specific information about '{query}' yet.\n\n"
            "However, here are related topics you can ask about:\n"
            "• OSI Model & Network Layers\n"
            "• Subnetting & IP Addressing\n"
            "• Network Devices (Switch, Router, Firewall)\n"
            "• BIOS/UEFI & CMOS\n"
            "• RAID Configurations\n"
            "• Network Security\n"
            "• Troubleshooting Tools (Ping, Tracert, Netstat)\n"
            "• Computer Maintenance\n\n"
            "Try asking about any of these topics or ask for 'lab preparation tips'!"
        )
    
    def get_quick_answer(self, query):
        """Get a concise quick answer for common questions"""
        quick_answers = {
            "what is switch": "A switch operates on Layer 2 (Data Link Layer) and forwards frames based on MAC addresses.",
            "what is router": "A router operates on Layer 3 (Network Layer) and forwards packets based on IP addresses.",
            "difference between tcp and udp": "TCP is reliable but slower; UDP is fast but unreliable. TCP = email/web, UDP = streaming/gaming.",
            "what is raid": "RAID uses multiple drives for performance or redundancy. RAID 0=speed, RAID 1=backup, RAID 5=balanced.",
            "how to subnet": "Subnetting divides networks using CIDR notation. Example: 192.168.1.0/24 means 24 bits for network, 8 for hosts.",
        }
        
        query_lower = query.lower()
        for key, answer in quick_answers.items():
            if key in query_lower:
                return answer
        return None


# ==================== FLASK ROUTES ====================

chatbot = ChatbotResponse()

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Add to history
    chatbot.conversation_history.append({
        'user': user_message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Check for quick answers first
    quick_answer = chatbot.get_quick_answer(user_message)
    if quick_answer:
        response = quick_answer
    else:
        response = chatbot.generate_response(user_message)
    
    return jsonify({
        'response': response,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/topics', methods=['GET'])
def get_topics():
    """Get all available topics"""
    topics = {}
    for category, data in KNOWLEDGE_BASE.items():
        if "topics" in data:
            topics[category] = data["topics"]
    return jsonify(topics)


@app.route('/api/learn/<topic>', methods=['GET'])
def learn_topic(topic):
    """Get detailed learning material for a specific topic"""
    for category, data in KNOWLEDGE_BASE.items():
        if category.replace('_', ' ') == topic.replace('-', ' '):
            return jsonify({
                'category': category,
                'content': data.get('content', {}),
                'topics': data.get('topics', [])
            })
    return jsonify({'error': 'Topic not found'}), 404


@app.route('/api/quiz', methods=['GET'])
def get_quiz():
    """Get quiz questions for practice"""
    quiz_questions = [
        {
            "id": 1,
            "question": "What layer does a switch operate on?",
            "options": ["Layer 1", "Layer 2", "Layer 3", "Layer 4"],
            "correct": 1,
            "explanation": "Switches operate on Layer 2 (Data Link Layer) using MAC addresses."
        },
        {
            "id": 2,
            "question": "What does CIDR notation /24 mean?",
            "options": ["24 hosts", "24 bits for network", "24 subnets", "24 routers"],
            "correct": 1,
            "explanation": "/24 means 24 bits are for the network portion, leaving 8 bits for hosts."
        },
        {
            "id": 3,
            "question": "Which RAID level provides redundancy with striping?",
            "options": ["RAID 0", "RAID 1", "RAID 5", "RAID 10"],
            "correct": 2,
            "explanation": "RAID 5 combines striping with parity for redundancy. Requires minimum 3 drives."
        },
        {
            "id": 4,
            "question": "What is the private IP range for Class A networks?",
            "options": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "All of above"],
            "correct": 0,
            "explanation": "10.0.0.0/8 is the Class A private range. All three are private ranges."
        },
        {
            "id": 5,
            "question": "Which port is used for SSH?",
            "options": ["21", "22", "23", "25"],
            "correct": 1,
            "explanation": "Port 22 is used for SSH (Secure Shell). Port 21 is FTP, 23 is Telnet, 25 is SMTP."
        }
    ]
    return jsonify(quiz_questions)


@app.route('/api/resources', methods=['GET'])
def get_resources():
    """Get learning resources and study materials"""
    resources = {
        "flashcards": [
            {"term": "OSI Model", "definition": "7-layer framework describing network communication (Physical, Data Link, Network, Transport, Session, Presentation, Application)"},
            {"term": "Subnetting", "definition": "Dividing large network into smaller subnets to reduce traffic and improve management"},
            {"term": "RAID 5", "definition": "Striping with parity - minimum 3 drives, survives 1 failure, (n-1)/n efficiency"},
            {"term": "DHCP", "definition": "Dynamic Host Configuration Protocol - automatically assigns IP addresses"},
            {"term": "CIDR", "definition": "Classless Inter-Domain Routing notation for specifying network address and prefix (e.g., 192.168.1.0/24)"}
        ],
        "references": [
            "CompTIA Network+ Objectives",
            "OSI Model Deep Dive",
            "Subnetting Calculator Practice",
            "RAID Configuration Guide",
            "Network Troubleshooting Flowchart"
        ],
        "video_topics": [
            "Understanding the OSI Model",
            "Subnetting Explained Step by Step",
            "RAID Configurations Comparison",
            "Network Troubleshooting Methodology",
            "Router vs Switch vs Hub"
        ]
    }
    return jsonify(resources)


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    return jsonify({
        'history': chatbot.conversation_history[-10:]  # Return last 10 messages
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Network Learning Chatbot',
        'version': '1.0'
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Network Learning Chatbot Backend Starting...")
    print("Available endpoints:")
    print("  POST /api/chat - Send chat message")
    print("  GET /api/topics - Get all topics")
    print("  GET /api/learn/<topic> - Get topic details")
    print("  GET /api/quiz - Get practice quiz")
    print("  GET /api/resources - Get learning resources")
    print("  GET /api/history - Get conversation history")
    print("\n📚 Knowledge base includes:")
    for category in KNOWLEDGE_BASE.keys():
        print(f"  - {category.replace('_', ' ').title()}")
    
    app.run(debug=True, port=port, host='0.0.0.0')
