# MTR DUAT - Parsers Package
"""
DOCX parsing modules for daily reports and manpower data extraction.
"""

__all__ = []

try:
    from .docx_parser import DailyReportParser, process_docx
    __all__.extend(["DailyReportParser", "process_docx"])
except ImportError:
    pass

try:
    from .manpower_parser import ManpowerParser
    __all__.append("ManpowerParser")
except ImportError:
    pass
