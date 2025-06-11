import os
import json
from dotenv import load_dotenv
import mindsdb_sdk  # Updated import
from flask import Flask, request, render_template, redirect, url_for


app = Flask(__name__)
load_dotenv()

# Initialize MindsDB connection - NEW WAY
con = mindsdb_sdk.connect(
    'http://127.0.0.1:47334'
)
project = con.get_project()
kb = project.knowledge_bases.get('company_kb')

def insert_sample_data():
    documents = [
        {"content": "Our company offers 30 days vacation policy for all employees", "department": "HR", "doc_type": "policy"},
        {"content": "The marketing team meets every Wednesday at 2pm", "department": "Marketing", "doc_type": "meeting"},
        {"content": "Expense reports must be submitted by the 5th of each month", "department": "Finance", "doc_type": "policy"}
    ]
    kb.insert(documents)

# Create Knowledge Base (10 points)
#  Use Metadata Columns (10 pts)
def create_knowledge_base():
    cohere_api_key = os.getenv('COHERE_API_KEY')
    try:
        project.query("""
        CREATE KNOWLEDGE_BASE company_kb
        USING
        embedding_model = {
        "provider": "cohere",
        "model_name": "embed-english-v3.0",
        "api_key": "{cohere_api_key}"
        },
        metadata_columns = ['department', 'doc_type'],  
        content_columns = ['content'];

        """)
        print("Knowledge Base created successfully")
    except Exception as e:
        print(f"Knowledge Base already exists or error: {e}")


# Insert sample data (10 points)
def insert_sample_data():
    documents = [
        {
            'content': 'Our company offers 30 days vacation policy for all employees',
            'department': 'HR',
            'doc_type': 'policy'
        },
        {
            'content': 'The marketing team meets every Wednesday at 2pm',
            'department': 'Marketing',
            'doc_type': 'meeting'
        },
        {
            'content': 'Expense reports must be submitted by the 5th of each month',
            'department': 'Finance',
            'doc_type': 'policy'
        }
    ]
    for doc in documents:
        project.query(f"""
        INSERT INTO company_kb (content, department, doc_type)
        VALUES ('{doc['content']}', '{doc['department']}', '{doc['doc_type']}')
        """)
    print("Sample data inserted")

# Create index (10 points)
def create_index():
    project.query("CREATE INDEX ON company_kb")
    print("Index created")

# Semantic search function (10 points)
#Use WHERE clauses that combine semantic search with SQL attribute filtering  ( [10 pts] Use metadata columns)
def semantic_search(query, department=None):
    base_query = f"""
    SELECT *
    FROM company_kb
    WHERE content = '{query}'
    """
    if department:
        base_query += f" AND department = '{department}'"
    results = project.query(base_query).fetch()
    # Convert DataFrame to list of dicts
    return results.to_dict(orient='records')

#Integrate JOBS (10 pts)
def setup_update_job():
    project.query("""
    CREATE JOB update_company_kb AS (
        INSERT INTO company_kb (content, department, doc_type)
        VALUES ('Daily test document added by job', 'IT', 'test')
    )
    EVERY day
    """)
    print("Update job created")

#Integrate with AI Tables or Agents (10 pts)
def setup_ai_table():
    project.query("""
    CREATE MODEL document_summarizer
    PREDICT summary
    USING
        engine = 'openai',
        prompt_template = 'Summarize this company document: {{content}}';
    """)
    def get_summarized_results(query):
        search_results = semantic_search(query)
        summaries = []
        for result in search_results:
            summary = project.query(f"""
            SELECT summary FROM document_summarizer
            WHERE content = '{result['content']}'
            """).fetch()
            summaries.append({
                'original': result['content'],
                'summary': summary[0]['summary']
            })
        return summaries
    return get_summarized_results

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form['query']
        department = request.form.get('department')
        raw_results = semantic_search(query, department)
        print(raw_results)
        print(type(raw_results))
        for i, row in enumerate(raw_results):
            print(f"Row {i}: {row} ({type(row)})")

        results = []
        for row in raw_results:
            # Extract content from chunk_content column
            content = row.get('chunk_content', '')
            
            # Parse metadata (JSON string)
            metadata_str = row.get('metadata', '{}')
            try:
                metadata = json.loads(metadata_str)
            except:
                metadata = {}
                
            results.append({
                'content': content,
                'department': metadata.get('department', ''),
                'doc_type': metadata.get('doc_type', '')
            })
            
        return render_template('results.html', results=results, query=query)
        
    return render_template('search.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/browse')
def browse():
    results = project.query("SELECT * FROM company_kb").fetch()
    results = results.to_dict(orient='records')
    print("Browse results:", results)
    processed = []
    for row in results:
        content = row.get('chunk_content', '')
        metadata = json.loads(row.get('metadata', '{}'))
        processed.append({
            'content': content,
            'department': metadata.get('department', ''),
            'doc_type': metadata.get('doc_type', '')
        })
    return render_template('browse.html', results=processed)

@app.route('/add', methods=['GET', 'POST'])
def add_document():
    if request.method == 'POST':
        content = request.form['content']
        department = request.form['department']
        doc_type = request.form['doc_type']
        print(f"Adding: content={content}, department={department}, doc_type={doc_type}")
        project.query(f"""
        INSERT INTO company_kb (content, department, doc_type)
        VALUES ('{content}', '{department}', '{doc_type}')
        """)
        print("Insert query executed")
        return redirect(url_for('browse'))
    return render_template('add.html')



if __name__ == '__main__':
    create_knowledge_base()
    insert_sample_data()
    create_index()
    setup_update_job()
    setup_ai_table()
    app.run(debug=True)
