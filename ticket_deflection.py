import os
from dotenv import load_dotenv
from autogen import ConversableAgent
import random
from typing import List, Dict
from system_messages import vpn_system_message, change_management_system_message, orchestrator_system_message

load_dotenv()
# Configuration
CONFIG = {
    "bedrock": [{
        "api_type": "bedrock",
        "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "aws_region": "us-west-2",
        "aws_access_key": os.getenv("AWS_ACCESS_KEY"),
        "aws_secret_key": os.getenv("AWS_SECRET_KEY"),
        "price": [0.003, 0.015],
        "temperature": 0.1,
        "cache_seed": None,
    }],
    "openai": [{
        "model": "gpt-4o",
        "api_type": "azure",
        "api_key": os.getenv("AZURE_OAI_API_KEY"),
        "base_url": os.getenv("AZURE_OAI_BASE_URL"),
        "api_version": os.getenv("AZURE_OAI_API_VERSION"),
    }]
}

LLM_CONFIG = {
    "bedrock": {"config_list": CONFIG["bedrock"]},
    "openai": {"config_list": CONFIG["openai"]}
}

# tools
def check_and_fetch_employee_status(employee_id: str) -> Dict:
    #Database call to fetch employee details
    return {
        'employee_id': employee_id,
        'user_name': "John Doe",
        'department': "Sales",
    }

def update_vpn_table(employee_id: str, name: str, department: str) -> bool:
    #Database call to update the VPN table
    return True

def process_approval_request(agent: ConversableAgent, proxy: ConversableAgent, message: str) -> str:
    #user proxy for approvals    
    result = proxy.initiate_chat(
        agent,
        max_turns=1,
        message=message
    )
    return "Approved" if "approved" in agent.last_message()["content"].lower() else "Rejected"

def send_approval_request(employee_id: str) -> str:
    #mimics the approval process (email, portal action etc)
    message = f"Approval needed for VPN access: {employee_id}"
    return process_approval_request(approval_agent, user_proxy, message)

def send_approval_request_for_change(request_title: str) -> str:
    #mimics the approval process (email, portal action etc)
    message = f"Approval needed for the following request: {request_title}"
    return process_approval_request(approval_agent, user_proxy, message)

def is_deployment_restricted(scheduled_change_time: str) -> bool:
    #checks if the change is scheduled during a restricted period
    return False

def create_jira_ticket(request: str, team: str) -> str:
    #jira api call to create a ticket
    return "CM_101"

def escalate_to_human_agent(request: List[str]) -> str:
    #create SD ticket if the request is not handled by the agents
    print("Raised ticket with the human agent. Your ticket id is ")
    return "TICKET_101"

def get_missing_data(missing_fields: str) -> str:
    #user proxy to request missing details in the Change Management form (or other forms)
    result = user_proxy.initiate_chat(
        form_filler_agent,
        max_turns=1,
        message=f"please provide the following details to proceed with your request {missing_fields}: "
    )
    return form_filler_agent.last_message()["content"]

def route_and_resolve(user_input: str) -> str:
    #orchestrator to route the request to the appropriate agent
    route_result = user_proxy.initiate_chat(
        router_agent,
        message=user_input
    )

    routing_path = router_agent.last_message()["content"].strip().upper()
    user_proxy.clear_history()
    if "human" in routing_path.lower():
        return escalate_to_human_agent(user_input)
    
    if "vpn" in routing_path.lower():
        chat_result = user_proxy.initiate_chat(
            vpn_assistant,
            message=user_input
        )
        return chat_result.chat_history[-1]['content']
        
    if "change" in routing_path.lower():
        chat_result = user_proxy.initiate_chat(
            change_management_agent,
            message=user_input
        )
        return chat_result.chat_history[-1]['content']
    return ""

# Initialize Agents
router_agent = ConversableAgent(
    name="Orchestrator",
    system_message=orchestrator_system_message,
    llm_config=LLM_CONFIG["openai"],
)

user_proxy = ConversableAgent(
    name="User",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None and "complete" in msg["content"].lower(),
    human_input_mode="NEVER"
)

approval_agent = ConversableAgent(
    name="Approval Agent",
    human_input_mode="ALWAYS",
)

form_filler_agent = ConversableAgent(
    name="Form Filler Agent",
    human_input_mode="ALWAYS"
)

vpn_assistant = ConversableAgent(
    name="VPN Assistant",
    system_message=vpn_system_message,
    llm_config=LLM_CONFIG["openai"],
)

change_management_agent = ConversableAgent(
    name="Change Management Agent",
    system_message=change_management_system_message,
    llm_config=LLM_CONFIG["openai"],
)

# Register functions with agents
def register_agent_functions():
    vpn_functions = [
        (check_and_fetch_employee_status, "check_and_fetch_employee_status", "Check for employee status"),
        (send_approval_request, "send_approval_request", "Trigger approval request"),
        (update_vpn_table, "update_vpn_table", "Provide VPN access")
    ]

    change_management_functions = [
        (get_missing_data, "get_missing_data", 
                        "Use this funciton to ask users for any missing fields/information in the change management request"),
        (create_jira_ticket, "create_jira_ticket", 
                        "Use this function to create a jira ticket with the right team to execute the change request. It returns the ticket id"),
        (is_deployment_restricted, "is_deployment_restricted", 
                        "Use this function to check if the change schedule falls within the restricted window. Returns true if it falls within schedule, false otherwise"),
        (send_approval_request_for_change, "send_approval_request_for_change", 
                        "Use this funciton to send approval request to proceed with the change management process")]
    
    for func, name, description in vpn_functions:
        vpn_assistant.register_for_llm(name=name, description=description)(func)
        user_proxy.register_for_execution(name=name)(func)

    for func, name, description in change_management_functions:
        change_management_agent.register_for_llm(name=name, description=description)(func)
        user_proxy.register_for_execution(name=name)(func)

register_agent_functions()

# Main execution
def main(request):
    return route_and_resolve(request)

if __name__ == "__main__":
    #request_ = "I need VPN access. Employee ID: 123456"
    request_ = "I need access to HR portal"
    # request_ = """
    # {
    #     "Title": "",
    #     "Description of Change": "This change involves upgrading the PostgreSQL database from version 12 to version 14 to improve performance and security. The upgrade includes backup of current databases and migration of configurations to the new version.",
    #     "Impact": "High",
    #     "Proposed Change Date and Time": "2024-11-05 22:00:00",
    #     "Rollback Plan": "In case of any issues, the databases will be restored from the backup taken before the upgrade. Configuration files will be reverted to the previous version to ensure minimal downtime. A failover will be performed to the secondary database to resume operations if necessary."
    # } """
    
    response = main(request_)