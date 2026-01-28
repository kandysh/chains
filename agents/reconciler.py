"""
Reconciler Agent - SKELETON
IMPLEMENT THE TODOs

This agent compares extracted data with trade suite data and decides
how to handle discrepancies using AI reasoning.
"""

from typing import Dict, Any, List, Optional
from models.schemas import Discrepancy
from models.alias_db import AliasDatabase
from utils.logging_config import get_logger

logger = get_logger(__name__)


class ReconcilerAgent:
    """
    Intelligent agent that reconciles extracted data with trade suite data.

    This agent:
    1. Compares each field between extracted and expected data
    2. Tries to resolve differences using aliases
    3. Uses AI to make decisions about how to handle discrepancies
    4. Suggests actions (create alias, recheck PDF, flag for human, etc.)

    This is the "brain" of the reconciliation process.
    """

    def __init__(self, trade_suite_db, alias_db: AliasDatabase):
        """
        Initialize the reconciler agent.

        Args:
            trade_suite_db: Access to trade suite database
            alias_db: Alias database for resolving variations

        TODO: Implement this method
        Steps:
        1. Store trade_suite_db and alias_db as instance variables
        2. Initialize LLM for semantic checks:
           - from langchain.chat_models import ChatOpenAI
           - self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
           - Use gpt-4o-mini for cost efficiency on semantic checks
        3. Log initialization
        """
        # TODO: Store dependencies
        # TODO: Initialize LLM for semantic equivalence checking
        logger.info("ReconcilerAgent initialized")
        pass

    def reconcile(
        self, extracted_data: Dict[str, Any], workflow_state
    ) -> List[Discrepancy]:
        """
        Main reconciliation logic.

        Compares extracted data with trade suite and identifies discrepancies
        that need resolution.

        Args:
            extracted_data: Data extracted from PDF
            workflow_state: Current workflow state

        Returns:
            List of Discrepancy objects that need resolution

        TODO: Implement this method
        Steps:
        1. Get counterparty_id from extracted_data (might need to determine this)
        2. Get trade record from trade_suite_db using trade_id
        3. If trade record not found:
           - Create Discrepancy for missing trade
           - Return [discrepancy]
        4. Initialize empty discrepancies list
        5. For each field in extracted_data:
           a. Get extracted_value
           b. Get expected_value from trade_suite_db record
           c. If they match exactly -> skip
           d. Try alias resolution:
              - resolved = alias_db.resolve(field, extracted_value, counterparty_id)
              - If resolved == expected_value -> apply alias and continue
           e. If still no match:
              - Call self._decide_on_discrepancy()
              - Create Discrepancy object with suggested action
              - Add to discrepancies list
           f. Log the discrepancy with workflow_state.add_step()
        6. Return discrepancies list

        HINT: Log each step using workflow_state.add_step()
        HINT: Some fields might not be in trade suite - handle gracefully
        """
        logger.info("Starting reconciliation")

        # TODO: Get counterparty_id from extracted_data
        # TODO: Get trade record from trade_suite_db
        # TODO: Compare each field
        # TODO: Try alias resolution
        # TODO: Call _decide_on_discrepancy for unresolved differences
        # TODO: Return list of Discrepancy objects
        pass

    def _decide_on_discrepancy(
        self,
        field: str,
        extracted_value: Any,
        expected_value: Any,
        counterparty_id: Optional[str],
    ) -> Dict[str, Any]:
        """
        Agent decides what action to take for a discrepancy.

        This is where the AI reasoning happens. The agent follows a decision tree
        to determine the best action.

        Decision tree:
        1. Check for similar existing aliases (threshold 0.75)
        2. If similarity > 0.9 → suggest_new_alias
        3. Check semantic equivalence with LLM
        4. If equivalent and confidence > 0.8 → suggest_new_alias
        5. If short abbreviation (<=3 chars) → suggest_counterparty_alias
        6. If suspicious format (special chars, etc.) → recheck_pdf
        7. Otherwise → flag_for_human

        Args:
            field: Field name with discrepancy
            extracted_value: Value from PDF
            expected_value: Value from trade suite
            counterparty_id: Counterparty ID for context

        Returns:
            Dictionary with:
            {
                'action': str,  # 'suggest_new_alias', 'recheck_pdf', 'flag_for_human', etc.
                'reasoning': str,  # Why this action was chosen
                'confidence': float,  # 0.0 to 1.0
                'suggested_alias': Dict (optional)  # {'from': ..., 'to': ..., 'scope': ...}
            }

        TODO: Implement this method (this is complex - break it down)
        Steps:
        1. Convert values to strings for comparison
        2. Find similar aliases:
           - similar = self.alias_db.find_similar(field, str(extracted_value), threshold=0.75)
           - If any match has similarity > 0.9:
             - Return action='suggest_new_alias' with high confidence
        3. Check semantic equivalence:
           - result = self._check_semantic_equivalence(field, extracted_value, expected_value)
           - If result['equivalent'] and result['confidence'] > 0.8:
             - Return action='suggest_new_alias'
        4. Check if short abbreviation:
           - If len(str(extracted_value)) <= 3:
             - Return action='suggest_counterparty_alias'
        5. Check for suspicious format:
           - If has special characters or looks malformed:
             - Return action='recheck_pdf'
        6. Default case:
           - Return action='flag_for_human' with reasoning

        HINT: Each return should include 'action', 'reasoning', 'confidence'
        HINT: If suggesting alias, include 'suggested_alias' dict
        """
        logger.info(f"Deciding on discrepancy for field: {field}")

        # TODO: Implement decision tree as described above
        # TODO: Check for similar aliases
        # TODO: Check semantic equivalence using LLM
        # TODO: Check for abbreviations
        # TODO: Check for suspicious formats
        # TODO: Return decision dictionary
        pass

    def _check_semantic_equivalence(
        self, field: str, value1: Any, value2: Any
    ) -> Dict[str, Any]:
        """
        Use LLM to check if two values mean the same thing.

        This is useful for cases like:
        - "JPM" vs "JP Morgan Chase"
        - "Interest Rate Swap" vs "IRS"
        - "Secured Overnight Financing Rate" vs "SOFR"

        Args:
            field: Field name for context
            value1: First value
            value2: Second value

        Returns:
            Dictionary with:
            {
                'equivalent': bool,
                'confidence': float,
                'reasoning': str
            }

        Example:
            result = reconciler._check_semantic_equivalence(
                'counterparty',
                'JPM',
                'JP Morgan Chase'
            )
            # Returns: {'equivalent': True, 'confidence': 0.95, 'reasoning': 'JPM is a common abbreviation...'}

        TODO: Implement this method
        Steps:
        1. Create a prompt asking if the values are semantically equivalent:
           Example prompt:
           "You are a financial data expert. Determine if these two values for field '{field}' mean the same thing:
           Value 1: {value1}
           Value 2: {value2}

           Consider:
           - Common abbreviations in finance
           - Alternative names for the same entity
           - Semantic meaning, not just string matching

           Respond in JSON format:
           {{
               \"equivalent\": true/false,
               \"confidence\": 0.0-1.0,
               \"reasoning\": \"brief explanation\"
           }}"

        2. Call self.llm with the prompt (use JSON mode if available)
        3. Parse the response
        4. Return the result dictionary

        HINT: Use JSON mode: model_kwargs={"response_format": {"type": "json_object"}}
        HINT: Handle JSON parsing errors gracefully
        """
        logger.debug(f"Checking semantic equivalence: {value1} vs {value2}")

        # TODO: Create semantic equivalence prompt
        # TODO: Call LLM with JSON mode
        # TODO: Parse response
        # TODO: Return {equivalent, confidence, reasoning}
        pass
