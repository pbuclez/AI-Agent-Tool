"""
The Bug Hunter tool runs alongside the main coding agent to detect bugs
in the agent's implementation and provide feedback.
"""

import asyncio
import logging
import os
from typing import Any, Optional, List
from utils.common import LLMTool, ToolImplOutput, DialogMessages
from utils.llm_client import LLMClient, TextResult, TextPrompt
from utils.workspace_manager import WorkspaceManager


class BugHunterTool(LLMTool):
    """A simple tool that analyzes code for bugs."""
    
    name = "bug_hunter"
    description = """Analyze code for bugs and issues. Detects syntax errors, logic errors, and common problems."""
    
    input_schema = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The code to analyze for bugs"
            },
            "file_path": {
                "type": "string",
                "description": "Optional file path for context"
            }
        },
        "required": ["code"]
    }
    
    def __init__(self, client: LLMClient, workspace_manager: WorkspaceManager):
        super().__init__()
        self.client = client
        self.workspace_manager = workspace_manager
        self.logger = logging.getLogger(__name__)
    
    def run_impl(self, tool_input: dict[str, Any], dialog_messages: Optional[DialogMessages] = None) -> ToolImplOutput:
        """Analyze code for bugs and return a report."""
        code = tool_input["code"]
        file_path = tool_input.get("file_path", "unknown")
        
        self.logger.info(f"Analyzing code in {file_path}")
        
        prompt = f"""Analyze this code for bugs and issues:

File: {file_path}

```python
{code}
```

Respond with:
- "NO_BUGS" if the code looks correct
- "BUGS_FOUND" followed by a list of specific issues if bugs are found

Be specific about what's wrong and suggest fixes."""

        try:
            response, _ = self.client.generate(
                messages=[[TextPrompt(text=prompt)]],
                max_tokens=1024,
                temperature=0.1
            )
            
            if response and isinstance(response[0], TextResult):
                analysis_result = response[0].text
                return ToolImplOutput(
                    tool_output=analysis_result,
                    tool_result_message=f"Bug analysis completed for {file_path}"
                )
            else:
                return ToolImplOutput(
                    tool_output="Failed to analyze code",
                    tool_result_message="Bug analysis failed"
                )
                
        except Exception as e:
            self.logger.error(f"Error in bug analysis: {e}")
            return ToolImplOutput(
                tool_output=f"Error during analysis: {str(e)}",
                tool_result_message="Bug analysis failed"
            )


class ParallelBugHunter:
    """Parallel bug hunter that monitors files and detects bugs."""
    
    def __init__(
        self,
        client: LLMClient,
        workspace_manager: WorkspaceManager,
        logger: logging.Logger,
        check_interval: float = 5.0
    ):
        self.client = client
        self.workspace_manager = workspace_manager
        self.logger = logger
        self.check_interval = check_interval
        
        self.bug_hunter_tool = BugHunterTool(client, workspace_manager)
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        
        self.on_bugs_found = None
    
    async def start(self):
        """Start the bug hunter."""
        if self.is_running:
            return
            
        self.is_running = True
        self.task = asyncio.create_task(self._monitor_loop())
        self.logger.info("Parallel bug hunter started")
        
    async def stop(self):
        """Stop the bug hunter."""
        self.is_running = False
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        self.logger.info("Parallel bug hunter stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        last_files = set()
        
        while self.is_running:
            try:
                current_files = self._get_python_files()
                
                new_files = current_files - last_files
                
                if new_files:
                    self.logger.info(f"Found {len(new_files)} new Python files")
                    
                    for file_path in new_files:
                        await self._check_file(file_path)
                
                last_files = current_files
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring: {e}")
                await asyncio.sleep(self.check_interval)
    
    def _get_python_files(self) -> set:
        """Get all Python files in workspace."""
        python_files = set()
        
        try:
            for root, dirs, files in os.walk(self.workspace_manager.root):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        python_files.add(file_path)
        except Exception as e:
            self.logger.error(f"Error getting Python files: {e}")
        
        return python_files
    
    async def _check_file(self, file_path: str):
        """Check a file for bugs."""
        try:
            # Skip large files
            if os.path.getsize(file_path) > 50000:
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            if len(code) < 50:
                return
            
            self.logger.info(f"Checking {file_path} for bugs")
            
            tool_input = {
                "code": code,
                "file_path": file_path
            }
            
            result = self.bug_hunter_tool.run_impl(tool_input)
            
            analysis_text = result.tool_output.lower()
            if analysis_text.startswith("bugs_found"):
                self.logger.warning(f"Bugs found in {file_path}")
                
                if self.on_bugs_found:
                    self.on_bugs_found(file_path, result.tool_output)

            elif analysis_text.startswith("no_bugs"):
                self.logger.info(f"No bugs found in {file_path}")
            else:
                # Fallback: check for common bug indicators
                bug_indicators = ["error", "bug", "issue", "problem", "fix", "wrong", "incorrect", "fails"]
                if any(indicator in analysis_text for indicator in bug_indicators):
                    self.logger.warning(f"Potential bugs found in {file_path} (fallback detection)")
                    if self.on_bugs_found:
                        self.on_bugs_found(file_path, result.tool_output)
                
        except Exception as e:
            self.logger.error(f"Error checking file {file_path}: {e}")