import logging
import time
import threading
import requests
from web3 import Web3
from typing import List, Dict, Optional
from eth_utils import encode_hex

logger = logging.getLogger("PINAIAgentSDK.Indexer")

class EventSignatures:
    """Event signatures for the IntentMatching contract"""
    OrderCreated = "OrderCreated(uint256,address,uint8,uint256)"
    OrderMatched = "OrderMatched(uint256,uint256,string)"
    AddressesTracked = "AddressesTracked(uint256,address[])"
    OrderCompleted = "OrderCompleted(uint256,uint256)"

class BlockchainIndexer:
    """
    Blockchain indexer for monitoring and processing smart contract events
    """
    
    def __init__(self, web3: Web3, agent_contract, account, intent_matching_contract=None, intent_matching_url=None):
        """
        Initialize the blockchain indexer

        Args:
            web3 (Web3): Web3 instance
            agent_contract: Agent contract instance
            account: Account instance
            intent_matching_contract: Intent matching contract instance (optional)
            intent_matching_url: URL for the intent matching service (optional)
        """
        self.web3 = web3
        self.agent_contract = agent_contract
        self.account = account
        self.intent_matching_contract = intent_matching_contract
        self.intent_matching_url = intent_matching_url
        
        self.stop_indexing = False
        self.indexer_thread = None
        self.indexed_events = []
        
        # Room tracking
        self.current_room_id = None
        self.current_order_id = None
        
        # Event signatures
        self.event_signatures = {
            Web3.keccak(text=EventSignatures.OrderCreated).hex(): self._handle_order_created,
            Web3.keccak(text=EventSignatures.OrderMatched).hex(): self._handle_order_matched,
            Web3.keccak(text=EventSignatures.AddressesTracked).hex(): self._handle_addresses_tracked,
            Web3.keccak(text=EventSignatures.OrderCompleted).hex(): self._handle_order_completed
        }
        
    def start(self):
        """Start the indexer service"""
        if not self.web3 or not self.intent_matching_contract:
            logger.warning("Blockchain components not initialized. Cannot start indexer.")
            return
            
        self.stop_indexing = False
        self.indexer_thread = threading.Thread(target=self._run_indexer)
        self.indexer_thread.daemon = True
        self.indexer_thread.start()
        logger.info("Blockchain indexer service started")
        
    def stop(self):
        """Stop the indexer service"""
        if self.indexer_thread and self.indexer_thread.is_alive():
            self.stop_indexing = True
            self.indexer_thread.join(timeout=2.0)
            logger.info("Blockchain indexer stopped")
            
    def _run_indexer(self):
        """Main indexer loop that monitors blockchain events"""
        if not self.intent_matching_contract:
            logger.error("Intent matching contract not initialized")
            return

        # Create filter for the contract address
        contract_filter = {
            'address': self.intent_matching_contract.address,
            'fromBlock': 'latest'
        }

        logger.info("Starting to listen for events...")

        last_processed_block = 0

        while not self.stop_indexing:
            try:
                if self.web3.eth.get_block_number() <= last_processed_block:
                    continue
                
                last_processed_block = self.web3.eth.get_block_number()

                # Get new blocks
                new_entries = self.web3.eth.get_filter_changes(
                    self.web3.eth.filter(contract_filter).filter_id
                )

                logger.info(f"New entries: {new_entries}")

                # Process any new events
                for event in new_entries:
                    self._process_event(event)

                # Small sleep to prevent high CPU usage
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in indexer: {e}")
                time.sleep(1)  # Sleep on error before retrying
                
    def _process_event(self, event):
        """
        Process a blockchain event
        
        Args:
            event: The blockchain event to process
        """
        try:
            logger.info(f"Processing event: {event}")
            # Extract event signature from first topic
            event_signature = event['topics'][0].hex()
            
            # Call appropriate handler based on event signature
            if event_signature in self.event_signatures:
                self.event_signatures[event_signature](event)
                logger.debug(f"Processed event with signature: {event_signature}")
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            
    def _get_block_timestamp(self, block_number):
        """Get timestamp for a block"""
        block = self.web3.eth.get_block(block_number)
        return block.timestamp

    def _handle_order_created(self, event):
        """Handle OrderCreated event"""
        try:
            order_id = int(event['topics'][1].hex(), 16)
            user_address = f"0x{event['topics'][2].hex()[-40:]}"
            
            logger.info(f"Order created - ID: {order_id}, User: {user_address}")
            
            # Submit bid
            bid_data = {
                "orderId": order_id,
                "userId": user_address,
                "agentId": 0,
                "amount": 100
            }
            
            # Submit bid
            self._submit_bid(bid_data)
            
        except Exception as e:
            logger.error(f"Error handling OrderCreated event: {e}")

    def _submit_bid(self, bid_data: Dict) -> None:
        self.base_url = "http://localhost:3000"
        """Submit a bid to the intent matching service"""
        if not self.base_url:
            logger.error("Base URL not set")
            return

        try:
            response = requests.post(
                f"{self.base_url}/bid",
                json=bid_data,
                headers={"Content-Type": "application/json"}
            )
            
            if 200 <= response.status_code < 300:
                logger.info(f"Bid submitted successfully: {response.json()}")
            else:
                logger.error(f"Bid submission failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error submitting bid: {e}")

    def _handle_order_matched(self, event):
        """Handle OrderMatched event"""
        try:
            order_id = int(event['topics'][1].hex(), 16)
            
            # Get order details from contract
            order = self.intent_matching_contract.functions.getOrder(order_id).call()
            
            self.current_order_id = order_id

            # TODO: handle order matched - start agent + personal AI communication
            logger.info(f"Order matched - ID: {order_id}")
            
        except Exception as e:
            logger.error(f"Error handling OrderMatched event: {e}")

    def _handle_addresses_tracked(self, event):
        """Handle AddressesTracked event"""
        # Implement if needed
        pass

    def _handle_order_completed(self, event):
        """Handle OrderCompleted event"""
        try:
            order_id = int(event['topics'][1].hex(), 16)
            
            # Get order details from contract
            order = self.intent_matching_contract.functions.getOrder(order_id).call()
            amount = order[1]  # Assuming amount is the second field
            
            logger.info(f"Order completed - ID: {order_id}, Amount: {amount}")
            
        except Exception as e:
            logger.error(f"Error handling OrderCompleted event: {e}")
