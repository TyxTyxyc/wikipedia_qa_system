import logging
import os
import re
from collections.abc import AsyncIterable
from typing import Any

from openai import AsyncOpenAI

from src.constants import ACTION_PLAN_PROMPT, MAX_ITERATIONS, MODEL_FAIL_TEXT, DOUBLE_CHECK_PROMPT
from src.state import MessagesState

logger = logging.getLogger(__name__)


class WikipediaQAAgent(object):
    """
    Agent capable of answering to arbitrary questions by
    planning and executing queries to Wikipedia
    """

    def __init__(self, tools_registrar):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        model_name = os.getenv("OPENAI_MODEL_NAME")

        if not api_key or not base_url:
            err_msg = "Please set OPENAI_API_KEY, OPENAI_BASE_URL and OPENAI_MODEL_NAME"
            logger.error(err_msg)
            raise Exception(err_msg)

        self.openai_client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.deepseek.com",
        )

        self.tools_registrar = tools_registrar
        self.model_name = model_name
        logger.info("WikipediaQAAgent initialized")

    async def stream(self, prompt, session_id) -> AsyncIterable[dict[str, Any]]:
        logger.info(f"started work for session_id {session_id}")

        yield {
            "is_task_complete": False,
            "updates": f"received prompt: {prompt}, processing",
        }

        state = MessagesState()
        state.update(
            {
                "role": "user",
                "content": ACTION_PLAN_PROMPT.format(
                    tools_description=self.tools_registrar.get_tools_list(),
                    user_prompt=prompt,
                ),
            }
        )

        for i in range(MAX_ITERATIONS):
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=state.construct_prompt(),
                tools=self.tools_registrar.get_tools_list(),
            )

            resp_message = response.choices[0].message
            state.update(resp_message.model_dump())
            logger.info('resp_message')
            logger.info(resp_message)

            if response.choices[0].finish_reason == "stop":
                # double check result
                state.update(
                    {
                        "role": "assistant",
                        "content": DOUBLE_CHECK_PROMPT
                    }
                )
                check_response = await self.openai_client.chat.completions.create(
                    model=self.model_name,
                    messages=state.construct_prompt(),
                )
                check_message = check_response.choices[0].message
                logger.info('check_message')
                logger.info(check_message)
                if "ok" not in check_message.content:
                    state.update(check_message.model_dump())
                    continue
                
                # extract final answer of the agent
                res = re.findall(
                    r"<final_answer>([\s\S]*)</final_answer>", resp_message.content
                )

                if len(res) > 1:
                    logger.warning("Model returned several finish tags")

                if len(res) == 0:
                    model_answer = MODEL_FAIL_TEXT
                else:
                    model_answer = res[0]

                yield {
                    "is_task_complete": True,
                    "updates": resp_message.content,
                    "result": model_answer
                }
                return

            yield {
                "is_task_complete": False,
                "updates": resp_message.content,
            }

            for tool_call in resp_message.tool_calls:
                call_result = self.tools_registrar.tool_call(
                    tool_call.function.name, **eval(tool_call.function.arguments)
                )

                # TODO: pydantic it
                tool_result_msg = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": call_result,
                }

                state.update(tool_result_msg)

                yield {
                    "is_task_complete": False,
                    "updates": f"tool {tool_call.function.name} called",
                }

        yield {
            "is_task_complete": True,
            "updates": "max iterations achieved",
            "result": MODEL_FAIL_TEXT,
        }
