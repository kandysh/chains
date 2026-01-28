"""
PDF Extractor Agent - SKELETON
IMPLEMENT THE TODOs

This is where your LangChain PDF extraction logic goes.
This agent is responsible for extracting trade data from PDF confirmations.
"""

import os
from typing import Dict, Any, Optional
from utils.logging_config import get_logger

logger = get_logger(__name__)


class PDFExtractor:
    """
    Extracts trade data from PDF confirmations using LangChain + OpenAI.

    This is the first agent in the pipeline. Its job is to:
    1. Read the PDF file
    2. Extract all relevant trade fields
    3. Return structured data

    The quality of extraction is critical - all downstream agents depend on this.
    """

    def __init__(self):
        """
        Initialize the PDF extractor with LangChain components.

        TODO: Implement this method
        Steps:
        1. Import required LangChain components:
           - from langchain.chat_models import ChatOpenAI
           - from langchain.document_loaders import PyPDFLoader
           - from langchain.prompts import ChatPromptTemplate
           - (or use your existing LangChain setup)
        2. Initialize your LLM:
           - self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
           - Or use whatever model you prefer
        3. Set up your extraction prompt template
        4. Initialize any other components you need

        HINT: This is where you put your existing LangChain extraction code
        HINT: Keep temperature=0 for consistent extraction
        """
        # TODO: Import LangChain components
        # TODO: Initialize self.llm
        # TODO: Set up prompt template
        # TODO: Initialize any other needed components
        logger.info("PDFExtractor initialized")
        pass

    def extract(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract all trade fields from a PDF confirmation.

        This is the main extraction method. It should:
        1. Load the PDF
        2. Extract text/content
        3. Use LLM to identify and extract structured fields
        4. Return a dictionary with all extracted data

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with extracted trade data in this format:
            {
                'trade_id': str,
                'counterparty': str,
                'notional': float or Decimal,
                'rate': str,
                'currency': str,
                'product': str,
                'trade_date': str (ISO format: 'YYYY-MM-DD'),
                'settlement_date': str (ISO format: 'YYYY-MM-DD')
            }

        Example output:
            {
                'trade_id': 'TR12345',
                'counterparty': 'JPM',
                'notional': 1000000,
                'rate': 'SOFR + 50',
                'currency': 'USD',
                'product': 'Interest Rate Swap',
                'trade_date': '2024-01-15',
                'settlement_date': '2024-01-17'
            }

        TODO: Implement this method
        Steps:
        1. Log the extraction attempt
        2. Load the PDF file:
           - Use PyPDFLoader or similar
           - Extract text content
        3. Create extraction prompt:
           - Ask LLM to extract all trade fields
           - Specify the exact fields you need
           - Request JSON output format
        4. Call LLM with the prompt
        5. Parse LLM response to extract structured data
        6. Validate that all required fields are present
        7. Return the extracted data dictionary

        HINT: This is where your existing PDF extraction code goes
        HINT: Use JSON mode if available: response_format={"type": "json_object"}
        HINT: Include example output in your prompt to guide the LLM
        HINT: Handle errors gracefully - PDF might be malformed
        """
        logger.info(f"Extracting data from PDF: {pdf_path}")

        # TODO: Load PDF file
        # TODO: Extract text/content from PDF
        # TODO: Create extraction prompt with all required fields
        # TODO: Call LLM to extract structured data
        # TODO: Parse LLM response to dictionary
        # TODO: Validate all fields are present
        # TODO: Return extracted data

        # Example return structure (remove this and implement actual extraction):
        # return {
        #     'trade_id': 'TR12345',
        #     'counterparty': 'JPM',
        #     'notional': 1000000,
        #     'rate': 'SOFR + 50',
        #     'currency': 'USD',
        #     'product': 'Interest Rate Swap',
        #     'trade_date': '2024-01-15',
        #     'settlement_date': '2024-01-17'
        # }
        pass

    def extract_field(
        self, pdf_path: str, field: str, focused_prompt: str
    ) -> Optional[str]:
        """
        Re-extract a specific field from the PDF with a focused prompt.

        This method is used by the Resolver agent when it wants to double-check
        a specific field value. The focused prompt helps guide the LLM to pay
        special attention to that field.

        Args:
            pdf_path: Path to the PDF file
            field: Name of the field to extract (e.g., 'counterparty', 'notional')
            focused_prompt: Specific prompt to guide extraction of this field

        Returns:
            Extracted value as string, or None if extraction fails

        Example:
            value = extractor.extract_field(
                'path/to/file.pdf',
                'counterparty',
                'Please carefully extract the counterparty name. Look for labels like "Counterparty:", "Party B:", or "Dealer:"'
            )

        TODO: Implement this method
        Steps:
        1. Log the focused extraction attempt
        2. Load the PDF (similar to extract method)
        3. Create a focused prompt that:
           - Explains what field to extract
           - Includes the focused_prompt parameter for guidance
           - Asks for just that single value
        4. Call LLM with focused prompt
        5. Parse and return the result
        6. Handle errors (return None if extraction fails)

        HINT: Use a lower temperature for focused extraction (temperature=0)
        HINT: This should be more careful/accurate than general extraction
        HINT: Include examples in the prompt specific to this field type
        """
        logger.info(f"Re-extracting field '{field}' from PDF: {pdf_path}")

        # TODO: Load PDF
        # TODO: Create focused prompt for this specific field
        # TODO: Call LLM
        # TODO: Parse and return result
        # TODO: Handle errors gracefully
        pass
