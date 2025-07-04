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
📊 **Per-Question Evaluation:** Custom logic to assess knowledge base accuracy for each test question.  
📝 **Feedback Analysis:** Collect and analyze user feedback for sentiment and actionable insights.  
🤖 **Agent Integration:** Create and use MindsDB Agents for advanced workflows.

---

## Prerequisites

- **Python 3.8+**
- **Docker** (for running MindsDB locally)
- **OpenAI API Key** (for embedding and semantic search)
- **MindsDB Python SDK**
- **Flask**
- **ChromaDB**
   
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
OPENAI_API_KEY=your-openai-api-key
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
Note you can test your commands here although they are directly implemented in app and can be directly seen in th application 
```
http://localhost:47334
```

9. ChromaDB Integration
ChromaDB is the default vector database for MindsDB knowledge bases.
When you create a knowledge base, MindsDB automatically sets up a ChromaDB instance to store document embeddings—no extra installation or configuration is needed for the default setup.

---
## 🔍 How It Works
1. Add Documents:
You add company policies, meeting notes, or other documents directly through the app.

2. Store in Knowledge Base:
The content is stored in the MindsDB knowledge base as text chunks.

3. Create AI Embeddings Index:
MindsDB uses OpenAI embeddings to create “smart embeddings”—a mathematical understanding of the meaning of each document.
Note: Embeddings are created automatically by MindsDB when the knowledge base is created, so manual index creation is not needed.

4. Ask Questions:
When you search or ask a question, the system finds relevant documents based on meaning, not just keywords using mindsDB's semantic search.

5. Generate Answers:
The AI model (OpenAI or MindsDB-powered AI models) summarizes or extracts answers from the most relevant documents using AI table created in the application.
---

# 🧠 Why This Works

- **MindsDB Knowledge Base:**
   - Your filing cabinet (stores the actual documents).
   - Your smart librarian (understands what documents mean and finds relevant ones).
- **OpenAI/MindsDB AI:**
   - Your assistant (reads relevant documents and answers your questions or summarizes content).

---
## 🏗️ Simple Architecture
<pre>
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
</pre>
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
metadata_columns = ['department', 'doc_type','answer'],
content_columns = ['content']
```

For feedbacks:
```
    CREATE KNOWLEDGE_BASE feedback_kb
    USING
      embedding_model = {
        "provider": "openai",
        "model_name": "text-embedding-3-small"
      },
      metadata_columns = ['doc_id', 'rating', 'analysis'],
      content_columns = ['comment'];
```
   **Note:** If your API key is not set as an environment variable in MindsDB, include the api_key field in embedding_model. Otherwise, leave it as shown in  code

    This will automatically add chromadb database under Datasources in left pane

  2. Insert Sample Data
  Insert test documents into your knowledge base:
  ```
  INSERT INTO company_kb (content, department, doc_type, answer)
  VALUES
  ('How much vacation do we get per year?', 'HR', 'policy','Our company offers 30 days vacation per year.'),
  ('When are Marketing team meetings?', 'Marketing', 'meeting','Marketing team meetings are every Wednesday at 2pm.'),
  ('What is the dress code?', 'HR', 'policy', 'Smart casual'),
  ('Where to submit reimbursements?', 'Finance', 'policy', 'Upload receipts in the portal within 7 days'),
  ('What is the WFH policy?', 'HR', 'policy', 'Work from home allowed 2 days/week with approval'),
  ('How do I reset my company email password?', 'IT', 'support', 'Use the self-service password reset tool or contact IT support.'),
  ('Where can I find the company holiday calendar?', 'HR', 'policy', 'It is available on the internal HR portal under "Resources".'),
  ('Who approves travel requests?', 'Operations', 'policy', 'Your department head must approve all travel requests.'),
  ('How can I book a meeting room?', 'Admin', 'procedure', 'Use the Outlook Room Booking tool or the Admin Desk app.'),
  ('What tools does the Design team use?', 'Design', 'tools', 'Figma, Adobe Creative Suite, and Canva.');

  ```
  For feedbacks:
  ```
  INSERT INTO feedback_kb (comment, doc_id, rating, analysis)
  VALUES 
  ('Clear vacation policy!', 1, 5, 'Positive'),
  ('Very detailed explanation of WFH policy.', 3, 4, 'Positive'),
  ('Didn’t find enough info on reimbursement steps.', 2, 2, 'Negative'),
  ('Too much jargon in the dress code document.', 4, 3, 'Neutral'),
  ('Appreciate the quick access to travel policy.', 5, 5, 'Positive'),
  ('Summary was vague and lacked clarity.', 6, 2, 'Negative'),
  ('Great layout and simple language.', 1, 5, 'Positive'),
  ('Helpful but missing real examples.', 3, 3, 'Neutral'),
  ('Outdated policy, needs revision.', 2, 1, 'Negative'),
  ('Loved how concise the remote work policy was.', 3, 5, 'Positive');

  ```

  3. Semantic Search
  Query your knowledge base with a semantic search:
  ```
  SELECT *
  FROM company_kb
  WHERE content = 'vacation policy';
  ```

  You can also try for feedbacks:
  ```
  SELECT * FROM feedback_kb
  WHERE MATCH('The vacation policy is helpful');
  ```
  4. Semantic Search with Metadata Filter
  Query your knowledge base with a semantic search:
  ```
  SELECT *
  FROM company_kb
  WHERE content = 'meeting'
   AND department = 'Marketing';

  ```
  For feedbacks:
  ```
  SELECT * FROM feedback_kb
  WHERE MATCH('unclear explanation')
   AND rating <= 3
   AND analysis = 'Negative';

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
    INSERT INTO company_kb (content, department, doc_type, answer)
    SELECT content, department, doc_type, answer
    FROM files.new_documents
    WHERE id > COALESCE(LAST, 0)
  )
  EVERY day
  ```
  This is equivalent to:
  ```
  INSERT INTO company_kb (content, department, doc_type, answer)
  SELECT content, department, doc_type, answer
  FROM files.new_documents
  WHERE id > 0; 
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
  feedback_analysis_model:
  ```
  CREATE MODEL feedback_analysis_model
  PREDICT analysis
  USING
    engine = 'openai',
    model_name = 'gpt-3.5-turbo',
    prompt_template = 'Analyze this user feedback and provide: sentiment (positive, neutral, negative), key points, and actionable suggestions. Feedback: {comment}';
  ```

  **Note:** If your API key is not set as an environment variable in MindsDB, include the api_key field in embedding_model. Otherwise, leave it as shown in  code

  8. Get Summary Results
  ```
  SELECT summary
  FROM document_summarizer
  WHERE content = 'Our company offers 30 days vacation per year. We believe that taking breaks is healthy and employee helath affects quality of work.'

  ```

  9. Agent Creation

  company_faq_agent:
  ```
  CREATE AGENT company_faq_agent
  USING
    model = 'openai_faq_model',
    include_knowledge_bases = ['project.company_kb'],
    prompt_template = 'You are a helpful assistant for company FAQs and policies. Use the knowledge base to answer: {question}';

  ```
  feedback_analysis_agent:
  ```
  CREATE AGENT feedback_analysis_agent
  USING
    model = 'feedback_analysis_model',
    include_knowledge_bases = ['project.feedback_kb'],
    prompt_template = 'Analyze: {comment}';

  ```
  10. Evaluate Knowledge Base
  Evaluate the relevancy and accuracy of documents returned by the knowledge base:
  ```
  EVALUATE KNOWLEDGE_BASE company_kb
  USING
  test_table = files.test_questions,
  version = 'doc_id',
  evaluate = true,
  llm = {
    'provider': 'openai',
    'api_key': 'your_openai_api_key',
    'model': 'gpt-4'
  }

  ```
  11. Create jobs
      /job can be used for creating job
  ```
  INSERT INTO files.test_questions (doc_id, question, expected_answer)
  VALUES (6, 'How many sick days are allowed per year?', 'Employees are allowed up to 10 sick days per year.');

  ```
  
