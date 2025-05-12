from typing import List, Optional
from dataclasses import dataclass
from rich import print
from rich.console import Console
from rich.panel import Panel

@dataclass
class CompilerError:
    message: str
    lineno: Optional[int] = None
    filename: Optional[str] = None
    
    def __str__(self) -> str:
        location = f" in {self.filename}" if self.filename else ""
        line_info = f" at line {self.lineno}" if self.lineno else ""
        return f"Error{location}{line_info}: {self.message}"

class ErrorManager:
    def __init__(self):
        self.errors: List[CompilerError] = []
        self.console = Console()
    
    def add_error(self, message: str, lineno: Optional[int] = None, filename: Optional[str] = None):
        """Add a new error to the error list"""
        self.errors.append(CompilerError(message, lineno, filename))
    
    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0
    
    def print_errors(self):
        """Print all accumulated errors in a nice format"""
        if not self.errors:
            return
            
        self.console.print("\n[bold red]Compilation Errors:[/bold red]")
        for error in self.errors:
            self.console.print(Panel(str(error), style="red"))
        self.console.print()
    
    def clear(self):
        """Clear all errors"""
        self.errors.clear()

# Global error manager instance
error_manager = ErrorManager()

def error(message: str, lineno: Optional[int] = None, filename: Optional[str] = None):
    """Add a new error to the global error manager"""
    error_manager.add_error(message, lineno, filename)

def errors_detected() -> bool:
    """Check if there are any errors in the global error manager"""
    return error_manager.has_errors()

def print_errors():
    """Print all errors from the global error manager"""
    error_manager.print_errors()

def clear_errors():
    """Clear all errors from the global error manager"""
    error_manager.clear() 