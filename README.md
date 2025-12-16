# wikipedia_qa_system

An agent which can make queries to Wikipedia in order to answer person's questions

Operates in Russian

## Prerequisites
- Python 3.12 or higher

## Setup
1. **Install deps**
   ```bash
   pip install -r requirements.txt
   ```
2. **Create .env file**
   ```bash
   OPENAI_API_KEY="your key to OpenAI-compatible model"
   OPENAI_BASE_URL="url to the model"
   OPENAI_MODEL_NAME="name of the model to use"
   ```

## Run
   Agent will be deployed on localhost:9001 by default
   ```bash
   python main.py
   ```
   You can specify other host/port in cmd:
   ```bash
   python main.py --host localhost --port 9001
   ```

## Client-side (async supported)
```python
import httpx
from a2a.client import A2ACardResolver, A2AClient

httpx_client = httpx.AsyncClient(timeout=60)
agent = 'http://localhost:9001/'
card_resolver = A2ACardResolver(httpx_client, agent)
card = await card_resolver.get_agent_card()
client = A2AClient(httpx_client, agent_card=card)

task_id = None
context_id = uuid4().hex

prompt = "Сколько понадобится времени гепарду, чтобы пересечь Москву-реку по Большому Каменному мосту?"

message = Message(
    role='user',
    parts=[TextPart(text=prompt)],
    message_id=str(uuid4()),
    task_id=task_id,
    context_id=context_id,
)

payload = MessageSendParams(
    id=str(uuid4()),
    message=message,
    configuration=MessageSendConfiguration(
        accepted_output_modes=['text'],
    ),
)

response_stream = client.send_message_streaming(
    SendStreamingMessageRequest(
        id=str(uuid4()),
        params=payload,
    )
)

async for result in response_stream:
    print(result)
   ```
   
