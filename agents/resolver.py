"""
Resolution Agent - SKELETON
IMPLEMENT THE TODOs

This agent executes the actions decided by the Reconciler.
It's the "hands" that actually make changes based on the "brain's" decisions.
"""

from typing import Dict, Any
from models.schemas import Discrepancy
from models.alias_db import AliasDatabase
from database.db import get_db, PendingAlias, HumanReviewTask
from utils.logging_config import get_logger

logger = get_logger(__name__)


class ResolutionAgent:
    """
    Executes resolution actions for discrepancies.

    This agent takes the decisions made by the Reconciler and actually
    executes them. Actions include:
    - Applying new aliases
    - Re-extracting fields from PDF
    - Creating human review tasks
    - Updating workflow state

    The Resolver has the authority to auto-apply high-confidence changes.
    """

    def __init__(self, pdf_extractor, alias_db: AliasDatabase):
        """
        Initialize the resolution agent.

        Args:
            pdf_extractor: PDFExtractor instance for re-extraction
            alias_db: AliasDatabase for applying aliases

        TODO: Implement this method
        Steps:
        1. Store pdf_extractor and alias_db as instance variables
        2. Set self.auto_apply_threshold = 0.85 (confidence threshold for auto-applying aliases)
        3. Log initialization
        """
        # TODO: Store dependencies
        # TODO: Set auto_apply_threshold
        logger.info("ResolutionAgent initialized")
        pass

    def execute(self, discrepancy: Discrepancy, workflow_state) -> Dict[str, Any]:
        """
        Execute the suggested action from the reconciler.

        This is the main execution method that routes to specific handlers.

        Args:
            discrepancy: Discrepancy object with suggested action
            workflow_state: Current workflow state

        Returns:
            Dictionary with:
            {
                'success': bool,
                'action': str,
                'resolved_value': Any (if success),
                'requires_human_review': bool
            }

        TODO: Implement this method
        Steps:
        1. Log the execution attempt
        2. Get suggested_action from discrepancy
        3. Route to appropriate handler based on action:
           - 'suggest_new_alias' -> self._handle_new_alias()
           - 'suggest_counterparty_alias' -> self._handle_counterparty_alias()
           - 'recheck_pdf' -> self._recheck_pdf_value()
           - 'flag_for_human' -> self._flag_for_human_review()
           - default -> self._flag_for_human_review()
        4. Log the result using workflow_state.add_step()
        5. Return the result dictionary

        HINT: Use a dictionary or if/elif chain for routing
        HINT: Always log the action taken
        """
        logger.info(f"Executing resolution for field: {discrepancy.field}")

        # TODO: Route to appropriate handler based on suggested_action
        # TODO: Call the handler method
        # TODO: Log the result with workflow_state.add_step()
        # TODO: Return result dictionary
        pass

    def _handle_new_alias(
        self, discrepancy: Discrepancy, workflow_state
    ) -> Dict[str, Any]:
        """
        Handle creating a new global alias.

        Decision logic:
        - If confidence >= auto_apply_threshold (0.85):
          * Auto-apply the alias
          * Update workflow_state.extracted_data with new value
          * Create pending alias record for later human approval
        - If confidence < threshold:
          * Create human review task
          * Don't auto-apply

        Args:
            discrepancy: Discrepancy with alias suggestion
            workflow_state: Current workflow state

        Returns:
            Result dictionary

        TODO: Implement this method
        Steps:
        1. Get suggested_alias from discrepancy
        2. Check if confidence >= self.auto_apply_threshold
        3. If yes (high confidence):
           a. Apply alias to alias_db:
              - alias_db.add_alias(field, from_value, to_value)
           b. Update workflow_state.extracted_data[field] = to_value
           c. Create PendingAlias record in database:
              - Get DB session
              - Create PendingAlias with status='PENDING'
              - Save to DB
           d. Log the auto-applied alias
           e. Return {success: True, action: 'auto_applied_alias', resolved_value: to_value, requires_human_review: False}
        4. If no (low confidence):
           a. Call self._create_human_review_task()
           b. Return {success: False, action: 'flagged_for_review', requires_human_review: True}

        HINT: Use next(get_db()) to get a database session
        HINT: Remember to commit the database transaction
        """
        logger.info(f"Handling new alias suggestion for field: {discrepancy.field}")

        # TODO: Check confidence threshold
        # TODO: If high confidence: auto-apply alias and create pending approval
        # TODO: If low confidence: create human review task
        # TODO: Return appropriate result
        pass

    def _handle_counterparty_alias(
        self, discrepancy: Discrepancy, workflow_state
    ) -> Dict[str, Any]:
        """
        Handle creating a counterparty-specific alias.

        Similar to _handle_new_alias but creates counterparty-specific mapping.

        Args:
            discrepancy: Discrepancy with alias suggestion
            workflow_state: Current workflow state

        Returns:
            Result dictionary

        TODO: Implement this method
        Steps similar to _handle_new_alias but:
        1. Get counterparty_id from workflow_state.extracted_data
        2. When adding alias: alias_db.add_alias(field, from, to, counterparty_id=counterparty_id)
        3. When creating PendingAlias: set counterparty_id field
        4. Return result

        HINT: This is very similar to _handle_new_alias, just with counterparty_id
        """
        logger.info(
            f"Handling counterparty alias suggestion for field: {discrepancy.field}"
        )

        # TODO: Similar to _handle_new_alias but with counterparty_id
        # TODO: Get counterparty_id from workflow_state
        # TODO: Apply counterparty-specific alias
        # TODO: Return result
        pass

    def _recheck_pdf_value(
        self, discrepancy: Discrepancy, workflow_state
    ) -> Dict[str, Any]:
        """
        Re-extract a specific field from the PDF with focused attention.

        This is used when the agent suspects the initial extraction might
        have been wrong (e.g., OCR error, unclear formatting).

        Args:
            discrepancy: Discrepancy for the field to recheck
            workflow_state: Current workflow state

        Returns:
            Result dictionary

        TODO: Implement this method
        Steps:
        1. Build a focused prompt for this specific field:
           - Example: f"Please carefully re-extract the {field} field. Look for labels like '{field}:', 'Party B:', etc. The expected value is around {expected_value}."
        2. Call pdf_extractor.extract_field():
           - new_value = self.pdf_extractor.extract_field(workflow_state.pdf_path, field, focused_prompt)
        3. If new_value is None or same as before:
           - Create human review task (extraction still unclear)
           - Return {success: False, requires_human_review: True}
        4. If new_value is different:
           - Update workflow_state.extracted_data[field] = new_value
           - Log the recheck with workflow_state.add_step()
           - Check if new_value matches expected_value
           - If matches: Return {success: True, action: 'rechecked_and_corrected', resolved_value: new_value, requires_human_review: False}
           - If still doesn't match: Continue with reconciliation (return partial success)
        5. Return result

        HINT: Use discrepancy.reasoning to build the focused prompt
        HINT: Re-extraction might still not match - that's OK, at least we tried
        """
        logger.info(f"Rechecking PDF value for field: {discrepancy.field}")

        # TODO: Build focused prompt for re-extraction
        # TODO: Call pdf_extractor.extract_field()
        # TODO: Compare new value with original and expected
        # TODO: Update workflow_state if value changed
        # TODO: Return result
        pass

    def _flag_for_human_review(
        self, discrepancy: Discrepancy, workflow_state
    ) -> Dict[str, Any]:
        """
        Create a human review task for this discrepancy.

        This is the fallback when the agent can't confidently resolve the issue.

        Args:
            discrepancy: Discrepancy that needs human review
            workflow_state: Current workflow state

        Returns:
            Result dictionary

        TODO: Implement this method
        Steps:
        1. Get database session
        2. Create HumanReviewTask record:
           - confirmation_id = workflow_state.confirmation_id
           - field = discrepancy.field
           - extracted_value = str(discrepancy.extracted_value)
           - expected_value = str(discrepancy.expected_value)
           - agent_reasoning = discrepancy.reasoning
           - status = ReviewTaskStatus.PENDING
        3. Save to database
        4. Log the task creation
        5. Return {success: False, action: 'flagged_for_human', requires_human_review: True}

        HINT: Import ReviewTaskStatus from database.db
        HINT: Don't forget to commit the transaction
        """
        logger.info(f"Flagging field for human review: {discrepancy.field}")

        # TODO: Get database session
        # TODO: Create HumanReviewTask record
        # TODO: Save to database
        # TODO: Log task creation
        # TODO: Return result indicating human review needed
        pass

    def _create_human_review_task(
        self, discrepancy: Discrepancy, workflow_state
    ) -> None:
        """
        Helper method to create human review task.

        This is called by other methods when they need to flag something for review.

        Args:
            discrepancy: Discrepancy to review
            workflow_state: Current workflow state

        TODO: Implement this method (similar to _flag_for_human_review)
        This should be the same logic as _flag_for_human_review
        but doesn't return a result - just creates the task.
        """
        # TODO: Create HumanReviewTask record (same as _flag_for_human_review)
        pass
