from typing import Dict, Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from logger.custom_logger import CustomLogger 
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import Metadata, PromptType

class DocumentAnalyzer:
    """Analyzes documents using LLMs and extracts structured metadata."""

    def __init__(self, llm_provider: str = "openai") -> None:
        """
        Initialize DocumentAnalyzer with LLM, parsers, and prompt.

        Args:
            llm_provider: Provider name for the LLM (default: "openai")
        """
        try:
            self.log = CustomLogger().get_logger(__name__)
            prompt_key = PromptType.DOCUMENT_ANALYSIS.value
            if prompt_key not in PROMPT_REGISTRY:
                raise KeyError('document_analysis')
            
            self.prompt: ChatPromptTemplate = PROMPT_REGISTRY[prompt_key]
            self.llm: BaseLanguageModel = ModelLoader().load_llm(llm_provider=llm_provider)
            self.parser: JsonOutputParser = JsonOutputParser(pydantic_object=Metadata)
            self.chain: Runnable = self.prompt | self.llm | self.parser

            self.log.info(
                "DocumentAnalyzer initialized successfully",
                llm_provider=llm_provider
            )
        
        except KeyError as e:
            self.log.error(
                "Prompt for `Document Analysis` not found in PROMPT_REGISTRY",
                prompt_key_not_found='document_analysis'
            )
            raise DocumentPortalException("Required prompt not found") from e
        except Exception as e:
            self.log.error("Error initializing DocumentAnalyzer", error=str(e))
            raise DocumentPortalException("Error initializing DocumentAnalyzer") from e
    
    def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """
        Analyze document text and extract structured metadata.
        
        Args:
            document_text: Text content of the document to analyze
            
        Returns:
            Dict[str, Any]: Extracted metadata from the document
            
        Raises:
            DocumentPortalException: If analysis fails or input is invalid
        """
        try:
            if not document_text or not document_text.strip():
                raise DocumentPortalException("Document text cannot be empty")
            
            if not isinstance(document_text, str):
                raise DocumentPortalException("Document text must be a string")

            input_data = {
                'format_instructions': self.parser.get_format_instructions(),
                'document_text': document_text.strip()
            }

            response: Dict[str, Any] = self.chain.invoke(input=input_data)

            if not isinstance(response, dict):
                raise DocumentPortalException("Invalid response format from LLM")

            self.log.info(
                "Document analysis completed successfully",
                document_analysis_keys=list(response.keys()) if isinstance(response, dict) else [],
                characters_analyzed=len(document_text)
            )

            return response

        except Exception as e:
            self.log.error(
                "Document analysis failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise DocumentPortalException(f"Document analysis failed: {str(e)}") from e