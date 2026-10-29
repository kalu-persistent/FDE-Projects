import re
from enum import Enum
class Intent(str,Enum): TECHNICAL="technical_web"; OPENING="internal_opening"; POLICY="policy_rag"; LEAVE="leave_balance"; ATTENDANCE="attendance"; GREETING="direct"; UNKNOWN="unknown"
RULES=[(Intent.GREETING,[r"^(hi|hello|hey|thanks|thank you)[!. ]*$"]),(Intent.ATTENDANCE,[r"\battendance\b",r"\bpresent days?\b"]),(Intent.LEAVE,[r"\bleave balance\b",r"\bleaves? remaining\b",r"\bleave count\b"]),(Intent.OPENING,[r"\b(opening|vacanc|job|position|hiring)\w*\b"]),(Intent.POLICY,[r"\b(policy|promotion|eligibility|criteria|reimbursement|holiday)\w*\b"]),(Intent.TECHNICAL,[r"\b(python|fastapi|docker|kubernetes|langgraph|rag|llm|api|database|error|code|technical)\b"])]
def detect_intent(q):
    for intent,patterns in RULES:
        if any(re.search(p,q,re.I) for p in patterns): return intent
    return Intent.UNKNOWN
def extract_employee_id(q,default):
    m=re.search(r"(?:employee|user|id)\s*#?\s*(\d+)",q,re.I); return int(m.group(1)) if m else default
