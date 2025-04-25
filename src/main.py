import os
import logging
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeInterpreterTool, 
    BingGroundingTool, 
    ToolSet, 
    OpenApiConnectionAuthDetails, 
    OpenApiConnectionSecurityScheme,
    OpenApiTool,
    )
from azure.identity import DefaultAzureCredential
from pathlib import Path
import jsonref
from utilities import Utilities


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

load_dotenv()

AGENT_NAME = os.getenv("AGENT_NAME")
AGENT_ID = os.getenv("AGENT_ID")
API_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME")
PROJECT_CONNECTION_STRING = os.environ["PROJECT_CONNECTION_STRING"]
BING_CONNECTION_NAME = os.getenv("BING_CONNECTION_NAME")
TRIPADVISOR_CONNECTION_ID = os.getenv("TRIPADVISOR_CONNECTION_KEY")
MAX_COMPLETION_TOKENS = 10240
MAX_PROMPT_TOKENS = 20480
# The LLM is used to generate the SQL queries.
# Set the temperature and top_p low to get more deterministic results.
TEMPERATURE = 0.6
TOP_P = 0.7
INSTRUCTIONS_FILE = "instructions/instructions.txt"

def initialize_tools():
    # Create bing grounding tool
    bing_connection = project_client.connections.get(
        connection_name=BING_CONNECTION_NAME
    )
    conn_id = bing_connection.id
    bing = BingGroundingTool(connection_id=conn_id)
    
    # Create code interpreter tool
    code_interpreter = CodeInterpreterTool()

    # Create Tripadvisor
    with open('./src/tripadvisor_openapi.json', 'r') as f:
        tripadvisor_spec = jsonref.loads(f.read())

    # Create Auth object for the OpenApiTool (note that connection or managed identity auth setup requires additional setup in Azure)
    auth = OpenApiConnectionAuthDetails(security_scheme=OpenApiConnectionSecurityScheme(connection_id=TRIPADVISOR_CONNECTION_ID))

    # Initialize agent Tripadvisor tool using the read in OpenAPI spec
    tripadvisor = OpenApiTool(name="tripadvisor", spec=tripadvisor_spec, description="Retrieve trip information for a location", auth=auth)
    
    # Create toolset of tools
    toolset = ToolSet()
    toolset.add(bing)
    toolset.add(code_interpreter)
    toolset.add(tripadvisor)
    return toolset


def load_instruction():
    try:
        instructions = utilities.load_instructions(INSTRUCTIONS_FILE)
        return instructions
    
    except Exception as e:
        logger.error("An error occurred initializing the agent: %s", str(e))
        logger.error("Please ensure you've enabled an instructions file.")
        

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(exclude_environment_credential=True, exclude_managed_identity_credential=True), 
    conn_str=PROJECT_CONNECTION_STRING
)

with project_client:
    toolset = initialize_tools()
    utilities = Utilities()
    instructions = load_instruction()
    
    agent = project_client.agents.create_agent(
        model=API_DEPLOYMENT_NAME,
        name="my-agent",
        instructions=instructions,
        toolset=toolset,
    )
    print(f"Created agent, agent ID: {agent.id}")

    # Create a thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    # Create a message
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Can you tell me your instruction?",
    )
    print(f"Created message, message ID: {message.id}")
        

    # Run the agent
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        # Check if you got "Rate limit is exceeded.", then you want to get more quota
        print(f"Run failed: {run.last_error}")

    # Get messages from the thread
    messages = project_client.agents.list_messages(thread_id=thread.id)
    
    # Uncomment to see the raw messages JSON
    print(f"Messages: {messages}")

    # Get the last message from the sender
    last_msg = messages.get_last_text_message_by_role("assistant")
    if last_msg:
        print(f"Last agent message: {last_msg.text.value}")

    # Generate an image file for the chart
    for image_content in messages.image_contents:
        print(f"Image File ID: {image_content.image_file.file_id}")
        file_name = f"{image_content.image_file.file_id}_image_file.png"
        project_client.agents.save_file(file_id=image_content.image_file.file_id, file_name=file_name)
        print(f"Saved image file to: {Path.cwd() / file_name}")

    # Delete the agent once done
    # project_client.agents.delete_agent(agent.id)
    # print("Deleted agent")
