# Test code for document ingestion and analysis using a DocumentHandler  and DocumentAnalyzer

# import os
# from pathlib import Path
# from typing import Dict, Any
# from src.document_analyzer.data_ingestion import DocumentHandler    
# from src.document_analyzer.data_analysis import DocumentAnalyzer  

# PDF_PATH = r"D:\KrishNaik\LLMOOPs-Projects\Project-1-Document-Portal\data\document_analysis\NIPS-2017-attention-is-all-you-need-Paper.pdf"

# class DummyFile:
#     """Simulates an uploaded file (Streamlit style)"""
    
#     def __init__(self, file_path: str) -> None:
#         self.name = Path(file_path).name
#         self._file_path = file_path

#     def getbuffer(self) -> bytes:
#         """Read and return file content as bytes"""
#         with open(self._file_path, "rb") as f:
#             return f.read()


# def main():
#     try:
#         # ---------- STEP 1: DATA INGESTION ----------
#         print("Starting PDF ingestion...")

#         if not os.path.exists(PDF_PATH):
#             raise FileNotFoundError(f"Test PDF not found at: {PDF_PATH}")
        
#         dummy_pdf = DummyFile(PDF_PATH)

#         handler = DocumentHandler(session_id="test_ingestion_analysis")
        
#         saved_path = handler.save_pdf(dummy_pdf)
#         print(f"PDF saved at: {saved_path}")

#         text_content = handler.read_pdf(saved_path)
#         print(f"Extracted text length: {len(text_content)} chars\n")

#         # ---------- STEP 2: DATA ANALYSIS ----------
#         print("Starting metadata analysis...")
#         analyzer = DocumentAnalyzer()  # Loads LLM + parser
        
#         analysis_result: Dict[str, Any] = analyzer.analyze_document(text_content)

#         # ---------- STEP 3: DISPLAY RESULTS ----------
#         print("\n=== METADATA ANALYSIS RESULT ===")
#         for key, value in analysis_result.items():
#             print(f"{key}: {value}")

#     except Exception as e:
#         print(f"Test failed: {e}")

# if __name__ == "__main__":
#     main()


# ---------------------------------------------------------------------------------------------------------------------------------



# Test Document Compare

import io
from pathlib import Path
from src.document_compare.data_ingestion import DocumentIngestion
from src.document_compare.document_comparator import DocumentComparatorLLM


def test_compare_docuemnts():
    ref_path = Path(r"D:\KrishNaik\LLMOOPs-Projects\Project-1-Document-Portal\data\Long_Report_V1.pdf")
    act_path = Path(r"D:\KrishNaik\LLMOOPs-Projects\Project-1-Document-Portal\data\Long_Report_V2.pdf")
    
    class FakeUpload:
        def __init__(self,file_path:Path):
            self.name = file_path.name
            self._buffer =  file_path.read_bytes()

        def getbuffer(self):
           return self._buffer
       
    comparator = DocumentIngestion()
    ref_upload = FakeUpload(ref_path)
    act_upload = FakeUpload(act_path)
    
    ref_file, act_file = comparator.save_uploaded_files(ref_upload, act_upload)
    combined_text = comparator.combine_documents()
    
    print("\n Combined Text Preview (First 1000 chars):\n")
    print(combined_text[:1000])
    
    llm_comparator = DocumentComparatorLLM()
    comparison_df = llm_comparator.compare_documents(combined_text)
    
    print("\n=== COMPARISON RESULT ===")
    print(comparison_df.head())
    
if __name__ == "__main__":
    test_compare_docuemnts()