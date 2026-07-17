# 🚀 Enterprise Employee Knowledge Assistant

An enterprise-grade **Employee Knowledge Assistant** built using **Model Context Protocol (MCP)**, **FastMCP**, **FastAPI**, **PostgreSQL**, and **Claude Desktop**. This project demonstrates how Large Language Models can securely interact with enterprise employee data through custom MCP tools and REST APIs.

---

## 📌 Overview

The Employee Knowledge Assistant enables AI applications such as Claude Desktop to retrieve employee information using custom MCP tools backed by a PostgreSQL database.

The application exposes both:

- **MCP Tools** for AI assistants
- **REST APIs** using FastAPI
- **PostgreSQL** as the enterprise data source

---

# 🏗 Architecture

```
                    Claude Desktop
                           │
                           ▼
                 Model Context Protocol
                           │
                           ▼
                     FastMCP Server
                           │
               ┌───────────┴───────────┐
               ▼                       ▼
        Employee MCP Tools        FastAPI REST API
               │                       │
               └───────────┬───────────┘
                           ▼
                  Python Business Logic
                           ▼
                    PostgreSQL Database
                           ▼
                     Employee Records
```

---

# ✨ Features

- Employee Lookup by Employee ID
- Employee Listing
- Employee Summary
- PostgreSQL Integration
- FastAPI REST APIs
- Claude Desktop Integration
- MCP Inspector Testing
- Environment Configuration (.env)
- Enterprise Project Structure

---

# 🛠 Tech Stack

### Backend

- Python 3.x
- FastAPI
- FastMCP
- Model Context Protocol (MCP)
- Uvicorn

### Database

- PostgreSQL
- pgAdmin4
- psycopg2

### AI

- Claude Desktop
- MCP Inspector

### Development

- Git
- GitHub
- VS Code
- python-dotenv

---

# 📁 Project Structure

```
mcp_employee_knowledge_assistant/

│
├── api.py
├── server.py
├── employees.csv
├── README.md
├── .env
├── database/
│
├── test_tools_locally.py
│
└── .gitignore
```

---

# MCP Tools

| Tool | Description |
|-------|-------------|
| list_employees | Returns all employees |
| employee_summary | Returns employee statistics |
| get_employee_by_id | Retrieves employee by Employee ID |

---

# REST APIs

| Endpoint | Description |
|-----------|-------------|
| GET /employees | List employees |
| GET /employees/{employee_id} | Employee lookup |
| GET /employee-summary | Employee summary |

Swagger UI

```
http://127.0.0.1:8000/docs
```

---

# Running FastAPI

```bash
uvicorn api:app --reload
```

---

# Running MCP Server

```bash
uv run --with mcp mcp run server.py
```

---

# Running Claude Desktop

Configure:

```
claude_desktop_config.json
```

```json
{
  "mcpServers": {
    "employee-knowledge-assistant": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp",
        "mcp",
        "run",
        "C:\\AI\\MCP\\mcp_employee_knowledge_assistant\\mcp_employee_knowledge_assistant\\server.py"
      ]
    }
  }
}
```

---

# Database

Database

```
employee_db
```

Table

```
employees
```

---


# Skills Demonstrated

- Model Context Protocol (MCP)
- FastMCP
- FastAPI
- REST API Development
- PostgreSQL
- SQL
- Python
- AI Tool Development
- Claude Desktop Integration
- MCP Inspector
- Environment Configuration
- Git
- GitHub

---

# Future Enhancements

- JWT Authentication
- CRUD Operations
- Docker
- Docker Compose
- Kubernetes
- GitHub Actions CI/CD
- Role-Based Access Control
- LangChain Integration
- LangGraph Integration
- Vector Database
- RAG Pipeline
- AWS Deployment
- Azure Deployment

---

# Author

**Gireesh Gopal Reddy Vuyyuru**

GitHub:
Mail:Girishsap45@gmail.com
https://github.com/gireeshvuyyuru501-design

LinkedIn:www.linkedin.com/in/girish-genai-engineer

(Add LinkedIn URL)

---

# License

This project is licensed under the MIT License.
