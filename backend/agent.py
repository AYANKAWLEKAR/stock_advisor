"""
AI Stock Advisor Agent using smolagents library
This agent interacts with the stock advisory API to provide personalized recommendations
"""

import asyncio
import json
from huggingface_hub import InferenceClient
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from smolagents import InferenceClientModel, ToolCallingAgent, Tool, LLM
from smolagents.tools import HttpTool
from smolagents import FinalAnswerTool
from smolagents import LiteLLMModel, CodeAgent
from dotenv import load_dotenv




@dataclass
class UserProfile:
    """User profile for stock recommendations, including the main parameters to be passed into the prediction agent"""
    risk_tolerance: str  # 'conservative', 'balanced', 'aggressive'
    investment_amount: float
    investment_goals: str
    time_horizon: str  # 'short-term', 'medium-term', 'long-term'


class StockAdvisorAgent:
    """Class built on top of smolagents api"""
    
    def __init__(self, api_base_url: str = "http://localhost:5000"):
        self.api_base_url = api_base_url
        model=LiteLLMModel(model_id="gpt-4o-mini")
   
        
        # Initialize the stock advisory API tools with the smolagents api
        self.tools = [
            FinalAnswerTool(),
            self.create_init_tool(),
            self.create_clusters_tool(),
            self.create_recommend_tool(),
            self.create_health_check_tool(),
            self.create_add_custom_stocks_tool(),
            self.create_remove_custom_stocks_tool(),
            self.create_list_custom_stocks_tool(),
            self.create_clear_custom_stocks_tool()
        ] 
        
        # Create the agent with tools
        self.agent = ToolCallingAgent(
            name="StockAdvisor",
            description="An AI agent that provides personalized stock recommendations based on user risk tolerance and investment goals",
            tools=self.tools,
            llm=self.llm, 
            system_prompt=self.get_system_prompt() #wrote object oriented so I can organize all code into one spot
        )
        
        # Track if API is initialized
        self.api_initialized = False
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return """
You are a professional financial advisor AI agent specializing in stock portfolio recommendations. 

Your capabilities:
1. Initialize the stock advisory system with market data
2. Analyze stock clusters and market conditions
3. Provide personalized stock recommendations based on user risk tolerance
4. Add custom stocks to the portfolio for analysis
5. Remove custom stocks from the portfolio
6. List current custom stocks in the portfolio
7. Clear all custom stocks from the portfolio
8. Explain investment strategies and portfolio allocations

Guidelines:
- Always initialize the API before making recommendations
- Consider user's risk tolerance (conservative, balanced, aggressive)
- Explain your recommendations clearly with reasoning
- Provide risk assessment and expected returns
- Suggest diversification strategies
- Be transparent about limitations and risks
- When users mention specific stocks, use the add_custom_stocks tool

Risk Tolerance Guidelines:
- Conservative: Low volatility, stable returns, capital preservation
- Balanced: Moderate risk-return trade-off, steady growth
- Aggressive: Higher risk for potentially higher returns, growth-focused

Custom Stock Management:
- Users can add specific stocks like "PLTR, MKL, RBLX" to the portfolio
- Use add_custom_stocks tool when users mention specific stock symbols
- Custom stocks are included in portfolio optimization and clustering
- Always confirm successful addition of custom stocks

Always ask for user's risk tolerance and investment amount before making recommendations.
"""
    
    def create_health_check_tool(self) -> Tool:
        """Create tool to check API health"""
        def health_check() -> str:
            """Check if api is working"""
            try:
                response = requests.get(f"{self.api_base_url}/health", timeout=10)
                if response.status_code == 200:
                    return "API is healthy"
                else:
                    return f"API  status code: {response.status_code}"
            except Exception as e:
                return f"API health check failed: {str(e)}"
        
        return Tool(
            name="health_check",
            description="Check if the stock advisory API is healthy and running",
            func=health_check
        )
    
    def create_init_tool(self) -> Tool:
        """Create tool to initialize the stock advisory system"""
        def initialize_system() -> str:
            """Initialize the stock advisory system with market data using api init"""
            try:
                response = requests.post(f"{self.api_base_url}/api/init", timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.api_initialized = True
                        clusters = data.get('clusters', {})
                        total_stocks = data.get('total_stocks', 0)
                        
                        cluster_summary = []
                        for cluster_id, cluster_data in clusters.items():
                            cluster_summary.append(
                                f"Cluster {cluster_id}: {cluster_data['size']} stocks, "
                                f"Risk Level: {cluster_data['risk_level']}, "
                                f"Avg Return: {cluster_data['avg_return']:.2%}, "
                                f"Avg Volatility: {cluster_data['avg_volatility']:.2%}"
                            )
                        
                        return f"""System initialized successfully!
                        
Total stocks analyzed: {total_stocks}

Stock Clusters:
{chr(10).join(cluster_summary)}

The system is now ready to provide personalized recommendations."""
                    else:
                        return f"Initialization failed: {data.get('message', 'Unknown error')}"
                else:
                    return f"API returned status code: {response.status_code}"
            except Exception as e:
                return f"Initialization failed: {str(e)}"
        
        return Tool(
            name="initialize_system",
            description="Initialize the stock advisory system with market data",
            func=initialize_system
        )
    
    def create_clusters_tool(self) -> Tool:
        """Create tool to get stock cluster analysis"""
        def get_clusters() -> str:
            """Get detailed analysis of stock clusters"""
            try:
                response = requests.get(f"{self.api_base_url}/api/clusters", timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        clusters = data.get('clusters', {})
                        
                        cluster_analysis = []
                        for cluster_id, cluster_data in clusters.items():
                            stocks = cluster_data.get('stocks', [])
                            cluster_analysis.append(f"""
Cluster {cluster_id} ({cluster_data.get('risk_level', 'Unknown')} Risk):
- Number of stocks: {cluster_data.get('size', 0)}
- Average annual return: {cluster_data.get('avg_return', 0):.2%}
- Average volatility: {cluster_data.get('avg_volatility', 0):.2%}
- Average Sharpe ratio: {cluster_data.get('avg_sharpe', 0):.2f}
- Sample stocks: {', '.join(stocks[:5])}{'...' if len(stocks) > 5 else ''}
""")
                        
                        return f"Stock Cluster Analysis:{''.join(cluster_analysis)}"
                    else:
                        return f"Failed to get clusters: {data.get('message', 'Unknown error')}"
                else:
                    return f"API returned status code: {response.status_code}"
            except Exception as e:
                return f"Failed to get clusters: {str(e)}"
        
        return Tool(
            name="get_clusters",
            description="Get detailed analysis of stock clusters and their characteristics from api call ",
            func=get_clusters
        )
    
    def create_recommend_tool(self) -> Tool:
        """Create tool to get stock recommendations"""
        def get_recommendations(risk_tolerance: str, investment_amount: float, investment_goals: str = "") -> str:
            """Get personalized stock recommendations based on risk tolerance and investment amount
            
            Args:
                risk_tolerance: 'conservative', 'balanced', or 'aggressive'
                investment_amount: Amount to invest in dollars
                investment_goals: Optional description of investment goals
            """
            try:
                payload = {
                    "risk_tolerance": risk_tolerance,
                    "investment_amount": investment_amount,
                    "investment_goals": investment_goals
                }
                
                response = requests.post(f"{self.api_base_url}/api/recommend", 
                                       json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        portfolio = data.get('portfolio', {})
                        backtest = data.get('backtest', {})
                        
                        # Format allocations
                        allocations = portfolio.get('allocations', {})
                        allocation_text = []
                        for stock, details in allocations.items():
                            weight = details.get('weight', 0)
                            dollar_amount = details.get('dollar_amount', 0)
                            shares = details.get('shares', 0)
                            allocation_text.append(
                                f"- {stock}: {weight:.1%} (${dollar_amount:,.2f}, {shares} shares)"
                            )
                        
                        # Format backtest results
                        backtest_summary = ""
                        if backtest:
                            backtest_summary = f"""
Historical Performance (Backtest):
- Total Return: {backtest.get('total_return', 0):.2%}
- Annual Return: {backtest.get('annual_return', 0):.2%}
- Volatility: {backtest.get('volatility', 0):.2%}
- Sharpe Ratio: {backtest.get('sharpe_ratio', 0):.2f}
- Maximum Drawdown: {backtest.get('max_drawdown', 0):.2%}
"""
                        
                        return f"""Stock Recommendations for {risk_tolerance.title()} Risk Profile:

Portfolio Summary:
- Total Investment: ${portfolio.get('total_investment', 0):,.2f}
- Expected Annual Return: {portfolio.get('expected_return', 0):.2%}
- Portfolio Volatility: {portfolio.get('volatility', 0):.2%}
- Sharpe Ratio: {portfolio.get('sharpe_ratio', 0):.2f}

Recommended Allocations:
{chr(10).join(allocation_text)}
{backtest_summary}

Investment Goals Considered: {investment_goals or 'Not specified'}

Note: These are algorithmic recommendations. Please consult with a financial advisor before making investment decisions. Past performance does not guarantee future results."""
                    else:
                        return f"Recommendation failed: {data.get('message', 'Unknown error')}"
                else:
                    return f"API returned status code: {response.status_code}"
            except Exception as e:
                return f"Recommendation failed: {str(e)}"
        
        return Tool(
            name="get_recommendations",
            description="Get personalized stock recommendations based on risk tolerance and investment amount",
            func=get_recommendations
        )
    
    def create_add_custom_stocks_tool(self) -> Tool:
        """Create tool to add custom stocks to the portfolio"""
        def add_custom_stocks(stock_symbols: str) -> str:
            """Add custom stocks to the portfolio for analysis
            
            Args:
                stock_symbols: Comma-separated list of stock symbols (e.g., "PLTR,MKL,RBLX")
            """
            try:
                # Parse stock symbols
                stocks = [s.strip().upper() for s in stock_symbols.split(',')]
                
                payload = {"stocks": stocks}
                response = requests.post(f"{self.api_base_url}/api/stocks/add", 
                                       json=payload, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        added = data.get('added', [])
                        failed = data.get('failed', [])
                        total = data.get('total_custom_stocks', 0)
                        
                        message = f"Successfully added {len(added)} custom stocks to the portfolio."
                        if added:
                            message += f" Added: {', '.join(added)}."
                        if failed:
                            message += f" Failed: {', '.join(failed)}."
                        message += f" Total custom stocks: {total}."
                        
                        return message
                    else:
                        return f"Failed to add stocks: {data.get('message', 'Unknown error')}"
                else:
                    return f"API returned status code: {response.status_code}"
            except Exception as e:
                return f"Failed to add custom stocks: {str(e)}"
        
        return Tool(
            name="add_custom_stocks",
            description="Add custom stocks to the portfolio for analysis. Input should be comma-separated stock symbols.",
            func=add_custom_stocks
        )
    
    def create_remove_custom_stocks_tool(self) -> Tool:
        """Create tool to remove custom stocks from the portfolio"""
        def remove_custom_stocks(stock_symbols: str) -> str:
            """Remove custom stocks from the portfolio
            
            Args:
                stock_symbols: Comma-separated list of stock symbols to remove
            """
            try:
                # Parse stock symbols
                stocks = [s.strip().upper() for s in stock_symbols.split(',')]
                
                payload = {"stocks": stocks}
                response = requests.post(f"{self.api_base_url}/api/stocks/remove", 
                                       json=payload, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        removed = data.get('removed', [])
                        not_found = data.get('not_found', [])
                        total = data.get('total_custom_stocks', 0)
                        
                        message = f"Successfully removed {len(removed)} custom stocks from the portfolio."
                        if removed:
                            message += f" Removed: {', '.join(removed)}."
                        if not_found:
                            message += f" Not found: {', '.join(not_found)}."
                        message += f" Total custom stocks: {total}."
                        
                        return message
                    else:
                        return f"Failed to remove stocks: {data.get('message', 'Unknown error')}"
                else:
                    return f"API returned status code: {response.status_code}"
            except Exception as e:
                return f"Failed to remove custom stocks: {str(e)}"
        
        return Tool(
            name="remove_custom_stocks",
            description="Remove custom stocks from the portfolio. Input should be comma-separated stock symbols.",
            func=remove_custom_stocks
        )
    
    def create_list_custom_stocks_tool(self) -> Tool:
        """Create tool to list custom stocks"""
        def list_custom_stocks() -> str:
            """Get list of custom stocks in the portfolio"""
            try:
                response = requests.get(f"{self.api_base_url}/api/stocks/list", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        custom_stocks = data.get('custom_stocks', [])
                        total_custom = data.get('total_custom_stocks', 0)
                        total_available = data.get('total_available_stocks', 0)
                        sp500_count = data.get('sp500_stocks_count', 0)
                        
                        if custom_stocks:
                            return f"""Custom Stocks in Portfolio:
{', '.join(custom_stocks)}

Summary:
- Custom stocks: {total_custom}
- S&P 500 stocks: {sp500_count}
- Total available stocks: {total_available}"""
                        else:
                            return f"""No custom stocks added yet.

Summary:
- Custom stocks: {total_custom}
- S&P 500 stocks: {sp500_count}
- Total available stocks: {total_available}

You can add custom stocks using the add_custom_stocks tool."""
                    else:
                        return f"Failed to get stock list: {data.get('message', 'Unknown error')}"
                else:
                    return f"API returned status code: {response.status_code}"
            except Exception as e:
                return f"Failed to get custom stocks: {str(e)}"
        
        return Tool(
            name="list_custom_stocks",
            description="Get list of custom stocks currently in the portfolio",
            func=list_custom_stocks
        )
    
    def create_clear_custom_stocks_tool(self) -> Tool:
        """Create tool to clear all custom stocks"""
        def clear_custom_stocks() -> str:
            """Clear all custom stocks from the portfolio"""
            try:
                response = requests.post(f"{self.api_base_url}/api/stocks/clear", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        removed_count = data.get('removed_count', 0)
                        return f"Successfully cleared {removed_count} custom stocks from the portfolio."
                    else:
                        return f"Failed to clear stocks: {data.get('message', 'Unknown error')}"
                else:
                    return f"API returned status code: {response.status_code}"
            except Exception as e:
                return f"Failed to clear custom stocks: {str(e)}"
        
        return Tool(
            name="clear_custom_stocks",
            description="Clear all custom stocks from the portfolio",
            func=clear_custom_stocks
        )
    
    async def chat(self, message: str) -> str:
        """Chat with the stock advisor agent"""
        try:
            # Ensure API is initialized
            if not self.api_initialized:
                await self.initialize_api()
            
            response = await self.agent.arun(message)
            return response
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again or check if the API is running."
    
    async def initialize_api(self) -> bool:
        """Initialize the API if not already done"""
        try:
            response = await self.agent.arun("Please initialize the stock advisory system with market data")
            self.api_initialized = "initialized successfully" in response.lower()
            return self.api_initialized
        except Exception as e:
            print(f"Failed to initialize API: {e}")
            return False
    
    def get_user_profile(self) -> UserProfile:
        """Get user profile through conversation"""
        # This would typically be done through a conversation interface
        # For demo purposes, returning a default profile
        return UserProfile(
            risk_tolerance="balanced",
            investment_amount=10000.0,
            investment_goals="Long-term growth with moderate risk",
            time_horizon="long-term"
        )


async def main():
    """Main function to demonstrate the stock advisor agent"""
    print("🤖 Stock Advisor AI Agent Starting...")
    
    # Initialize the agent
    agent = StockAdvisorAgent()
    
    print("Agent initialized. You can now ask for stock recommendations!")
    print("Example queries:")
    print("- 'I want conservative stock recommendations for $10,000'")
    print("- 'What are the best balanced portfolio options?'")
    print("- 'Show me aggressive growth stocks for $50,000 investment'")
    print("- 'Analyze the current market clusters'")
    print("\nType 'quit' to exit.\n")
    
    # Interactive chat loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye! Happy investing! 📈")
                break
            
            if not user_input:
                continue
            
            print("🤖 Agent: ", end="", flush=True)
            response = await agent.chat(user_input)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye! Happy investing! 📈")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.")


if __name__ == "__main__":
    asyncio.run(main())
