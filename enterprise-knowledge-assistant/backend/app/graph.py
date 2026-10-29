from typing import TypedDict,Any
from langgraph.graph import StateGraph,START,END
from .router import detect_intent,extract_employee_id,Intent
from .security import UserContext
from .services import web_search,openings,employee_report,policy_search

class State(TypedDict,total=False): question:str; user:UserContext; intent:str; result:dict[str,Any]

def classify(st): return {"intent":detect_intent(st["question"]).value}

def route(st): return st["intent"]

def technical(st): return {"result":web_search(st["question"])}

def opening(st): return {"result":openings(st["question"])}

def policy(st): return {"result":policy_search(st["question"],st["user"])}

def leave(st): return {"result":employee_report(st["user"],extract_employee_id(st["question"],st["user"].id),"leave")}

def attendance(st): return {"result":employee_report(st["user"],extract_employee_id(st["question"],st["user"].id),"attendance")}

def direct(st): return {"result":{"answer":"Hello. Ask about company policy, leave, attendance, openings, or a technical topic.","sources":[]}}

def unknown(st): return {"result":{"answer":"I could not safely classify that request. Please mention policy, leave balance, attendance, opening, or the technical topic.","sources":[]}}

g=StateGraph(State); g.add_node("classify",classify)

for n,f in [(Intent.TECHNICAL.value,technical),(Intent.OPENING.value,opening),(Intent.POLICY.value,policy),(Intent.LEAVE.value,leave),(Intent.ATTENDANCE.value,attendance),(Intent.GREETING.value,direct),(Intent.UNKNOWN.value,unknown)]: g.add_node(n,f); g.add_edge(n,END)
g.add_edge(START,"classify"); g.add_conditional_edges("classify",route,{x.value:x.value for x in Intent}); graph=g.compile()
