"""
Alias Database - SKELETON
IMPLEMENT THE TODOs

This module manages aliases (alternative names for the same thing).
For example: "JPM" -> "JP Morgan Chase", "SOFRRATE" -> "Secured Overnight Financing Rate"

There are two types of aliases:
1. Global aliases - Apply to all counterparties (e.g., "USD" -> "US Dollar")
2. Counterparty-specific aliases - Only apply to specific counterparties
   (e.g., "JPM" might mean "JP Morgan Chase" for one counterparty but something else for another)
"""

from typing import Dict, Optional, List, Tuple
from utils.helpers import calculate_string_similarity


class AliasDatabase:
    """
    In-memory database of value aliases for data normalization.

    This is the "knowledge base" that helps reconcile variations in how the same
    thing might be written. For example, a PDF might say "JPM" but your trade
    suite has "JP Morgan Chase".

    Attributes:
        global_aliases: Aliases that apply to all counterparties
                       Format: {'field': {'from_value': 'to_value', ...}}
        counterparty_aliases: Aliases specific to each counterparty
                             Format: {'counterparty_id': {'field': {'from': 'to', ...}}}
    """

    def __init__(self):
        """
        Initialize the alias database with pre-populated global aliases.

        TODO: Implement this method
        Steps:
        1. Initialize self.global_aliases as a dictionary with these pre-populated values:
           {
               'counterparty': {
                   'JPM': 'JP Morgan Chase',
                   'GS': 'Goldman Sachs',
                   'MS': 'Morgan Stanley',
                   'BAML': 'Bank of America Merrill Lynch',
                   'Citi': 'Citigroup'
               },
               'rate': {
                   'SOFR': 'Secured Overnight Financing Rate',
                   'SOFRRATE': 'Secured Overnight Financing Rate',
                   'LIBOR': 'London Interbank Offered Rate'
               },
               'currency': {
                   'USD': 'US Dollar',
                   'EUR': 'Euro',
                   'GBP': 'British Pound',
                   'JPY': 'Japanese Yen',
                   'INR': 'Indian Rupee'
               },
               'product': {
                   'IRS': 'Interest Rate Swap',
                   'CDS': 'Credit Default Swap',
                   'FX': 'Foreign Exchange'
               }
           }
        2. Initialize self.counterparty_aliases as an empty dictionary
        """
        # TODO: Initialize self.global_aliases with the structure above
        # TODO: Initialize self.counterparty_aliases as empty dict {}
        pass

    def resolve(
        self, field: str, value: str, counterparty_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Try to resolve a value to its canonical form using aliases.

        Resolution order:
        1. First try counterparty-specific alias (if counterparty_id provided)
        2. Then try global alias
        3. Return None if no alias found

        Args:
            field: The field name (e.g., 'counterparty', 'rate', 'currency')
            value: The value to resolve (e.g., 'JPM', 'SOFR')
            counterparty_id: Optional counterparty ID for counterparty-specific lookup

        Returns:
            The canonical value if alias found, None otherwise

        Example:
            >>> db = AliasDatabase()
            >>> db.resolve('counterparty', 'JPM')
            'JP Morgan Chase'
            >>> db.resolve('currency', 'USD')
            'US Dollar'
            >>> db.resolve('counterparty', 'Unknown')
            None

        TODO: Implement this method
        Steps:
        1. If counterparty_id is provided:
           - Check if counterparty_id exists in self.counterparty_aliases
           - Check if field exists in that counterparty's aliases
           - Check if value exists in that field's aliases
           - If found, return the alias value
        2. Check if field exists in self.global_aliases
        3. Check if value exists in that field's aliases
        4. If found, return the alias value
        5. Otherwise return None
        """
        # TODO: Try counterparty-specific alias first (if counterparty_id provided)
        # TODO: Then try global alias
        # TODO: Return None if not found
        pass

    def add_alias(
        self,
        field: str,
        from_value: str,
        to_value: str,
        counterparty_id: Optional[str] = None,
    ) -> None:
        """
        Add a new alias to the database.

        Args:
            field: The field name (e.g., 'counterparty', 'rate')
            from_value: The value to alias from (e.g., 'JPM')
            to_value: The canonical value to alias to (e.g., 'JP Morgan Chase')
            counterparty_id: If provided, add as counterparty-specific alias,
                           otherwise add as global alias

        Example:
            >>> db = AliasDatabase()
            >>> db.add_alias('counterparty', 'JP Morgan', 'JP Morgan Chase')
            >>> db.resolve('counterparty', 'JP Morgan')
            'JP Morgan Chase'

        TODO: Implement this method
        Steps:
        1. If counterparty_id is None (global alias):
           - Ensure field exists in self.global_aliases (create dict if needed)
           - Add from_value -> to_value mapping
        2. If counterparty_id is provided (counterparty-specific):
           - Ensure counterparty_id exists in self.counterparty_aliases
           - Ensure field exists in that counterparty's aliases
           - Add from_value -> to_value mapping
        """
        # TODO: Determine if global or counterparty-specific
        # TODO: Ensure nested dictionary structure exists
        # TODO: Add the alias mapping
        pass

    def find_similar(
        self, field: str, value: str, threshold: float = 0.75
    ) -> List[Tuple[str, float]]:
        """
        Find similar values in the alias database using string similarity.

        This is useful when you want to suggest: "Did you mean X?"

        Args:
            field: The field to search in (e.g., 'counterparty')
            value: The value to find similar matches for
            threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            List of (canonical_value, similarity_score) tuples, sorted by similarity

        Example:
            >>> db = AliasDatabase()
            >>> db.find_similar('counterparty', 'Goldman', threshold=0.7)
            [('Goldman Sachs', 0.85)]

        TODO: Implement this method
        Steps:
        1. Get all target values (canonical values) for this field from global_aliases
        2. For each target value:
           - Calculate similarity using calculate_string_similarity helper
           - If similarity >= threshold, add (target_value, similarity) to results
        3. Sort results by similarity (highest first)
        4. Return the sorted list

        HINT: Use the calculate_string_similarity helper from utils.helpers
        HINT: For sorting, use: sorted(results, key=lambda x: x[1], reverse=True)
        """
        # TODO: Get all target values for this field
        # TODO: Calculate similarity for each target value
        # TODO: Filter by threshold
        # TODO: Sort by similarity (highest first)
        # TODO: Return list of (value, similarity) tuples
        pass

    def get_all_aliases(self, field: Optional[str] = None) -> Dict:
        """
        Get all aliases, optionally filtered by field.

        Args:
            field: If provided, only return aliases for this field

        Returns:
            Dictionary of aliases

        Example:
            >>> db = AliasDatabase()
            >>> db.get_all_aliases('currency')
            {'USD': 'US Dollar', 'EUR': 'Euro', ...}

        TODO: Implement this method
        Steps:
        1. If field is provided:
           - Return self.global_aliases.get(field, {})
        2. If field is None:
           - Return self.global_aliases
        """
        # TODO: Return filtered or all aliases
        pass
