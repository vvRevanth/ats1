import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import json
import pandas as pd

# Choose either Approach 1 or 2 for API key handling:

# Approach 1: Using Environment Variables (Recommended)
#   - Create a .env file in your project's root directory with the line:
#     API_KEY=YOUR_GOOGLE_API_KEY (replace with your actual API key)
#   - Install python-dotenv: pip install python-dotenv

import os
from dotenv import load_dotenv

def configure_gemini_api():
    # Load environment variables from the .env file (if it exists)
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    if API_KEY is None:
        # If API key not found in environment, prompt user for input
        st.error("API Key not found. Please enter your Google API Key:")
        API_KEY = st.text_input("Enter your Google API Key", type="password")
        if not API_KEY:
            st.stop("API Key is required. Please enter it to proceed.")
    genai.configure(api_key=API_KEY)

# Approach 2: Hardcoding the API Key (Not Recommended)
#   - Replace 'YOUR_GOOGLE_API_KEY' with your actual API key (**not** recommended)
# API_KEY = "YOUR_GOOGLE_API_KEY"  # Not recommended!

# Function to get response from Gemini AI
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

# Function to extract text from uploaded PDF file
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Load job postings data
@st.cache_data
def load_job_postings():
    job_postings = pd.read_csv('jobp.csv')
    return job_postings

# Streamlit app
st.title("Resume Matcher ATS")

job_postings = load_job_postings()
if 'title' not in job_postings.columns:
    st.error("Job postings data does not contain the 'title' column.")
    st.stop()

# Filter job titles
# search_query = st.multiselect("Search Job Titles", job_postings['title'].unique())
selected_job_titles = st.sidebar.multiselect("Selected Job Titles", job_postings['title'].unique())
if not selected_job_titles:
    st.info("Please select at least one job title.")
    st.stop()

# Show job description for the first selected job title
selected_job_title = selected_job_titles[0]
jd = job_postings[job_postings['title'] == selected_job_title]['description'].values[0]

uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")
submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        input_prompt = f"""
        Hey Act Like a skilled or very experienced ATS (Application Tracking System)
        with a deep understanding of the tech field, software engineering, data science, data analyst
        and big data engineering. Your task is to evaluate the resume based on the given job description.
        You must consider the job market is very competitive and you should provide the 
        best assistance for improving the resumes. Assign the percentage Matching based 
        on JD and the missing keywords with high accuracy.
        resume:{text}
        description:{jd}
        
        I want the response in one single string having the structure
        {{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
        """
        configure_gemini_api()  # Call the configure function here
        response = get_gemini_response(input_prompt)
        st.subheader("Response:")
        parsed_response = json.loads(response)
        for key, value in parsed_response.items():
            
