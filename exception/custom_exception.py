import sys
import traceback
from typing import Union

from logger.custom_logger import CustomLogger


logger = CustomLogger().get_logger(__file__)


class DocumentPortalException(Exception):

    def __init__(self, error_message: Union[str, Exception]) -> None:
 
        self.error_message: str = str(error_message)

        super().__init__(self.error_message)

        exc_type, exc_value, exc_tb = sys.exc_info()

        self.file_name: str = (
            exc_tb.tb_frame.f_code.co_filename
            if exc_tb is not None
            else "<unknown>"
        )
        self.line_number: int = (
            exc_tb.tb_lineno if exc_tb is not None else -1
        )
        self.traceback_str: str = (
            "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            if exc_tb is not None
            else ""
        )


    def __str__(self) -> str:
        return (
            f"Error in [{self.file_name}] at line [{self.line_number}]\n"
            f"Message : {self.error_message}\n"
            f"Traceback:\n{self.traceback_str}"
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.error_message!r})"


    def log(self, *, include_traceback: bool = True) -> None:

        if include_traceback:
            logger.error(str(self))
        else:
            logger.error(
                "Error in [%s] at line [%d]: %s",
                self.file_name,
                self.line_number,
                self.error_message,
            )


if __name__ == "__main__":
    try:
        result = 1 / 0
        print(result)
    except ZeroDivisionError as e:
        app_exc = DocumentPortalException(e)
        app_exc.log()                    
        raise app_exc from e   
