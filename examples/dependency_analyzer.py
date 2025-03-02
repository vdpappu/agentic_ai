import os
from dotenv import load_dotenv
from autogen import ConversableAgent
from typing import Dict, List, Any

# Define system messages (these would be defined in a separate file)
ORCHESTRATOR_SYSTEM_MESSAGE = """You are the Dependency Analysis Orchestrator. You coordinate the analysis of service dependencies by delegating to specialized agents. You decide which agent should analyze what aspect of the dependency data."""

MAPPER_SYSTEM_MESSAGE = """You are the Dependency Mapper Agent. You analyze topology data to identify and track changes in service dependencies. Your goal is to maintain an accurate map of how services are connected."""

ANOMALY_SYSTEM_MESSAGE = """You are the Anomaly Detection Agent. You analyze metrics, logs, and traces to identify unusual patterns in service dependencies and performance that may indicate issues."""

class DynamicDependencyAnalyzer:
    def __init__(self):
        load_dotenv()
        self.config = self._setup_config()
        self.agents = self._create_agents()
        self._register_agent_functions()
        self.dependency_cache = {}  # Store recent dependency maps
        
    def _setup_config(self):
        """Set up configuration for LLM models."""
        # Example configuration - in real implementation, use environment variables
        config = {
            "openai": [{
                "model": "gpt-4o",
                "api_type": "azure",
                "api_key": os.getenv("AZURE_OAI_API_KEY"),
                "base_url": os.getenv("AZURE_OAI_BASE_URL"),
                "api_version": os.getenv("AZURE_OAI_API_VERSION"),
                "temperature": 0.1,
            }]
        }
        return {"openai": {"config_list": config["openai"]}}
    
    def _create_agents(self):
        """Create specialized agents for dependency analysis."""
        # Create agents that will collaborate on analyzing dependencies
        agents = {
            # Orchestrator agent to coordinate the analysis workflow
            "orchestrator": ConversableAgent(
                name="Dependency Analysis Orchestrator",
                system_message=ORCHESTRATOR_SYSTEM_MESSAGE,
                llm_config=self.config["openai"],
            ),
            
            # User proxy agent for executing tool functions
            "user_proxy": ConversableAgent(
                name="User Proxy",
                llm_config=False,
                is_termination_msg=lambda msg: msg.get("content") is not None and "analysis complete" in msg["content"].lower(),
                human_input_mode="NEVER"
            ),
            
            # Dependency mapping agent
            "mapper": ConversableAgent(
                name="Dependency Mapper",
                system_message=MAPPER_SYSTEM_MESSAGE,
                llm_config=self.config["openai"],
            ),
            
            # Anomaly detection agent
            "anomaly_detector": ConversableAgent(
                name="Dependency Anomaly Detector",
                system_message=ANOMALY_SYSTEM_MESSAGE,
                llm_config=self.config["openai"],
            ),
        }
        return agents
    
    def _register_agent_functions(self):
        """Register the tool functions each agent can use."""
        # Here we're just showing some key functions to implement
        
        # Mapper agent functions
        mapper_functions = [
            (self.fetch_topology_data, "fetch_topology_data", 
             "Fetch the current service topology showing connections between services"),
            (self.detect_topology_changes, "detect_topology_changes", 
             "Detect changes in the service topology compared to previous state")
        ]
        
        # Anomaly detector functions
        anomaly_functions = [
            (self.fetch_metrics_data, "fetch_metrics_data", 
             "Fetch metrics data for services and their dependencies"),
            (self.fetch_trace_data, "fetch_trace_data", 
             "Fetch distributed tracing data showing request flows"),
            (self.analyze_dependency_health, "analyze_dependency_health", 
             "Analyze the health of dependencies based on metrics and traces")
        ]
        
        # Register functions with each specialized agent
        for func, name, description in mapper_functions:
            self.agents["mapper"].register_for_llm(name=name, description=description)(func)
            self.agents["user_proxy"].register_for_execution(name=name)(func)
        
        for func, name, description in anomaly_functions:
            self.agents["anomaly_detector"].register_for_llm(name=name, description=description)(func)
            self.agents["user_proxy"].register_for_execution(name=name)(func)
    
    # Tool function implementations - these would fetch real data in a production system
    
    def fetch_topology_data(self) -> Dict[str, Any]:
        """
        Fetch the current service topology from service mesh or APM system.
        
        Returns:
            Dictionary with service topology information
        """
        # In a real implementation, this would call APIs to get topology data
        # Example of simplified topology data
        return {
            "services": [
                {"id": "frontend", "type": "web"},
                {"id": "checkout", "type": "api"},
                {"id": "payment", "type": "api"},
                {"id": "inventory", "type": "api"},
            ],
            "dependencies": [
                {"source": "frontend", "target": "checkout", "calls_per_minute": 250},
                {"source": "checkout", "target": "payment", "calls_per_minute": 175},
                {"source": "checkout", "target": "inventory", "calls_per_minute": 320},
            ]
        }
    
    def detect_topology_changes(self) -> Dict[str, Any]:
        """
        Compare current topology with last known state to detect changes.
        
        Returns:
            Dictionary containing topology changes
        """
        current = self.fetch_topology_data()
        # In a real implementation, compare with previously cached data
        # For this example, we'll simulate some changes
        return {
            "new_services": [],
            "removed_services": [],
            "new_dependencies": [
                {"source": "payment", "target": "inventory", "calls_per_minute": 45}
            ],
            "changed_dependencies": [
                {
                    "source": "checkout", 
                    "target": "inventory",
                    "previous_calls_per_minute": 200,
                    "current_calls_per_minute": 320,
                    "percent_change": 60
                }
            ]
        }
    
    def fetch_metrics_data(self, services: List[str] = None) -> Dict[str, Any]:
        """
        Fetch metrics data for specified services.
        
        Args:
            services: List of service IDs to fetch metrics for
            
        Returns:
            Dictionary with metrics data
        """
        # In a real implementation, this would query a metrics database
        return {
            "inventory": {
                "latency_p95": 250,  # milliseconds
                "error_rate": 0.02,
                "request_rate": 320,
                "cpu_usage": 0.75,
                "memory_usage": 0.82,
                "db_connections": 95,  # <-- Suspicious value
                "db_connection_limit": 100
            },
            "payment": {
                "latency_p95": 120,
                "error_rate": 0.005,
                "request_rate": 175
            },
            "checkout": {
                "latency_p95": 450,  # <-- Higher than normal
                "error_rate": 0.01,
                "request_rate": 250
            }
        }
    
    def fetch_trace_data(self, service_id: str = None, limit: int = 100) -> List[Dict]:
        """
        Fetch recent trace data, optionally filtered by service.
        
        Args:
            service_id: Optional service ID to filter traces
            limit: Maximum number of traces to return
            
        Returns:
            List of trace data
        """
        # In a real implementation, this would query a tracing system like Jaeger or Zipkin
        return [
            {
                "trace_id": "abc123",
                "start_time": "2023-06-15T14:22:10.324Z",
                "spans": [
                    {"service": "frontend", "operation": "GET /checkout", "duration_ms": 520},
                    {"service": "checkout", "operation": "process_order", "duration_ms": 480},
                    {"service": "inventory", "operation": "verify_stock", "duration_ms": 320, "error": False},
                    {"service": "payment", "operation": "process_payment", "duration_ms": 110, "error": False}
                ]
            },
            {
                "trace_id": "def456",
                "start_time": "2023-06-15T14:22:11.128Z",
                "spans": [
                    {"service": "frontend", "operation": "GET /checkout", "duration_ms": 610},
                    {"service": "checkout", "operation": "process_order", "duration_ms": 590},
                    {"service": "inventory", "operation": "verify_stock", "duration_ms": 480, "error": False},
                    {"service": "payment", "operation": "process_payment", "duration_ms": 120, "error": False}
                ]
            }
        ]
    
    def analyze_dependency_health(self, service_id: str) -> Dict[str, Any]:
        """
        Analyze health of a service's dependencies using metrics and traces.
        
        Args:
            service_id: The service to analyze dependencies for
            
        Returns:
            Analysis of dependency health
        """
        # In a real implementation, this would combine metrics and trace data
        # to analyze the health of dependencies
        
        # For this example, we'll return a simulated analysis for checkout service
        if service_id == "checkout":
            return {
                "service_id": "checkout",
                "dependencies": [
                    {
                        "service_id": "payment",
                        "health": "healthy",
                        "latency_trend": "stable",
                        "error_rate_trend": "stable"
                    },
                    {
                        "service_id": "inventory",
                        "health": "degraded",
                        "latency_trend": "increasing",
                        "error_rate_trend": "stable",
                        "anomalies": [
                            {
                                "type": "resource_saturation",
                                "description": "DB connection pool nearing capacity (95%)",
                                "severity": "high"
                            }
                        ]
                    }
                ]
            }
        return {"service_id": service_id, "dependencies": []}
    
    def fetch_logs_data(self, service_id: str, time_range_minutes: int = 15) -> List[Dict]:
        """
        Fetch recent logs for a service.
        
        Args:
            service_id: Service ID to fetch logs for
            time_range_minutes: Time range in minutes for log retrieval
            
        Returns:
            List of log entries
        """
        # In a real implementation, this would query a log system like Elasticsearch
        if service_id == "inventory":
            return [
                {"timestamp": "2023-06-15T14:10:02Z", "level": "WARN", "message": "High database connection count (90/100)"},
                {"timestamp": "2023-06-15T14:15:22Z", "level": "ERROR", "message": "Connection leak detected in validateInventory method"},
                {"timestamp": "2023-06-15T14:18:45Z", "level": "WARN", "message": "High database connection count (93/100)"},
                {"timestamp": "2023-06-15T14:20:12Z", "level": "WARN", "message": "High database connection count (95/100)"}
            ]
        return []
    
    def analyze_root_cause(self, issue_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform root cause analysis of an issue.
        
        Args:
            issue_info: Information about the issue
            
        Returns:
            Root cause analysis
        """
        # In a real implementation, this would use the LLM agent to analyze
        # all available data and determine the root cause
        
        # For now, we'll return a simulated analysis
        return {
            "source_service": "checkout",
            "symptom": "Increased latency (P95: 450ms)",
            "root_cause_service": "inventory",
            "root_cause": "Database connection pool saturation in inventory service",
            "evidence": [
                "Inventory service showing 95/100 active DB connections",
                "Logs indicate connection leak in validateInventory method",
                "Latency increase correlates with deployment of inventory service v2.3.1 (2 hours ago)",
                "Traces show inventory.verify_stock operation taking 320-480ms (baseline: 150ms)"
            ],
            "recommendations": [
                {
                    "type": "immediate",
                    "action": "Increase DB connection pool size in inventory service from 100 to 150",
                    "expected_impact": "Alleviate immediate pressure and reduce latency"
                },
                {
                    "type": "fix",
                    "action": "Fix connection leak in validateInventory method",
                    "evidence": "Log entries showing connection leak warnings"
                }
            ]
        }
    
    def process_analysis_request(self, request: str) -> str:
        """
        Process a dependency analysis request.
        
        Args:
            request: The analysis request
            
        Returns:
            Analysis results in natural language
        """
        # First, let the orchestrator decide what specialized agents need to be involved
        self.agents["user_proxy"].initiate_chat(
            self.agents["orchestrator"],
            message=request
        )
        
        # The orchestrator will now coordinate the analysis flow between agents
        # Each agent will use their specialized functions to analyze different aspects
        
        # For this simplified implementation, we'll simulate the final response
        # In a real implementation, the agents would collaborate to build this response
        
        if "checkout" in request.lower() and "latency" in request.lower():
            # Simulate the agents' collaborative analysis for a checkout latency issue
            root_cause = self.analyze_root_cause({
                "service": "checkout",
                "issue": "latency",
                "severity": "medium"
            })
            
            # Format the response in natural language
            response = f"""
                Analysis Complete:

                The increased latency in the checkout service (currently P95: 450ms) is being caused by a bottleneck in the inventory service.

                Root Cause:
                - The inventory service's database connection pool is nearly saturated (95/100 connections in use)
                - Logs show evidence of a connection leak in the validateInventory method
                - This issue began following the deployment of inventory service v2.3.1 approximately 2 hours ago

                Impact:
                - Checkout operations are experiencing ~60% higher latency than normal
                - This is affecting approximately 250 requests per minute
                - No significant increase in error rates observed yet, but risk is high if connections continue to increase

                Recommendations:
                1. Immediate: Increase the DB connection pool size from 100 to 150 to alleviate pressure
                2. Fix: Resolve the connection leak in the validateInventory method in inventory service
                3. Long-term: Implement connection usage monitoring with alerts at 80% threshold

                Analysis complete.
                """
            return response
                            
        return "Could not determine the appropriate analysis path for this request."
        

# Example usage:
if __name__ == "__main__":
    analyzer = DynamicDependencyAnalyzer()
    
    request = "We're seeing increased latency in the checkout service. Can you investigate if any dependencies are causing this?"
    analysis = analyzer.process_analysis_request(request)
    print(analysis)
