# Test code for document ingestion and analysis using a DocumentHandler  and DocumentAnalyzer

import os
from pathlib import Path
from typing import Dict, Any
from src.document_analyzer.data_ingestion import DocumentHandler    
from src.document_analyzer.data_analysis import DocumentAnalyzer  

PDF_PATH = r"D:\KrishNaik\LLMOOPs-Projects\Project-1-Document-Portal\data\document_analysis\NIPS-2017-attention-is-all-you-need-Paper.pdf"

class DummyFile:
    """Simulates an uploaded file (Streamlit style)"""
    
    def __init__(self, file_path: str) -> None:
        self.name = Path(file_path).name
        self._file_path = file_path

    def getbuffer(self) -> bytes:
        """Read and return file content as bytes"""
        with open(self._file_path, "rb") as f:
            return f.read()


def main():
    try:
        # ---------- STEP 1: DATA INGESTION ----------
        print("Starting PDF ingestion...")

        if not os.path.exists(PDF_PATH):
            raise FileNotFoundError(f"Test PDF not found at: {PDF_PATH}")
        
        dummy_pdf = DummyFile(PDF_PATH)

        handler = DocumentHandler(session_id="test_ingestion_analysis")
        
        saved_path = handler.save_pdf(dummy_pdf)
        print(f"PDF saved at: {saved_path}")

        text_content = handler.read_pdf(saved_path)
        print(f"Extracted text length: {len(text_content)} chars\n")

        # ---------- STEP 2: DATA ANALYSIS ----------
        print("Starting metadata analysis...")
        analyzer = DocumentAnalyzer()  # Loads LLM + parser
        
        analysis_result: Dict[str, Any] = analyzer.analyze_document(text_content)

        # ---------- STEP 3: DISPLAY RESULTS ----------
        print("\n=== METADATA ANALYSIS RESULT ===")
        for key, value in analysis_result.items():
            print(f"{key}: {value}")

    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    main()