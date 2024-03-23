from dotenv import load_dotenv

load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input,pdf_cotent,prompt):
    model=genai.GenerativeModel('gemini-pro-vision')
    response=model.generate_content([input,pdf_content[0],prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        ## Convert the PDF to image
        images=pdf2image.convert_from_bytes(uploaded_file.read())

        first_page=images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

## Streamlit App

st.set_page_config(page_title="ATS Resume EXpert")
st.header("ATS Tracking System")
input_text=st.text_area("Job Description: ",key="input")
uploaded_file=st.file_uploader("Upload your resume(PDF)...",type=["pdf"])


if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")


submit1 = st.button("Tell Me About the Resume")

#submit2 = st.button("How Can I Improvise my Skills")

submit3 = st.button("Percentage match")

input_prompt1 = """
 You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description. 
  Please share your professional evaluation on whether the candidate's profile aligns with the role. 
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content=input_pdf_setup(uploaded_file)
        response=get_gemini_response(input_prompt1,pdf_content,input_text)
        st.subheader("The Repsonse is")
        st.write(response)
    else:
        st.write("Please uplaod the resume")

elif submit3:
    if uploaded_file is not None:
        pdf_content=input_pdf_setup(uploaded_file)
        response=get_gemini_response(input_prompt3,pdf_content,input_text)
        st.subheader("The Repsonse is")
        st.write(response)
    else:
        st.write("Please uplaod the resume")



   










'''import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import json
import pandas as pd

# Define your Google API Key
API_KEY = "AIzaSyD2oLQHkz9sYQvKZN6VaZ7ZI2t2N79wefQ"

# Function to configure Gemini AI model with the provided API key
def configure_gemini_api(api_key):
    genai.configure(api_key=api_key)

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

# Sample Job Postings Data
job_postings = pd.DataFrame({
    "job_id": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
    "company_id": [201, 202, 203, 204, 205, 201, 202, 203, 204, 205],
    "title": ["Software Engineer", "Data Scientist", "Data Analyst", "Marketing Manager", "Sales Representative", 
              "Software Engineer", "Data Scientist", "Data Analyst", "Marketing Manager", "Sales Representative"],
    "description": [
        "Develop and maintain software applications...",
        "Analyze large datasets to extract insights...",
        "Clean and prepare data for analysis...",
        "Develop and execute marketing campaigns...",
        "Build relationships with potential customers...",
        "Develop and maintain software applications...",
        "Analyze large datasets to extract insights...",
        "Clean and prepare data for analysis...",
        "Develop and execute marketing campaigns...",
        "Build relationships with potential customers..."
    ],
    "max_salary": [120000, 150000, 100000, 80000, 75000, 120000, 150000, 100000, 80000, 75000],
    "med_salary": [100000, 120000, 80000, 65000, 60000, 100000, 120000, 80000, 65000, 60000],
    "min_salary": [80000, 100000, 60000, 50000, 45000, 80000, 100000, 60000, 50000, 45000],
    "pay_period": ["Yearly", "Yearly", "Yearly", "Yearly", "Yearly", "Yearly", "Yearly", "Yearly", "Yearly", "Yearly"],
    "formatted_work_type": ["Full-time", "Full-time", "Full-time", "Full-time", "Full-time", "Full-time", "Full-time", "Full-time", "Full-time", "Full-time"],
    "location": ["San Francisco, CA", "New York, NY", "Seattle, WA", "Los Angeles, CA", "Chicago, IL", 
                 "San Francisco, CA", "New York, NY", "Seattle, WA", "Los Angeles, CA", "Chicago, IL"],
    "applies": [25, 18, 12, 30, 42, 25, 18, 12, 30, 42],
    # Add remaining columns with sample data or leave as placeholder for
})

# Filter job titles
#wsearch_query = st.multiselect("Search Job Titles", job_postings['title'].unique())
selected_job_titles = st.multiselect("Selected Job Titles", job_postings['title'].unique())
if not selected_job_titles:
    st.info("Please select at least one job title.")
    st.stop()

description_source = st.radio("Select Job Description Source:", ("From CSV File", "Enter Manually"))
selected_job_title = None
jd = None

if description_source == "From CSV File":
    selected_job_title = selected_job_titles[0]
    jd = job_postings[job_postings['title'] == selected_job_title]['description'].values[0]
elif description_source == "Enter Manually":
    jd = st.text_area("Enter Job Description:")

# Show job description for the first selected job title
#selected_job_title = selected_job_titles[0]
#jd = job_postings[job_postings['title'] == selected_job_title]['description'].values[0]

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
        configure_gemini_api(API_KEY)
        response = get_gemini_response(input_prompt)
        st.subheader("Response:")
        parsed_response = json.loads(response)
        for key, value in parsed_response.items():
            st.write(f"**{key}:** {value}")

# Streamlit app
st.set_page_config(layout="wide")
st.title("CV checking")

# Main Banner
st.video("video.mp4")
st.write("""
    # Unlock more interview opportunities by optimizing your resume with Career Nest
    ## Find your dream Career
    """)

# Our Classes section
st.write("""
    ## Our Goals
    A job recommendation website streamlines job search by offering personalized, relevant job opportunities.
    It uses algorithms to match job seekers with employment options based on their qualifications, preferences, and career objectives.
    The website aims to deliver accurate job listings, ensure diversity across industries, and enhance user engagement through intuitive navigation and interactive features.
    It saves time and effort for job seekers, maximizing the likelihood of finding suitable employment options. It also prioritizes long-term career development by providing resources and networking opportunities. Monetization strategies like job postings and premium memberships sustain the website's operations.
    """)

st.write("""
    ## Our Work
    Career Nest is a platform that uses advanced algorithms and data analytics to transform the job search process. It provides personalized job suggestions that match each user's skills, preferences, and career aspirations.
    The platform empowers job seekers of all backgrounds and experience levels to navigate the job market confidently, offering tools for resume building, interview preparation, networking, and career development.
    Career Nest is committed to accuracy and relevance, continuously refining its recommendation engine to ensure the delivery of the most suitable opportunities
    """)

st.write("""
    ## Our Passion
    Our career guidance platform is dedicated to assisting individuals in discovering their ideal career paths.
    Through a thoughtfully curated selection of images, we illustrate career achievements, personal growth, and networking opportunities. Our commitment to inclusivity ensures equal access to a diverse array of job opportunities spanning various industries.
    Embracing innovation and technology, our platform showcases cutting-edge tools and futuristic landscapes. With a mission to inspire and connect with users on their career journeys, our platform endeavors to empower individuals to pursue fulfilling and rewarding professional paths.
    """)

# Scanner Section
'''
