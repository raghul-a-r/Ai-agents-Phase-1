# 🚀 5-Agent Autonomous NSE Trading System

## ⭐ NEW FEATURES

✅ **Portfolio Analyzer** - Runs 9:30 AM Mon-Fri, provides insights to Market Scout  
✅ **Market Scout** - Updates watchlist based on portfolio gaps (runs 9:32 AM)  
✅ **Automated Scheduling** - Agents run at specific times automatically  
✅ **Countdown Timers** - UI shows when agents run next  
✅ **Intelligent Watchlist** - Auto-adds/removes stocks with reasoning  
✅ **Complete Workflow** - Portfolio Analysis → Stock Discovery → Trading  

---

## 📅 AGENT SCHEDULE

**9:30 AM Mon-Fri:** Portfolio Analyzer analyzes portfolio health  
**9:32 AM Mon-Fri:** Market Scout updates watchlist based on portfolio gaps  
**9:35 AM:** Agent Analysis on updated watchlist  
**11:30 AM:** Agent Analysis  
**1:30 PM:** Agent Analysis  

---

## 🎓 FOR PROFESSOR: SCHEDULE CODE LOCATIONS

### **`market_hours.py`**
- **Lines 10-12:** Market hours config (9:30 AM - 3:30 PM IST)
- **Lines 58-62:** Portfolio Analyzer schedule (9:30 AM Mon-Fri)
- **Lines 89-92:** Market Scout schedule (9:32 AM Mon-Fri)
- **Lines 109-114:** Agent Analysis schedule (3x daily)

### **`main.py`**
- **Lines 261-272:** Portfolio Analyzer trigger
- **Lines 277-295:** Market Scout trigger + immediate Agent Analysis
- **Lines 305-310:** Scheduled Agent Analysis runs

---

## 🚀 QUICK START

```bash
# For 4:30 PM demo (no time restrictions):
python main_demo.py

# For visual dashboard:
streamlit run app.py
```

---

## 📊 THE 5 AGENTS

1. **Technical Analyst** - Analyzes RSI, moving averages, trends
2. **Sentiment Analyst** - Analyzes news and market sentiment
3. **Decision Maker** - Synthesizes and makes final decisions
4. **Market Scout** ⭐ - Discovers stocks, manages watchlist
5. **Portfolio Analyzer** ⭐ - Analyzes portfolio health, identifies gaps

---

## 🔄 COMPLETE WORKFLOW

1. **9:30 AM:** Portfolio Analyzer finds gaps (e.g., "need IT stocks")
2. **9:32 AM:** Market Scout adds IT stocks to watchlist with reasoning
3. **9:35 AM:** Agent Analysis runs on updated watchlist
4. **11:30 AM & 1:30 PM:** Continued analysis and trading

---

## 📝 FILES INCLUDED

- `main.py` - WITH scheduling (for live operation)
- `main_demo.py` - NO scheduling (for 4:30 PM demo)
- `app.py` - Streamlit dashboard with countdown timers
- `market_hours.py` - All scheduling logic here
- `agents/market_scout.py` - Watchlist management
- `agents/portfolio_analyzer.py` - Portfolio analysis
- Plus all other agent and utility files

---

**Run `python main_demo.py` to see all 5 agents in action!** 🚀
