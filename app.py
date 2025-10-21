"""Streamlit UI for AxleWave Discovery."""
import streamlit as st
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from config import VECTOR_STORE_DIR
from utils.vector_store import VectorStore
from utils.llm_client import LLMClient
from utils.rag import RAGSystem
from orchestrator import CompanyDiscoveryOrchestrator


# Page config
st.set_page_config(
    page_title="AxleWave Discovery",
    page_icon="🚗",
    layout="wide"
)

# Title
st.title("🚗 AxleWave Company Discovery AI")
st.markdown("*Discover potential customers and partners for DealerFlow Cloud™*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    provider = st.selectbox(
        "LLM Provider",
        ["Perplexity", "OpenAI", "Anthropic"],
        help="Choose your LLM provider"
    )
    
    # Map display names to provider codes
    provider_map = {
        "OpenAI": "openai",
        "Perplexity": "perplexity",
        "Anthropic": "anthropic"
    }
    selected_provider = provider_map[provider]
    
    top_n = st.slider(
        "Number of Results",
        min_value=5,
        max_value=20,
        value=10,
        help="How many companies to return"
    )
    
    st.markdown("---")
    st.markdown("### 👩‍💻 Created By")
    st.info("Heli")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    discovery_type = st.radio(
        "What are you looking for?",
        ["Potential Customers", "Potential Partners"],
        horizontal=True
    )

with col2:
    st.metric("Status", "Ready", delta="System Online")

# Additional criteria
additional_criteria = st.text_area(
    "Additional Search Criteria (optional)",
    placeholder="e.g., Focus on California dealerships, or Must have 50+ locations",
    height=100
)

# Search button
if st.button("🔍 Discover Companies"):
    
    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    try:
        # Initialize vector store (cached once)
        @st.cache_resource
        def get_vector_store():
            """Load and cache vector store."""
            vector_store = VectorStore()
            
            # Load documents if empty (first run)
            if not vector_store.is_populated():
                from utils.document_loader import load_axlewave_documents
                docs_dir = os.path.join(os.path.dirname(__file__), "data", "axlewave_docs")
                documents = load_axlewave_documents(docs_dir)
                
                all_chunks = []
                for doc in documents:
                    chunks = vector_store.chunk_text(doc['content'])
                    all_chunks.extend(chunks)
                
                vector_store.add_documents(
                    documents=all_chunks,
                    metadatas=[{"source": "axlewave_docs"} for _ in all_chunks]
                )
                print("Loaded {} documents into vector store".format(len(documents)))
            
            return vector_store
        
        # Initialize RAG system (cached per provider)
        @st.cache_resource
        def get_rag_system(provider_name, _vector_store):
            """Initialize and cache RAG system."""
            llm = LLMClient(provider=provider_name)
            rag = RAGSystem(_vector_store, llm)
            return rag
        
        # Show initialization progress
        init_progress = st.progress(0)
        init_status = st.empty()
        
        init_status.text("Loading ChromaDB vector store...")
        init_progress.progress(0.3)
        vector_store = get_vector_store()
        
        init_status.text("Initializing RAG system...")
        init_progress.progress(0.6)
        rag = get_rag_system(selected_provider, vector_store)
        
        init_status.text("Setting up AI agents...")
        init_progress.progress(0.9)
        orchestrator = CompanyDiscoveryOrchestrator(rag)
        
        init_progress.progress(1.0)
        init_status.empty()
        init_progress.empty()
        
        st.success(f"Using {provider} for AI generation")
        
        # Run discovery with progress tracking
        query_type = "customer" if "Customer" in discovery_type else "partner"
        
        # Create progress containers
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(progress_pct, status_msg):
            """Update progress bar and status."""
            progress_bar.progress(progress_pct)
            status_text.text(status_msg)
        
        with st.spinner(f"🔍 Discovering {query_type}s..."):
            results = orchestrator.discover(
                query_type=query_type,
                additional_criteria=additional_criteria,
                top_n=top_n,
                progress_callback=update_progress
            )
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        if results:
            st.session_state.results = results
            st.success(f"✅ Found {len(results)} companies!")
        else:
            st.error("❌ No results found. Try different criteria.")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.exception(e)

