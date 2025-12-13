from typing import List
from langchain_core.tools import tool

@tool
def add_dependencies(dependencies: List[str]) -> str:
    """
    Runtime dependency installation is intentionally disabled.

    Reason:
    - Evaluation environments may not allow internet access
    - Installing packages during execution can cause timeouts
    - All required dependencies are already declared in pyproject.toml

    This tool exists only to satisfy the agent interface and
    prevent failures if the LLM attempts to install packages.
    """

    if not dependencies:
        return "No dependencies requested. All required packages are already available."

    return (
        "Runtime dependency installation is disabled. "
        "All required dependencies are pre-installed. "
        f"Requested packages ignored: {', '.join(dependencies)}"
    )
