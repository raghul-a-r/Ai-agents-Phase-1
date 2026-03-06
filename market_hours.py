"""
Market Hours Utility - Check if NSE market is open and scheduling logic
"""
from datetime import datetime, timedelta
import pytz

# ========================================
# PROFESSOR: MARKET HOURS CONFIGURATION
# Lines 10-12: Market operates 9:30 AM - 3:30 PM IST, Monday-Friday
# ========================================
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30

def is_market_open():
    """Check if NSE market is currently open (9:30 AM - 3:30 PM IST, Mon-Fri)"""
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # ========================================
    # PROFESSOR: MARKET HOURS CHECK
    # Lines 24-25: Market hours defined here
    # ========================================
    market_open_time = now.replace(hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MINUTE, second=0, microsecond=0)
    market_close_time = now.replace(hour=MARKET_CLOSE_HOUR, minute=MARKET_CLOSE_MINUTE, second=0, microsecond=0)
    
    # ========================================
    # PROFESSOR: WEEKDAY CHECK
    # Line 31: Monday = 0, Sunday = 6
    # Only trades Monday-Friday
    # ========================================
    is_weekday = now.weekday() < 5
    
    # Check if within market hours
    is_open = is_weekday and market_open_time <= now <= market_close_time
    
    return is_open, now

def get_market_status():
    """Get detailed market status message"""
    is_open, now = is_market_open()
    
    if is_open:
        return True, f"🟢 Market OPEN - Current time: {now.strftime('%I:%M %p IST')}"
    else:
        if now.weekday() >= 5:
            return False, f"🔴 Market CLOSED (Weekend) - {now.strftime('%A, %I:%M %p IST')}"
        else:
            return False, f"🔴 Market CLOSED - Market hours: 9:30 AM - 3:30 PM IST (Current: {now.strftime('%I:%M %p IST')})"

def should_run_portfolio_analyzer():
    """
    Portfolio Analyzer runs at 9:30 AM Monday-Friday (market open)
    
    ========================================
    PROFESSOR: PORTFOLIO ANALYZER SCHEDULE
    Lines 58-62: Runs ONCE per day at market open
    Only on weekdays (Monday-Friday)
    ========================================
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # Check if weekday
    if now.weekday() >= 5:
        return False
    
    # Check if exactly 9:30 AM (within 2-minute window for safety)
    current_time = now.time()
    target_time = datetime.strptime("09:30", "%H:%M").time()
    
    # Allow 2-minute window (9:30-9:32)
    time_diff = (datetime.combine(datetime.today(), current_time) - 
                 datetime.combine(datetime.today(), target_time)).total_seconds()
    
    return 0 <= time_diff <= 120  # Within 2 minutes

def should_run_market_scout():
    """
    Market Scout runs ONCE per day after Portfolio Analyzer (around 9:32 AM)
    
    ========================================
    PROFESSOR: MARKET SCOUT SCHEDULE
    Lines 89-92: Runs after Portfolio Analyzer completes
    ONCE per day at ~9:32 AM Monday-Friday
    ========================================
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    if now.weekday() >= 5:
        return False
    
    # Runs a few minutes after market open
    current_time = now.time()
    # Allow window 9:32-9:35 (after Portfolio Analyzer)
    return datetime.strptime("09:32", "%H:%M").time() <= current_time <= datetime.strptime("09:35", "%H:%M").time()

def should_run_agent_analysis():
    """
    Agent Analysis runs at: 9:35 AM (after Scout), 11:30 AM, 1:30 PM
    
    ========================================
    PROFESSOR: AGENT ANALYSIS SCHEDULE
    Lines 109-114: Runs THREE times per day
    - 9:35 AM: After Market Scout adds stocks
    - 11:30 AM: 2 hours after first run
    - 1:30 PM: 2 hours after second run
    ========================================
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    if now.weekday() >= 5:
        return False
    
    current_time = now.time()
    
    # Three trigger times (2-minute windows)
    trigger_times = [
        (datetime.strptime("09:35", "%H:%M").time(), datetime.strptime("09:37", "%H:%M").time()),  # After Scout
        (datetime.strptime("11:30", "%H:%M").time(), datetime.strptime("11:32", "%H:%M").time()),  # 2 hours later
        (datetime.strptime("13:30", "%H:%M").time(), datetime.strptime("13:32", "%H:%M").time()),  # 2 hours later
    ]
    
    for start_time, end_time in trigger_times:
        if start_time <= current_time <= end_time:
            return True
    
    return False

def get_next_run_times():
    """
    Get countdown to next agent runs
    
    ========================================
    PROFESSOR: NEXT RUN CALCULATION
    Lines 143-180: Calculates when each agent runs next
    Shows countdown timers in UI
    ========================================
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # Define run times
    portfolio_analyzer_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_scout_time = now.replace(hour=9, minute=32, second=0, microsecond=0)
    agent_analysis_times = [
        now.replace(hour=9, minute=35, second=0, microsecond=0),
        now.replace(hour=11, minute=30, second=0, microsecond=0),
        now.replace(hour=13, minute=30, second=0, microsecond=0),
    ]
    
    # If past today's time, move to next weekday
    if now > portfolio_analyzer_time:
        portfolio_analyzer_time += timedelta(days=1)
        while portfolio_analyzer_time.weekday() >= 5:
            portfolio_analyzer_time += timedelta(days=1)
    
    if now > market_scout_time:
        market_scout_time += timedelta(days=1)
        while market_scout_time.weekday() >= 5:
            market_scout_time += timedelta(days=1)
    
    # Find next agent analysis time
    next_agent_analysis = None
    for analysis_time in agent_analysis_times:
        if now < analysis_time:
            next_agent_analysis = analysis_time
            break
    
    if not next_agent_analysis:
        # Move to tomorrow's first run
        next_agent_analysis = now.replace(hour=9, minute=35, second=0, microsecond=0) + timedelta(days=1)
        while next_agent_analysis.weekday() >= 5:
            next_agent_analysis += timedelta(days=1)
    
    return {
        'portfolio_analyzer': portfolio_analyzer_time,
        'market_scout': market_scout_time,
        'agent_analysis': next_agent_analysis,
        'current_time': now
    }

def time_until_next_check(hours=2):
    """Get time until next check (in seconds)"""
    return hours * 60 * 60  # hours in seconds
