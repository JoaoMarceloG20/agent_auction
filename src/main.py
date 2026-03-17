import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
#from langchain.agents.structured import StructuredAgent
from prompts import AGENT_DESCRIPTION, AGENT_INSTRUCTIONS, AGENT_KNOWLEDGE


load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "MEU_VERIFY_TOKEN")


agent = create_agent(
    model="claude-sonnet-4-6",
    #tools="",
    system_prompt=AGENT_DESCRIPTION + AGENT_INSTRUCTIONS + AGENT_KNOWLEDGE,
    checkpointer = InMemorySaver(),
)


config = {"configurable": {"thread_id": "default"}}

# print("Agente iniciado. Ctrl+C para sair.\n")
# while True:
#     try:
#         user_input = input("Você: ")
#         response = agent.invoke(
#             {"messages": [{"role": "user", "content": user_input}]},
#             config=config,
#         )
#         print(f"\nAgente: {response['messages'][-1].content}\n")
#     except KeyboardInterrupt:
#         print("\nEncerrando.")
#         break

app = FastAPI()

@app.get("/webhook/whatsapp")
async def verify_webhook(
    hub_mode: str = Query("", alias="hub.mode"),
    hub_challenge: str = Query("", alias="hub.challenge"),
    hub_verify_token: str = Query("", alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    return PlainTextResponse("Erro de verificação", status_code=403)

@app.post("/webhook/whatsapp")
async def receive_message(request: Request):
    data = await request.json()

    # Estrutura típica do payload do WhatsApp Cloud API
    entry = data.get("entry", [])[0] if data.get("entry") else None
    if not entry:
        return JSONResponse({"status": "no_entry"})

    changes = entry.get("changes", [])[0]
    value = changes.get("value", {})
    messages = value.get("messages", [])

    if not messages:
        # Pode ser um evento de status, ignore
        return JSONResponse({"status": "no_messages"})

    message = messages[0]
    from_number = message.get("from")       # número do usuário
    text = message.get("text", {}).get("body", "")

    if not text:
        return JSONResponse({"status": "no_text"})

    # Chamar seu agente LangChain/LangGraph
    response = agent.invoke(
        {"messages": [{"role": "user", "content": text}]},
        config=config,
    )
    agent_reply = response["messages"][-1].content

    # Enviar resposta pelo WhatsApp
    send_whatsapp_message(to=from_number, text=agent_reply)

    return JSONResponse({"status": "ok"})


def send_whatsapp_message(to: str, text: str):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }

    r = httpx.post(url, headers=headers, json=payload)
    r.raise_for_status()
