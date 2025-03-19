AGENT_CONTRACT_ABI = [
    # VERSION
    {
        "inputs": [],
        "name": "VERSION",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    # create
    {
        "inputs": [
            {"internalType": "address", "name": "_agentOwner", "type": "address"},
            {"internalType": "string", "name": "_agentName", "type": "string"},
            {"internalType": "string", "name": "_serviceEndpoint", "type": "string"},
            {"internalType": "string", "name": "_description", "type": "string"},
            {"internalType": "uint256", "name": "_agentId", "type": "uint256"},
            {"internalType": "bytes32", "name": "_category", "type": "bytes32"}
        ],
        "name": "create",
        "outputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    },
    # updateAgentStatusByAgentId
    {
        "inputs": [
            {"internalType": "uint256", "name": "agentId", "type": "uint256"},
            {"internalType": "enum AgentManager.AgentStatus", "name": "newStatus", "type": "uint8"}
        ],
        "name": "updateAgentStatusByAgentId",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    # getAgentByAgentId
    {
        "inputs": [{"internalType": "uint256", "name": "agentId", "type": "uint256"}],
        "name": "getAgentByAgentId",
        "outputs": [{
            "components": [
                {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
                {"internalType": "uint256", "name": "agentId", "type": "uint256"},
                {"internalType": "string", "name": "name", "type": "string"},
                {"internalType": "string", "name": "serviceEndpoint", "type": "string"},
                {"internalType": "string", "name": "description", "type": "string"},
                {"internalType": "bytes32", "name": "category", "type": "bytes32"},
                {"internalType": "address", "name": "owner", "type": "address"},
                {"internalType": "address", "name": "tba", "type": "address"},
                {"internalType": "uint256", "name": "stakeAmount", "type": "uint256"},
                {"internalType": "uint8", "name": "reputationScore", "type": "uint8"},
                {"internalType": "enum AgentManager.AgentStatus", "name": "status", "type": "uint8"},
                {"internalType": "uint64", "name": "lastActiveTime", "type": "uint64"},
                {"internalType": "uint64", "name": "bidCount", "type": "uint64"},
                {"internalType": "uint64", "name": "dealCount", "type": "uint64"}
            ],
            "internalType": "struct AgentManager.Agent",
            "name": "",
            "type": "tuple"
        }],
        "stateMutability": "view",
        "type": "function"
    },
    # getAgentStatus
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "getAgentStatus",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

INTENT_MATCHING_CONTRACT_ABI = [
    {
        "type": "constructor",
        "inputs": [
            {
                "name": "_agentRegistry",
                "type": "address",
                "internalType": "address"
            }
        ],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "addIntentAddressTracking",
        "inputs": [
            {
                "name": "_intentId",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_addresses",
                "type": "address[]",
                "internalType": "address[]"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "addIntentBusinessTracking",
        "inputs": [
            {
                "name": "_intentId",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_businesses",
                "type": "string[]",
                "internalType": "string[]"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "agentRegistry",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "address",
                "internalType": "contract AgentRegistry"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "completeIntent",
        "inputs": [
            {
                "name": "_orderId",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_isSuccessful",
                "type": "bool",
                "internalType": "bool"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "getIntentAddressTracker",
        "inputs": [
            {
                "name": "_intentId",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "address[]",
                "internalType": "address[]"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getIntentBusinessTracker",
        "inputs": [
            {
                "name": "_intentId",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "string[]",
                "internalType": "string[]"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getOrder",
        "inputs": [
            {
                "name": "_orderId",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "tuple",
                "internalType": "struct IntentOrder",
                "components": [
                    {
                        "name": "id",
                        "type": "uint256",
                        "internalType": "uint256"
                    },
                    {
                        "name": "amount",
                        "type": "uint256",
                        "internalType": "uint256"
                    },
                    {
                        "name": "isCompleted",
                        "type": "bool",
                        "internalType": "bool"
                    },
                    {
                        "name": "isSuccessful",
                        "type": "bool",
                        "internalType": "bool"
                    },
                    {
                        "name": "isDisbursed",
                        "type": "bool",
                        "internalType": "bool"
                    },
                    {
                        "name": "user",
                        "type": "address",
                        "internalType": "address"
                    },
                    {
                        "name": "agentId",
                        "type": "uint256",
                        "internalType": "uint256"
                    },
                    {
                        "name": "roomKey",
                        "type": "string",
                        "internalType": "string"
                    },
                    {
                        "name": "category",
                        "type": "uint8",
                        "internalType": "enum AgentRegistry.Category"
                    }
                ]
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "matchedIntent",
        "inputs": [
            {
                "name": "_orderId",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_agentId",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_roomKey",
                "type": "string",
                "internalType": "string"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "owner",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "address",
                "internalType": "address"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "renounceOwnership",
        "inputs": [],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "submitIntent",
        "inputs": [
            {
                "name": "_category",
                "type": "uint8",
                "internalType": "enum AgentRegistry.Category"
            }
        ],
        "outputs": [],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "transferOwnership",
        "inputs": [
            {
                "name": "newOwner",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "event",
        "name": "AddressesTracked",
        "inputs": [
            {
                "name": "intentId",
                "type": "uint256",
                "indexed": True,
                "internalType": "uint256"
            },
            {
                "name": "addresses",
                "type": "address[]",
                "indexed": False,
                "internalType": "address[]"
            }
        ],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "BusinessesTracked",
        "inputs": [
            {
                "name": "intentId",
                "type": "uint256",
                "indexed": True,
                "internalType": "uint256"
            },
            {
                "name": "businesses",
                "type": "string[]",
                "indexed": False,
                "internalType": "string[]"
            }
        ],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "OrderCompleted",
        "inputs": [
            {
                "name": "orderId",
                "type": "uint256",
                "indexed": True,
                "internalType": "uint256"
            },
            {
                "name": "agentId",
                "type": "uint256",
                "indexed": True,
                "internalType": "uint256"
            }
        ],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "OrderCreated",
        "inputs": [
            {
                "name": "id",
                "type": "uint256",
                "indexed": True,
                "internalType": "uint256"
            },
            {
                "name": "user",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            },
            {
                "name": "category",
                "type": "uint8",
                "indexed": True,
                "internalType": "enum AgentRegistry.Category"
            },
            {
                "name": "amount",
                "type": "uint256",
                "indexed": False,
                "internalType": "uint256"
            }
        ],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "OrderMatched",
        "inputs": [
            {
                "name": "orderId",
                "type": "uint256",
                "indexed": True,
                "internalType": "uint256"
            },
            {
                "name": "agentId",
                "type": "uint256",
                "indexed": True,
                "internalType": "uint256"
            },
            {
                "name": "roomKey",
                "type": "string",
                "indexed": False,
                "internalType": "string"
            }
        ],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "OwnershipTransferred",
        "inputs": [
            {
                "name": "previousOwner",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            },
            {
                "name": "newOwner",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            }
        ],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "PaymentDisbursed",
        "inputs": [
            {
                "name": "owner",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            },
            {
                "name": "id",
                "type": "uint256",
                "indexed": True,
                "internalType": "uint256"
            },
            {
                "name": "name",
                "type": "string",
                "indexed": False,
                "internalType": "string"
            }
        ],
        "anonymous": False
    }
]
