import os
import json
from dotenv import load_dotenv
import mindsdb_sdk
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
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
        result = project.query(f"""
        CREATE KNOWLEDGE_BASE company_kb
        USING
            embedding_model = {{
                "provider": "openai",
                "model_name": "text-embedding-3-small",
                "api_key": "{openai_api_key}"
            }},
            metadata_columns = ['department', 'doc_type','answer'],
            content_columns = ['content']
        """)
        result.fetch()  # Ensure the query is executed
        kbs = project.knowledge_bases.list()
        print("Available Knowledge Bases:", [kb.name for kb in kbs])
        kb = project.knowledge_bases.get('company_kb')
        print("Knowledge Base created successfully")
    except Exception as e:
        print(f"Knowledge Base error: {e}")

def create_feedback_knowledge_base():
    global kb
    openai_api_key = os.getenv('OPENAI_API_KEY')
    try:
        project.query(f"""
        CREATE KNOWLEDGE_BASE feedback_kb
        USING
            embedding_model = {{
                "provider": "openai",
                "model_name": "text-embedding-3-small",
                "api_key": "{openai_api_key}"
            }},
            metadata_columns = ['doc_id', 'rating','analysis'],
            content_columns = ['comment']
        """).fetch()  # Ensure the query is executed
        kbs = project.knowledge_bases.list()
        print("Available Knowledge Bases:", [kb.name for kb in kbs])
        kb = project.knowledge_bases.get('feedback_kb')
        print("Knowledge Base created successfully")
    except Exception as e:
        print(f"Knowledge Base error: {e}")

def create_feedback_analysis_model():
    try:
        project.query("""
        CREATE MODEL IF NOT EXISTS feedback_analysis_model
        PREDICT analysis
        USING
            engine = 'openai_engine',
            model_name = 'gpt-3.5-turbo',
            prompt_template = 'Analyze this feedback and describe the sentiment strictly as "positive", "neutral", or "negative". Feedback: {{comment}}'
        """).fetch()
        print("Feedback analysis model created successfully")
    except Exception as e:
        print("Error creating feedback analysis model:", str(e))

def create_feedback_analysis_agent():
    try:
        # Get your model (or create it if not exists)
        model = project.models.get('feedback_analysis_model')
        # Create agent
        agent = project.agents.create(
            'feedback_analysis_agent',
            model,
            params={
                'include_knowledge_bases': ['project.feedback_kb'],
                'prompt_template': 'You are a feedback analysis assistant. Analyze user feedback and provide insights: {comment}'
            }
        )
        print("Feedback analysis agent created successfully")
        return agent
    except Exception as e:
        print("Error creating feedback analysis agent:", str(e))
        return None

def submit_feedback(doc_id, rating, comment, analysis=None):
    metadata = json.dumps({
        'doc_id': doc_id,
        'rating': rating,
        'analysis': analysis or ''
    })
    project.query(f"""
        INSERT INTO feedback_kb (comment, metadata)
        VALUES ('{comment}', '{metadata}')
    """).fetch()  # Ensure the query is executed

def setup_test_questions():
    test_questions = [
        {"doc_id": 1, "question": "How much vacation per year?", "expected_answer": "30 days vacation"},
        {"doc_id": 2, "question": "When are Marketing team meetings?", "expected_answer": "Marketing team meetings every Wednesday at 2pm."},
        {"doc_id": 3, "question": "What is the dress code?", "expected_answer": "Smart casual"},
        {"doc_id": 4, "question": "Where to submit reimbursements?", "expected_answer": "Upload receipts in the portal within 7 days"},
        {"doc_id": 5, "question": "What is the WFH policy?", "expected_answer": "Work from home allowed 2 days/week with approval"}
    ]

    # Drop the table if it exists
    project.query("DROP TABLE IF EXISTS files.test_questions").fetch()

    # Create test table with question column
    project.query("""
    CREATE TABLE IF NOT EXISTS files.test_questions (
        doc_id INT PRIMARY KEY,
        question TEXT,
        expected_answer TEXT
    )
    """).fetch()

    # Insert test questions
    for q in test_questions:
        project.query(f"""
        INSERT INTO files.test_questions (doc_id, question, expected_answer)
        VALUES ({q['doc_id']}, '{q['question'].replace("'", "''")}', '{q['expected_answer'].replace("'", "''")}')
        """).fetch()

    print("Test questions table created and populated")

