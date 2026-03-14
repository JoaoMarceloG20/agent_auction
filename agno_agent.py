from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.os import AgentOS
#from agno.os.interfaces.whatsapp import Whatsapp

from prompts import AGENT_DESCRIPTION, AGENT_INSTRUCTIONS, AGENT_KNOWLEDGE

agent_db = SqliteDb(db_file="agno.db")

agno_auction = Agent(
    name="SDR AceleraGen",
    model=Claude(id="claude-sonnet-4-6"),
    db=agent_db,
    description=AGENT_DESCRIPTION,
    instructions=AGENT_INSTRUCTIONS,
    additional_context=AGENT_KNOWLEDGE,
    add_datetime_to_context=True,
    add_history_to_context=True,
    enable_session_summaries=True,           
    add_session_summary_to_context=True,
    num_history_runs=10,
    read_chat_history=True,
    markdown=True,

)

agent_os = AgentOS(
    agents=[agno_auction],
    ###interfaces=[Whatsapp(agent=agno_auction)],
)

app = agent_os.get_app()

# Configure CORS to allow AgentOS dashboard to connect
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://os.agno.com", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
