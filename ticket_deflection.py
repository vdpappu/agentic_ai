import os
from dotenv import load_dotenv
from autogen import ConversableAgent
from typing import List, Dict

# Import system messages
from system_messages import (
    ORCHESTRATOR_SYSTEM_MESSAGE,
    VPN_SYSTEM_MESSAGE,
    CHANGE_MANAGEMENT_SYSTEM_MESSAGE
)

# Load environment variables
load_dotenv()

class AgentSystem:
    def __init__(self):
        self.config = self._setup_config()
        self.agents = self._create_agents()
        self._register_agent_functions()
    
    def _setup_config(self):
        """Set up configuration for LLM models."""
        """Replace this with the custom config """
        # config = {
        #     "bedrock": [{
        #         "api_type": "bedrock",
        #         "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        #         "aws_region": "us-west-2",
        #         "aws_access_key": os.getenv("AWS_ACCESS_KEY"),
        #         "aws_secret_key": os.getenv("AWS_SECRET_KEY"),
        #         "price": [0.003, 0.015],
        #         "temperature": 0.1,
        #         "cache_seed": None,
        #     }],
        #     "openai": [{
        #         "model": "gpt-4o",
        #         "api_type": "azure",
        #         "api_key": os.getenv("AZURE_OAI_API_KEY"),
        #         "base_url": os.getenv("AZURE_OAI_BASE_URL"),
        #         "api_version": os.getenv("AZURE_OAI_API_VERSION"),
        #     }]
        # }
        
        # return {
        #     "bedrock": {"config_list": config["bedrock"]},
        #     "openai": {"config_list": config["openai"]}
        }
    
    def _create_agents(self):
        """Create all the agents needed for the system."""
        agents = {
            # Router agent to direct requests to appropriate specialized agents
            "router": ConversableAgent(
                name="Orchestrator",
                system_message=ORCHESTRATOR_SYSTEM_MESSAGE,
                llm_config=self.config["openai"],
            ),
            
            # User proxy agent that acts as intermediary
            "user_proxy": ConversableAgent(
                name="User",
                llm_config=False,
                is_termination_msg=lambda msg: msg.get("content") is not None and "complete" in msg["content"].lower(),
                human_input_mode="NEVER"
            ),
            
            # Approval agent for handling approval requests
            "approval": ConversableAgent(
                name="Approval Agent",
                human_input_mode="ALWAYS",
            ),
            
            # Form filler agent for gathering missing information
            "form_filler": ConversableAgent(
                name="Form Filler Agent",
                human_input_mode="ALWAYS"
            ),
            
            # VPN assistant for handling VPN access requests
            "vpn": ConversableAgent(
                name="VPN Assistant",
                system_message=VPN_SYSTEM_MESSAGE,
                llm_config=self.config["openai"],
            ),
            
            # Change management agent for handling change requests
            "change_management": ConversableAgent(
                name="Change Management Agent",
                system_message=CHANGE_MANAGEMENT_SYSTEM_MESSAGE,
                llm_config=self.config["openai"],
            ),
        }
        
        return agents
    
    def _register_agent_functions(self):
        """Register functions with the appropriate agents."""
        
        # --- VPN Tool Wrappers ---
        def check_employee_status(employee_id: str) -> Dict:
            """Check for employee status in database."""
            return self.check_and_fetch_employee_status(employee_id)
        
        def send_approval(employee_id: str) -> str:
            """Trigger approval request for VPN access."""
            return self.send_approval_request(employee_id)
        
        def update_vpn(employee_id: str, name: str, department: str) -> bool:
            """Update the VPN access table."""
            return self.update_vpn_table(employee_id, name, department)
        
        # --- Change Management Tool Wrappers ---
        def get_missing(missing_fields: str) -> str:
            """Ask users for any missing fields/information."""
            return self.get_missing_data(missing_fields)
        
        def create_ticket(request: str, team: str) -> str:
            """Create a JIRA ticket with the right team."""
            return self.create_jira_ticket(request, team)
        
        def check_restriction(scheduled_change_time: str) -> bool:
            """Check if the change falls within a restricted window."""
            return self.is_deployment_restricted(scheduled_change_time)
        
        def send_change_approval(request_title: str) -> str:
            """Send approval request for change management."""
            return self.send_approval_request_for_change(request_title)
        
        # Register all functions with their respective agents
        function_registrations = [
            # (agent_name, function_name, description, wrapper_function)
            ("vpn", "check_and_fetch_employee_status", "Check for employee status", check_employee_status),
            ("vpn", "send_approval_request", "Trigger approval request", send_approval),
            ("vpn", "update_vpn_table", "Provide VPN access", update_vpn),
            ("change_management", "get_missing_data", "Ask users for missing information", get_missing),
            ("change_management", "create_jira_ticket", "Create a JIRA ticket", create_ticket),
            ("change_management", "is_deployment_restricted", "Check for restricted windows", check_restriction),
            ("change_management", "send_approval_request_for_change", "Send approval request", send_change_approval),
        ]
        
        # Register functions for both LLM and execution
        for agent_name, func_name, description, wrapper_func in function_registrations:
            self.agents[agent_name].register_for_llm(name=func_name, description=description)(wrapper_func)
            self.agents["user_proxy"].register_for_execution(name=func_name)(wrapper_func)
    
    # Tool Functions
    def check_and_fetch_employee_status(self, employee_id: str) -> Dict:
        """
        Check employee status in database.
        
        Args:
            employee_id: The employee's ID to look up
            
        Returns:
            Dictionary with employee information
        """
        # In a real implementation, this would query a database
        return {
            'employee_id': employee_id,
            'user_name': "John Doe",
            'department': "Sales",
        }

    def update_vpn_table(self, employee_id: str, name: str, department: str) -> bool:
        """
        Update the VPN access table.
        
        Args:
            employee_id: The employee's ID
            name: The employee's name
            department: The employee's department
            
        Returns:
            True if successful, False otherwise
        """
        # In a real implementation, this would update a database
        return True

    def process_approval_request(self, agent, proxy, message: str) -> str:
        """
        Process an approval request through agent interaction.
        
        Args:
            agent: The approval agent
            proxy: The user proxy agent
            message: The approval request message
            
        Returns:
            "Approved" or "Rejected"
        """
        proxy.initiate_chat(
            agent,
            max_turns=1,
            message=message
        )
        return "Approved" if "approved" in agent.last_message()["content"].lower() else "Rejected"

    def send_approval_request(self, employee_id: str) -> str:
        """
        Send a VPN access approval request.
        
        Args:
            employee_id: The employee's ID
            
        Returns:
            Approval status
        """
        message = f"Approval needed for VPN access: {employee_id}"
        return self.process_approval_request(
            self.agents["approval"], 
            self.agents["user_proxy"], 
            message
        )

    def send_approval_request_for_change(self, request_title: str) -> str:
        """
        Send a change request approval.
        
        Args:
            request_title: Title of the change request
            
        Returns:
            Approval status
        """
        message = f"Approval needed for the following request: {request_title}"
        return self.process_approval_request(
            self.agents["approval"], 
            self.agents["user_proxy"], 
            message
        )

    def is_deployment_restricted(self, scheduled_change_time: str) -> bool:
        """
        Check if a deployment time falls in a restricted period.
        
        Args:
            scheduled_change_time: The scheduled time for the change
            
        Returns:
            True if restricted, False if allowed
        """
        # In a real implementation, this would check against a calendar or policy
        return False

    def create_jira_ticket(self, request: str, team: str) -> str:
        """
        Create a JIRA ticket for a change request.
        
        Args:
            request: The details of the request
            team: The team to assign the ticket to
            
        Returns:
            Ticket ID
        """
        # In a real implementation, this would call the JIRA API
        return "CM_101"

    def escalate_to_human_agent(self, request: List[str]) -> str:
        """
        Escalate a request to a human agent.
        
        Args:
            request: The user's request
            
        Returns:
            Ticket ID for human follow-up
        """
        print("Raised ticket with the human agent. Your ticket id is ")
        return "TICKET_101"

    def get_missing_data(self, missing_fields: str) -> str:
        """
        Request missing information from the user.
        
        Args:
            missing_fields: The fields that need to be filled
            
        Returns:
            The user's response with the missing information
        """
        result = self.agents["user_proxy"].initiate_chat(
            self.agents["form_filler"],
            max_turns=1,
            message=f"Please provide the following details to proceed with your request {missing_fields}: "
        )
        return self.agents["form_filler"].last_message()["content"]

    def route_and_resolve(self, user_input: str) -> str:
        """
        Main function to route a request to the appropriate agent and get a response.
        
        Args:
            user_input: The user's request
            
        Returns:
            The response from the appropriate agent
        """
        # Route the request using the router agent
        self.agents["user_proxy"].initiate_chat(
            self.agents["router"],
            message=user_input
        )

        routing_path = self.agents["router"].last_message()["content"].strip().upper()
        self.agents["user_proxy"].clear_history()
        
        # Route to human agent
        if "human" in routing_path.lower():
            return self.escalate_to_human_agent(user_input)
        
        # Route to VPN agent
        if "vpn" in routing_path.lower():
            chat_result = self.agents["user_proxy"].initiate_chat(
                self.agents["vpn"],
                message=user_input
            )
            return chat_result.chat_history[-1]['content']
            
        # Route to change management agent
        if "change" in routing_path.lower():
            chat_result = self.agents["user_proxy"].initiate_chat(
                self.agents["change_management"],
                message=user_input
            )
            return chat_result.chat_history[-1]['content']
        
        # If no routing path matched
        return "Unable to determine the appropriate agent for your request."

    def process_request(self, request: str) -> str:
        """
        Public API to process a user request.
        
        Args:
            request: The user's request text
            
        Returns:
            The response to the user
        """
        return self.route_and_resolve(request)

if __name__ == "__main__":
    # Create the agent system
    agent_system = AgentSystem()
    
    #request = "I need VPN access. Employee ID: 123456"
    #request = "I need access to HR portal"
    request = """
        {
            "Title": "",
            "Description of Change": "This change involves upgrading the PostgreSQL database from version 12 to version 14 to improve performance and security. The upgrade includes backup of current databases and migration of configurations to the new version.",
            "Impact": "High",
            "Proposed Change Date and Time": "2024-11-05 22:00:00",
            "Rollback Plan": "In case of any issues, the databases will be restored from the backup taken before the upgrade. Configuration files will be reverted to the previous version to ensure minimal downtime. A failover will be performed to the secondary database to resume operations if necessary."
        } """
    # Process each test request
    response = agent_system.process_request(request)