def evaluate_knowledge_base():
    openai_api_key = os.getenv('OPENAI_API_KEY')
    setup_test_questions()  # Ensure test questions are set up

    test_data = project.query("SELECT * FROM files.test_questions").fetch()
    if test_data.empty:
        print("Test table is empty! Check your insert statements.")
        return []

    try:
        result = project.query(f"""
        EVALUATE KNOWLEDGE_BASE company_kb
        USING
            test_table = files.test_questions,
            version = 'doc_id',
            evaluate=true
                    
        """)

        results= result.fetch()
        print(results)
        return results.to_dict(orient='records') if not results.empty else []

    except Exception as e:
        print(f"Evaluation error: {e}")
        return []

def setup_ai_tables():
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_api_key:
        print("Warning: OPENAI_API_KEY not set for AI tables setup.")
    try:
        project.query(
            f"""
            CREATE ML_ENGINE IF NOT EXISTS openai_engine FROM openai
            USING api_key = '{openai_api_key}';
            """
        ).fetch() 
        project.query(
            """
            CREATE MODEL IF NOT EXISTS document_summarizer
            PREDICT summary
            USING
            engine = 'openai_engine',
            model_name = 'gpt-3.5-turbo',
            prompt_template = 'Summarize this company document: {{content}}';
        """
        ).fetch() 
        print("AI tables created")
    except Exception as e:
        print(f"Error setting up AI tables: {e}")

def drop_existing_objects():
    try:
        project.query("DROP MODEL IF EXISTS document_summarizer").fetch()
        project.query("DROP MODEL IF EXISTS feedback_analysis_model").fetch()
        project.query("DROP ML_ENGINE IF EXISTS openai_engine").fetch()
        project.query("DROP KNOWLEDGE_BASE IF EXISTS company_kb").fetch()
        project.query("DROP KNOWLEDGE_BASE IF EXISTS feedback_kb").fetch()
        print("Dropped existing objects")
    except Exception as e:
        print("Error dropping objects:", str(e))

def insert_sample_data():
    kb = project.knowledge_bases.get('company_kb')
    feedback_kb = project.knowledge_bases.get('feedback_kb')

    documents = [
        {"content": "How much vacation per year?", "department": "HR", "doc_type": "policy", "answer": "30 days vacation"},
        {"content": "The office Open?", "department": "Support", "doc_type": "announcement", "answer": "9am to 5pm"},
        {"content": "When are Marketing team meetings?", "department": "Marketing", "doc_type": "announcement", "answer": "Marketing team meetings every Wednesday at 2pm."},
        {"content": "What is the dress code?", "department": "HR", "doc_type": "policy", "answer": "Smart casual"},
        {"content": "Where to submit reimbursements?", "department": "Finance", "doc_type": "policy", "answer": "Upload receipts in the portal within 7 days"},
        {"content": "What is the WFH policy?", "department": "HR", "doc_type": "policy", "answer": "Work from home allowed 2 days/week with approval"},
        {"content": "When is the compliance test scheduled?", "department": "HR", "doc_type": "test", "answer": "Office hours"}
    ]
    feedback_documents = [
        {"comment": "The vacation policy is great!", "doc_id": 1, "rating": 5, "analysis": "Positive"},
        {"comment": "The office hours are too short.", "doc_id": 2, "rating": 2, "analysis": "Negative"},
        {"comment": "I love the marketing meetings.", "doc_id": 3, "rating": 5, "analysis": "Positive"},
        {"comment": "Dress code is too strict.", "doc_id": 4, "rating": 3, "analysis": "Neutral"},
        {"comment": "Reimbursement process is confusing.", "doc_id": 5, "rating": 2, "analysis": "Negative"},
        {"comment": "WFH policy is flexible and helpful.", "doc_id": 6, "rating": 5, "analysis": "Positive"},
        {"comment": "Compliance test was easy to pass.", "doc_id": 7, "rating": 4, "analysis": "Positive"}
    ]

    # Insert into company_kb
    for doc in documents:
        kb.insert({
            'content': doc['content'],
            'department': doc['department'],
            'doc_type': doc['doc_type'],
            'answer': doc['answer']
        })

    # Insert into feedback_kb
    for doc in feedback_documents:
        feedback_kb.insert({
            'comment': doc['comment'],
            'doc_id': doc['doc_id'],
            'rating': doc['rating'],
            'analysis': doc['analysis']
        })

    print("Sample data inserted successfully")

