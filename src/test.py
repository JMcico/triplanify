from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str="eastus.api.azureml.ms;43b6c267-0ba5-4555-ae31-5f2c67344699;triplanify.ai;triplanifyai")

agent = project_client.agents.get_agent("asst_gFX71fIQImneiuBkEjLM5jUs")

thread = project_client.agents.create_thread()

message = project_client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="Hi Tripadvisor, can you help me make a plan for traveling in Paris?"
)

run = project_client.agents.create_and_process_run(
    thread_id=thread.id,
    agent_id=agent.id)
messages = project_client.agents.list_messages(thread_id=thread.id)

for text_message in messages.text_messages:
    print(text_message.as_dict())