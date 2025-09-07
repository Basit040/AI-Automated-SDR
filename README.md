# 🤖 AI Sales Agent System

An intelligent sales agent system that automatically generates, selects, and sends cold sales emails using OpenAI's Agent SDK and SendGrid. This project demonstrates agentic design patterns including agent workflows, tool usage, and agent collaboration.

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd ai-sales-agent-system
```

### 2. Create Environment File

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
```

### 3. Update Email Addresses

Edit `sales_agent.py` lines 59-60 with your email addresses:

```python
self.from_email = "your-verified-email@domain.com"  # Must be verified in SendGrid
self.to_email = "recipient@domain.com"              # Your recipient email
```

### 4. Run with UV

```bash
uv run sales_agent.py
```

## 🔧 Setup Requirements

### OpenAI API Key
- Get from: https://platform.openai.com/api-keys
- Add to `.env` file

### SendGrid Setup
1. Create account at: https://sendgrid.com/
2. Verify sender email: Settings → Sender Authentication → Verify Single Sender
3. Generate API key: Settings → API Keys → Create API Key
4. Add API key to `.env` file

## 🎯 What It Does

The system demonstrates three agentic design patterns:

### 1. **Agent Workflow Pattern**
- **Professional Agent**: Creates formal, serious emails
- **Engaging Agent**: Generates witty, humorous content  
- **Concise Agent**: Produces brief, direct messages

### 2. **Tool Pattern**
- Functions wrapped with `@function_tool` decorator
- Agents can call `send_email()` and `send_html_email()` functions
- Agents can use other agents as tools

### 3. **Handoff Pattern**
- **Sales Manager** → generates and selects best email
- **Email Manager** → formats with HTML and subject line, then sends

## 📋 Two Workflows

### Basic Workflow
1. Generate 3 emails in parallel (different personas)
2. AI selects the best email
3. Display result (no sending)

### Automated SDR Workflow  
1. Sales Manager generates multiple drafts using agent tools
2. Sales Manager selects best email
3. Sales Manager hands off to Email Manager
4. Email Manager creates subject line and HTML format
5. Email Manager sends the final email automatically

## 🔍 Monitoring

- **OpenAI Traces**: https://platform.openai.com/traces
- **Console Output**: Detailed step-by-step progress
- **Email Delivery**: Check inbox and spam folder

## 🛠️ Troubleshooting

### SSL Certificate Issues
```bash
uv pip install --upgrade certifi
```

### Email Not Received
- Check spam folder
- Verify sender email in SendGrid dashboard
- Ensure API key has send permissions
- Check SendGrid activity logs

### Configuration Issues
```bash
uv run --help sales_agent.py
```

Run the script - it will validate your configuration and show helpful error messages.

## 📁 Project Structure

```
ai-sales-agent-system/
├── sales_agent.py          # Complete application (single file)
├── .env                    # Your API keys (create this)
├── .env.example           # Template for environment variables
└── README.md              # This file
```

## 🔒 Security

- Never commit `.env` files
- Use environment variables for API keys
- Verify sender email in SendGrid
- Update email addresses before running

## 🎊 Features

- **Multi-Agent Email Generation**: 3 different writing styles
- **Intelligent Selection**: AI picks the most effective email
- **Automatic Formatting**: HTML conversion and subject generation
- **SendGrid Integration**: Reliable email delivery
- **OpenAI Tracing**: Monitor agent interactions
- **Error Handling**: Comprehensive error messages and validation
- **UV Compatible**: Run with `uv run sales_agent.py`

---

**Ready to automate your sales outreach!** 🚀

Run `uv run sales_agent.py` and watch the AI agents generate, select, and send your cold emails automatically.
