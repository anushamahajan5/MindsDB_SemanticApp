# 🌐 Company Knowledge Assistant 🧠✨

Your AI-powered company knowledge base and assistant, built with MindsDB, OpenAI, and Flask.

---

## 📜 Overview

This project is a modern, AI-powered assistant for company policies, meeting notes, and important documents.  
Think of it as the ChatGPT for your company’s knowledge base—now equipped with semantic search, summarization, and easy browsing.

It supports:

⚙️ **OpenAI integration via MindsDB ML Engine**  
🧠 **AI-augmented Knowledge Base querying**  
🗂️ **Inserting and browsing company documents**  
🔍 **Semantic search with department filtering**  
⚖️ **Full Flask backend with modern, responsive UI**  
📝 **AI-powered document summarization**  
🤖 **Chat with AI for instant answers**  
🔄 **Automated daily updates via scheduled jobs**

---

## 🚀 Features

💬 **Semantic Search:** Find answers using natural language—no need for exact keywords.  
🌱 **AI-Powered Summarization:** Get concise summaries of any FAQ or policy.  
🗃️ **Easy Document Management:** Add, browse, and update documents with ease.  
🔧 **Automated Updates:** Daily job inserts test documents and keeps your KB fresh.  
💻 **Modern UI:** Clean, responsive interface built with Bootstrap 5.  
🤖 **AI Chat:** Ask questions and get instant answers from your knowledge base.

---


## Prerequisites

- **Python 3.8+**
- **Docker** (for running MindsDB locally)
- **Cohere API Key** (for embedding and semantic search)
- **MindsDB Python SDK**
- **Flask**
   
## Installation

1. **🧪 Clone the repository:**
```
git clone https://github.com/your-username/company-knowledge-assistant.git
cd company-knowledge-assistant
```


2. **✨Set up a virtual environment (optional but recommended):**
```
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

3. **📦 Install dependencies:**
```
pip install flask mindsdb-sdk python-dotenv
```

4. **🐳 Run MindsDB with Docker:**
```
docker run -p 47334:47334 mindsdb/mindsdb
```
### Suggested Approach:
Pass your api when running mindsDB locally using:
```
docker run -p 47334:47334 -e OPENAI_API_KEY=sk-.....A mindsdb/mindsdb
```

5. **🔑 Create a `.env` file in your project root or u can directly set it in settings of mindsDB GUI if you are using that:**
```
COHERE_API_KEY=your-cohere-api-key
```

6. **🚀 Start the Flask app:**
```
python app.py

