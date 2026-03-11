from typing import List, Dict, Any
from dotenv import load_dotenv
import pandas as pd

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable

from model.models import SummaryResponse, PromptType
from prompt.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException


class DocumentComparatorLLM:
    """Compares documents using LLMs and returns structured comparison results."""

    def __init__(self, llm_provider: str = "openai") -> None:
        """
        Initialize DocumentComparatorLLM with LLM, parsers, and prompt.

        Args:
            llm_provider: Provider name for the LLM (default: "google")
        """
        try:
            load_dotenv()
            
            self.log = CustomLogger().get_logger(__name__)

            prompt_key = PromptType.DOCUMENT_COMPARISON.value
            if prompt_key not in PROMPT_REGISTRY:
                raise KeyError(prompt_key)
            
            self.prompt: ChatPromptTemplate = PROMPT_REGISTRY[prompt_key]
            self.loader = ModelLoader()
            self.llm: BaseLanguageModel = self.loader.load_llm(llm_provider=llm_provider)
            self.parser: JsonOutputParser = JsonOutputParser(pydantic_object=SummaryResponse)
            
            self.chain: Runnable = self.prompt | self.llm | self.parser
            
            self.log.info(
                "DocumentComparatorLLM initialized successfully",
                llm_provider=llm_provider
            )
            
        except KeyError as e:
            self.log.error(
                "Prompt for document comparison not found in PROMPT_REGISTRY",
                prompt_key_not_found=str(e)
            )
            raise DocumentPortalException("Required prompt not found") from e
        except Exception as e:
            self.log.error("Error initializing DocumentComparatorLLM", error=str(e))
            raise DocumentPortalException("Error initializing DocumentComparatorLLM") from e
    
    def compare_documents(self, combined_docs: str) -> pd.DataFrame:
        """
        Compares documents and returns a structured comparison as DataFrame.

        Args:
            combined_docs: Combined text of documents to compare
            
        Returns:
            pd.DataFrame: Structured comparison results with 'Page' and 'Changes' columns
            
        Raises:
            DocumentPortalException: If comparison fails or input is invalid
        """
        try:
            if not combined_docs or not combined_docs.strip():
                raise DocumentPortalException("Combined documents text cannot be empty")
            
            if not isinstance(combined_docs, str):
                raise DocumentPortalException("Combined documents must be a string")

            inputs = {
                "combined_docs": combined_docs.strip(),
                "format_instruction": self.parser.get_format_instructions()
            }
            
            self.log.info(
                "Starting document comparison",
                document_length=len(combined_docs)
            )
            
            response: List[Dict[str, str]] = self.chain.invoke(inputs)  # [{'Page': '1', 'Changes': 'Fixed grammatical errors'}, 
                                                                        # {'Page': '3', 'Changes': 'Updated outdated references'}, 
                                                                        # {'Page': '5', 'Changes': 'Added new section on methodology'}]
            
            if not isinstance(response, list):
                raise DocumentPortalException(f"Invalid response type from LLM: expected list, got {type(response)}")
            
            self.log.info(
                "Document comparison completed successfully",
                response_items=len(response)
            )
            
            return self._format_response(response)

        except Exception as e:
            self.log.error(
                "Error in compare_documents",
                error=str(e),
                error_type=type(e).__name__
            )
            raise DocumentPortalException(f"An error occurred while comparing documents: {str(e)}") from e


    def _format_response(self, response_parsed: List[Dict[str, str]]) -> pd.DataFrame:
        """
        Formats the response from the LLM into a structured DataFrame.

        Args:
            response_parsed: List of dictionaries from LLM response
                           Each dict has 'Page' and 'Changes' keys
            
        Returns:
            pd.DataFrame: Formatted comparison results with 'Page' and 'Changes' columns
            
        Raises:
            DocumentPortalException: If formatting fails
        """
        try:
            if not isinstance(response_parsed, list):
                raise DocumentPortalException("Response must be a list of dictionaries")
            
            if not response_parsed:
                self.log.warning("Empty response received from LLM")
                return pd.DataFrame(columns=['Page', 'Changes'])

            # Process and validate each item
            validated_data = []
            for i, item in enumerate(response_parsed):
                if not isinstance(item, dict):
                    self.log.warning(f"Skipping invalid item at index {i}: expected dict, got {type(item)}")
                    continue
                    
                validated_data.append({
                    'Page': str(item.get('Page', '')),
                    'Changes': str(item.get('Changes', ''))
                })

            df = pd.DataFrame(validated_data, columns=['Page', 'Changes'])
            
            self.log.info(
                "Response formatted into DataFrame successfully",
                dataframe_shape=df.shape,
                columns=list(df.columns)
            )
            
            return df
            
        except Exception as e:
            self.log.error(
                "Error formatting response into DataFrame",
                error=str(e),
                error_type=type(e).__name__
            )
            raise DocumentPortalException("Error formatting response into structured format") from e