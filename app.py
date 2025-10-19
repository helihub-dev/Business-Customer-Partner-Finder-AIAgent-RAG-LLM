"""Streamlit UI for AxleWave Discovery."""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

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
        ["Demo Mode (Free)", "Perplexity", "OpenAI", "Anthropic"],
        help="Choose your LLM provider. Demo mode uses simulated responses."
    )
    
    # Map display names to provider codes
    provider_map = {
        "Demo Mode (Free)": "demo",
        "Perplexity": "perplexity",
        "OpenAI": "openai",
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
    st.markdown("### 💰 Estimated Cost")
    if selected_provider == "demo":
        st.success("Free - Demo Mode")
    else:
        st.info(f"~${0.10 * top_n:.2f} per search")

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
        with st.spinner("🚀 Initializing AI agents..."):
            # Load vector store
            vector_store = VectorStore()
            
            # Load documents
            from utils.document_loader import load_axlewave_documents
            docs_dir = Path("data/axlewave_docs")
            documents = load_axlewave_documents(docs_dir)
            
            # Add to vector store
            all_chunks = []
            for doc in documents:
                chunks = vector_store.chunk_text(doc['content'])
                all_chunks.extend(chunks)
            vector_store.add_documents(
                documents=all_chunks,
                metadatas=[{"source": "axlewave_docs"} for _ in all_chunks]
            )
            
            # Initialize LLM
            llm = LLMClient(provider=selected_provider)
            st.success(f"Using {provider} for AI generation")
            
            # Initialize RAG
            rag = RAGSystem(vector_store, llm)
            
            # Initialize orchestrator
            orchestrator = CompanyDiscoveryOrchestrator(rag)
        
        # Run discovery
        query_type = "customer" if "Customer" in discovery_type else "partner"
        
        with st.spinner(f"🔍 Discovering {query_type}s..."):
            results = orchestrator.discover(
                query_type=query_type,
                additional_criteria=additional_criteria,
                top_n=top_n
            )
        
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

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "AxleWave Technologies | DealerFlow Cloud™ | Powered by AI"
    "</div>",
    unsafe_allow_html=True
)
