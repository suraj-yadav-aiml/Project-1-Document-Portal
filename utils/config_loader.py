from omegaconf import OmegaConf
from omegaconf.dictconfig import DictConfig
from pathlib import Path

def load_config(config_path: str = "config/config.yaml") -> DictConfig:
    """Load configuration with OmegaConf."""
    
    config_file = Path(config_path).resolve()

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    if not config_file.is_file():
        raise ValueError(f"Configuration path is not a file: {config_file}")

    try:
        return OmegaConf.load(config_file)
    except Exception as e:
        raise RuntimeError(f"Unexpected error loading configuration from '{config_path}': {str(e)}")


if __name__ == "__main__":

    config = load_config()
    print(config)
    print(type(config))                     # <class 'omegaconf.dictconfig.DictConfig'>
    print(config.faiss_db.collection_name)  # Clean dot notation
    print(config.retriever.top_k)           # Automatic type conversion
    print(type(config.retriever.top_k))

    print(list(config.keys()))

    print("llm" in config)

    model_name = "groq"
    print(config.llm.get(model_name))