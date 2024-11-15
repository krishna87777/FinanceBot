import os
import logging
from PyPDF2 import PdfReader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import streamlit as st

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class IntelligentInvestorChatbot:
    def __init__(self, pdf_path: str = "THE-INTELLIGENT-INVESTOR.pdf"):
        self.pdf_path = pdf_path
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.vector_store = None
        self.qa_chain = None
        self._initialize()

    def _initialize(self):
        if not self.api_key:
            st.error("Missing OpenAI API Key")
            return

        try:
            # Check cache first
            if "vector_store" not in st.session_state:
                with st.spinner("Loading financial wisdom..."):
                    text = self._load_pdf()
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=1000,
                        chunk_overlap=200
                    )
                    chunks = text_splitter.split_text(text)

                    embeddings = OpenAIEmbeddings(
                        model="text-embedding-3-small",
                        openai_api_key=self.api_key
                    )

                    st.session_state.vector_store = FAISS.from_texts(chunks, embeddings)

            self.vector_store = st.session_state.vector_store

            # Initialize QA chain
            llm = ChatOpenAI(
                model_name="gpt-3.5-turbo-0125",
                temperature=0.3,
                openai_api_key=self.api_key
            )

            prompt_template = """Answer as Benjamin Graham using this context:
            {context}
            Question: {question}
            Answer:"""

            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
                chain_type_kwargs={"prompt": PromptTemplate.from_template(prompt_template)}
            )

        except Exception as e:
            logger.error(f"Initialization error: {str(e)}")
            st.error("Failed to initialize financial expert")

    def _load_pdf(self):
        text = []
        with open(self.pdf_path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text())
        return "\n".join(text)

    def respond(self, question: str) -> str:
        if not self.qa_chain:
            return "Financial advisor not ready yet..."

        try:
            result = self.qa_chain.invoke({"query": question[:500]})
            return result["result"]
        except Exception as e:
            logger.error(f"Response error: {str(e)}")
            return "I'm having trouble answering that. Please try rephrasing."