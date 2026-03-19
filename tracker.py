"""
Tracking System - Logs every step of the document generation process.
Tracks token usage, timing, status, and costs into a JSON file.
"""
import json
import os
import time
from datetime import datetime
from typing import Optional
from config import TRACKING_DIR


class ProcessTracker:
    """Tracks the entire document generation pipeline and saves to JSON."""

    def __init__(self, job_id: str):
        self.job_id = job_id
        self.file_path = os.path.join(TRACKING_DIR, f"{job_id}.json")
        self.data = {
            "job_id": job_id,
            "status": "initialized",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "user_inputs": {},
            "document_plan": {},
            "total_tokens": {
                "input": 0,
                "output": 0,
                "total": 0,
            },
            "cost_estimate_usd": 0.0,
            "total_duration_seconds": 0,
            "steps": [],
            "errors": [],
        }
        self._start_time = time.time()
        self._log_lines: list[str] = []
        self._save()

    def _save(self):
        """Persist current tracking data to JSON file."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def log(self, message: str):
        """Append a timestamped log line for live debug output."""
        elapsed = round(time.time() - self._start_time, 1)
        line = f"[{elapsed:>7.1f}s] {message}"
        self._log_lines.append(line)

    def get_logs(self) -> list[str]:
        """Return all log lines."""
        return self._log_lines

    def set_status(self, status: str):
        """Update overall job status."""
        self.data["status"] = status
        self.data["total_duration_seconds"] = round(time.time() - self._start_time, 2)
        self._save()

    def set_user_inputs(self, inputs: dict):
        """Store the user's input details."""
        self.data["user_inputs"] = inputs
        self._save()

    def set_document_plan(self, plan: dict):
        """Store the generated document plan/outline."""
        self.data["document_plan"] = plan
        self._save()

    def start_step(self, step_name: str, description: str = "") -> str:
        """Begin tracking a new step. Returns the step ID."""
        step = {
            "step_id": f"step_{len(self.data['steps']) + 1}",
            "step_name": step_name,
            "description": description,
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "duration_seconds": 0,
            "tokens": {"input": 0, "output": 0, "total": 0},
            "llm_calls": 0,
        }
        self.data["steps"].append(step)
        self.data["status"] = f"running: {step_name}"
        self._save()
        return step["step_id"]

    def complete_step(
        self,
        step_id: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        llm_calls: int = 1,
        status: str = "completed",
    ):
        """Mark a step as completed and record token usage."""
        for step in self.data["steps"]:
            if step["step_id"] == step_id:
                step["status"] = status
                step["completed_at"] = datetime.now().isoformat()
                step["tokens"]["input"] = input_tokens
                step["tokens"]["output"] = output_tokens
                step["tokens"]["total"] = input_tokens + output_tokens
                step["llm_calls"] = llm_calls

                # Calculate duration
                started = datetime.fromisoformat(step["started_at"])
                completed = datetime.fromisoformat(step["completed_at"])
                step["duration_seconds"] = round(
                    (completed - started).total_seconds(), 2
                )
                break

        # Update totals
        self._update_totals()
        self._save()

    def fail_step(self, step_id: str, error: str):
        """Mark a step as failed."""
        for step in self.data["steps"]:
            if step["step_id"] == step_id:
                step["status"] = "failed"
                step["completed_at"] = datetime.now().isoformat()
                break

        self.data["errors"].append(
            {
                "step_id": step_id,
                "error": error,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self._save()

    def _update_totals(self):
        """Recalculate total token usage and cost."""
        total_input = sum(s["tokens"]["input"] for s in self.data["steps"])
        total_output = sum(s["tokens"]["output"] for s in self.data["steps"])

        self.data["total_tokens"]["input"] = total_input
        self.data["total_tokens"]["output"] = total_output
        self.data["total_tokens"]["total"] = total_input + total_output

        # Cost estimation (GPT-4o pricing: $2.50/1M input, $10/1M output)
        input_cost = (total_input / 1_000_000) * 2.50
        output_cost = (total_output / 1_000_000) * 10.00
        self.data["cost_estimate_usd"] = round(input_cost + output_cost, 4)

        self.data["total_duration_seconds"] = round(
            time.time() - self._start_time, 2
        )

    def complete_job(self, output_file: str = ""):
        """Mark the entire job as completed."""
        self.data["status"] = "completed"
        self.data["completed_at"] = datetime.now().isoformat()
        self.data["total_duration_seconds"] = round(
            time.time() - self._start_time, 2
        )
        if output_file:
            self.data["output_file"] = output_file
        self._update_totals()
        self._save()

    def fail_job(self, error: str):
        """Mark the entire job as failed."""
        self.data["status"] = "failed"
        self.data["completed_at"] = datetime.now().isoformat()
        self.data["total_duration_seconds"] = round(
            time.time() - self._start_time, 2
        )
        self.data["errors"].append(
            {"step_id": "job", "error": error, "timestamp": datetime.now().isoformat()}
        )
        self._save()

    def get_progress(self) -> dict:
        """Get current progress summary for frontend display."""
        total_steps = len(self.data["steps"])
        completed_steps = sum(
            1 for s in self.data["steps"] if s["status"] == "completed"
        )
        current_step = None
        for s in self.data["steps"]:
            if s["status"] == "in_progress":
                current_step = s["step_name"]
                break

        return {
            "job_id": self.job_id,
            "status": self.data["status"],
            "progress": f"{completed_steps}/{total_steps}",
            "progress_pct": round(
                (completed_steps / total_steps * 100) if total_steps > 0 else 0
            ),
            "current_step": current_step,
            "total_tokens": self.data["total_tokens"]["total"],
            "cost_usd": self.data["cost_estimate_usd"],
            "duration_seconds": round(time.time() - self._start_time, 2),
        }

    def load(self) -> dict:
        """Load tracking data from file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        return self.data
