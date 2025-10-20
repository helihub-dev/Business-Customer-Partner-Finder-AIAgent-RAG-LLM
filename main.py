"""Main CLI interface for AxleWave Discovery."""
import sys
import argparse
import json
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import VECTOR_STORE_DIR
from utils.vector_store import AxleWaveVectorStore
from utils.llm_client import LLMClient
from utils.rag import RAGSystem
from orchestrator import CompanyDiscoveryOrchestrator


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AxleWave Company Discovery - Find customers and partners"
    )
    parser.add_argument(
        '--type',
        choices=['customers', 'partners'],
        required=True,
        help='Type of companies to discover'
    )
    parser.add_argument(
        '--criteria',
        default='',
        help='Additional search criteria'
    )
    parser.add_argument(
        '--output',
        default='results.csv',
        help='Output file path (CSV or JSON)'
    )
    parser.add_argument(
        '--top-n',
        type=int,
        default=10,
        help='Number of companies to return'
    )
    parser.add_argument(
        '--provider',
        choices=['openai', 'anthropic'],
        default='openai',
        help='LLM provider'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize components
        print("🔧 Initializing system...")
        
        # Load vector store
        vector_store = AxleWaveVectorStore(VECTOR_STORE_DIR)
        vector_store.create_collection()
        
        # Initialize LLM
        llm = LLMClient(provider=args.provider)
        
        # Initialize RAG
        rag = RAGSystem(vector_store, llm)
        
        # Initialize orchestrator
        orchestrator = CompanyDiscoveryOrchestrator(rag)
        
        # Run discovery
        query_type = args.type.rstrip('s')  # customers -> customer
        results = orchestrator.discover(
            query_type=query_type,
            additional_criteria=args.criteria,
            top_n=args.top_n
        )
        
        if not results:
            print("❌ No results found")
            return 1
        
        # Display results
        print("\n" + "="*60)
        print("📊 RESULTS")
        print("="*60)
        print(orchestrator.format_results(results))
        
        # Save results
        output_path = Path(args.output)
        
        if output_path.suffix == '.json':
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
        else:
            # CSV
            df = pd.DataFrame(results)
            # Convert lists to strings
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(
                        lambda x: ', '.join(x) if isinstance(x, list) else x
                    )
            df.to_csv(output_path, index=False)
        
        print(f"\n✅ Results saved to: {output_path}")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
