"""
Firebase client for state management and real-time data streaming.
Centralized database layer for the trading ecosystem.
"""
import json
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore, db
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1.document import DocumentReference

from config import config

class FirebaseClient:
    """Firebase client for Firestore and Realtime Database operations"""
    
    def __init__(self):
        self._firestore_client: Optional[FirestoreClient] = None
        self._realtime_db = None
        self._initialized = False
        self.logger = logging.getLogger(__name__)
        
    def initialize(self) -> None:
        """Initialize Firebase with error handling and validation"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(config.firebase.credentials_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': config.firebase.project_id,
                    'databaseURL': config.firebase.database_url
                })
                self.logger.info("Firebase initialized successfully")
            
            self._firestore_client = firestore.client()
            self._realtime_db = db.reference()
            self._initialized = True
            
        except FileNotFoundError as e:
            self.logger.error(f"Firebase credentials file not found: {e}")
            raise
        except ValueError as e:
            self.logger.error(f"Invalid Firebase configuration: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    @property
    def firestore(self) -> FirestoreClient:
        """Get Firestore client with lazy initialization"""
        if not self._initialized:
            self.initialize()
        if self._firestore_client is None:
            raise RuntimeError("Firestore client not initialized")
        return self._firestore_client
    
    @property
    def realtime_db(self):
        """Get Realtime Database reference"""
        if not self._initialized:
            self.initialize()
        return self._realtime_db
    
    # Firestore Operations
    def save_trading_state(self, state: Dict[str, Any], collection: str = "trading_states") -> str:
        """Save trading state to Firestore"""
        try:
            state['timestamp'] = datetime.utcnow().isoformat()
            doc_ref = self.firestore.collection(collection).document()
            doc_ref.set(state)
            return doc_ref.id
        except Exception as e:
            self.logger.error(f"Failed to save trading state: {e}")
            raise
    
    def get_trading_state(self, document_id: str, collection: str = "trading_states") -> Optional[Dict[str, Any]]:
        """Retrieve trading state from Firestore"""
        try:
            doc_ref = self.firestore.collection(collection).document(document_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            self.logger.error(f"Failed to get trading state: {e}")
            return None
    
    def update_market_data(self, symbol: str, timeframe: str, data: List[Dict[str, Any]]) -> bool:
        """Update market data in Firestore with batch operations"""
        try:
            collection_name = f"market_data_{symbol.replace('/', '_')}_{timeframe}"
            batch = self.firestore.batch()
            
            for i, candle in enumerate(data):
                doc_ref = self.firestore.collection(collection_name).document(str(i))
                batch.set(doc_ref, candle)
            
            batch.commit()
            self.logger.info(f"Updated {len(data)} candles for {symbol} {timeframe}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update market data: {e}")
            return False
    
    # Realtime Database Operations
    def stream_order_updates(self, callback):
        """Stream real-time order updates"""
        try:
            orders_ref = self.realtime_db.child('orders')
            orders_ref.listen(c