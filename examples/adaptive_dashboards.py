import os
from dotenv import load_dotenv
from autogen import ConversableAgent
from typing import Dict, List, Any
import datetime

class DynamicContextualReportingSystem:
    def __init__(self):
        load_dotenv()
        self.config = self._setup_config()
        self.agents = self._create_agents()
        self._register_agent_functions()
        self.user_preferences = {}
        self.report_history = []
        
    def _setup_config(self):
        """Set up configuration for LLM models."""
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
        """Create specialized agents for dynamic reporting."""
        agents = {
            # Orchestrator agent to coordinate reporting workflow
            "orchestrator": ConversableAgent(
                name="Report Orchestrator",
                system_message="""You are the Report Orchestrator. You analyze user reporting needs and context
                to determine what data should be collected and how it should be presented. You coordinate with 
                specialized reporting agents to create contextually relevant reports.""",
                llm_config=self.config["openai"],
            ),
            
            # User proxy agent
            "user_proxy": ConversableAgent(
                name="User Proxy",
                llm_config=False,
                is_termination_msg=lambda msg: msg.get("content") is not None and "report complete" in msg["content"].lower(),
                human_input_mode="NEVER"
            ),
            
            # Metric analyst agent
            "metric_analyst": ConversableAgent(
                name="Metric Analyst",
                system_message="""You analyze metrics data to identify trends, anomalies, and insights.
                You determine which metrics are most relevant to the current reporting context and extract
                meaningful patterns.""",
                llm_config=self.config["openai"],
            ),
            
            # Narrative builder agent
            "narrative_builder": ConversableAgent(
                name="Narrative Builder",
                system_message="""You create coherent narratives from analytical insights. Your job is to 
                transform data points, trends, and correlations into clear, contextual stories that explain 
                what's happening in the system with appropriate level of detail for the audience.""",
                llm_config=self.config["openai"],
            ),
        }
        return agents
    
    def _register_agent_functions(self):
        """Register specialized functions with the appropriate agents."""
        # Metric analyst functions
        metric_functions = [
            (self.fetch_metrics_data, "fetch_metrics_data", 
             "Fetch relevant metrics based on context"),
            (self.analyze_metric_trends, "analyze_metric_trends", 
             "Analyze trends in metrics data over time"),
            (self.identify_correlated_metrics, "identify_correlated_metrics", 
             "Identify metrics that are correlated with each other")
        ]
        
        # Narrative builder functions
        narrative_functions = [
            (self.get_user_context, "get_user_context", 
             "Get information about the user's role and reporting preferences"),
            (self.generate_visualizations, "generate_visualizations", 
             "Generate relevant data visualizations"),
            (self.retrieve_historical_context, "retrieve_historical_context", 
             "Retrieve historical context for current metrics")
        ]
        
        # Register with metric analyst agent
        for func, name, description in metric_functions:
            self.agents["metric_analyst"].register_for_llm(name=name, description=description)(func)
            self.agents["user_proxy"].register_for_execution(name=name)(func)
        
        # Register with narrative builder agent
        for func, name, description in narrative_functions:
            self.agents["narrative_builder"].register_for_llm(name=name, description=description)(func)
            self.agents["user_proxy"].register_for_execution(name=name)(func)
    

    def fetch_metrics_data(self, metric_types: List[str], timeframe: str) -> Dict[str, Any]:
        """
        Fetch metrics data based on specified types and timeframe.
        
        Args:
            metric_types: Types of metrics to fetch (e.g., ['cpu', 'memory', 'latency'])
            timeframe: Time range (e.g., 'last_24h', 'last_week')
            
        Returns:
            Dictionary with metrics data
        """
        # In a real implementation, this would query metrics databases
        # Just providing sample data for demonstration
        return {
            "cpu_utilization": {
                "service_a": [45, 48, 52, 49, 51],
                "service_b": [62, 65, 70, 72, 68]
            },
            "request_latency": {
                "api_gateway": [120, 125, 118, 130, 122],
                "payment_service": [85, 82, 180, 175, 90]
            },
            "error_rate": {
                "login_service": [0.02, 0.01, 0.01, 0.03, 0.01],
                "checkout_service": [0.01, 0.01, 0.04, 0.05, 0.02]
            },
            "business_metrics": {
                "conversion_rate": [3.2, 3.1, 2.8, 2.9, 3.4],
                "cart_abandonment": [24, 25, 28, 27, 23]
            }
        }
    
    def analyze_metric_trends(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze trends in provided metrics data.
        
        Args:
            metrics_data: Dictionary containing metrics data
            
        Returns:
            Analysis of trends
        """
        """In a real implementation, this would perform statistical trend analysis
        Just providing sample analysis for demonstration"""
        return {
            "significant_changes": [
                {
                    "metric": "payment_service.request_latency",
                    "change": "+110%%"
                    "timeframe": "2 days ago",
                    "current_value": 90,
                    "previous_value": 85,
                    "peak_value": 180
                },
                {
                    "metric": "checkout_service.error_rate",
                    "change": "+400%%",
                    "timeframe": "3 days ago",
                    "current_value": 0.02,
                    "previous_value": 0.01,
                    "peak_value": 0.05
                }
            ],
            "stable_metrics": [
                "cpu_utilization",
                "login_service.error_rate"
            ]
        }
    
    def identify_correlated_metrics(self, metrics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify correlations between different metrics.
        
        Args:
            metrics_data: Dictionary containing metrics data
            
        Returns:
            List of correlated metrics with correlation strengths
        """
        # In a real implementation, this would perform correlation analysis
        return [
            {
                "metrics": ["payment_service.request_latency", "checkout_service.error_rate"],
                "correlation": 0.92,
                "timeframe": "last 5 days",
                "significance": "high"
            },
            {
                "metrics": ["payment_service.request_latency", "cart_abandonment"],
                "correlation": 0.85,
                "timeframe": "last 5 days",
                "significance": "high"
            }
        ]

    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get context information about the user.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            Dictionary with user context information
        """
        # In a real implementation, this would fetch user profiles from a database
        user_contexts = {
            "dev_team": {
                "role": "developer",
                "technical_level": "high",
                "focus_areas": ["service_health", "error_rates", "deployment_impact"],
                "preferred_detail_level": "detailed",
                "preferred_visualization": "metrics_graphs"
            },
            "ops_team": {
                "role": "operations",
                "technical_level": "high",
                "focus_areas": ["system_stability", "resource_utilization", "anomalies"],
                "preferred_detail_level": "detailed",
                "preferred_visualization": "metrics_with_logs"
            },
            "business": {
                "role": "product_management",
                "technical_level": "medium",
                "focus_areas": ["user_impact", "business_metrics", "summary_health"],
                "preferred_detail_level": "summary",
                "preferred_visualization": "business_impact_dashboard"
            },
            "executive": {
                "role": "executive",
                "technical_level": "low",
                "focus_areas": ["business_impact", "critical_issues", "trends"],
                "preferred_detail_level": "high_level",
                "preferred_visualization": "status_summary"
            }
        }
        
        return user_contexts.get(user_id, user_contexts["dev_team"])
    
    def generate_visualizations(self, data: Dict[str, Any], visualization_type: str) -> List[str]:
        """
        Generate visualizations based on the provided data.
        
        Args:
            data: Data to visualize
            visualization_type: Type of visualization to generate
            
        Returns:
            List of visualization descriptions or references
        """
        visualizations = []
        
        if visualization_type == "metrics_graphs":
            visualizations = [
                "Line chart showing payment_service latency spike correlating with checkout error rate increase",
                "Heat map of service dependencies highlighting the payment service connection strain"
            ]
        elif visualization_type == "business_impact_dashboard":
            visualizations = [
                "Conversion funnel showing 12% drop at payment step during incident period",
                "Revenue impact estimation chart: \$15,000 lost during 2-hour incident window"
            ]
        elif visualization_type == "status_summary":
            visualizations = [
                "System health scorecard: 3 services degraded, 18 healthy",
                "Business impact summary: Medium severity on checkout flow, no impact on browsing"
            ]
            
        return visualizations
    
    def retrieve_historical_context(self, metrics: List[str], timeframe: str) -> Dict[str, Any]:
        """
        Retrieve historical context for specified metrics.
        
        Args:
            metrics: List of metrics to retrieve historical context for
            timeframe: Timeframe for historical data
            
        Returns:
            Historical context information
        """
        # In a real implementation, this would query historical data
        return {
            "payment_service.request_latency": {
                "baseline": 85,
                "p95_normal": 110,
                "previous_incidents": [
                    {
                        "date": "2023-04-15",
                        "peak_value": 195,
                        "duration_hours": 1.5,
                        "root_cause": "Database connection pool exhaustion",
                        "resolution": "Increased connection pool size and implemented connection timeout"
                    }
                ]
            },
            "checkout_service.error_rate": {
                "baseline": 0.01,
                "p95_normal": 0.03,
                "previous_incidents": [
                    {
                        "date": "2023-05-22",
                        "peak_value": 0.08,
                        "duration_hours": 2.2,
                        "root_cause": "Payment gateway timeout setting too low",
                        "resolution": "Increased timeout and added circuit breaker"
                    }
                ]
            }
        }
    
    def fetch_topology_data(self) -> Dict[str, Any]:
        """
        Fetch current service topology information.
        
        Returns:
            Dictionary with topology data
        """
        # In a real implementation, this would query service mesh or APM tools
        return {
            "services": [
                {"id": "web_ui", "type": "frontend"},
                {"id": "api_gateway", "type": "gateway"},
                {"id": "user_service", "type": "microservice"},
                {"id": "catalog_service", "type": "microservice"},
                {"id": "checkout_service", "type": "microservice"},
                {"id": "payment_service", "type": "microservice"},
                {"id": "inventory_service", "type": "microservice"},
            ],
            "dependencies": [
                {"source": "web_ui", "target": "api_gateway"},
                {"source": "api_gateway", "target": "user_service"},
                {"source": "api_gateway", "target": "catalog_service"},
                {"source": "api_gateway", "target": "checkout_service"},
                {"source": "checkout_service", "target": "payment_service"},
                {"source": "checkout_service", "target": "inventory_service"},
                {"source": "payment_service", "target": "user_service"}
            ],
            "recent_changes": [
                {"service": "payment_service", "type": "deployment", "version": "2.3.5", "timestamp": "2023-06-14T18:30:00Z"}
            ]
        }
    
    def fetch_logs_data(self, services: List[str], timeframe: str, filter_terms: List[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch logs for specified services.
        
        Args:
            services: List of services to fetch logs for
            timeframe: Time range for log retrieval
            filter_terms: Optional terms to filter logs
            
        Returns:
            List of log entries
        """
        # In a real implementation, this would query a logging system
        sample_logs = [
            {"timestamp": "2023-06-15T10:22:15Z", "service": "payment_service", "level": "ERROR", "message": "Connection timeout to payment gateway"},
            {"timestamp": "2023-06-15T10:22:18Z", "service": "payment_service", "level": "WARN", "message": "Retrying payment gateway connection (attempt 1)"},
            {"timestamp": "2023-06-15T10:22:25Z", "service": "payment_service", "level": "WARN", "message": "Retrying payment gateway connection (attempt 2)"},
            {"timestamp": "2023-06-15T10:22:35Z", "service": "payment_service", "level": "ERROR", "message": "Payment gateway connection failed after retries"},
            {"timestamp": "2023-06-15T10:22:36Z", "service": "checkout_service", "level": "ERROR", "message": "Payment processing failed: timeout"}
        ]
        
        # Filter logs if filter terms provided
        if filter_terms:
            filtered_logs = []
            for log in sample_logs:
                if any(term.lower() in log["message"].lower() for term in filter_terms):
                    filtered_logs.append(log)
            return filtered_logs
            
        return sample_logs
    
    def create_contextual_report(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a contextual report based on the request information.
        
        Args:
            request_info: Information about the report request
            
        Returns:
            Generated report
        """
        # Extract request details
        user_role = request_info.get("user_role", "dev_team")
        report_type = request_info.get("report_type", "status")
        timeframe = request_info.get("timeframe", "last_24h")
        focus_areas = request_info.get("focus_areas", ["service_health"])
        
        # In a real implementation, this would coordinate the agent workflow
        # For this example, we simulate the final report
        
        # Get user context information
        user_context = self.get_user_context(user_role)
        
        # Fetch relevant metrics based on user context and focus areas
        metrics_data = self.fetch_metrics_data(focus_areas, timeframe)
        
        # Analyze trends in metrics
        trends = self.analyze_metric_trends(metrics_data)
        
        # Identify correlations
        correlations = self.identify_correlated_metrics(metrics_data)
        
        # Get historical context for key metrics
        key_metrics = [item["metric"] for item in trends.get("significant_changes", [])]
        historical_context = self.retrieve_historical_context(key_metrics, "last_3_months") if key_metrics else {}
        
        # Get topology information if relevant
        topology = self.fetch_topology_data() if "dependencies" in focus_areas else {}
        
        # Generate appropriate visualizations
        visualizations = self.generate_visualizations(
            {
                "metrics": metrics_data,
                "trends": trends,
                "correlations": correlations
            },
            user_context.get("preferred_visualization", "metrics_graphs")
        )
        
        # Now we use the narrative builder agent to create the contextual report
        # In a full implementation, this would be a call to the agent
        # For this example, we simulate a response based on the user role
        
        if user_role == "executive":
            narrative = """
                    ## Executive System Status Report

                    ### System Health Summary
                    - Overall system health is DEGRADED due to payment processing issues
                    - Business Impact: MEDIUM (estimated $15,000 revenue impact over 2 hours)
                    - 3 of 21 critical services showing performance degradation
                    - Issue contained to checkout flow; browsing and account functions unaffected

                    ### Key Insights
                    - Payment processing latency increased 110% over baseline following yesterdays deployment
                    - This correlates strongly with a 5% increase in cart abandonment rate
                    - Technical teams have identified the cause and implemented a fix
                    - System is now recovering with metrics trending toward normal levels

                    ### Recommendations
                    - Monitor conversion rates closely over next 24 hours
                    - Consider extending current promotion by 1 day to recover lost sales
                    
                    ## Operations Status Report

                    ### Current System State
                    - Payment service showing 110% latency increase (now recovering)
                    - Checkout error rate peaked at 5% (4x normal), now at 2% and declining
                    - Root cause: Connection pool exhaustion in payment service following v2.3.5 deployment
                    - Fix implemented: Connection pool size increased and leak fixed in payment gateway client

                    ### Correlation Analysis
                    - Strong correlation (0.92) between payment latency and checkout errors
                    - Payment service deployment at 18:30 yesterday directly preceded metric degradation
                    - Similar pattern to April 15th incident (see historical reference)

                    ### Action Items
                    - Monitor connection pool metrics for next 24 hours
                    - Implement permanent fix in next release (scheduled June 20)
                    - Add connection pool monitoring alerts at 70% threshold
                    - Update runbook with new recovery procedure
                    
                    ## Development Team System Report

                    ### Service Health
                    - **Payment Service**: Degraded performance (latency +110%, now recovering)
                      - Connection pool exhaustion following deployment of v2.3.5
                      - Peak latency of 180ms vs. baseline of 85ms
                      - Error logs show payment gateway connection timeouts
                      - Connection pool usage peaked at 98% before resolution

                    - **Checkout Service**: Secondary impact
                      - Error rate increased to 5% (baseline: 1%)
                      - Errors directly correlated with payment service latency
                      - No code issues in checkout service itself

                    ### Deployment Impact Analysis
                    - Deployment of payment-service:2.3.5 at 2023-06-14T18:30:00Z
                      - Changes included payment gateway client update and connection pooling changes
                      - Metrics degradation began 22 minutes after deployment
                      - Similar connection issues observed in staging but at lower volume

                    ### Technical Details
                    - Connection leak found in PaymentGatewayClient.processPayment() method
                      - Connection was not being released in exception code path
                      - Fix implemented: Added try-with-resources pattern
                      - PR #3245 contains the fix (merged to main)

                    ### Recommendations
                    - Add unit tests for connection release in error scenarios
                    - Implement connection pool monitoring in metrics dashboard
                    - Review similar connection patterns in other services
            """
        
        # Construct the final report
        report = {
            "title": f"System Status Report - {datetime.datetime.now().strftime(
            "%Y-%m-%d")}",
            "generated_for": user_role,
            "narrative": narrative,
            "visualizations": visualizations,
            "key_metrics": {
                "highlighted": key_metrics,
                "current_values": {k: metrics_data.get(k.split(".")[0], {}).get(k.split(".")[1], "N/A") 
                                 for k in key_metrics} if key_metrics else {}
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # In a real implementation, we would store this report in report_history
        self.report_history.append({
            "report_id": len(self.report_history) + 1,
            "timestamp": datetime.datetime.now(),
            "user_role": user_role,
            "request_info": request_info
        })
        
        return report
    
    def process_report_request(self, request: str) -> str:
        """
        Process a reporting request and generate a contextual report.
        
        Args:
            request: The reporting request
            
        Returns:
            Generated report in formatted text
        """
        # First, have the orchestrator agent understand the request
        # This would determine what kind of report is needed and for whom
        self.agents["user_proxy"].initiate_chat(
            self.agents["orchestrator"],
            message=request
        )
        
        # In a real implementation, the orchestrator would parse the request
        # and determine the appropriate reporting parameters
        # For this example, we simulate this process based on keywords
        
        request_info = {
            "report_type": "status",
            "timeframe": "last_24h",
        }
        
        if "executive" in request.lower() or "business" in request.lower():
            request_info["user_role"] = "executive"
            request_info["focus_areas"] = ["business_metrics", "critical_issues"]
        elif "operations" in request.lower() or "ops" in request.lower():
            request_info["user_role"] = "ops_team"
            request_info["focus_areas"] = ["system_stability", "anomalies"]
        else:
            request_info["user_role"] = "dev_team"
            request_info["focus_areas"] = ["service_health", "deployment_impact"]
            
        if "performance" in request.lower():
            request_info["focus_areas"].append("performance")
        if "errors" in request.lower():
            request_info["focus_areas"].append("error_rates")
        if "business" in request.lower():
            request_info["focus_areas"].append("business_metrics")
            
        # Generate the contextual report
        report = self.create_contextual_report(request_info)
        
        # Format the report for presentation
        formatted_report = f"""
        # {report["title"]}
        Generated for: {report["generated_for"]} role

        {report["narrative"]}

        ## Visualizations
        {"- " + chr(10) + "- ".join(report["visualizations"]) if report["visualizations"] else "No visualizations generated"}

        Report complete.
        """
                return formatted_report

        # Example usage:
if __name__ == "__main__":
    reporter = DynamicContextualReportingSystem()
    
    # Example requests to test the system
    test_requests = [
        "Generate a system status report for executives focused on business impact",
        "Create a detailed technical report on recent performance issues for the dev team",
        "Provide an operations summary of system stability over the last 24 hours"]

    # Process each test request
    for request in test_requests:
        print("=" * 80)
        print(f"Request: {request}")
        print("=" * 80)
        response = reporter.process_report_request(request)
        print(response)
        print("=" * 80)
