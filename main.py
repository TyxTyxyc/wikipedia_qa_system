import logging

import click
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from dotenv import load_dotenv

from src.agent_executor import WikipediaQAAgentExecutor

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", default="localhost", help="Hostname to bind the server to.")
@click.option("--port", default=9001, help="Port to bind the server to.")
def main(host, port):
    try:
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="wikipedia_qa_system",
            name="Wikipedia Q&A system (in Russian)",
            description="Answers to arbitrary question using queries to wikipedia."
            "Works in Russian",
            tags=["qa", "text"],
            examples=["Что такое сепулькарий?"],
        )

        agent_card = AgentCard(
            name="Wikipedia Q&A system (in Russian)",
            description="Answers to arbitrary question using queries to wikipedia (in Russian).",
            url=f"http://{host}:{port}/",
            version="0.0.1",
            default_input_modes=["text"],
            default_output_modes=["text"],
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=WikipediaQAAgentExecutor(), task_store=InMemoryTaskStore()
        )

        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )

        logger.info(f"Starting Wikipedia Q&A system server on http://{host}:{port}")

        uvicorn.run(server.build(), host=host, port=port)

    except Exception as e:
        logger.error(f"Error occured during serve {e}")
        exit(1)


if __name__ == "__main__":
    main()
