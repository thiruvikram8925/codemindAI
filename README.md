
# 🧠 CodeMind – AI Codebase Intelligence Assistant

An AI-powered Codebase Intelligence Assistant that helps developers understand software projects using Generative AI and Retrieval-Augmented Generation (RAG).

## 🚀 Features

- Upload complete software projects using ZIP files.
- Automatically extract source code.
- Intelligent code chunking.
- Semantic code search using Sentence Transformers.
- Vector similarity search using FAISS.
- AI-powered code explanations using Groq LLM.
- RAG-based question answering.
- Source file references.
- Interactive Streamlit interface.

## 🛠️ Technologies Used

- Python
- Streamlit
- Retrieval-Augmented Generation (RAG)
- Sentence Transformers
- FAISS
- Groq LLM
- NumPy

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/CodeMind-AI-Codebase-Intelligence.git
```

Navigate to the project:

```bash
cd CodeMind-AI-Codebase-Intelligence
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🔑 API Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Get your API key from https://console.groq.com/keys.

Never upload your `.env` file to GitHub.

## ▶️ Run the Application

```bash
streamlit run app.py
```

Upload a ZIP file containing your source code and start asking questions about your project.

## 🧠 How It Works

1. User uploads a software project.
2. Source code is extracted and divided into chunks.
3. Sentence Transformers converts chunks into embeddings.
4. FAISS stores and retrieves relevant code.
5. Groq LLM generates answers using retrieved code as context.
6. Streamlit displays AI answers and source references.

## 👨‍💻 Author

Thiruvikram N.

B.Tech – Artificial Intelligence and Data Science
