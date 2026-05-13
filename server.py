from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os

# 导入自定义模块
from config import SERVER_HOST, SERVER_PORT
from engines.tarot import TarotEngine
from engines.interpreter import AIInterpreter
from database import (
    register_user, login_user, get_user_by_token, logout_user,
    save_divination_log, get_user_logs
)

app = FastAPI(title="MysticForetell API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 临时内存存储（实际项目建议使用 Redis）
sessions = {}

# 数据模型
class CardInResponse(BaseModel):
    name: str
    status: str
    meaning: str
    element: str
    image_desc: str
    deep_meaning: str = ""

class InterpretRequest(BaseModel):
    cards: List[CardInResponse]
    spread_type: str
    user_context: Optional[str] = ""

class ShuffleRequest(BaseModel):
    question: str
    spread: str

class AuthRequest(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = ""

# ========== 用户认证 API ==========

@app.post("/api/auth/register")
async def api_register(req: AuthRequest):
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    if len(req.username) < 2 or len(req.username) > 20:
        raise HTTPException(status_code=400, detail="用户名长度需要在2-20个字符之间")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度至少6位")
    
    result = register_user(req.username, req.password, req.nickname)
    if not result["success"]:
        raise HTTPException(status_code=409, detail=result["message"])
    return result

@app.post("/api/auth/login")
async def api_login(req: AuthRequest):
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    
    result = login_user(req.username, req.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result

@app.post("/api/auth/logout")
async def api_logout(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token:
        logout_user(token)
    return {"success": True}

@app.get("/api/auth/me")
async def api_me(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="登录已过期")
    return user

@app.get("/api/auth/history")
async def api_history(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="登录已过期")
    logs = get_user_logs(user["id"])
    return {"logs": logs}

# ========== 占卜 API ==========

@app.post("/api/tarot/shuffle")
async def shuffle_deck(request: ShuffleRequest):
    session_id = str(uuid.uuid4())
    deck = TarotEngine.get_shuffled_deck()
    # 存储洗好的牌以及用户的上下文
    sessions[session_id] = {
        "deck": deck,
        "question": request.question,
        "spread": request.spread
    }
    return {"session_id": session_id, "total": len(deck)}

@app.get("/api/tarot/reveal/{session_id}/{index}")
async def reveal_card(session_id: str, index: int):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    deck = sessions[session_id]["deck"]
    if index < 0 or index >= len(deck):
        raise HTTPException(status_code=400, detail="Invalid card index")
    
    card_info = deck[index]
    detail = TarotEngine.get_card_detail(card_info['name'], card_info['is_reverse'])
    return detail

@app.post("/api/interpret")
async def interpret(request: InterpretRequest, req: Request):
    try:
        cards_data = [c.model_dump() for c in request.cards]
        
        # 增加元素分析逻辑
        elements = [c['element'] for c in cards_data]
        element_counts = {e: elements.count(e) for e in set(elements)}
        
        content = await AIInterpreter.get_interpretation(
            cards_data, 
            request.spread_type, 
            request.user_context,
            element_analysis=element_counts
        )
        
        # 保存占卜日志
        token = req.headers.get("Authorization", "").replace("Bearer ", "")
        user = get_user_by_token(token) if token else None
        save_divination_log(
            user_id=user["id"] if user else None,
            username=user["nickname"] if user else "游客",
            question=request.user_context or "未指定问题",
            spread_type=request.spread_type,
            cards=[{"name": c["name"], "status": c["status"]} for c in cards_data],
            interpretation=content
        )
        
        return {"interpretation": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== 静态文件托管 ==========
# 挂载静态资源目录（注意：必须在 API 路由之后挂载，否则会拦截 API 请求）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/css", StaticFiles(directory=os.path.join(BASE_DIR, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(BASE_DIR, "js")), name="js")
app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, "assets")), name="assets")

@app.get("/")
async def serve_index():
    """根路径直接返回 index.html"""
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
