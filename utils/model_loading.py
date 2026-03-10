import os
from typing import Dict, List, Literal
from omegaconf.dictconfig import DictConfig

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from utils.config_loader import load_config
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

from dotenv import load_dotenv


log = CustomLogger().get_logger(__name__)

LLMProvider       = Literal["groq", "google", "openai"]
EmbeddingProvider = Literal["google", "openai"]
APIKeys           = Dict[str, str]


_REQUIRED_ENV_KEYS: list[str] = [
    "GOOGLE_API_KEY",
    "GROQ_API_KEY",
    "OPENAI_API_KEY",
]

_LLM_KEY_MAP: dict[str, str] = {
    "groq":      "GROQ_API_KEY",
    "google":    "GOOGLE_API_KEY",
    "openai":    "OPENAI_API_KEY",
}

_EMBEDDING_KEY_MAP: dict[str, str] = {
    "google": "GOOGLE_API_KEY",
    "openai": "OPENAI_API_KEY",
}


class ModelLoader: 
    """Handles loading of embedding models and LLMs based on configuration."""

    def __init__(self) -> None:
        """Initialize ModelLoader with environment validation and config loading."""
        load_dotenv()
        self.api_keys: APIKeys = self._validate_env()
        self.config: DictConfig = load_config()
        log.info(
            "ModelLoader initialized",
            config_keys=list(self.config.keys()),
        )

    def _validate_env(self) -> APIKeys:

        api_keys = {key: os.getenv(key, "") for key in _REQUIRED_ENV_KEYS}
        missing  = [k for k, v in api_keys.items() if not v]

        if missing:
            log.error("Missing environment variables", missing_env_keys=missing)
            raise DocumentPortalException(
                f"Missing required environment variables: {missing}"
            )

        log.info(
            "Environment variables validated",
            available_env_keys=list(api_keys.keys()),
        )
        return api_keys
    
    def _get_provider_config(self, section: str, provider: str) -> DictConfig:

        section_cfg = self.config[section]

        if provider not in section_cfg:
            log.error(
                "Provider not found in config",
                section=section,
                provider=provider,
            )
            raise DocumentPortalException(
                f"Provider '{provider}' not found under config['{section}']. "
                f"Available: {list(section_cfg.keys())}"
            )

        return section_cfg[provider]
    
    def load_llm(
        self,
        llm_provider: LLMProvider = "openai",
    ) -> BaseChatModel:

        log.info("Loading LLM", provider=llm_provider)

        try:
            cfg         = self._get_provider_config("llm", llm_provider)
            model_name  = cfg.model_name
            temperature = cfg.temperature
            max_tokens  = cfg.max_tokens
            api_key     = self.api_keys[_LLM_KEY_MAP[llm_provider]]

            if llm_provider == "groq":
                llm = ChatGroq(
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=api_key,
                )

            elif llm_provider == "google":
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    api_key=api_key,
                )

            elif llm_provider == "openai":
                llm = ChatOpenAI(
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=api_key,
                )

            log.info(
                "LLM loaded successfully",
                llm_provider=llm_provider,
                model=model_name,
            )
            return llm
  
        except Exception as e:
            log.error("Error loading LLM", provider=llm_provider, error=str(e))
            raise DocumentPortalException(f"Error loading LLM for provider '{llm_provider}'") from e
    
    def load_embeddings(
        self,
        embedding_provider: EmbeddingProvider = 'openai',
    ) -> Embeddings:
 
        log.info("Loading embedding model", provider=embedding_provider)

        try:
            cfg        = self._get_provider_config("embedding_model", embedding_provider)
            model_name = cfg.model_name
            api_key    = self.api_keys[_EMBEDDING_KEY_MAP[embedding_provider]]

            if embedding_provider == "google":
                embeddings = GoogleGenerativeAIEmbeddings(
                    model=model_name,
                    google_api_key=api_key,
                )

            elif embedding_provider == "openai":
                embeddings = OpenAIEmbeddings(
                    model=model_name,
                    api_key=api_key,
                )

            else:
                raise DocumentPortalException(
                    f"Embedding provider '{provider}' is not supported. "
                    f"Supported: {list(_EMBEDDING_KEY_MAP.keys())}"
                )

            log.info(
                "Embedding model loaded successfully",
                provider=embedding_provider,
                model=model_name,
            )
            return embeddings
        except Exception as e:
            log.error("Error loading the embedding model", error=str(e))
            raise DocumentPortalException("Error loading the embedding model") from e


if __name__ == "__main__":
    loader = ModelLoader()
    llm = loader.load_llm()
    result=llm.invoke("Hello, how are you?")
    print(f"LLM Result: {result.content}")
