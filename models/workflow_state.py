"""
Workflow State Management - SKELETON
IMPLEMENT THE TODOs

This module tracks the state of a confirmation as it moves through the agent system.
Think of this as the "memory" that allows agents to see what previous agents did.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AgentStep(BaseModel):
    """
    Represents a single action taken by an agent.

    Attributes:
        timestamp: When the action occurred
        agent: Name of the agent (e.g., 'Extractor', 'Reconciler', 'Resolver')
        action: Description of the action taken
        result: Dictionary containing the result data
    """

    timestamp: datetime
    agent: str
    action: str
    result: Dict[str, Any]


class AgentDecision(BaseModel):
    """
    Represents a decision made by an agent.

    Attributes:
        agent: Name of the agent making the decision
        reasoning: Why the agent made this decision
        decision: The decision made (e.g., 'suggest_new_alias', 'flag_for_human')
        confidence: Confidence score (0.0 to 1.0)
    """

    agent: str
    reasoning: str
    decision: str
    confidence: float


class WorkflowState:
    """
    Tracks the state of a confirmation as it moves through the agent system.

    This is the central state object that gets passed between agents and accumulates
    all the information about what happened during processing.

    Attributes:
        confirmation_id: Unique ID for this confirmation
        pdf_path: Path to the uploaded PDF file
        steps: List of all actions taken by agents
        decisions: List of all decisions made by agents
        retries: Number of times processing has been retried
        max_retries: Maximum allowed retries
        status: Current status (e.g., 'processing', 'completed', 'failed')
        confidence: Overall confidence score (0.0 to 1.0)
        extracted_data: The data extracted from the PDF
        validation_result: Result from the validation layers
    """

    def __init__(self, confirmation_id: str, pdf_path: str):
        """
        Initialize a new workflow state.

        Args:
            confirmation_id: Unique identifier for this confirmation
            pdf_path: Path to the PDF file being processed
        """
        self.confirmation_id = confirmation_id
        self.pdf_path = pdf_path
        self.steps: List[AgentStep] = []
        self.decisions: List[AgentDecision] = []
        self.retries = 0
        self.max_retries = 3
        self.status = "processing"
        self.confidence = 0.0
        self.extracted_data: Dict[str, Any] = {}
        self.validation_result = None

    def add_step(self, agent: str, action: str, result: Dict[str, Any]) -> None:
        """
        Log an action taken by an agent.

        This creates a permanent record in the workflow history that can be
        reviewed later to understand what happened during processing.

        Args:
            agent: Name of the agent (e.g., 'Reconciler', 'Resolver')
            action: Description of what was done (e.g., 'applied_global_alias', 'rechecked_pdf')
            result: Dictionary with details about the result

        Example:
            state.add_step('Reconciler', 'applied_global_alias', {
                'field': 'counterparty',
                'from': 'JPM',
                'to': 'JP Morgan Chase'
            })

        TODO: Implement this method
        Steps:
        1. Create an AgentStep instance with timestamp=datetime.utcnow()
        2. Append it to self.steps
        3. Log this step using the logging utility (import from utils.logging_config)
           Format: f"{agent}: {action} - {result}"
        """
        # TODO: Create AgentStep with current timestamp
        # TODO: Append to self.steps
        # TODO: Log the step with logging.info()
        pass

    def add_decision(
        self, agent: str, reasoning: str, decision: str, confidence: float = 0.0
    ) -> None:
        """
        Log a decision made by an agent.

        Decisions are different from steps - they represent choices the agent made
        about how to handle a situation (e.g., "should I suggest an alias or flag for human?").

        Args:
            agent: Name of the agent making the decision
            reasoning: Why the agent made this decision
            decision: The decision made (e.g., 'suggest_new_alias', 'flag_for_human')
            confidence: How confident the agent is (0.0 to 1.0)

        Example:
            state.add_decision(
                'Reconciler',
                'JPM is 90% similar to existing alias JP Morgan Chase',
                'suggest_new_alias',
                0.9
            )

        TODO: Implement this method
        Steps:
        1. Create an AgentDecision instance
        2. Append it to self.decisions
        3. Optionally log the decision
        """
        # TODO: Create AgentDecision instance
        # TODO: Append to self.decisions
        pass

    def can_retry(self) -> bool:
        """
        Check if we can retry processing this confirmation.

        We limit retries to prevent infinite loops when an agent can't resolve
        an issue.

        Returns:
            True if retries < max_retries, False otherwise

        TODO: Implement this method
        Return True if self.retries < self.max_retries
        """
        # TODO: Return True if retries < max_retries
        pass

    def increment_retry(self) -> None:
        """
        Increment the retry counter.

        Call this when starting a new retry attempt.

        TODO: Implement this method
        Simply increment self.retries by 1
        """
        # TODO: Increment self.retries
        pass

    def to_dict(self) -> Dict:
        """
        Convert the entire state to a dictionary for API responses or database storage.

        This is useful for:
        - Returning state to the API caller
        - Storing state in the database
        - Debugging and logging

        Returns:
            Dictionary containing all state information

        Expected format:
        {
            'confirmation_id': str,
            'status': str,
            'confidence': float,
            'retries': int,
            'steps': List[dict],  # Each AgentStep as dict
            'decisions': List[dict],  # Each AgentDecision as dict
            'extracted_data': dict,
            'validation_result': dict or None
        }

        TODO: Implement this method
        Steps:
        1. Convert each AgentStep to dict using .dict() method
        2. Convert each AgentDecision to dict using .dict() method
        3. Return a dictionary with all the fields listed above
        """
        # TODO: Create dictionary with all state fields
        # TODO: Convert steps list to list of dicts
        # TODO: Convert decisions list to list of dicts
        # TODO: Return the complete dictionary
        pass
