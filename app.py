import os
import json
from dotenv import load_dotenv
import mindsdb_sdk
from flask import Flask, request, render_template, redirect, url_for, session
import nest_asyncio
nest_asyncio.apply()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')
load_dotenv()

# Initialize MindsDB connection
con = mindsdb_sdk.connect('http://localhost:47334')
project = con.get_project()
print("Connected to MindsDB project:", project.name)
kb = None

# Create Knowledge Base (10 points)
# Use Metadata Columns (10 pts)
def create_knowledge_base():
    global kb
    openai_api_key = os.getenv('OPENAI_API_KEY')
    try:
        project.query(f"""
        CREATE KNOWLEDGE_BASE company_kb
        USING
            embedding_model = {{
                "provider": "openai",
                "model_name": "text-embedding-3-small",
                "api_key": "{openai_api_key}"
            }},
            metadata_columns = ['department', 'doc_type'],
            content_columns = ['content']
        """)
        kbs = project.knowledge_bases.list()
        print("Available Knowledge Bases:", [kb.name for kb in kbs])
        kb = project.knowledge_bases.get('company_kb')
        print("Knowledge Base created successfully")
    except Exception as e:
        print(f"Knowledge Base error: {e}")

def setup_ai_tables():
    openai_api_key = os.getenv('OPENAI_API_KEY')
    project.query(f"""
    CREATE ML_ENGINE openai_engine FROM openai
    USING api_key = '{openai_api_key}';
    """)
    project.query(f"""
    CREATE MODEL document_summarizer
    PREDICT summary
    USING
        engine = 'openai_engine',
        model_name = 'gpt-3.5-turbo',
        prompt_template = 'Summarize this company document: {{content}}';
    """)
    print("AI tables created")

def insert_sample_data():
    documents = [
        {"content": "Our company offers 30 days vacation per year.", "department": "HR", "doc_type": "policy"},
        {"content": "Marketing team meetings are every Wednesday at 2pm.", "department": "Marketing", "doc_type": "meeting"},
        {"content": "IT support is available 24/7 for urgent issues.", "department": "IT", "doc_type": "procedure"},
        {"content": "Sales targets are reviewed quarterly.", "department": "Sales", "doc_type": "strategy"},
        {"content": "Finance manages budgets and approves expenses.", "department": "Finance", "doc_type": "report"},
        {"content": "Legal reviews all contracts before signing.", "department": "Legal", "doc_type": "procedure"}
    ]
    
    if kb:
        try:
            # Batch insert using raw SQL
            values = ",".join([
                f"('{doc['content']}', '{doc['department']}', '{doc['doc_type']}')" 
                for doc in documents
            ])
            project.query(f"""
            INSERT INTO company_kb (content, department, doc_type)
            VALUES {values}
            """)
            print("Sample FAQs & policies inserted successfully")
        except Exception as e:
            print(f"Insert error: {e}")

def create_index():
    project.query("CREATE INDEX ON company_kb")
    print("Index created")

def semantic_search(query, department=None):
    query = query.replace("'", "''")
    base_query = f"""
    SELECT chunk_content, metadata
    FROM company_kb
    WHERE content = '{query}'
    """
    print("Executing semantic search query:", base_query)
    try:
        results = project.query(base_query).fetch()
        processed_results = []
        for _, row in results.iterrows():
            try:
                metadata = json.loads(row['metadata'])
            except:
                metadata = {}
            processed_results.append({
                'content': row['chunk_content'],
                'department': metadata.get('department', ''),
                'doc_type': metadata.get('doc_type', '')
            })
        # Filter by department in Python
        if department:
            processed_results = [
                r for r in processed_results
                if r['department'].replace('department: ', '') == department
            ]
        print("Processed results:", processed_results)
        return processed_results
    except Exception as e:
        print("Semantic search error:", str(e))
        return []

def setup_update_job():
    project.query("""
    CREATE JOB update_company_kb AS (
        INSERT INTO company_kb (content, department, doc_type)
        SELECT content, department, doc_type
        FROM files.new_documents
        WHERE id > COALESCE(LAST, 0)
    )
    EVERY day
    """)
    print("Update job created")


def get_summarized_results(query):
    summaries = []
    if query:
        summary = project.query(f"""
        SELECT summary FROM document_summarizer
        WHERE content = '{query}'
        """).fetch()
        if summary is not None and not summary.empty:
            summaries.append({
                'original': query,
                'summary': summary.iloc[0]['summary']
            })
    return summaries


@app.route('/search', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form['query']
        department = request.form.get('department')
        
        # Basic input validation
        if not query.strip():
            return render_template('search.html', error="Please enter a search query")
            
        results = semantic_search(query, department)
        return render_template('results.html', 
                             results=results, 
                             query=query,
                             department=department)
    
    return render_template('search.html')


@app.route('/')
def about():
    return render_template('about.html')

@app.route('/browse')
def browse():
    department = request.args.get('department', '')
    results = project.query("SELECT * FROM company_kb").fetch()
    results = results.to_dict(orient='records')
    processed = []
    for row in results:
        content = row.get('chunk_content', '')
        metadata = json.loads(row.get('metadata', '{}'))
        dept = metadata.get('department', '')
        # Clean up department name if needed
        dept = dept.replace('department: ', '')
        processed.append({
            'content': content,
            'department': dept,
            'doc_type': metadata.get('doc_type', '')
        })
    # Filter by department if specified
    if department:
        processed = [r for r in processed if r['department'] == department]
    return render_template('browse.html', results=processed, department=department)

@app.route('/add', methods=['GET', 'POST'])
def add_document():
    print("Connected to MindsDB project:", project.name)
    print("Knowledge base:", kb.name if kb else "None")

    if request.method == 'POST':
        content = request.form['content']
        department = request.form['department']
        doc_type = request.form['doc_type']
        sql = f"""
        INSERT INTO company_kb (content, department, doc_type)
        VALUES ('{content}', '{department}', '{doc_type}')
        """
        print("Executing SQL:", sql)
        try:
            project.query(sql)
            print("Insert query executed")
        except Exception as e:
            print("Insert error:", repr(e))
        return redirect(url_for('browse'))
    return render_template('add.html')

@app.route('/summarize', methods=['GET', 'POST'])
def summarize():
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            summaries = get_summarized_results(query)
            return render_template('summarize.html', summaries=summaries, query=query)
    # GET: Show the form
    return render_template('summarize.html', summaries=None, query=None)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'chat_history' not in session:
        session['chat_history'] = []

    if request.method == 'POST':
        user_input = request.form.get('user_input')
        if user_input:
            # Add user message
            session['chat_history'].append({'sender': 'user', 'text': user_input})

            # Use semantic search to find relevant docs
            results = semantic_search(user_input)
            if results:
                # Summarize top result as bot response
                top_content = results[0]['content']
                summary = get_summarized_results(top_content)
                if summary:
                    bot_response = summary[0]['summary']
                else:
                    bot_response = "Sorry, I couldn't find a summary."
            else:
                bot_response = "Sorry, I couldn't find any relevant information."

            # Add bot response
            session['chat_history'].append({'sender': 'bot', 'text': bot_response})

    return render_template('chat.html', chat_history=session.get('chat_history', []))
if __name__ == '__main__':
    create_knowledge_base()
    setup_ai_tables()  # <-- Added to ensure Ollama models are ready
    insert_sample_data()
    create_index()
    setup_update_job()
    app.run(host='0.0.0.0', port=5000, debug=True)

