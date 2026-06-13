# 📊 Data Analyst Agent (Python + Agentic AI)

An **agentic AI system** built in Python where Claude autonomously decides when to query a database, writes its own SQL, executes it, and explains the results in plain business language — through a real **tool-use loop**, not a scripted pipeline.

---

## 🎯 What Makes This "Agentic"

Unlike a simple chatbot or a fixed script, this agent:

1. **Receives a goal** (your business question) — not a command
2. **Decides for itself** whether it needs data, and which tool to call
3. **Writes its own SQL** based on the schema it's given
4. **Executes the tool**, reads the real results
5. **Reasons over results** and decides if it needs to query again or answer
6. **Responds** with insights + follow-up questions

This is the **tool-use / function-calling agent loop** — the same pattern used in production AI agents.

---

## 🗂️ Sample Database

A realistic e-commerce dataset is auto-generated in SQLite (in-memory, no setup needed):

| Table | Columns |
|---|---|
| `orders` | order_id, customer_id, product_id, category, quantity, price, order_date, status, city |
| `products` | product_id, name, category, cost_price, sell_price, stock |
| `customers` | customer_id, name, city, segment, signup_date |

50 customers, 30 products, 500 orders — generated fresh every run.

---

## 🚀 Setup & Run

### 1. Clone and navigate
```bash
git clone https://github.com/YOUR_USERNAME/data-analyst-agent-python.git
cd data-analyst-agent-python
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API key
```bash
cp .env.example .env
```
Edit `.env` and add your [Anthropic API key](https://console.anthropic.com/):
```
ANTHROPIC_API_KEY=your_key_here
```

### 5. Run the agent
```bash
python agent.py
```

---

## 💬 Example Session

```
🧑 You: Which product category generates the most revenue?

🔧 Agent is using tool: run_sql_query
   Input: {'query': "SELECT category, SUM(price * quantity) AS revenue 
            FROM orders WHERE status != 'Cancelled' 
            GROUP BY category ORDER BY revenue DESC"}

🤖 Agent: Electronics generates the highest revenue at ₹X, followed by
Fashion at ₹Y. This suggests Electronics is your strongest category by
order value, though margins should be checked separately.

Follow-up questions you might explore:
- What are the profit margins by category (sell_price - cost_price)?
- How does revenue vary by city for the top category?
```

---

## 🧩 How the Agent Loop Works (Architecture)

```
┌─────────────────────────────────────────────┐
│  User asks: "Which category drives revenue?" │
└───────────────────┬───────────────────────────┘
                     ▼
        ┌─────────────────────────┐
        │   Claude (with tools)   │
        │   Decides: needs data   │
        └───────────┬─────────────┘
                     ▼
        ┌─────────────────────────┐
        │  Tool: run_sql_query     │
        │  Claude writes the SQL  │
        └───────────┬─────────────┘
                     ▼
        ┌─────────────────────────┐
        │   SQLite Database        │
        │   Executes & returns     │
        │   real rows               │
        └───────────┬─────────────┘
                     ▼
        ┌─────────────────────────┐
        │   Claude reasons over    │
        │   results, writes answer │
        │   + insights + follow-up │
        └───────────┬─────────────┘
                     ▼
              Response to User
```

---

## 📁 Project Structure

```
data-analyst-agent-python/
├── agent.py            # Main agent loop + CLI interface
├── tools.py            # Tool definitions + execution logic
├── database.py         # SQLite database setup with sample data
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🔮 Possible Extensions

- [ ] Add a `create_chart` tool that saves matplotlib charts as images
- [ ] Connect to a real PostgreSQL/MySQL database instead of SQLite
- [ ] Add a `export_to_csv` tool for downloading results
- [ ] Wrap with a Streamlit UI for a web interface
- [ ] Add a `get_table_schema` self-check before every query (already partially implemented)
- [ ] Multi-agent setup: one agent for SQL, one for visualization, one for narrative insights

---

## 🛠️ Tech Stack

- **Python 3.9+**
- **Anthropic SDK** (Claude Sonnet 4) — agent reasoning + tool use
- **SQLite** — lightweight embedded database
- **Pandas** — query result formatting

---

## 👤 Author

**Prachursya** — Data Analyst | SQL · Python · Power BI · Tableau  
[LinkedIn](https://linkedin.com/in/YOUR_PROFILE) · [GitHub](https://github.com/YOUR_USERNAME)

---

## 📄 License

MIT License
