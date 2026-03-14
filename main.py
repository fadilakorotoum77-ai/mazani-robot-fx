import os
import httpx
import uvicorn
import yfinance as yf
import pandas as pd
from fastapi import FastAPI, Request

app = FastAPI()

# Récupération des clés Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def analyze_market():
    """L'intelligence qui évite le hasard"""
    try:
        # On récupère l'Or en direct (2026)
        gold = yf.Ticker("GC=F")
        df = gold.history(period="5d", interval="1h")
        
        # Filtre EMA Institutionnel
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        
        price = round(df['Close'].iloc[-1], 2)
        ema20 = df['EMA20'].iloc[-1]
        ema50 = df['EMA50'].iloc[-1]
        
        # Logique de décision
        if price > ema20 > ema50:
            return "🔥 TENDANCE FORTE HAUSSIÈRE", price, "✅ CONFIRMÉ"
        elif price < ema20 < ema50:
            return "❄️ TENDANCE FORTE BAISSIÈRE", price, "✅ CONFIRMÉ"
        else:
            return "⚠️ ZONE DE HASARD (Attendre)", price, "❌ RISQUÉ"
    except:
        return "Analyse indisponible", 0, "❌"

@app.post("/webhook")
async def handle_signal(request: Request):
    diag, prix, statut = analyze_market()
    
    msg = (f"🤖 **MAZANI ROBOT FX - IA**\n\n"
           f"💰 PRIX RÉEL : **{prix} $**\n"
           f"📊 ANALYSE : {diag}\n"
           f"🛡️ FILTRE : **{statut}**\n\n"
           f"💡 *Le marché transfère l'argent des actifs vers les patients.*")
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    return {"ok": True}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
