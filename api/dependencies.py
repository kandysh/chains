"""
API Dependencies - SKELETON
IMPLEMENT THE TODOs

This module provides singleton instances of various components for dependency injection.
"""

import os
import pandas as pd
from functools import lru_cache
from models.alias_db import AliasDatabase
from agents.extractor import PDFExtractor
from orchestrator import AgenticOrchestrator


class TradeSuiteDB:
    """
    Mock trade suite database.

    In a real system, this would connect to your actual trade suite.
    For now, we'll use a pandas DataFrame with sample data.
    """

    def __init__(self):
        """
        Initialize with sample trade data.

        TODO: Implement this method
        Steps:
        1. Load your actual trade suite data if available
        2. For now, create sample data:
           - Create a pandas DataFrame with columns:
             ['trade_id', 'counterparty', 'notional', 'rate', 'currency',
              'product', 'trade_date', 'settlement_date']
           - Add 5 sample trades
        3. Store as self.trades

        Example sample data:
        {
            'trade_id': ['TR12345', 'TR12346', 'TR12347', 'TR12348', 'TR12349'],
            'counterparty': ['JP Morgan Chase', 'Goldman Sachs', 'Morgan Stanley', 'Citigroup', 'Bank of America Merrill Lynch'],
            'notional': [1000000, 5000000, 2500000, 15000000, 750000],
            'rate': ['SOFR + 50', 'SOFR + 75', 'SOFR + 45', 'SOFR + 100', 'SOFR + 60'],
            'currency': ['USD', 'USD', 'USD', 'USD', 'USD'],
            'product': ['Interest Rate Swap', 'Interest Rate Swap', 'Interest Rate Swap', 'Interest Rate Swap', 'Interest Rate Swap'],
            'trade_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19'],
            'settlement_date': ['2024-01-17', '2024-01-18', '2024-01-19', '2024-01-22', '2024-01-23']
        }
        """
        # TODO: Create sample trade data using pandas DataFrame
        # TODO: In production, replace with actual trade suite connection
        pass

    def get_trade(self, trade_id: str):
        """
        Get a trade by ID.

        Args:
            trade_id: Trade ID to look up

        Returns:
            Dictionary with trade data, or None if not found

        TODO: Implement this method
        Steps:
        1. Query self.trades DataFrame for matching trade_id
        2. If found, convert row to dictionary and return
        3. If not found, return None

        HINT: Use: self.trades[self.trades['trade_id'] == trade_id]
        HINT: Use .to_dict('records')[0] to convert row to dict
        """
        # TODO: Query DataFrame for trade_id
        # TODO: Return dict or None
        pass

    def get_all_trades(self):
        """
        Get all trades.

        Returns:
            List of trade dictionaries

        TODO: Implement this method
        Return self.trades.to_dict('records')
        """
        # TODO: Return all trades as list of dicts
        pass


# Singleton instances
_alias_db = None
_pdf_extractor = None
_trade_suite_db = None
_orchestrator = None


@lru_cache()
def get_alias_db() -> AliasDatabase:
    """
    Get singleton AliasDatabase instance.

    TODO: Implement this function
    Steps:
    1. Use global _alias_db variable
    2. If None, create new AliasDatabase instance
    3. Return the instance

    HINT: Use 'global _alias_db' to modify the global variable
    """
    # TODO: Implement singleton pattern
    # TODO: Return AliasDatabase instance
    pass


@lru_cache()
def get_pdf_extractor() -> PDFExtractor:
    """
    Get singleton PDFExtractor instance.

    TODO: Implement this function (same pattern as get_alias_db)
    """
    # TODO: Implement singleton pattern
    # TODO: Return PDFExtractor instance
    pass


@lru_cache()
def get_trade_suite_db() -> TradeSuiteDB:
    """
    Get singleton TradeSuiteDB instance.

    TODO: Implement this function (same pattern as get_alias_db)
    """
    # TODO: Implement singleton pattern
    # TODO: Return TradeSuiteDB instance
    pass


@lru_cache()
def get_orchestrator() -> AgenticOrchestrator:
    """
    Get singleton AgenticOrchestrator instance.

    TODO: Implement this function
    Steps:
    1. Get dependencies:
       - pdf_extractor = get_pdf_extractor()
       - alias_db = get_alias_db()
       - trade_suite_db = get_trade_suite_db()
    2. Create orchestrator if not exists:
       - orchestrator = AgenticOrchestrator(pdf_extractor, alias_db, trade_suite_db)
    3. Return orchestrator

    HINT: Use global _orchestrator
    """
    # TODO: Get dependencies
    # TODO: Create orchestrator if not exists
    # TODO: Return orchestrator
    pass
