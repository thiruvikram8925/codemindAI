
import streamlit as st
import zipfile
import shutil
from pathlib import Path
from pathlib import PurePosixPath
import os

from modules.code_loader import load_code_files
from modules.code_chunker import create_chunks
from modules.embeddings import (
    load_embedding_model,
    generate_embeddings
)
from modules.vector_store import create_faiss_index
from modules.rag_pipeline import answer_question
from modules.project_analyzer import analyze_project

# -----------------------------
# APP CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="CodeMind AI",
    page_icon="🧠",
    layout="wide"
)

PROJECT_DIR = Path("extracted_project")


# -----------------------------
# LOAD EMBEDDING MODEL
# -----------------------------

@st.cache_resource
def get_embedding_model():
    return load_embedding_model()


# -----------------------------
# SAFE ZIP EXTRACTION
# -----------------------------

def extract_zip(uploaded_file):

    if PROJECT_DIR.exists():
        shutil.rmtree(PROJECT_DIR)

    PROJECT_DIR.mkdir(parents=True, exist_ok=True)

    uploaded_file.seek(0)

    extracted_files = 0
    total_size = 0
    max_files = 500
    max_size = 100 * 1024 * 1024

    with zipfile.ZipFile(uploaded_file, "r") as zip_ref:

        for member in zip_ref.infolist():

            if member.is_dir():
                continue

            if member.flag_bits & 0x1:
                continue

            if member.file_size < 0:
                continue

            extracted_files += 1
            total_size += member.file_size

            if extracted_files > max_files:
                raise ValueError("ZIP contains too many files.")

            if total_size > max_size:
                raise ValueError("ZIP is larger than 100 MB uncompressed.")

            relative_path = PurePosixPath(member.filename)

            if relative_path.is_absolute() or ".." in relative_path.parts:
                continue

            target = (PROJECT_DIR / Path(*relative_path.parts)).resolve()

            if PROJECT_DIR.resolve() not in target.parents:
                continue

            target.parent.mkdir(parents=True, exist_ok=True)

            with zip_ref.open(member) as source:
                with target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)

    return extracted_files


# -----------------------------
# BUILD CODEBASE INDEX
# -----------------------------

def build_project_index():

    documents = load_code_files(str(PROJECT_DIR))

    if not documents:
        raise ValueError("No supported source code files found.")

    chunks = create_chunks(documents)

    if not chunks:
        raise ValueError("No code chunks could be generated.")

    model = get_embedding_model()

    texts = [chunk["text"] for chunk in chunks]

    embeddings = generate_embeddings(texts, model)

    index = create_faiss_index(embeddings)

    return documents, chunks, model, index


# -----------------------------
# HEADER
# -----------------------------

st.title("🧠 CodeMind AI")
st.caption(
    "AI-powered Codebase Intelligence Assistant"
)

st.markdown(
    "Upload your software project and ask questions "
    "about its code using AI."
)

st.divider()


# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:

    st.title("📁 Project Upload")

    uploaded_file = st.file_uploader(
        "Upload your project ZIP file",
        type=["zip"]
    )

    build_button = st.button(
        "🚀 Analyze Project",
        use_container_width=True,
        disabled=uploaded_file is None
    )

    st.divider()

    st.subheader("Project Status")

    if st.session_state.get("project_ready", False):

        st.success("Project analyzed successfully!")

        st.write(
            "Files:",
            st.session_state.get("file_count", 0)
        )

        st.write(
            "Code chunks:",
            st.session_state.get("chunk_count", 0)
        )

    else:
        st.info("Upload a ZIP file to begin.")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()


# -----------------------------
# PROCESS UPLOADED PROJECT
# -----------------------------

if build_button and uploaded_file is not None:

    try:

        st.session_state["project_ready"] = False

        with st.spinner("Extracting project files..."):

            extracted_count = extract_zip(uploaded_file)

        st.success(
            f"Extracted {extracted_count} files."
        )

        with st.spinner(
            "Analyzing code and creating vector database..."
        ):

            documents, chunks, model, index = build_project_index()

        st.session_state["documents"] = documents
        st.session_state["chunks"] = chunks
        st.session_state["embedding_model"] = model
        st.session_state["faiss_index"] = index

        st.session_state["file_count"] = len(documents)
        st.session_state["chunk_count"] = len(chunks)
        
        project_analysis = analyze_project(documents)
        st.session_state["project_analysis"] = project_analysis

        st.session_state["project_ready"] = True
        st.session_state["messages"] = []

        st.success("Your project is ready for AI questions!")

        st.rerun()

    except Exception as error:

        st.error(f"Project processing failed: {error}")


