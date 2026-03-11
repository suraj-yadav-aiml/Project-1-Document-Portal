from pathlib import Path
from typing import Tuple, BinaryIO, Union
import fitz  # PyMuPDF

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

class DocumentIngestion:
    """Handles document ingestion operations including PDF reading, saving, and combining."""

    def __init__(self, base_dir: Union[str, Path] = "data/document_compare") -> None:
        """
        Initialize DocumentIngestion with base directory.

        Args:
            base_dir: Base directory for document operations. Can be str or Path.
        """
        try:
            self.log = CustomLogger().get_logger(__name__)
            
            self.base_dir = Path(base_dir)
            self.base_dir.mkdir(parents=True, exist_ok=True)
            
            self.log.info(
                "DocumentIngestion initialized successfully",
                base_dir=str(self.base_dir)
            )
            
        except Exception as e:
            self.log.error("Error initializing DocumentIngestion", error=str(e))
            raise DocumentPortalException("Error initializing DocumentIngestion") from e
    
    def delete_existing_files(self) -> int:
        """
        Deletes existing PDF files in the base directory.

        Returns:
            int: Number of files deleted
            
        Raises:
            DocumentPortalException: If file deletion fails
        """
        try:
            files_deleted = 0
            
            if self.base_dir.exists() and self.base_dir.is_dir():
                for file_path in self.base_dir.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() == ".pdf":
                        file_path.unlink()
                        files_deleted += 1
                        self.log.info("PDF file deleted", path=str(file_path))
                
                self.log.info(
                    "Directory cleaned successfully",
                    directory=str(self.base_dir),
                    files_deleted=files_deleted
                )
            
            return files_deleted
            
        except Exception as e:
            self.log.error(
                "Error deleting existing files",
                directory=str(self.base_dir),
                error=str(e)
            )
            raise DocumentPortalException("An error occurred while deleting existing files") from e
    
    def save_uploaded_files(self, reference_file: BinaryIO, actual_file: BinaryIO) -> Tuple[Path, Path]:
        """
        Saves uploaded files to the base directory after cleaning existing files.

        Args:
            reference_file: Reference file object (Streamlit UploadedFile or similar)
            actual_file: Actual file object (Streamlit UploadedFile or similar)
            
        Returns:
            Tuple[Path, Path]: Paths to saved reference and actual files
            
        Raises:
            DocumentPortalException: If file saving fails
        """
        try:
            if not hasattr(reference_file, 'name') or not hasattr(actual_file, 'name'):
                raise DocumentPortalException("Invalid file objects: missing name attribute")
            
            self.delete_existing_files()
            self.log.info("Existing files deleted successfully")

            ref_filename = Path(reference_file.name).name
            act_filename = Path(actual_file.name).name
            
            if not ref_filename.lower().endswith(".pdf"):
                raise DocumentPortalException(f"Reference file must be PDF: {ref_filename}")
            
            if not act_filename.lower().endswith(".pdf"):
                raise DocumentPortalException(f"Actual file must be PDF: {act_filename}")

            ref_path = self.base_dir / ref_filename
            act_path = self.base_dir / act_filename


            try:
                with open(ref_path, "wb") as f:
                    f.write(reference_file.getbuffer())
            except Exception as e:
                raise DocumentPortalException(f"Failed to save reference file: {str(e)}") from e

            try:
                with open(act_path, "wb") as f:
                    f.write(actual_file.getbuffer())
            except Exception as e:
                raise DocumentPortalException(f"Failed to save actual file: {str(e)}") from e

            self.log.info(
                "Files saved successfully",
                reference_file_path=str(ref_path),
                actual_file_path=str(act_path),
                ref_size=ref_path.stat().st_size if ref_path.exists() else 0,
                act_size=act_path.stat().st_size if act_path.exists() else 0
            )
            
            return ref_path, act_path
            
        except Exception as e:
            self.log.error(
                "Error saving uploaded files",
                error=str(e),
                error_type=type(e).__name__
            )
            raise DocumentPortalException(f"An error occurred while saving uploaded files: {str(e)}") from e
    
    def read_pdf(self, pdf_path: Union[str, Path]) -> str:
        """
        Reads a PDF file and extracts text from each page.

        Args:
            pdf_path: Path to the PDF file. Can be str or Path.
            
        Returns:
            str: Extracted text from all pages with page markers
            
        Raises:
            DocumentPortalException: If PDF reading fails
        """
        try:
            pdf_file_path = Path(pdf_path)

            if not pdf_file_path.exists():
                raise DocumentPortalException(f"PDF file not found: {pdf_file_path}")
            
            if not pdf_file_path.is_file():
                raise DocumentPortalException(f"Path is not a file: {pdf_file_path}")

            with fitz.open(str(pdf_file_path)) as doc:
                if doc.is_encrypted:
                    raise DocumentPortalException(f"PDF is encrypted: {pdf_file_path.name}")
                
                all_text = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    if text.strip():
                        all_text.append(f"\n--- Page {page_num + 1} ---\n{text}")
                
                extracted_text = "\n".join(all_text)
                
                self.log.info(
                    "PDF read successfully",
                    file=str(pdf_file_path),
                    pages=len(all_text),
                    characters=len(extracted_text)
                )
                
                return extracted_text
                
        except fitz.FileDataError as e:
            self.log.error("Invalid PDF file format", pdf_file_path=str(pdf_path), error=str(e))
            raise DocumentPortalException(f"Invalid PDF file format: {str(e)}") from e
        except Exception as e:
            self.log.error(
                "Error reading PDF",
                file=str(pdf_path),
                error=str(e),
                error_type=type(e).__name__
            )
            raise DocumentPortalException(f"An error occurred while reading the PDF: {str(e)}") from e
    
    def combine_documents(self) -> str:
        """
        Combines all PDF documents in the base directory into a single text.

        Returns:
            str: Combined text from all documents with document markers
            
        Raises:
            DocumentPortalException: If document combination fails
        """
        try:
            content_dict = {}
            doc_parts = []
            
            # Find all PDF files
            pdf_files = [
                f for f in self.base_dir.iterdir() 
                if f.is_file() and f.suffix.lower() == ".pdf"
            ]
            
            if not pdf_files:
                raise DocumentPortalException("No PDF files found in directory for combination")
            
            # Read each PDF file
            for pdf_file in sorted(pdf_files):
                try:
                    content = self.read_pdf(pdf_file)
                    content_dict[pdf_file.name] = content
                    self.log.debug(
                        "Document read for combination",
                        pdf_file_path=str(pdf_file),
                        characters=len(content)
                    )
                except Exception as e:
                    self.log.warning(
                        "Failed to read document for combination",
                        pdf_file_path=str(pdf_file),
                        error=str(e)
                    )
                    raise DocumentPortalException("Failed to read the document for combination")

            if not content_dict:
                raise DocumentPortalException("No documents could be read for combination")

            for filename, content in content_dict.items():
                doc_parts.append(f"Document: {filename}\n{content}")

            combined_text = "\n\n" + "\n\n".join(doc_parts) + "\n\n"
            
            self.log.info(
                "Documents combined successfully",
                document_count=len(doc_parts),
                total_characters=len(combined_text),
                documents=list(content_dict.keys())
            )
            
            return combined_text

        except Exception as e:
            self.log.error(
                "Error combining documents",
                error=str(e),
                error_type=type(e).__name__
            )
            raise DocumentPortalException(f"An error occurred while combining documents: {str(e)}") from e