---
## 🧪 Usage

- **🏠 Homepage:** Search for documents using natural language queries.
- **🔍 Browse:** View all documents in the knowledge base.
- **➕ Add:** Insert new policies, meetings, or other documents.
- **📝 Summarize:** Get AI-generated summaries of any document.
- 📊 **Per-Question Evaluation:** Custom logic to assess knowledge base accuracy for each test question.  
- 📝 **Feedback Analysis:** Collect and analyze user feedback for sentiment and actionable insights.  
- 🤖 **Agent Integration:** Create and use MindsDB Agents for advanced workflows.

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
    ├── evaluate.html
    ├── feedback.html
    ├── related.html
    ├── results.html
    ├── summarize.html
    └── search.html
    
</pre>
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

## 🦻 Future Scope
1. Currently, adding FAQs/policy and feedback is not working on GUI; they have to be added using the MindsDB GUI. job created also not working
2. The feedback is not being shown on the app, but later can be integrated to show feedback from feedback_kb
3. Expand semantic search to include more data sources and support multilingual queries.
4. Enhance AI features with automated tagging, summarization, and personalized recommendations.
5. Integrate with messaging platforms and voice assistants for multi-channel access.
6. Add analytics and collaboration tools for insights and user contributions.

---

## 🎥 Video Demo
[Link](https://drive.google.com/file/d/1-4EXA5nU2v-onwUYrHLChLY7GsxwwOlz/view?usp=sharing)

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
- **✅ Jobs Integration[10 pts]**  
  - Sets up a MindsDB JOB to periodically insert new data
  - setup_update_job() called as soon as application runs
- **✅ AI Tables/Agents Integration[10 pts]**  
  - Multi-step workflow: KB results are fed into MindsDB AI Tables for summarization and to generate chat response
  1. **User Input:** The user enters a question or message in the chat.
  2. **Semantic Search:** The app queries the MindsDB knowledge base to find relevant documents.
  3. **Summarization:** The top result is fed into a MindsDB AI Table (`document_summarizer`) to generate a summary.
  4. **Chat Response:** The summary is returned as the bot’s reply.
  - The summarization is a multi-step workflow:
  User Input → Semantic Search (KB) → Summarization (MindsDB AI Table) → Chat Response
- **✅ Agent Creation[10 pts]**
  - created `feedback_analysis_agent` for analysis of feedback given by user for a document.
  - Feedback can be positive,negative or neutral.
- **✅ Evaluate the relevancy and accuracy of the documents returned by KB[20pts]**
  - Used `EVALUATE KNOWLEDGE_BASE` and OPENAI api for evaluating company kb.
- **✅ Video & README[30pts]:**  
  - Includes a video demo and clear README [link](https://drive.google.com/file/d/1-4EXA5nU2v-onwUYrHLChLY7GsxwwOlz/view?usp=sharing)
- **✅ Documentation & Showcase [5pts]:**  
  - Medium article: [link](https://medium.com/@anushamahajan5/building-a-company-knowledge-assistant-with-mindsdb-and-cohere-572dfff41b93)