# -----------------------------
# PROJECT EXPLORER
# -----------------------------

if st.session_state.get("project_ready", False):

    analysis = st.session_state["project_analysis"]

    st.divider()

    st.subheader("🔍 Project Intelligence")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Files", analysis["total_files"])
    col2.metric("Python Files", analysis["python_files"])
    col3.metric("Functions", analysis["total_functions"])
    col4.metric("Classes", analysis["total_classes"])

    with st.expander("📁 Explore Project Files"):

        for item in analysis["files"]:

            with st.container(border=True):

                st.markdown(f"**{item['file']}**")

                if item["functions"]:
                    st.write("Functions:", ", ".join(item["functions"]))
                else:
                    st.write("Functions: None detected")

                if item["classes"]:
                    st.write("Classes:", ", ".join(item["classes"]))
                else:
                    st.write("Classes: None detected")

                if item["imports"]:
                    st.write("Imports:", ", ".join(item["imports"]))

    with st.expander("🔗 Dependency Analysis"):

        if analysis["dependencies"]:

            for dependency in analysis["dependencies"]:

                st.markdown(
                    f"`{dependency['source']}` → "
                    f"`{dependency['imports']}`"
                )

        else:
            st.info(
                "No local Python dependencies detected."
            )

    if st.button("🧠 Generate Architecture Overview"):

        with st.spinner("Analyzing project architecture..."):

            try:

                result = answer_question(
                    "Explain the overall architecture of this "
                    "software project. Describe its main modules, "
                    "their responsibilities, and how they interact.",
                    st.session_state["embedding_model"],
                    st.session_state["faiss_index"],
                    st.session_state["chunks"]
                )

                st.markdown("### Project Architecture")
                st.write(result["answer"])

                with st.expander("View architecture source files"):

                    for source in result["sources"]:
                        st.write(
                            f"{source['file']} — {source['name']}"
                        )

            except Exception as error:
                st.error(f"Analysis failed: {error}")

# -----------------------------
# MAIN CHAT INTERFACE
# -----------------------------

st.subheader("💬 Ask CodeMind")

if st.session_state.get("project_ready", False):

    st.success("Codebase connected. Ask your questions!")

    # Display previous messages
    for message in st.session_state.get("messages", []):

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if message.get("sources"):

                with st.expander("📂 View source files"):

                    for source in message["sources"]:

                        st.markdown(
                            f"""
                            **File:** `{source['file']}`

                            **Function/Class:** `{source['name']}`

                            **Lines:** {source['lines']}

                            **Similarity:** {source['score']}
                            """
                        )

    # Chat input
    user_query = st.chat_input(
        "Ask anything about your codebase..."
    )

    if user_query:

        st.session_state["messages"].append({
            "role": "user",
            "content": user_query
        })

        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):

            with st.spinner("CodeMind is analyzing your code..."):

                try:

                    result = answer_question(
                        user_query,
                        st.session_state["embedding_model"],
                        st.session_state["faiss_index"],
                        st.session_state["chunks"]
                    )

                    answer = result["answer"]
                    sources = result["sources"]

                    st.markdown(answer)

                    with st.expander("📂 View source files"):

                        for source in sources:

                            st.markdown(
                                f"""
                                **File:** `{source['file']}`

                                **Function/Class:** `{source['name']}`

                                **Lines:** {source['lines']}

                                **Similarity:** {source['score']}
                                """
                            )

                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                except Exception as error:

                    st.error(f"AI response failed: {error}")

else:

    st.info(
        "👈 Upload your project ZIP file from the sidebar "
        "and click Analyze Project to start."
    )

    st.markdown("### ✨ What CodeMind can do")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📁")
        st.write("**Understand Projects**")
        st.caption("Analyze multiple source code files.")

    with col2:
        st.markdown("### 🔍")
        st.write("**Find Code**")
        st.caption("Retrieve relevant functions and classes.")

    with col3:
        st.markdown("### 🤖")
        st.write("**AI Explanations**")
        st.caption("Get answers using your actual codebase.")
