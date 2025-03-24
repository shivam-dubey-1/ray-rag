import gradio as gr
import requests
import json
import time
import pandas as pd

# Configure API endpoint
API_BASE_URL = "http://:8000"
# Set this to your service endpoint

# Fixed parameters
TOP_K = 3
MAX_TOKENS = 256
TEMPERATURE = 0.7

# Sample queries list
SAMPLE_QUERIES = [
    "smartwatch battery life",
    "noise cancellation headphones",
    "cameras for low light photography",
    "smartphones with best cameras",
    "gaming consoles with best graphics",
    "smart home security cameras",
    "lightweight laptops with long battery life",
    "waterproof portable speakers"
]

def make_api_request(endpoint, query):
    """Make a request to the specified API endpoint"""
    url = f"{API_BASE_URL}/{endpoint}"
    
    # Create payload based on endpoint type
    if endpoint == "retrieve":
        payload = {
            "query": query,
            "top_k": TOP_K
        }
    elif endpoint == "generate":
        payload = {
            "query": query,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS
        }
    else:  # rag endpoint
        payload = {
            "query": query,
            "top_k": TOP_K,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "include_context": True
        }
    
    try:
        response = requests.post(
            url, 
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"API Error: {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {"error": f"Request Error: {str(e)}"}

def query_all_endpoints(query):
    """Query all three endpoints and return results"""
    # Get the start time
    start_time = time.time()
    
    # Make requests to all three endpoints
    retrieve_results = make_api_request("retrieve", query)
    generate_results = make_api_request("generate", query)
    rag_results = make_api_request("rag", query)
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Process retrieve results for table
    retrieve_df = None
    if "error" not in retrieve_results and "results" in retrieve_results:
        df_data = []
        for i, result in enumerate(retrieve_results.get("results", [])):
            df_data.append({
                "Result #": i+1,
                "Source": result.get('source', 'Unknown'),
                "Score": f"{result.get('score', 0):.4f}",
                "Text Preview": result.get('text', '')[:100] + "..."
            })
        retrieve_df = pd.DataFrame(df_data)
    
    # Generate simplified outputs
    retrieve_html = "<h3>Vector DB Results</h3>"
    if "error" in retrieve_results:
        retrieve_html += f"<p>Error: {retrieve_results['error']}</p>"
    else:
        for i, result in enumerate(retrieve_results.get("results", [])):
            source = result.get('source', 'Unknown')
            score = result.get('score', 0)
            text = result.get('text', '')[:150] + "..."
            retrieve_html += f"<div style='margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;'>"
            retrieve_html += f"<strong>Result {i+1}:</strong> {source} (Score: {score:.4f})<br>"
            retrieve_html += f"<p>{text}</p>"
            retrieve_html += "</div>"
    
    # Generate output
    generate_html = "<h3>LLM Response (No Context)</h3>"
    if "error" in generate_results:
        generate_html += f"<p>Error: {generate_results['error']}</p>"
    else:
        model = generate_results.get('model', 'Unknown')
        answer = generate_results.get('answer', 'No answer provided.')
        generate_html += f"<div style='padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;'>"
        generate_html += f"<strong>Model:</strong> {model}<br><br>"
        generate_html += f"<p>{answer}</p>"
        generate_html += "</div>"
    
    # RAG output
    rag_html = "<h3>RAG-Enhanced Response</h3>"
    if "error" in rag_results:
        rag_html += f"<p>Error: {rag_results['error']}</p>"
    else:
        model = rag_results.get('model', 'Unknown')
        answer = rag_results.get('answer', 'No answer provided.')
        context_count = rag_results.get('context_count', 0)
        
        rag_html += f"<div style='padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;'>"
        rag_html += f"<strong>Model:</strong> {model}<br>"
        rag_html += f"<em>Used {context_count} context documents</em><br><br>"
        rag_html += f"<p>{answer}</p>"
        rag_html += "</div>"
    
    # Create dataframes for the other tabs
    generate_df = None
    if "error" not in generate_results:
        generate_df = pd.DataFrame([{
            "Model": generate_results.get('model', 'Unknown'),
            "Query": query,
            "Answer": generate_results.get('answer', 'No answer provided.')
        }])
    
    rag_df = None
    if "error" not in rag_results:
        rag_df = pd.DataFrame([{
            "Model": rag_results.get('model', 'Unknown'),
            "Query": query,
            "Context Count": rag_results.get('context_count', 0),
            "Answer": rag_results.get('answer', 'No answer provided.')
        }])
    
    # Context data for RAG tab
    context_df = None
    if "error" not in rag_results and "contexts" in rag_results:
        context_data = []
        for i, context in enumerate(rag_results.get("contexts", [])):
            context_data.append({
                "Context #": i+1,
                "Source": context.get('source', 'Unknown'),
                "Score": f"{context.get('score', 0):.4f}",
                "Text": context.get('text', 'No text available')
            })
        context_df = pd.DataFrame(context_data)
    
    status_msg = f"Query completed in {elapsed_time:.2f} seconds"
    
    return (
        gr.HTML(retrieve_html),
        gr.HTML(generate_html),
        gr.HTML(rag_html),
        retrieve_df,
        generate_df,
        rag_df,
        context_df,
        gr.Markdown(status_msg)
    )

def load_sample_query(query):
    """Load a sample query into the input box"""
    return query

# Custom CSS for better styling
custom_css = """
.sample-query-btn {
    font-family: 'Roboto', sans-serif;
    font-weight: 600;
    font-size: 14px;
    background-color: #f0f2f6;
    border: 1px solid #d9e1eb;
    border-radius: 6px;
    padding: 8px 12px;
    margin: 4px;
    transition: background-color 0.3s, transform 0.2s;
}
.sample-query-btn:hover {
    background-color: #e0e4ea;
    transform: translateY(-2px);
}
.results-container {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 15px;
    margin-top: 10px;
    background-color: #f9f9f9;
}
.section-header {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 5px;
}
"""

# Create the Gradio interface
with gr.Blocks(title="RAG API Comparison", theme=gr.themes.Soft(), css=custom_css) as demo:
    gr.Markdown("# RAG API Comparison Tool")
    gr.Markdown("Compare Vector DB retrieval, direct LLM generation, and RAG-enhanced responses side by side.")
    
    with gr.Row():
        with gr.Column():
            query_input = gr.Textbox(
                label="Enter your query",
                placeholder="Type a query to compare across all three endpoints...",
                lines=2
            )
            
            submit_btn = gr.Button("Submit Query", variant="primary")
            status = gr.Markdown("Ready to query")
    
    gr.Markdown("### Sample Queries")
    with gr.Row():
        sample_buttons = [gr.Button(query, elem_classes=["sample-query-btn"]) for query in SAMPLE_QUERIES[:4]]
    
    with gr.Row():
        sample_buttons_row2 = [gr.Button(query, elem_classes=["sample-query-btn"]) for query in SAMPLE_QUERIES[4:]]
    
    with gr.Tabs():
        with gr.TabItem("Side-by-Side Comparison"):
            with gr.Row():
                retrieve_html = gr.HTML("<h3>Vector DB Results</h3><p>Submit a query to see results...</p>")
                generate_html = gr.HTML("<h3>LLM Response (No Context)</h3><p>Submit a query to see results...</p>")
                rag_html = gr.HTML("<h3>RAG-Enhanced Response</h3><p>Submit a query to see results...</p>")
        
        with gr.TabItem("Vector DB Results"):
            retrieve_table = gr.DataFrame(
                headers=["Result #", "Source", "Score", "Text Preview"],
                label="Vector DB Results"
            )
            
        with gr.TabItem("LLM Response"):
            generate_table = gr.DataFrame(
                headers=["Model", "Query", "Answer"],
                label="LLM Response"
            )
            
        with gr.TabItem("RAG Response"):
            rag_table = gr.DataFrame(
                headers=["Model", "Query", "Context Count", "Answer"],
                label="RAG Enhanced Response"
            )
            
        with gr.TabItem("RAG Contexts"):
            context_table = gr.DataFrame(
                headers=["Context #", "Source", "Score", "Text"],
                label="RAG Contexts Used"
            )
    
    # Set up button click events
    submit_btn.click(
        query_all_endpoints,
        inputs=[query_input],
        outputs=[
            retrieve_html,
            generate_html,
            rag_html,
            retrieve_table,
            generate_table,
            rag_table,
            context_table,
            status
        ]
    )
    
    # Set up sample query buttons
    for btn in sample_buttons + sample_buttons_row2:
        btn.click(
            load_sample_query,
            inputs=[btn],
            outputs=[query_input]
        )

# Launch the app
if __name__ == "__main__":
    demo.launch(share=True)  # Bind to all interfaces for Cloud9