def create_index():
    project.query("CREATE INDEX ON company_kb")
    print("Index created")

def semantic_search(query, department=None):
    query = query.replace("'", "''")
    base_query = f"""
    SELECT chunk_content, metadata, relevance
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
            relevance = row.get('relevance', 0)
            if relevance > 0.6:  # <-- Only include if relevance > 0.5
                processed_results.append({
                    'content': row['chunk_content'],
                    'department': metadata.get('department', ''),
                    'doc_type': metadata.get('doc_type', ''),
                    'answer': metadata.get('answer', ''),
                    'relevance': relevance
                })
        # Filter by department if specified
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
    try:
        project.query("DROP JOB IF EXISTS update_company_kb").fetch()
        project.query("""
        CREATE JOB update_company_kb AS (
            INSERT INTO company_kb (content, metadata)
            SELECT content,
                   json_object('department', department, 'doc_type', doc_type, 'answer', answer)
            FROM files.new_documents
            WHERE id > COALESCE(LAST, 0)
        )
        EVERY day
        """).fetch()
        print("Update job created")
    except Exception as e:
        print(f"Job error: {e}")

def create_openai_model():
    openai_api_key = os.getenv('OPENAI_API_KEY')
    try:
        project.query(f"""
        CREATE MODEL openai_faq_model
        PREDICT answer
        USING
            engine = 'openai',
            model_name = 'gpt-3.5-turbo', 
            openai_api_key = '{openai_api_key}',
            prompt_template = 'You are a helpful assistant for company FAQs and policies. Use the knowledge base to answer: {question}'

        """).fetch() 
        print("OpenAI model created successfully")
    except Exception as e:
        print("Error creating OpenAI model:", str(e))

def get_summarized_results(query):
    summaries = []
    if query:
        try:
            models = [m.name for m in project.models.list()]
            print("Available models:", models)
            if 'document_summarizer' not in models:
                print("document_summarizer model not found!")
                summaries.append({
                    'original': query,
                    'summary': 'Error: Summarizer model not found.'
                })
                return summaries
            
            summary = project.query(f"""
            SELECT summary FROM document_summarizer
            WHERE content = '{query.replace("'", "''")}'
            """).fetch()
            if summary is not None and not summary.empty:
              summaries.append({
                'original': query,
                'summary': summary.iloc[0]['summary']
              })
            else:
              summaries.append({
                    'original': query,
                    'summary': 'No summary generated.'
                })
        except Exception as e:
            # Log the error for debugging
            print(f"Error occurred during summarization: {e}")
            summaries.append({
                'original': query,
                'summary': 'Error: Unrecognized characters in input.'
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
    print("Fetched results from company_kb:", results)
    processed = []
    for row in results:
        content = row.get('chunk_content', '')
        metadata = json.loads(row.get('metadata', '{}'))
        dept = metadata.get('department', '')
        processed.append({
            'content': content,
            'department': dept,
            'doc_type': metadata.get('doc_type', ''),
            'answer': metadata.get('answer', '')
        })
        print({'content': content, 'department': dept, 'doc_type': metadata.get('doc_type', ''), 'answer': metadata.get('answer', '')})

    # Filter by department if specified
    if department:
        processed = [r for r in processed if r['department'] == department]
    return render_template('browse.html', results=processed, department=department)

@app.route('/add', methods=['GET', 'POST'])
def add_document():
    kb = project.knowledge_bases.get('company_kb')
    if request.method == 'POST':
        content = request.form['content']
        answer = request.form['answer']
        department = request.form['department']
        doc_type = request.form['doc_type']
        kb.insert({
            'content': content,
            'department': department,
            'doc_type': doc_type,
            'answer': answer
        })
        return redirect(url_for('browse'))
    return render_template('add.html')

@app.route('/jobs', methods=['GET'])
def list_jobs():
    jobs = project.jobs.list()
    jobs_info = [{'name': job.name, 'query': job.data.get('query'), 'schedule': job.data.get('schedule_str')} for job in jobs]
    return render_template('jobs.html', jobs=jobs_info)

@app.route('/jobs/create', methods=['POST'])
def create_job():
    name = request.form.get('name')
    query = request.form.get('query')
    repeat_str = request.form.get('repeat_str', None)

    # Basic validation
    if not name or not query:
        flash('Job name and query are required!', 'popup')
        return redirect(url_for('list_jobs'))

    try:
        # Try to create the job (this will fail if the query is invalid)
        job = project.jobs.create(
            name=name,
            query_str=query,
            repeat_str=repeat_str
        )
        flash(f'Job {name} created successfully!', 'popup')
    except Exception as e:
        # Show the error as a popup
        flash(f'Error creating job: {str(e)}', 'popup')

    return redirect(url_for('list_jobs'))


@app.route('/summarize', methods=['GET', 'POST'])
def summarize():
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            summaries = get_summarized_results(query)
            return render_template('summarize.html', summaries=summaries, query=query)
    # GET: Show the form
    return render_template('summarize.html', summaries=None, query=None)

@app.route('/evaluate', methods=['GET', 'POST'])
def evaluate():
    if request.method == 'POST':
        # Optionally, you could allow users to upload a test file or input test questions here
        pass
    # Run evaluation and get results
    results = evaluate_knowledge_base()
    # For rendering, you may want to extract the first row if results is a list of dicts
    # Or pass the whole list if your template can handle it
    summary = results[0] if results else None
    return render_template('evaluate.html', summary=summary, results=results)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'chat_history' not in session:
        session['chat_history'] = []

    if request.method == 'POST':
        user_input = request.form.get('user_input')
        if user_input:
            # Add user message
            session['chat_history'].append({'sender': 'user', 'text': user_input})

            # Handle greetings
            if user_input.lower() in ['hi', 'hello', 'hey']:
                bot_response = "Hello! How can I help you with company FAQs or policies today?"
            else:
                # Use semantic search to find relevant docs
                results = semantic_search(user_input)
                if results and results[0]['relevance'] > 0.7:
                    bot_response = results[0]['answer'] or "Sorry, I couldn't find a summary."
                else:
                    bot_response = "Sorry, I couldn't find any relevant information."

            # Add bot response
            session['chat_history'].append({'sender': 'bot', 'text': bot_response})

    return render_template('chat.html', chat_history=session.get('chat_history', []))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    # Query the knowledge base
    docs_df = project.query("SELECT id, chunk_content FROM company_kb LIMIT 10").fetch()
    # Convert to list of dicts if not empty, else empty list
    docs = docs_df.to_dict(orient='records') if not docs_df.empty else []

    if request.method == 'POST':
        doc_id = request.form.get('doc_id')
        rating = request.form.get('rating')
        comment = request.form.get('comment', '')
        print(f"Received feedback: doc_id={doc_id}, rating={rating}, comment={comment}")

        # Analyze feedback using the agent
        analysis = analyze_feedback(comment)
        print("Feedback analysis:", analysis)

        # Insert feedback into feedback_kb
        submit_feedback(doc_id, rating, comment)

        flash(f'Feedback submitted and analyzed: {analysis}', 'popup')
        return redirect(url_for('feedback'))

    # Always pass 'docs' to the template
    return render_template('feedback.html', documents=docs)

def analyze_feedback(comment):
    try:
        result = project.query(f"""
            SELECT analysis
            FROM feedback_analysis_model
            WHERE comment = '{comment}'
        """).fetch()
        return result.iloc[0]['analysis'] if not result.empty else "No analysis found"
    except Exception as e:
        print("Error analyzing feedback:", str(e))
        return "Could not analyze feedback due to an error."

if __name__ == '__main__':
    drop_existing_objects()
    setup_ai_tables()
    create_knowledge_base()
    create_feedback_knowledge_base()
    create_feedback_analysis_model()
    insert_sample_data()
    create_index()
    setup_update_job()
    app.run(host='0.0.0.0', port=5000, debug=True)

