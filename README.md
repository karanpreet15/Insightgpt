# 📊 InsightGPT – AI-Powered Analytics Assistant

InsightGPT is an AI-powered analytics platform that enables users to analyze CSV datasets using natural language. Instead of writing SQL queries manually, users can simply ask questions in plain English and receive SQL-generated results, visualizations, business insights, and downloadable reports.

Built with **Streamlit**, **DuckDB**, **Ollama**, and **Qwen2.5-Coder**, the application runs completely locally without requiring external API keys.

---

## 🚀 Features

* Natural Language to SQL conversion
* Automatic DuckDB query execution
* CSV dataset upload and analysis
* Intelligent chart generation
* AI-powered business insights
* PDF report generation
* Query history tracking
* Fully local execution using Ollama
* No API costs or rate limits

---

## 🏗️ Architecture

```text
User Question
      │
      ▼
Qwen2.5-Coder (Ollama)
      │
      ▼
Generated SQL Query
      │
      ▼
DuckDB Execution
      │
      ▼
Result Dataset
      │
 ┌────┴────┐
 ▼         ▼
Charts   Business Insights
      │
      ▼
PDF Report Generation
```

---

## 🛠️ Tech Stack

### Frontend

* Streamlit

### Database Engine

* DuckDB

### AI Model

* Ollama
* Qwen2.5-Coder 7B

### Data Processing

* Pandas
* NumPy

### Visualization

* Plotly

### Reporting

* ReportLab

---

## 📂 Project Structure

```text
InsightGPT/
│
├── app.py
├── requirements.txt
│
├── core/
│   ├── llm.py
│   ├── data_loader.py
│   ├── nl_to_sql.py
│   ├── sql_engine.py
│   ├── chart_generator.py
│   ├── insights_generator.py
│   └── pdf_report.py
│
└── datasets/
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/InsightGPT.git
cd InsightGPT
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Ollama

Download and install Ollama:

https://ollama.com

Pull the model:

```bash
ollama pull qwen2.5-coder:7b
```

Verify installation:

```bash
ollama list
```

---

## ▶️ Run Application

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

## 📈 Example Questions

* What are my top 10 selling products by revenue?
* Which customers generated the highest sales?
* Show monthly sales trends.
* Which region contributes the most revenue?
* What are the lowest-performing products?
* Show category-wise revenue breakdown.

---

## 📄 PDF Reporting

InsightGPT allows users to export:

* Generated SQL Queries
* Query Results
* Charts
* Business Insights

into a downloadable PDF report.

---

## 🎯 Key Highlights

* Conversational analytics using natural language
* Automated SQL generation and execution
* Dynamic visualizations and reporting
* Fully offline and local deployment
* No dependency on paid AI APIs

---

## 🔮 Future Enhancements

* Multi-file dataset joins
* Voice-based analytics assistant
* Dashboard generation from prompts
* Advanced forecasting and predictive analytics
* Role-based authentication
* Database connectivity (MySQL, PostgreSQL, Snowflake)

---

## 👨‍💻 Author

Karanpreet Singh

B.Tech Electronics & Computer Engineering

Thapar Institute of Engineering & Technology

Data Analytics | AI | Machine Learning | Generative AI