# Display results
if st.session_state.get('results'):
    st.markdown("---")
    st.header("📊 Results")
    
    results = st.session_state.results
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Format for display
    display_df = df[[
        'company_name', 
        'website_url', 
        'locations', 
        'estimated_size', 
        'fit_score',
        'category'
    ]].copy()
    
    display_df.columns = [
        'Company Name',
        'Website',
        'Locations',
        'Size',
        'Fit Score',
        'Category'
    ]
    
    # Convert lists to strings
    display_df['Locations'] = display_df['Locations'].apply(
        lambda x: ', '.join(x) if isinstance(x, list) else x
    )
    
    # Display table
    st.dataframe(display_df)
    
    # Show filtered companies if any
    filtered_companies = results[0].get('_filtered_companies', []) if results else []
    if filtered_companies:
        st.markdown("---")
        st.subheader("🚫 Filtered Out Companies")
        st.info("Removed {} companies that didn't match criteria: '{}'".format(
            len(filtered_companies), 
            additional_criteria
        ))
        
        with st.expander("View {} filtered companies".format(len(filtered_companies))):
            filtered_data = []
            for company in filtered_companies:
                filtered_data.append({
                    "Company": company.get('company_name', 'Unknown'),
                    "Location": ", ".join(company.get('locations', ['N/A'])),
                    "Reason": company.get('match_reason', 'Did not match criteria')
                })
            
            if filtered_data:
                filtered_df = pd.DataFrame(filtered_data)
                st.dataframe(filtered_df, use_container_width=True)
    
    # Detailed view
    st.markdown("### 📋 Detailed Information")
    
    for i, company in enumerate(results, 1):
        with st.expander(f"{i}. {company['company_name']} - Score: {company['fit_score']}/100"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Website:** {company['website_url']}")
                st.markdown(f"**Size:** {company['estimated_size']}")
                st.markdown(f"**Category:** {company['category']}")
            
            with col2:
                st.markdown(f"**Locations:** {', '.join(company.get('locations', ['N/A']))}")
                st.markdown(f"**Fit Score:** {company['fit_score']}/100")
            
            st.markdown("**Rationale:**")
            st.info(company['rationale'])
    
    # Export options
    st.markdown("---")
    st.markdown("### 💾 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV export
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            "axlewave_discovery_results.csv",
            "text/csv",
            
        )
    
    with col2:
        # JSON export
        import json
        json_str = json.dumps(results, indent=2)
        st.download_button(
            "📥 Download JSON",
            json_str,
            "axlewave_discovery_results.json",
            "application/json",
            
        )

# Prompt Tracing Section
st.markdown("---")
st.header("📊 Prompt Performance Tracing")

# Cost calculation explanation (outside expander)
with st.expander("💡 How Costs & Latency Are Calculated"):
    st.markdown("""
    **Latency Calculation:**
    - Measured as: `end_time - start_time` (in seconds)
    - Includes: LLM API call + network time
    - Tracked per prompt execution
    
    **Cost Calculation:**
    - Formula: `tokens_used × $0.000002`
    - Based on: gpt-4o-mini pricing (~$0.002 per 1K tokens)
    - Actual cost may vary by model and provider
    
    **Token Counting:**
    - Input tokens: Prompt + context
    - Output tokens: LLM response
    - Total: Input + Output tokens
    """)

with st.expander("View Prompt Execution Metrics", expanded=False):
    from utils.prompt_tracer import get_tracer
    import json
    
    tracer = get_tracer()
    stats = tracer.get_stats()
    
    if stats["total_traces"] == 0:
        st.info("No prompt traces yet. Run a discovery search to see metrics.")
    else:
        # Overall stats
        st.subheader("📈 Overall Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Prompts", stats["total_traces"])
        with col2:
            st.metric("Success Rate", "{}%".format(stats['success_rate']))
        with col3:
            st.metric("Avg Latency", "{}s".format(stats['avg_latency']))
        with col4:
            st.metric("Total Cost", "${}".format(stats['total_cost']))
        
        # Per-agent breakdown
        st.subheader("🤖 Performance by Agent")
        
        by_prompt = stats.get("by_prompt", {})
        if by_prompt:
            # Group by agent
            agent_groups = {
                "Research Agent": [],
                "Enrichment Agent": [],
                "Scoring Agent": [],
                "Validation Agent": []
            }
            
            for name, pstats in by_prompt.items():
                if "research" in name.lower() or "rag" in name.lower():
                    agent_groups["Research Agent"].append((name, pstats))
                elif "enrich" in name.lower():
                    agent_groups["Enrichment Agent"].append((name, pstats))
                elif "scor" in name.lower():
                    agent_groups["Scoring Agent"].append((name, pstats))
                elif "valid" in name.lower():
                    agent_groups["Validation Agent"].append((name, pstats))
            
            # Display each agent's prompts
            for agent_name, prompts in agent_groups.items():
                if prompts:
                    st.markdown("**{}** ({} prompts)".format(agent_name, len(prompts)))
                    prompt_data = []
                    for name, pstats in prompts:
                        prompt_data.append({
                            "Prompt": name.replace("_", " ").title(),
                            "Count": pstats["count"],
                            "Success %": "{}%".format(pstats['success_rate']),
                            "Avg Latency": "{}s".format(pstats['avg_latency']),
                            "Avg Tokens": int(pstats["avg_tokens"]),
                            "Total Cost": "${:.4f}".format(pstats["count"] * pstats["avg_tokens"] * 0.000002)
                        })
                    
                    prompt_df = pd.DataFrame(prompt_data)
                    st.dataframe(prompt_df, use_container_width=True)
                    st.markdown("")  # Spacing
        
        # Recent traces with pagination
        st.subheader("📜 Recent Executions")
        
        # Pagination controls
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            show_all = st.checkbox("Show all traces", value=False)
        with col2:
            limit = st.number_input("Limit", min_value=10, max_value=1000, value=50, step=10)
        
        recent = tracer.get_recent_traces(limit=1000 if show_all else limit)
        
        if recent:
            trace_data = []
            for trace in reversed(recent):  # Most recent first
                trace_data.append({
                    "Timestamp": trace["timestamp"],
                    "Prompt": trace["prompt_name"].replace("_", " "),
                    "Status": "✅" if trace["success"] else "❌",
                    "Latency (s)": trace.get('latency_seconds', 0),
                    "Tokens": trace.get("tokens_used", 0),
                    "Cost ($)": trace.get("estimated_cost", 0)
                })
            
            trace_df = pd.DataFrame(trace_data)
            st.dataframe(trace_df, use_container_width=True)
            
            # Download options
            st.markdown("### 💾 Export Trace Data")
            col1, col2 = st.columns(2)
            
            with col1:
                csv = trace_df.to_csv(index=False)
                st.download_button(
                    "📥 Download Traces (CSV)",
                    csv,
                    "prompt_traces.csv",
                    "text/csv"
                )
            
            with col2:
                json_str = json.dumps(recent, indent=2)
                st.download_button(
                    "📥 Download Traces (JSON)",
                    json_str,
                    "prompt_traces.json",
                    "application/json"
                )
        else:
            st.info("No traces found")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "AxleWave Technologies | DealerFlow Cloud™ | Powered by AI"
    "</div>",
    unsafe_allow_html=True
)