```
7. **🌐 Open your browser to:**
```
http://localhost:5000
```

8. **Open the mindsDB GUI here:**
Note you are going to test all queries here
```
http://localhost:47334
```
---
## 🔍 How It Works
1. Add Documents:
You add company policies, meeting notes, or other documents directly through the app.

2. Store in Knowledge Base:
The content is stored in the MindsDB knowledge base as text chunks.

3. Create AI Index:
MindsDB uses OpenAI embeddings to create “smart embeddings”—a mathematical understanding of the meaning of each document. These are created by default soo running a query will give you syntax error.

4. Ask Questions:
When you search or ask a question, the system finds relevant documents based on meaning, not just keywords using mindsDB's semantic search.

5. Generate Answers:
The AI model (OpenAI or MindsDB-powered) summarizes or extracts answers from the most relevant documents using AI table created in the application.
---

# 🧠 Why This Works

- **MindsDB Knowledge Base:**
   - Your filing cabinet (stores the actual documents).
   - Your smart librarian (understands what documents mean and finds relevant ones).
- **OpenAI/MindsDB AI:**
   - Your assistant (reads relevant documents and answers your questions or summarizes content).

---
## 🏗️ Simple Architecture

┌─────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│   Your      │───▶│   MindsDB Knowledge  │◄──▶│   OpenAI /      │
│  Documents  │    │        Base          │    │   MindsDB AI    │
└─────────────┘    └─────────────────────┘    └─────────────────┘
       │                                              │
       │                                              ▼
       │                                      ┌─────────────────┐
       └─────────────────────────────────────▶│   Semantic      │
                                              │   Search &      │
                                              │   Answers       │
                                              └─────────────────┘

---
## 🔄 Data Flow

1. Add:
You add documents through the app.

2. Store:
Documents are stored in the MindsDB knowledge base as text chunks.

3. Index:
MindsDB creates embeddings for semantic search.

4. Query:
You ask questions or search for information.

5. Answer:
The AI finds relevant documents and generates answers or summaries.

## 🤖 AI Models (Cloud & Local)
- **Embeddings**:
    - OpenAI text-embedding-3-small (cloud-based, fast and accurate)
    - MindsDB-managed embeddings for semantic search.
- **Summarization & QA**:
    - OpenAI GPT-3.5-turbo (cloud-based, powerful for summarization and chat).
    - MindsDB-powered models for local or custom AI workflows.
- **Lightweight & Scalable**:
    - Runs on your local machine or in the cloud.
    - No GPU required for most use cases.

## Sample Queries to be tested in MindsDB GUI
  
  1. Create Knowledge Base
  Test the creation of your knowledge base:
  ```
  CREATE KNOWLEDGE_BASE company_kb
  USING
    embedding_model = {
        "provider": "openai",
        "model_name": "text-embedding-3-small"
    },
    metadata_columns = ['department', 'doc_type'],
    content_columns = ['content']

  ```
  **Note:** If your API key is not set as an environment variable in MindsDB, include the api_key field in embedding_model. Otherwise, leave it as shown in  code

  2. Insert Sample Data
  Insert test documents into your knowledge base:
  ```
  INSERT INTO company_kb (content, department, doc_type)
  VALUES
    ('Our company offers 30 days vacation per year.', 'HR', 'policy'),
    ('Marketing team meetings are every Wednesday at 2pm.', 'Marketing', 'meeting'),
    ('IT support is available 24/7 for urgent issues.', 'IT', 'procedure')

  ```

  3. Semantic Search
  Query your knowledge base with a semantic search:
  ```
  SELECT *
  FROM company_kb
  WHERE content = 'vacation policy';
  ```
  4. Semantic Search with Metadata Filter
  Query your knowledge base with a semantic search:
  ```
  SELECT *
  FROM company_kb
  WHERE content = 'meeting'
   AND department = 'Marketing';

  ```
  5. Browse All Documents
  List all documents in your knowledge base:
  ```
  SELECT * FROM company_kb

  ```

  6. Create and Test Update Job
  **Note:** This tests the setup_update_job() function. Ensure you upload the new_documents.csv file using *Add→Upload File* in GUI. It will be visible under Files in Datasources in left Pane.
  Schedule a job to update the knowledge base from your uploaded file:
  ```
  CREATE JOB update_company_kb AS (
    INSERT INTO company_kb (content, department, doc_type)
    SELECT content, department, doc_type
    FROM files.new_documents
    WHERE id > COALESCE(LAST, 0)
  )
  EVERY day
  ```
  7. Create a Documet Summarizer model/ Setup AI Table
  Open AI Model:
  ```
  CREATE ML_ENGINE openai_engine FROM openai
  ```
  document_summarizer Model:
  ```
  CREATE MODEL document_summarizer
  PREDICT summary
  USING
    engine = 'openai_engine',
    model_name = 'gpt-3.5-turbo',
    prompt_template = 'Summarize this company document: {{content}}';
  ```
  **Note:** If your API key is not set as an environment variable in MindsDB, include the api_key field in embedding_model. Otherwise, leave it as shown in  code

  8. Get Summary Results
  ```
  SELECT summary
  FROM document_summarizer
  WHERE content = 'Our company offers 30 days vacation per year.'

  ```
---
## 🧪 Usage

- **🏠 Homepage:** Search for documents using natural language queries.
- **🔍 Browse:** View all documents in the knowledge base.
- **➕ Add:** Insert new policies, meetings, or other documents.
- **📝 Summarize:** Get AI-generated summaries of any document.
- **🤖 Chat:** Interact with the AI assistant for quick answers.

---

## Project Structure

<pre>
company-knowledge-assistant/
├── app.py # Flask application
├── README.md # This file
├── requirements.txt # Python dependencies
├── .env # Environment variables
├── static/ styles.css
└── templates/ # HTML templates
    ├── about.html
    ├── add.html
    ├── browse.html
    ├── chat.html
    ├── results.html
    ├── summarize.html
    └── search.html
    
</pre>
---

## 🧑‍🎓 Sample Data

- **"Our company offers 30 days vacation per year."** (HR, policy)
- **"Marketing team meetings are every Wednesday at 2pm."** (Marketing, meeting)
- **"IT support is available 24/7 for urgent issues."** (IT, procedure)
---
## 🧪 Example Semantic Search SQL

```
SELECT chunk_content, metadata
FROM company_kb
WHERE content = 'vacation policy'
AND metadata.department = 'HR'
```


---

## 📦 Tech Stack

| Layer      | Stack                |
|------------|---------------------|
| Backend    | Flask + Jinja2      |
| AI Layer   | MindsDB + OpenAI    |
| DB Engine  | MindsDB KB          |
| Frontend   | Bootstrap 5         |

---

## ❤️ Acknowledgments

- **🧠 MindsDB** – Making ML as easy as SQL
- **🤖 OpenAI** – For semantic search and summarization
- **⚡ Flask** – Simple and flexible web framework
- **🎨 Bootstrap** – For the modern UI
- **🐳 Docker** – For local MindsDB setup

---

## 🦻 Developer Notes

Got errors like table doesn't exist? Restart the server—it auto-creates everything on init.  
Want to reset? Just nuke and relaunch. KBs are created on each fresh start.  
Add more metadata tags, departments, or features—this KB is born to scale.

---

## 🎥 Video Demo

Include a short video demo showcasing the app's features: search, browse, add, summarize, and chat.

---


# 🏆 MindsDB Knowledge Base Quest Documentation
## ✅ How This Project Meets the Quest Requirements

- **✅ App with KBs [40pts]:**  
  - Executes `CREATE KNOWLEDGE_BASE`
  - Ingests data with `INSERT INTO knowledge_base`
  - Retrieves data with semantic queries (`SELECT ... WHERE content = 'query'`)
  - Uses `CREATE INDEX ON KNOWLEDGE_BASE` ( ChromaDB provides the index features by default.)
- **✅ Metadata Columns[10pts]:**  
  - Defines and uses `metadata_columns` (department, doc_type)
  - Filters with SQL (`WHERE metadata.department = 'HR'`)
- **✅ Jobs Integration:**  
  - Sets up a MindsDB JOB to periodically insert new data
  - setup_update_job() called as soon as application runs
- **✅ AI Tables/Agents Integration:**  
  - Multi-step workflow: KB results are fed into MindsDB AI Tables for summarization and to generate chat response
  1. **User Input:** The user enters a question or message in the chat.
  2. **Semantic Search:** The app queries the MindsDB knowledge base to find relevant documents.
  3. **Summarization:** The top result is fed into a MindsDB AI Table (`document_summarizer`) to generate a summary.
  4. **Chat Response:** The summary is returned as the bot’s reply.
  - The summarization is a multi-step workflow:
  User Input → Semantic Search (KB) → Summarization (MindsDB AI Table) → Chat Response

 
- **✅ Video & README[30pts]:**  
  - Includes a video demo and clear README [link](https://drive.google.com/file/d/17NRnqUIUEhthzalcsSGnFnhS6HMLUZrP/view?usp=sharing)
- **✅ Documentation & Showcase [5pts]:**  
  - Medium article: [link](https://medium.com/@anushamahajan5/building-a-company-knowledge-assistant-with-mindsdb-and-cohere-572dfff41b93)
- **✅ Feedback & Feature Suggestions[5pts]:**  
  - Submitted feedback via MindsDB Product Feedback Form

---

**Enjoy your Company Knowledge Assistant!**
