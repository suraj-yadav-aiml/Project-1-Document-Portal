import os
import uuid
import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime, timezone

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException


class DocumentHandler:
    """Handles document operations like saving and reading PDF files."""

    def __init__(self, data_dir: Optional[Path] = None, session_id: Optional[str] = None) -> None:
        """
        Initialize DocumentHandler with data directory and session.

        Args:
            data_dir: Directory to store documents (uses env var or default if None).
            session_id: Unique session identifier (auto-generated if None).
        """
        try:
            self.log = CustomLogger().get_logger(__name__)

            self.data_dir = (
                data_dir or
                Path.cwd() / "data" / "document_analysis"
            )
            self.data_dir.mkdir(parents=True, exist_ok=True)

            self.log.info("Data directory ?",data_dir_path=self.data_dir)

            self.session_id = (
                session_id or
                f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            )

            self.session_path = self.data_dir / self.session_id
            self.session_path.mkdir(exist_ok=True)

        except Exception as e:
            self.log.error("Error initializing the Document Handler", error=str(e))
            raise DocumentPortalException("Error initializing the Document Handler") from e

    
    def save_pdf(self, uploaded_file: BinaryIO) -> Path:
        """
        Save an uploaded PDF file to the session directory.

        Args:
            uploaded_file: A file-like object with a .name attribute and .getbuffer() method.

        Returns:
            Path to the saved PDF file.

        Raises:
            DocumentPortalException: If the file is not a PDF or cannot be saved.
        """
        try:
            file_name = Path(uploaded_file.name).name

            if not file_name.lower().endswith(".pdf"):
                raise DocumentPortalException("Invalid file type. Only PDF files are allowed.")

            saved_pdf_path = self.session_path / file_name

            with open(saved_pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            self.log.info(
                "PDF file saved successfully.",
                pdf_file_name=file_name,
                pdf_file_path=str(saved_pdf_path),
                session_id=self.session_id,
            )

            return saved_pdf_path

        except Exception as e:
            self.log.error(
                "Error saving the PDF file",
                pdf_file_name=getattr(uploaded_file, "name", "unknown"),
                error=str(e)
            )
            raise DocumentPortalException("Error saving the PDF file") from e
    

    def read_pdf(self, pdf_file_path: Path) -> str:
        """
        Extract text from a PDF file.

        Args:
            pdf_file_path: Path to the PDF file.

        Returns:
            Full text extracted from the PDF.

        Raises:
            DocumentPortalException: If the file cannot be read or parsed.
        """
        try:
            if not pdf_file_path.exists():
                raise DocumentPortalException(f"PDF file does not exist: {pdf_file_path}")

            text_chunks = []
            with fitz.open(str(pdf_file_path)) as doc:
                for page_num, page in enumerate(doc, start=1):
                    text_chunks.append(f"\n--- Page {page_num} ---\n{page.get_text()}")

            full_text = "\n".join(text_chunks)

            self.log.info(
                "PDF read successfully.",
                pdf_path=str(pdf_file_path),
                session_id=self.session_id,
                pages=len(text_chunks),
            )

            return full_text

        except Exception as e:
            self.log.error("Error reading the PDF file", pdf_path=str(pdf_file_path), error=str(e))
            raise DocumentPortalException("Error reading the PDF file") from e


if __name__ == "__main__":

    class DummyFile:
        def __init__(self,file_path):
            self.name = Path(file_path).name
            self._file_path = file_path
        
        def getbuffer(self):
            return open(file=self._file_path, mode='rb').read()
    
    pdf_file_path = r"D:\KrishNaik\LLMOOPs-Projects\Project-1-Document-Portal\data\document_analysis\NIPS-2017-attention-is-all-you-need-Paper.pdf"
    dummy_pdf = DummyFile(file_path=pdf_file_path)

    handler = DocumentHandler()

    try:
        saved_pdf_path = handler.save_pdf(uploaded_file=dummy_pdf)
        print(saved_pdf_path)

        pdf_content = handler.read_pdf(pdf_file_path=saved_pdf_path)
        print(f"PDF Content\n{pdf_content[:500]}")
    except Exception as e:
        print(f"Error : \n{str(e)}")
