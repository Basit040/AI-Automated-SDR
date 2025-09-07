#!/usr/bin/env python3
"""
AI Sales Agent System
====================

An intelligent sales agent system that automatically generates, selects, and sends 
cold sales outreach emails using OpenAI's Agent SDK and SendGrid.

This system demonstrates agentic design patterns:
1. Agent Workflow - Multiple agents working in parallel
2. Tool Usage - Functions wrapped as tools for agents  
3. Agent Collaboration - Agents working together via tools and handoffs

Usage:
    uv run sales_agent.py

Requirements:
    - OpenAI API key
    - SendGrid API key and verified sender email
    - Environment variables in .env file

Author:Abdul Basit
"""

import os
import asyncio
from typing import Dict
from dotenv import load_dotenv
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

# Import the agents framework
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent

# Global configuration - UPDATE THESE EMAIL ADDRESSES
FROM_EMAIL = "abdulbasitnedian@outlook.com"  # Must be verified in SendGrid
TO_EMAIL = "abdulbasitnedian@gmail.com"              # Your recipient email
TEST_MODE = False  # Set to False to actually send emails


# Standalone tool functions (not class methods to avoid 'self' parameter issues)
@function_tool
def send_email(body: str) -> Dict[str, str]:
    """
    Send a plain text email using SendGrid.
    
    Args:
        body (str): The email body content
        
    Returns:
        Dict[str, str]: Status of email sending operation
    """
    if TEST_MODE:
        print("📧 SIMULATING EMAIL SEND (TEST MODE):")
        print("=" * 50)
        print(f"TO: {TO_EMAIL}")
        print(f"FROM: {FROM_EMAIL}")
        print("SUBJECT: Sales Email")
        print("BODY:")
        print(body)
        print("=" * 50)
        print("✅ Email would be sent successfully!")
        return {"status": "success", "status_code": 202}
    
    try:
        print(f"📧 Sending plain text email...")
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email(FROM_EMAIL)
        to_email = To(TO_EMAIL)
        content = Content("text/plain", body)
        mail = Mail(from_email, to_email, "Sales Email", content).get()
        response = sg.client.mail.send.post(request_body=mail)
        
        if response.status_code == 202:
            print("✅ Email sent successfully!")
            return {"status": "success", "status_code": response.status_code}
        else:
            print(f"❌ Email failed with status code: {response.status_code}")
            return {"status": "error", "status_code": response.status_code}
            
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return {"status": "error", "message": str(e)}


@function_tool 
def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """
    Send an HTML formatted email using SendGrid.
    
    Args:
        subject (str): Email subject line
        html_body (str): HTML formatted email body
        
    Returns:
        Dict[str, str]: Status of email sending operation
    """
    if TEST_MODE:
        print("📧 SIMULATING HTML EMAIL SEND (TEST MODE):")
        print("=" * 50)
        print(f"TO: {TO_EMAIL}")
        print(f"FROM: {FROM_EMAIL}")
        print(f"SUBJECT: {subject}")
        print("HTML BODY:")
        print(html_body[:300] + "..." if len(html_body) > 300 else html_body)
        print("=" * 50)
        print("✅ HTML email would be sent successfully!")
        return {"status": "success", "status_code": 202}
    
    try:
        print(f"📧 Sending HTML email with subject: '{subject}'...")
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email(FROM_EMAIL)
        to_email = To(TO_EMAIL)
        content = Content("text/html", html_body)
        mail = Mail(from_email, to_email, subject, content).get()
        response = sg.client.mail.send.post(request_body=mail)
        
        if response.status_code == 202:
            print("✅ HTML email sent successfully!")
            return {"status": "success", "status_code": response.status_code}
        else:
            print(f"❌ Email failed with status code: {response.status_code}")
            return {"status": "error", "status_code": response.status_code}
            
    except Exception as e:
        print(f"❌ Error sending HTML email: {str(e)}")
        return {"status": "error", "message": str(e)}


