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
        project.query(f"""
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
        """)
        kbs = project.knowledge_bases.list()
        print("Available Knowledge Bases:", [kb.name for kb in kbs])
        kb = project.knowledge_bases.get('feedback_kb')
        print("Knowledge Base created successfully")
    except Exception as e:
        print(f"Knowledge Base error: {e}")

def create_feedback_analysis_model():
    openai_api_key = os.getenv('OPENAI_API_KEY')
    try:
        project.query(f"""
        CREATE MODEL feedback_analysis_model
        PREDICT analysis
        USING
            engine = 'openai',
            model_name = 'gpt-3.5-turbo',  # or 'gpt-4' if available
            openai_api_key = '{openai_api_key}',
           prompt_template = 'Analyze this feedback and describe the sentiment strictly as "positive", "neutral", or "negative". Also provide key points and actionable suggestions. Feedback: {comment}';
        """)
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
    """)

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
        {"content": "ompany vacation per year.", "department": "HR", "doc_type": "policy", "answer": "30 days vacation"},
        {"content": "The office Open?", "department": "Operations", "doc_type": "hours", "answer": "9am to 5pm"}
    ]

    feedback_documents = [
        {"comment": "The vacation policy is great!", "doc_id": 1, "rating": 5, "analysis": "Positive feedback on vacation policy"},
        {"comment": "The office hours are too short.", "doc_id": 2, "rating": 2, "analysis": "Negative feedback on office hours"}
    ]
    
    if kb:
        try:
            # Batch insert using raw SQL
            values = ",".join([
                f"('{doc['content']}', '{doc['department']}', '{doc['doc_type']}', '{doc['answer']}')" 
                for doc in documents
            ])
            project.query(f"""
            INSERT INTO company_kb (content, department, doc_type, answer)
            VALUES {values}
            """)

            feedback_values = ",".join([
                f"('{doc['comment']}', {doc['doc_id']}, {doc['rating']}, '{doc['analysis']}')" 
                for doc in feedback_documents
            ])
            project.query(f"""
            INSERT INTO feedback_kb (comment, doc_id, rating, analysis)
            VALUES {feedback_values}
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
    project.query("""
    CREATE JOB update_company_kb AS (
        INSERT INTO company_kb (content, department, doc_type, answer)
        SELECT content, department, doc_type, answer
        FROM files.new_documents
        WHERE id > COALESCE(LAST, 0)
    )
    EVERY day
    """)
    print("Update job created")

def create_openai_model():
    openai_api_key = os.getenv('OPENAI_API_KEY')
    try:
        project.query(f"""
        CREATE MODEL openai_faq_model
        PREDICT answer
        USING
            engine = 'openai',
            model_name = 'gpt-3.5-turbo',  # or 'gpt-4' if available
            openai_api_key = '{openai_api_key}',
            prompt_template = 'You are a helpful assistant for company FAQs and policies. Use the knowledge base to answer: {question}'

        """)
        print("OpenAI model created successfully")
    except Exception as e:
        print("Error creating OpenAI model:", str(e))

def get_summarized_results(query):
    summaries = []
    if query:
        try:
            summary = project.query(f"""
            SELECT summary FROM document_summarizer
            WHERE content = '{query}'
            """).fetch()
            if summary is not None and not summary.empty:
              summaries.append({
                'original': query,
                'summary': summary.iloc[0]['summary']
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
    if request.method == 'POST':
        content = request.form['content']
        answer = request.form['answer']
        department = request.form['department']
        doc_type = request.form['doc_type']
        metadata = json.dumps({
            'answer': answer,
            'department': department,
            'doc_type': doc_type
        })
        sql = f"""
        INSERT INTO company_kb (content, metadata)
        VALUES ('{content}', '{metadata}')
        """
        project.query(sql)
        flash('Document added successfully!', 'success')
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
    if request.method == 'POST':
        doc_id = request.form.get('doc_id')
        rating = request.form.get('rating')
        comment = request.form.get('comment', '')
        print(f"Received feedback: doc_id={doc_id}, rating={rating}, comment={comment}")

        # Insert feedback into feedback_kb
        submit_feedback(doc_id, rating, comment)

        # Analyze feedback using the agent
        analysis = analyze_feedback(comment)
        print("Feedback analysis:", analysis)
        flash(f'Feedback submitted and analyzed: {analysis}', 'success') 
        return redirect(url_for('browse'))
    return render_template('feedback.html')


def analyze_feedback(comment):
    analysis = None
    try:
        result = project.query(f"""
            SELECT analysis
            FROM feedback_analysis_model
            WHERE comment = '{comment}'
        """).fetch()
        analysis = result.iloc[0]['analysis'] if not result.empty else None
    except Exception as e:
        print("Error analyzing feedback:", str(e))
        analysis = "Could not analyze feedback due to an error."
    return analysis
    print(f"Analysis for feedback '{comment}': {analysis}")

@app.route('/analyze-feedback', methods=['POST'])
def analyze_feedback_route():
    feedback = request.form.get('feedback')
    if feedback:
        analysis = analyze_feedback(feedback)
        return jsonify({'analysis': analysis})
    return jsonify({'error': 'No feedback provided'})

if __name__ == '__main__':
    create_knowledge_base()
    setup_ai_tables()  # <-- Added to ensure Ollama models are ready
    insert_sample_data()
    create_index()
    setup_update_job()
    app.run(host='0.0.0.0', port=5000, debug=True)

