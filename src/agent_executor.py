import logging
from typing import override

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, TextPart, UnsupportedOperationError
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError

from src.agent import WikipediaQAAgent
from src.tools import get_tool_registrar

logger = logging.getLogger(__name__)


class WikipediaQAAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = WikipediaQAAgent(get_tool_registrar())

    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        query = context.get_user_input()
        if not query:
            logger.warning("No user input found in context.")
            return
        task = context.current_task

        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        logger.info(
            f"Executing VideoGenerationAgent for task {task.id} with query: '{query}'"
        )

        await self.process_request(query, updater)

    async def process_request(
        self,
        query: str,
        task_updater: TaskUpdater
    ):
        async for item in self.agent.stream(query, task_updater.context_id):
            if item["is_task_complete"] == True:
                task_status = TaskState.completed
                result = item["result"]
            else:
                task_status = TaskState.working

            logger.info(f"updates are {item['updates']}")
            agent_update_message = new_agent_text_message(
                item["updates"], task_updater.context_id, task_updater.task_id
            )

            if task_status == TaskState.completed:
                final_message_obj = new_agent_text_message(
                    "task completed", task_updater.context_id, task_updater.task_id
                )
                await task_updater.add_artifact([TextPart(text=result)])
                await task_updater.complete(final_message_obj)
                break

            await task_updater.update_status(task_status, agent_update_message)

    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise ServerError(error=UnsupportedOperationError())
