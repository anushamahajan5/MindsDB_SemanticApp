# Company Knowledge Assistant

A modern web application for searching, browsing, and managing company policies, meetings, and documents using semantic search powered by Cohere AI and MindsDB.

---

## Features

- **Semantic Search:** Find relevant company documents using natural language queries.
- **Browse All Documents:** View all documents in the knowledge base.
- **Add New Documents:** Easily add new policies, meetings, or other documents.
- **Filter by Department:** Narrow down results by department (HR, Marketing, Finance, IT).
- **Modern UI:** Clean, responsive interface built with Bootstrap 5.
- Automated daily updates
- Document summarization

---

## Prerequisites

- **Python 3.8+**
- **Docker** (for running MindsDB locally)
- **Cohere API Key** (for embedding and semantic search)
- **MindsDB Python SDK**
- **Flask**
   
## Installation

1. **Clone the repository:**
```
git clone https://github.com/anushamahajan5/company-knowledge-assistant.git
cd company-knowledge-assistant
```


2. **Set up a virtual environment (optional but recommended):**
```
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```
pip install flask mindsdb-sdk python-dotenv / Install requirements: `pip install -r requirements.txt`
```

4. **Run MindsDB with Docker:**
```
docker run -p 47334:47334 mindsdb/mindsdb
```
5. **Create a `.env` file in your project root:**
COHERE_API_KEY=your-cohere-api-key


6. **Start the Flask app:**
```
python app.py
```

7. **Open your browser to:**

http://localhost:5000


---

## Usage

- **Search:** Enter a query and optionally filter by department.
- **Browse:** View all documents in the knowledge base.
- **Add Document:** Add new documents with content, department, and type.
- **About:** Learn more about the app and its features.

## Project Structure

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
    ├── results.html
    └── search.html

---

## License

MIT

---

## Acknowledgments

- **MindsDB** for knowledge base management
- **Cohere** for semantic search and embeddings
- **Bootstrap** for the modern UI

---

**Enjoy your Company Knowledge Assistant!**

## Usage

1. Access the web interface at `http://localhost:5000`
2. Enter your search query
3. Optionally select a department to filter results

## Video Demo