class SalesAgentSystem:
    """
    Complete sales agent system for generating and sending cold emails.
    
    Implements multiple agentic design patterns for automated email outreach.
    """
    
    def __init__(self):
        """Initialize the sales agent system and verify configuration."""
        print("🤖 Initializing AI Sales Agent System...")
        
        # Load environment variables
        load_dotenv(override=True)
        
        # Check for OpenAI API key (always required)
        if not os.environ.get('OPENAI_API_KEY'):
            raise ValueError("❌ OPENAI_API_KEY environment variable is required")
        
        # Check for SendGrid API key (only if not in test mode)
        if not TEST_MODE and not os.environ.get('SENDGRID_API_KEY'):
            raise ValueError("❌ SENDGRID_API_KEY environment variable is required for real email sending")
        
        mode = "TEST MODE (emails simulated)" if TEST_MODE else "LIVE MODE (emails will be sent)"
        print(f"✅ Configuration loaded successfully - {mode}")
        
        self._setup_agents()
        self._setup_tools()
        
    def _setup_agents(self):
        """Create different agent personas for email generation."""
        print("🎭 Setting up agent personas...")
        
        # Agent Instructions - Different writing styles for email generation
        professional_instructions = """You are a sales agent working for ComplAI, 
        a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. 
        You write professional, serious cold emails."""
        
        engaging_instructions = """You are a humorous, engaging sales agent working for ComplAI, 
        a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. 
        You write witty, engaging cold emails that are likely to get a response."""
        
        concise_instructions = """You are a busy sales agent working for ComplAI, 
        a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. 
        You write concise, to the point cold emails."""
        
        # Create agent instances with different personalities
        self.sales_agent1 = Agent(
            name="Professional Sales Agent",
            instructions=professional_instructions,
            model="gpt-4o-mini"
        )
        
        self.sales_agent2 = Agent(
            name="Engaging Sales Agent", 
            instructions=engaging_instructions,
            model="gpt-4o-mini"
        )
        
        self.sales_agent3 = Agent(
            name="Concise Sales Agent",
            instructions=concise_instructions,
            model="gpt-4o-mini"
        )
        
        # Agent for selecting the best email from multiple options
        self.sales_picker = Agent(
            name="Sales Picker",
            instructions="""You pick the best cold sales email from the given options. 
            Imagine you are a customer and pick the one you are most likely to respond to. 
            Do not give an explanation; reply with the selected email only.""",
            model="gpt-4o-mini"
        )
        
        # Specialized agents for email formatting
        self.subject_writer = Agent(
            name="Email Subject Writer",
            instructions="""You can write a subject for a cold sales email. 
            You are given a message and you need to write a subject for an email that is likely to get a response.""",
            model="gpt-4o-mini"
        )
        
        self.html_converter = Agent(
            name="HTML Email Body Converter",
            instructions="""You can convert a text email body to an HTML email body. 
            You are given a text email body which might have some markdown 
            and you need to convert it to an HTML email body with simple, clear, compelling layout and design.""",
            model="gpt-4o-mini"
        )
        
        print("✅ All agents created successfully")
        
    def _setup_tools(self):
        """Set up tools and create the main sales manager agent."""
        print("🔧 Setting up tools and manager agents...")
        
        # Convert agents to tools so other agents can use them
        description = "Write a cold sales email"
        self.tool1 = self.sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
        self.tool2 = self.sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
        self.tool3 = self.sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)
        
        # Create specialized tools for email formatting
        self.subject_tool = self.subject_writer.as_tool(
            tool_name="subject_writer", 
            tool_description="Write a subject for a cold sales email"
        )
        self.html_tool = self.html_converter.as_tool(
            tool_name="html_converter",
            tool_description="Convert a text email body to an HTML email body"
        )
        
        # Create the email manager agent for handoffs
        # This agent handles formatting and sending emails
        self.emailer_agent = Agent(
            name="Email Manager",
            instructions="""You are an email formatter and sender. You receive the body of an email to be sent. 
            You first use the subject_writer tool to write a subject for the email, 
            then use the html_converter tool to convert the body to HTML. 
            Finally, you use the send_html_email tool to send the email with the subject and HTML body.""",
            tools=[self.subject_tool, self.html_tool, send_html_email],  # Use standalone function
            model="gpt-4o-mini",
            handoff_description="Convert an email to HTML and send it"
        )
        
        # Create the main sales manager with tools and handoffs
        # This demonstrates the handoff pattern - one agent delegates to another
        sales_manager_instructions = """
        You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
         
        Follow these steps carefully:
        1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
         
        2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
        You can use the tools multiple times if you're not satisfied with the results from the first try.
         
        3. Handoff for Sending: Pass ONLY the winning email draft to the 'Email Manager' agent. The Email Manager will take care of formatting and sending.
         
        Crucial Rules:
        - You must use the sales agent tools to generate the drafts – do not write them yourself.
        - You must hand off exactly ONE email to the Email Manager – never more than one.
        """
        
        self.sales_manager = Agent(
            name="Sales Manager",
            instructions=sales_manager_instructions,
            tools=[self.tool1, self.tool2, self.tool3],  # Tools for generating emails
            handoffs=[self.emailer_agent],               # Handoff to email manager
            model="gpt-4o-mini"
        )
        
        print("✅ Tools and manager agents configured")
    
    def send_test_email(self):
        """Send a test email to verify SendGrid configuration."""
        if TEST_MODE:
            print("📤 Test mode enabled - would send test email to verify configuration")
            return True
            
        print("📤 Testing SendGrid configuration...")
        try:
            sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            from_email = Email(FROM_EMAIL)
            to_email = To(TO_EMAIL)
            content = Content("text/plain", "This is a test email from the AI Sales Agent System")
            mail = Mail(from_email, to_email, "Test Email - AI Sales Agent", content).get()
            response = sg.client.mail.send.post(request_body=mail)
            
            if response.status_code == 202:
                print("✅ Test email sent successfully! Check your inbox (and spam folder)")
                return True
            else:
                print(f"❌ Test email failed with status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send test email: {e}")
            print("💡 Common issues:")
            print("   • Check your SENDGRID_API_KEY in .env file")
            print("   • Verify sender email in SendGrid dashboard")
            print("   • Update email addresses in this script")
            return False
    
    async def generate_parallel_emails(self, message: str = "Write a cold sales email"):
        """
        Demonstrate the Agent Workflow pattern by generating emails in parallel.
        
        Args:
            message (str): The prompt message for email generation
            
        Returns:
            List[str]: List of generated email outputs
        """
        print("🔄 Generating emails with different agent personas...")
        print("   • Professional Agent: Formal, serious approach")
        print("   • Engaging Agent: Witty, humorous approach") 
        print("   • Concise Agent: Brief, direct approach")
        
        # Use OpenAI tracing to monitor the agent interactions
        with trace("Parallel Email Generation"):
            # Run all three agents in parallel using asyncio.gather
            results = await asyncio.gather(
                Runner.run(self.sales_agent1, message),
                Runner.run(self.sales_agent2, message), 
                Runner.run(self.sales_agent3, message),
            )
        
        outputs = [result.final_output for result in results]
        
        print(f"\n📧 Generated {len(outputs)} emails:")
        for i, output in enumerate(outputs, 1):
            print(f"\n--- Email {i} (Agent {i}) ---")
            print(output[:200] + "..." if len(output) > 200 else output)
            
        return outputs
    
    async def select_best_email(self, emails: list) -> str:
        """
        Use the sales picker agent to select the best email from options.
        
        Args:
            emails (list): List of email options to choose from
            
        Returns:
            str: The selected best email
        """
        print("\n🎯 Selecting best email from generated options...")
        
        # Format all emails for the picker agent to evaluate
        email_options = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(emails)
        
        with trace("Email Selection"):
            best = await Runner.run(self.sales_picker, email_options)
        
        print("✅ Best email selected!")
        return best.final_output
    
    async def run_basic_workflow(self, message: str = "Write a cold sales email"):
        """
        Run the basic workflow: generate emails in parallel and pick the best.
        
        Args:
            message (str): The prompt message for email generation
        """
        print("\n" + "="*60)
        print("🚀 RUNNING BASIC WORKFLOW (Generate + Select)")
        print("="*60)
        
        # Step 1: Generate emails using multiple agents in parallel
        emails = await self.generate_parallel_emails(message)
        
        # Step 2: Select the best email using the picker agent
        best_email = await self.select_best_email(emails)
        
        print(f"\n📋 FINAL RESULT:")
        print("-" * 40)
        print(best_email)
        print("-" * 40)
        
        print("\n✨ Basic workflow complete!")
        return best_email
    
    async def run_automated_sdr(self, message: str = "Send out a cold sales email addressed to Dear CEO from Alice"):
        """
        Run the full automated SDR (Sales Development Representative) workflow.
        
        Args:
            message (str): The prompt message for the sales manager
        """
        print("\n" + "="*60)
        print("🤖 RUNNING AUTOMATED SDR WORKFLOW (Full Pipeline)")
        print("="*60)
        mode_text = "simulate sending" if TEST_MODE else "actually send"
        print(f"This will generate, select, format, and {mode_text} an email automatically!")
        
        # The sales manager will:
        # 1. Use tools to generate multiple email drafts
        # 2. Select the best one
        # 3. Hand off to email manager for formatting and sending
        with trace("Automated SDR Pipeline"):
            result = await Runner.run(self.sales_manager, message)
        
        print(f"\n📋 SALES MANAGER RESULT:")
        print("-" * 40)
        print(result.final_output)
        print("-" * 40)
        
        print("\n✅ Automated SDR workflow complete!")
        if not TEST_MODE:
            print("📧 Check your email inbox (and spam folder) for the sent email")
        print("🔍 View detailed traces at: https://platform.openai.com/traces")
        
        return result


