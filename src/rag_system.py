"""
RAG (Retrieval-Augmented Generation) system for the Siegel creation guide.
Uses OpenAI GPT-4, LangChain, and FAISS for document retrieval and question answering.
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ChatMessageHistory
from langchain.schema import Document
from langchain.prompts import PromptTemplate

from .utils import get_data_files, clean_text_for_embedding, chunk_text


class SiegelRAGSystem:
    """RAG system for answering questions about Siegel creation."""
    
    def __init__(self, data_dir: str = "data", vector_store_dir: str = "vector_store"):
        self.data_dir = Path(data_dir)
        self.vector_store_dir = Path(vector_store_dir)
        self.vector_store_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.embeddings = None
        self.vector_store = None
        self.llm = None
        self.qa_chain = None
        self.memory = None
        
        # Files to track changes
        self.index_file = self.vector_store_dir / "faiss_index"
        self.metadata_file = self.vector_store_dir / "metadata.pkl"
        
    def initialize(self) -> bool:
        """Initialize the RAG system."""
        try:
            # Get OpenAI API key from Streamlit secrets or environment
            openai_api_key = None
            try:
                openai_api_key = st.secrets["general"]["OPENAI_API_KEY"]
            except KeyError:
                # Fallback to environment variable
                openai_api_key = os.getenv("OPENAI_API_KEY")
            
            if not openai_api_key:
                st.error("OpenAI API key not found. Please set OPENAI_API_KEY in Streamlit secrets or .env file.")
                return False
            
            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=openai_api_key
            )
            
            # Initialize LLM
            self.llm = ChatOpenAI(
                model_name="gpt-4",
                temperature=0.1,
                openai_api_key=openai_api_key
            )
            
            # Load or create vector store
            if self._vector_store_exists():
                self._load_vector_store()
            else:
                self._create_vector_store()
            
            # Initialize memory - Updated to resolve deprecation warning
            # Using ChatMessageHistory instead of deprecated ConversationBufferWindowMemory
            self.chat_history = ChatMessageHistory()
            self.memory = None  # We'll handle memory manually to avoid deprecation
            
            # Create QA chain
            self._create_qa_chain()
            
            return True
            
        except Exception as e:
            st.error(f"Error initializing RAG system: {str(e)}")
            return False
    
    def _vector_store_exists(self) -> bool:
        """Check if vector store exists."""
        return (
            self.index_file.with_suffix('.faiss').exists() and
            self.index_file.with_suffix('.pkl').exists() and
            self.metadata_file.exists()
        )
    
    def _load_vector_store(self):
        """Load existing vector store."""
        try:
            self.vector_store = FAISS.load_local(
                str(self.index_file),
                self.embeddings
            )
            st.success("✅ Vector store loaded successfully")
        except Exception as e:
            st.warning(f"Error loading vector store: {e}. Creating new one...")
            self._create_vector_store()
    
    def _create_vector_store(self):
        """Create new vector store from data files."""
        with st.spinner("🔄 Creating vector store from data files..."):
            documents = self._load_documents()
            
            if not documents:
                st.error("No documents found to create vector store")
                return
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            
            chunks = text_splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = FAISS.from_documents(
                chunks,
                self.embeddings
            )
            
            # Save vector store
            self.vector_store.save_local(str(self.index_file))
            
            # Save metadata
            metadata = {
                "num_documents": len(documents),
                "num_chunks": len(chunks),
                "created_at": str(Path().cwd())
            }
            
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(metadata, f)
            
            st.success(f"✅ Vector store created with {len(chunks)} chunks from {len(documents)} documents")
    
    def _load_documents(self) -> List[Document]:
        """Load all documents from data directory."""
        documents = []
        
        # Load the main guide
        guide_file = self.data_dir / "information" / "sigil_creation_guide.md"
        if guide_file.exists():
            with open(guide_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean and chunk the content
            clean_content = clean_text_for_embedding(content)
            
            documents.append(Document(
                page_content=clean_content,
                metadata={
                    "source": str(guide_file),
                    "type": "guide",
                    "title": "Siegel Creation Guide"
                }
            ))
        
        # Load component descriptions
        components_dir = self.data_dir / "sigil components"
        if components_dir.exists():
            for component_type_dir in components_dir.iterdir():
                if component_type_dir.is_dir():
                    component_info = f"Component Type: {component_type_dir.name}\n"
                    component_info += f"Available components in {component_type_dir.name}:\n"
                    
                    for component_file in component_type_dir.iterdir():
                        if component_file.is_file():
                            component_info += f"- {component_file.stem}\n"
                    
                    documents.append(Document(
                        page_content=component_info,
                        metadata={
                            "source": str(component_type_dir),
                            "type": "component_info",
                            "component_type": component_type_dir.name
                        }
                    ))
        
        # Load complete sigil examples
        sigils_dir = self.data_dir / "complete_sigils"
        if sigils_dir.exists():
            sigil_examples = "Complete Sigil Examples:\n"
            for sigil_file in sigils_dir.iterdir():
                if sigil_file.suffix.lower() == '.png':
                    city_name = sigil_file.stem.replace('_sigil', '')
                    sigil_examples += f"- {city_name}: Complete sigil available\n"
            
            if sigil_examples.strip() != "Complete Sigil Examples:":
                documents.append(Document(
                    page_content=sigil_examples,
                    metadata={
                        "source": str(sigils_dir),
                        "type": "sigil_examples",
                        "title": "Complete Sigil Examples"
                    }
                ))
        
        return documents
    
    def _create_qa_chain(self):
        """Create the conversational QA chain."""
        # Custom prompt template
        template = """Du bist ein Experte für das Siegel-Erstellungssystem. Beantworte Fragen basierend auf dem bereitgestellten Kontext über die Erstellung von Stadtsiegeln.

