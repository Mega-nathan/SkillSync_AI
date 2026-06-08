import logging
from typing import Callable, Optional

# Setup logger
logger = logging.getLogger(__name__)


class ProgressManager:
    """Manages progress signaling throughout the analysis pipeline."""

    def __init__(self, callback: Optional[Callable] = None):
        """
        Initialize progress manager.
        
        Args:
            callback: Optional async function to send progress updates
        """
        self.callback = callback
        self.current_step = 0
        self.total_steps = 6
        self.steps_log = []

    async def update_step(self, step_name: str, status: str, data: Optional[dict] = None):
        """
        Update progress step.
        
        Args:
            step_name: Name of the step
            status: Status message
            data: Additional data to include
        """
        self.current_step += 1
        progress_data = {
            "step": step_name,
            "status": status,
            "step_number": self.current_step,
            "total_steps": self.total_steps,
            "percentage": (self.current_step / self.total_steps) * 100,
            "data": data or {}
        }

        # Log the progress
        logger.info(f"✓ PROGRESS [{self.current_step}/{self.total_steps}] {step_name}: {status}")
        self.steps_log.append(progress_data)

        # Send callback if provided
        if self.callback:
            await self.callback(progress_data)

        return progress_data

    def log_data(self, label: str, data: any):
        """Log intermediate data for debugging."""
        logger.info(f"📊 DATA: {label}")
        if isinstance(data, str):
            logger.info(f"   {data[:200]}..." if len(data) > 200 else f"   {data}")
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    logger.info(f"   {key}: {value[:100]}..." if len(value) > 100 else f"   {key}: {value}")
                else:
                    logger.info(f"   {key}: {value}")
        elif isinstance(data, list):
            logger.info(f"   Total items: {len(data)}")
            for idx, item in enumerate(data[:3]):
                logger.info(f"   [{idx}] {item}")
            if len(data) > 3:
                logger.info(f"   ... and {len(data) - 3} more")

    def get_summary(self):
        """Get progress summary."""
        return {
            "total_steps": self.total_steps,
            "completed_steps": self.current_step,
            "steps_log": self.steps_log
        }
