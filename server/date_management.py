from datetime import datetime

def isRainy():
    # current_week = datetime.now().isocalendar().week
    current_week = 45
    if (current_week > 20 and current_week < 45) : return True
    else: return False