Kontext: {context}

Chat-Verlauf: {chat_history}

Frage: {question}

Anweisungen:
- Antworte auf Deutsch
- Verwende nur Informationen aus dem bereitgestellten Kontext
- Sei präzise und hilfreich
- Wenn du die Antwort nicht weißt, sage es ehrlich
- Gib konkrete Schritte und Beispiele, wenn möglich
- Beziehe dich auf die Siegel-Komponenten und deren Verwendung

Antwort:"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "chat_history", "question"]
        )
        
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            ),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True,
            verbose=False
        )
    
    def ask_question(self, question: str) -> Tuple[str, List[Document]]:
        """Ask a question and get an answer with sources."""
        try:
            if not self.qa_chain:
                return "RAG system not initialized. Please check your configuration.", []
            
            # Get response
            response = self.qa_chain({
                "question": question
            })
            
            answer = response.get("answer", "Entschuldigung, ich konnte keine Antwort finden.")
            source_docs = response.get("source_documents", [])
            
            return answer, source_docs
            
        except Exception as e:
            error_msg = f"Error processing question: {str(e)}"
            st.error(error_msg)
            return "Es tut mir leid, es gab einen Fehler bei der Verarbeitung Ihrer Frage.", []
    
    def get_relevant_documents(self, query: str, k: int = 5) -> List[Document]:
        """Get relevant documents for a query."""
        if not self.vector_store:
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return docs
        except Exception as e:
            st.error(f"Error retrieving documents: {e}")
            return []
    
    def clear_memory(self):
        """Clear conversation memory."""
        if self.memory:
            self.memory.clear()
    
    def get_vector_store_info(self) -> Dict[str, Any]:
        """Get information about the vector store."""
        info = {
            "exists": self._vector_store_exists(),
            "num_documents": 0,
            "num_chunks": 0
        }
        
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'rb') as f:
                    metadata = pickle.load(f)
                info.update(metadata)
            except Exception:
                pass
        
        return info
    
    def rebuild_vector_store(self):
        """Force rebuild of vector store."""
        # Remove existing files
        for file in self.vector_store_dir.glob("*"):
            if file.is_file():
                file.unlink()
        
        # Recreate
        self._create_vector_store()
        
        # Update QA chain
        if self.vector_store:
            self._create_qa_chain()
