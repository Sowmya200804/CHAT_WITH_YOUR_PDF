
import streamlit as st
from google import genai
from dotenv import load_dotenv
from pypdf import PdfReader
import chromadb
import os

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Nova AI | Chat with your PDF",
    page_icon="📚",
    layout="wide"
)

# ==========================================
# LOAD CSS DIRECTLY IN PYTHON
# ==========================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

/* Main background */
.stApp {
    background:
        radial-gradient(ellipse at top left,
        rgba(121, 85, 237, 0.22), transparent 40%),
        radial-gradient(ellipse at bottom right,
        rgba(0, 200, 220, 0.15), transparent 40%),
        linear-gradient(135deg, #080d1b, #10162b, #101027);
    color: #edf2ff;
    font-family: 'Inter', sans-serif;
}

/* Main content */
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Headings */
h1, h2, h3 {
    font-family: 'Outfit', sans-serif !important;
    color: #f4f0ff !important;
    letter-spacing: -0.5px;
}

/* Main title gradient */
h1 {
    font-size: clamp(2rem, 5vw, 3.3rem) !important;
    font-weight: 800 !important;
    background: linear-gradient(
        90deg, #ffffff, #c4a7ff, #71e7ff
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Paragraphs */
p, label, .stMarkdown {
    color: #cbd5ef;
    line-height: 1.8;
}

/* Dividers */
hr {
    border-color: rgba(167, 180, 255, 0.2) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(
        110deg, #7955ed, #536dfe, #00bcd4
    );
    color: white !important;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 14px;
    padding: 0.7rem 1.4rem;
    font-family: 'Outfit', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    min-height: 46px;
    box-shadow: 0 5px 22px rgba(91,87,240,0.25);
    transition: all 0.25s ease;
}

/* Button hover */
.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(0,195,230,0.3);
    border-color: #75eaff;
}

/* Text input */
.stTextInput input {
    background: rgba(18,27,51,0.9) !important;
    color: white !important;
    border: 1px solid #39476b !important;
    border-radius: 12px !important;
    padding: 12px 15px !important;
    font-family: 'Inter', sans-serif !important;
}

/* Input focus */
.stTextInput input:focus {
    border-color: #9b87ff !important;
    box-shadow: 0 0 0 2px rgba(155,135,255,0.18);
}

/* Input placeholder */
.stTextInput input::placeholder {
    color: #8795b5 !important;
}

/* PDF uploader */
[data-testid="stFileUploader"] {
    background: rgba(20,29,54,0.75);
    border: 1px dashed #8171e8;
    border-radius: 18px;
    padding: 18px;
    transition: all 0.3s ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: #55dff3;
    background: rgba(44,45,86,0.75);
}

/* Expander */
[data-testid="stExpander"] {
    background: rgba(23,32,59,0.7);
    border: 1px solid rgba(151,137,255,0.28);
    border-radius: 15px;
    overflow: hidden;
}

[data-testid="stExpander"] summary {
    color: #d9d4ff !important;
    font-weight: 600;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 14px;
}

/* Spinner */
[data-testid="stSpinner"] p {
    color: #91eaff !important;
}

/* Success and info text */
[data-testid="stAlert"] p {
    color: #e5edff !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #0c1224;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(#7955ed, #00bcd4);
    border-radius: 10px;
}

/* Text selection */
::selection {
    background: #7458dd;
    color: white;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }

    h1 {
        font-size: 2rem !important;
    }

    .stButton > button {
        width: 100%;
    }
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("🔑 GEMINI_API_KEY is missing in your .env file.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# ==========================================
# CHROMADB
# ==========================================

chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(
    name="gemini_rag_collection"
)

# ==========================================
# HEADER
# ==========================================

st.markdown("""
<style>
h1 {
    font-family: "Segoe UI", "Segoe UI Emoji",
                 "Noto Color Emoji", sans-serif !important;
    -webkit-text-fill-color: initial;
}
</style>
""", unsafe_allow_html=True)

st.title("📚 Nova AI — Chat with your PDF")

st.markdown("""
### ✨ Your documents. Your questions. Instant insights.

Transform lengthy PDFs into clear answers with your
personal AI document assistant.

<div style="
    background: linear-gradient(
        110deg,
        rgba(121,85,237,0.18),
        rgba(0,188,212,0.12)
    );
    border: 1px solid rgba(151,137,255,0.3);
    border-radius: 16px;
    padding: 18px;
    margin: 20px 0;
">
    <h3 style="margin:0; color:#cbbcff;">
        🧠 Meet Nova — Your AI Reading Companion
    </h3>
    <p style="margin-bottom:0;">
        📄 Upload &nbsp; → &nbsp;
        ⚡ Process &nbsp; → &nbsp;
        💬 Ask &nbsp; → &nbsp;
        💡 Discover
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ==========================================
# PDF TEXT EXTRACTION
# ==========================================

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text

# ==========================================
# TEXT CHUNKING
# ==========================================

def create_chunks(text, chunk_size=1000):
    chunks = []

    for start in range(0, len(text), chunk_size):
        chunk = text[start:start + chunk_size]

        if chunk.strip():
            chunks.append(chunk)

    return chunks

# ==========================================
# GEMINI EMBEDDING
# ==========================================

def create_embedding(text):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    return response.embeddings[0].values

# ==========================================
# STORE CHUNKS IN CHROMADB
# ==========================================

def store_chunks(chunks):
    global collection

    try:
        chroma_client.delete_collection(
            "gemini_rag_collection"
        )
    except Exception:
        pass

    collection = chroma_client.get_or_create_collection(
        name="gemini_rag_collection"
    )

    embeddings = []

    for chunk in chunks:
        embeddings.append(create_embedding(chunk))

    ids = [f"chunk_{i}" for i in range(len(chunks))]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings
    )

    return len(chunks)

# ==========================================
# GENERATE CREATIVE AI ANSWER
# ==========================================

def generate_answer(question, context):
    prompt = f"""
You are Nova, a friendly and intelligent AI PDF assistant. 📚✨

Answer using ONLY the information in the provided PDF context.

Instructions:
1. Start with a direct answer.
2. Use simple English.
3. Use relevant emojis naturally.
4. Use headings and bullet points when helpful.
5. Explain technical concepts step by step.
6. Use tables for comparisons when appropriate.
7. Give examples only when supported by the context.
8. End with a short takeaway when useful.
9. Never invent facts or use outside information.

If the answer is not in the document, say:
"🔎 I couldn't find this information in your uploaded PDF.
Please try another question related to the document."

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

NOVA'S ANSWER:
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text or "I couldn't generate an answer. Please try again."

# ==========================================
# UPLOAD PDF
# ==========================================

st.subheader("📂 Upload Your Document")

uploaded_file = st.file_uploader(
    "Choose a PDF to begin your AI-powered journey",
    type=["pdf"]
)

# ==========================================
# PROCESS PDF
# ==========================================

if uploaded_file is not None:
    st.success(f"📄 Selected document: {uploaded_file.name}")

    if st.button("⚡ Process My PDF", use_container_width=True):

        with st.spinner("📖 Reading your document..."):
            text = extract_text_from_pdf(uploaded_file)

        if not text.strip():
            st.error(
                "❌ Could not extract text. "
                "This PDF may contain scanned images."
            )

        else:
            chunks = create_chunks(text)

            st.info(f"🧩 Created {len(chunks)} text chunks.")

            try:
                with st.spinner(
                    "🧠 Creating embeddings and learning your document..."
                ):
                    number_of_chunks = store_chunks(chunks)

                st.session_state.pdf_processed = True
                st.session_state.pdf_name = uploaded_file.name

                st.success(
                    f"🎉 PDF processed successfully! "
                    f"{number_of_chunks} chunks are ready."
                )

            except Exception as e:
                st.error(f"⚠️ PDF processing failed: {e}")

# ==========================================
# QUESTION SECTION
# ==========================================

if st.session_state.get("pdf_processed", False):

    st.divider()

    st.subheader("💬 Ask Nova Anything")

    st.caption(
        "Ask questions about your PDF and discover its key insights. ✨"
    )

    question = st.text_input(
        "🔍 What would you like to know?",
        placeholder="e.g. Explain the main concepts in simple words..."
    )

    if st.button("🤖 Generate My Answer", use_container_width=True):

        if not question.strip():
            st.warning("✍️ Please enter a question first.")

        else:
            try:
                with st.spinner("🔎 Searching your document..."):

                    question_embedding = create_embedding(question)

                    results = collection.query(
                        query_embeddings=[question_embedding],
                        n_results=min(3, collection.count())
                    )

                documents = results["documents"][0]

                if not documents:
                    st.warning("No relevant information was found.")
                    st.stop()

                context = "\n\n".join(documents)

                with st.expander("📖 Explore Retrieved Context"):
                    for i, doc in enumerate(documents, start=1):
                        st.markdown(f"**🧩 Chunk {i}**")
                        st.write(doc)
                        st.divider()

                with st.spinner("✨ Nova is preparing your answer..."):
                    answer = generate_answer(question, context)

                st.markdown("---")
                st.subheader("🤖 Nova's Answer")

                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(
                            135deg,
                            rgba(121,85,237,0.16),
                            rgba(0,188,212,0.10)
                        );
                        border: 1px solid rgba(151,137,255,0.35);
                        border-radius: 18px;
                        padding: 24px;
                        margin-top: 12px;
                    ">
                        <div style="
                            color: #8cecff;
                            font-size: 14px;
                            font-weight: 700;
                            margin-bottom: 12px;
                        ">
                            ✨ NOVA AI · DOCUMENT-BASED RESPONSE
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Render the answer as Markdown so headings,
                # lists, tables and emojis display correctly.
                st.markdown(answer)

            except Exception as e:
                st.error(f"⚠️ Something went wrong: {e}")

else:
    st.info(
        "🚀 Upload and process a PDF above to unlock "
        "your personal AI document assistant."
    )

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown("""
<div style="text-align:center; padding:15px;">
    <p style="color:#9baac9;">
        💜 Built with Streamlit + Gemini AI + ChromaDB
    </p>
    <p style="color:#7888a8; font-size:13px;">
        Nova AI — Read smarter. Learn faster. Discover more. ✨
    </p>
</div>
""", unsafe_allow_html=True)