async def main():
    """
    Main function demonstrating the AI Sales Agent System.
    """
    print("🎉 Welcome to the AI Sales Agent System!")
    print("=" * 60)
    print("Demonstrating Agentic Design Patterns:")
    print("• Agent Workflow - Multiple agents working in parallel")
    print("• Tool Usage - Functions wrapped as tools for agents")
    print("• Agent Collaboration - Handoffs between specialized agents")
    print("=" * 60)
    
    if TEST_MODE:
        print("🧪 RUNNING IN TEST MODE - emails will be simulated")
        print("   Set TEST_MODE = False in the script to send real emails")
    else:
        print("🚀 RUNNING IN LIVE MODE - emails will be sent!")
    
    print("=" * 60)
    
    try:
        # Initialize the system
        sales_system = SalesAgentSystem()
        
        # Step 1: Test email configuration (if not in test mode)
        if not TEST_MODE:
            print("\n📤 Step 1: Testing SendGrid configuration...")
            if not sales_system.send_test_email():
                print("\n❌ Email test failed. Please check your configuration:")
                print("1. Ensure SENDGRID_API_KEY is set in your .env file")
                print("2. Verify sender email in SendGrid dashboard")
                print(f"3. Update email addresses in script (FROM_EMAIL, TO_EMAIL)")
                print("\n💡 Or set TEST_MODE = True to run in simulation mode")
                return
        else:
            print("\n📤 Step 1: Skipping email test (TEST_MODE enabled)")
        
        # Step 2: Run basic workflow (generate and select, but don't send)
        print("\n🔄 Step 2: Running Basic Workflow...")
        await sales_system.run_basic_workflow(
            "Write a cold sales email to a tech startup CEO about SOC2 compliance"
        )
        
        # Step 3: Run automated SDR workflow (full pipeline)
        print("\n🚀 Step 3: Running Automated SDR Workflow...")
        await sales_system.run_automated_sdr(
            "Send out a professional cold sales email addressed to 'Dear Startup Founder' from Alice at ComplAI"
        )
        
        # Completion message
        print("\n" + "="*60)
        print("🎊 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        if TEST_MODE:
            print("🧪 All emails were simulated (TEST_MODE enabled)")
            print("💡 Set TEST_MODE = False to send real emails")
        else:
            print("📧 Check your email inbox and spam folder for sent emails")
        
        print("🔍 View detailed agent traces at: https://platform.openai.com/traces")
        print("📚 Each trace shows the complete agent workflow and tool usage")
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n🔧 Setup Instructions:")
        print("1. Create a .env file with your API keys:")
        print("   OPENAI_API_KEY=your_openai_api_key_here")
        if not TEST_MODE:
            print("   SENDGRID_API_KEY=your_sendgrid_api_key_here")
        print("2. Update email addresses at top of script")
        print("3. For testing, set TEST_MODE = True")
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    # Entry point - run the main demonstration
    asyncio.run(main())