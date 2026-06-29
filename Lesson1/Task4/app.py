import streamlit as st
from pathlib import Path
from rag.config import get_settings
from rag.engine import RAGEngine, build_index
from rag.vector_store import VectorStore

st.set_page_config(page_title="RAG Bot", layout="wide")

def initialize_session_state():
    if "engine" not in st.session_state:
        st.session_state.engine = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "sources_history" not in st.session_state:
        st.session_state.sources_history = []
    if "session_doc_count" not in st.session_state:
        st.session_state.session_doc_count = 0
    if "session_reset_done" not in st.session_state:
        st.session_state.session_reset_done = False

initialize_session_state()

@st.cache_resource(show_spinner=False)
def initialize_engine(llm_backend: str, embed_backend: str):
    settings = get_settings()
    settings.llm_backend = llm_backend
    settings.embed_backend = embed_backend
    return RAGEngine(settings)

with st.sidebar:
    st.header("RAG Bot")
    
    llm_backend = st.selectbox("LLM Backend", ["groq", "azure", "claude", "ollama"])
    embed_backend = st.selectbox("Embed Backend", ["local", "ollama", "azure"])
    
    top_k_base = st.slider("Base KB chunks", 1, 8, 3)
    top_k_session = st.slider("Session chunks", 0, 5, 2)
    chunk_size = st.slider("Chunk size", 200, 1500, 800, 100)
    
    uploaded_file = st.file_uploader("Upload Document", type=["pdf", "txt", "md"])
    if uploaded_file and st.session_state.engine:
        if st.button("Add to Session"):
            with st.spinner("Ingesting..."):
                st.session_state.engine.ingest_document(uploaded_file.read(), uploaded_file.name)
                st.session_state.session_doc_count += 1
                st.success("File added to session.")
                
    if st.button("Rebuild Base Index"):
        with st.spinner("Rebuilding..."):
            initialize_engine.clear()
            settings = get_settings()
            settings.llm_backend = llm_backend
            settings.embed_backend = embed_backend
            settings.chunk_size = chunk_size
            build_index(settings)
            st.session_state.engine = None
            st.success("Index rebuilt.")
            st.rerun()

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.sources_history = []
        if st.session_state.engine:
            st.session_state.engine.session_store = VectorStore()
            st.session_state.engine._session_doc_count = 0
        st.session_state.session_doc_count = 0
        st.rerun()

if st.session_state.engine is None:
    st.session_state.engine = initialize_engine(llm_backend, embed_backend)

if not st.session_state.session_reset_done:
    st.session_state.engine.session_store = VectorStore()
    st.session_state.engine._session_doc_count = 0
    st.session_state.session_doc_count = 0
    st.session_state.session_reset_done = True

st.title("RAG Bot")

assistant_turn_idx = 0
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if assistant_turn_idx < len(st.session_state.sources_history):
                sources = st.session_state.sources_history[assistant_turn_idx]
                if sources:
                    with st.expander("Sources"):
                        for src in sources:
                            store_type = src.get("store_type", "base")
                            st.write(f"**{src['source']}** ({store_type}) - Score: {src.get('score', 0):.3f}")
                            st.caption(src["text"][:200] + "...")
            assistant_turn_idx += 1

prompt = st.chat_input("Ask RAG Bot...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        engine = st.session_state.engine
        engine.settings.llm_backend = llm_backend
        engine.settings.embed_backend = embed_backend
        engine.settings.chunk_size = chunk_size

        history = st.session_state.messages[:-1]
        token_stream, sources = engine.query(
            query=prompt,
            history=history,
            top_k_base=top_k_base,
            top_k_session=top_k_session,
        )

        for token in token_stream:
            full_response += token
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        
        if sources:
            with st.expander("Sources", expanded=True):
                for src in sources:
                    store_type = src.get("store_type", "base")
                    st.write(f"**{src['source']}** ({store_type}) - Score: {src.get('score', 0):.3f}")
                    st.caption(src["text"][:200] + "...")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.sources_history.append(sources)
    st.rerun()
