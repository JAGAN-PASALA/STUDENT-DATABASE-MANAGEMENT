from fastapi import APIRouter, HTTPException, status
from app.schemas import ChatQueryRequest, ChatQueryResponse
from app.chatbot.graph import ask_agent

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])

@router.post("/", response_model=ChatQueryResponse)
def query_student_database(request: ChatQueryRequest):
    try:
        answer = ask_agent(request.query)
        return ChatQueryResponse(query=request.query, response=str(answer))
    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            err_msg = "Gemini API rate limit exceeded. Please wait a minute and retry."
            
        return ChatQueryResponse(
            query=request.query,
            response=f"⚠️ Notice: {err_msg}"
        )