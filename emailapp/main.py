import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool, FilePurpose, FunctionTool, ToolSet
from pathlib import Path
from user_functions import send_email

# load environment variables from local .env file
load_dotenv()
PROJECT_CONNECTION_STRING = os.getenv("AZURE_AI_AGENT_PROJECT_CONNECTION_STRING")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")
FILE_PATH = Path(__file__).parent.parent / os.getenv("NBA_CSV_FILE_PATH")  # Adjusted to resolve relative path

# create ai project client
project_client = AIProjectClient.from_connection_string(
  conn_str=PROJECT_CONNECTION_STRING,
  credential=DefaultAzureCredential()
)
with project_client:

    # upload a file and add it to the client 
    file = project_client.agents.upload_file_and_poll(
        file_path=FILE_PATH, purpose=FilePurpose.AGENTS
    )
    print(f"Uploaded file, file ID: {file.id}")

    # create a code interpreter tool instance referencing the uploaded file
    code_interpreter = CodeInterpreterTool(file_ids=[file.id])

    # create an agent
    agent = project_client.agents.create_agent(
        model="gpt-4o-mini",
        name="assistant-coach-agent",
        instructions="You are a Basketball assistant coach that knows everything about the game of Basketball. You give advice about Basketball rules, training, statistics and strategies.",
        tools=code_interpreter.definitions,
        tool_resources=code_interpreter.resources,
    )
    print(f"Using agent: {agent.name}")

    # create a thread with message
    thread = project_client.agents.create_thread()
    print(f"Thread created: {thread.id}")

    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Could you please create a bar chart for 3Pointers made vs attempts during the NBA seasons 1996 until 2020 and save it as a .png file?",
    )

    # ask the agent to perform work on the thread
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)

    # fetch and print the conversation history including the last message
    print("\nConversation Log:\n")
    messages = project_client.agents.list_messages(thread_id=thread.id)
    for message_data in reversed(messages.data):
        last_message_content = message_data.content[-1]
        print(f"{message_data.role}: {last_message_content.text.value}\n")

    # fetch any generated files
    for file_path_annotation in messages.file_path_annotations:
        saved_file_name = Path(file_path_annotation.text).name
        project_client.agents.save_file(file_id=file_path_annotation.file_path.file_id, file_name=saved_file_name)
        print(f"File saved as {saved_file_name}")
        # Send email with the generated file attached
        recipient = os.getenv("EMAIL_RECIPIENT") or "your-recipient@example.com"
        subject = "Basketball AI Agent: Generated File"
        body = f"Please find the generated file '{saved_file_name}' attached."
        file_path = str(Path(saved_file_name).resolve())
        email_result = send_email(recipient, subject, body, file_path=file_path)
        print(f"Email send result: {email_result}")

    # clean up
    project_client.agents.delete_agent(agent.id)
    project_client.agents.delete_thread(thread.id)