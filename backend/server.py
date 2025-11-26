from fastapi import FastAPI, File, UploadFile  # Bring in FastAPI tools to build the web app and handle file uploads
from fastapi.middleware.cors import CORSMiddleware  # Import the CORS tool to allow web pages from different sites to talk to this server
import shutil, os  # Get tools for copying files and working with the computer's file system
from PyPDF2 import PdfReader  # Import a tool to read and extract text from PDF files
import re  # Bring in regular expressions to help clean up text
from collections import Counter  # Import a counter to keep track of how many times words appear

# === FastAPI setup ===  # This section sets up the main FastAPI application
app = FastAPI()  # Create the main FastAPI app object
UPLOAD_FOLDER = "uploads"  # Set the name of the folder where uploaded files will be stored
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Make sure the uploads folder exists, and don't complain if it's already there

# Enable CORS  # Allow other websites to make requests to this server
app.add_middleware(  # Add a special layer to the app
    CORSMiddleware,  # Use the CORS middleware
    allow_origins=["*"],  # Let any website connect (not safe for real use)
    allow_credentials=True,  # Allow sending login info if needed
    allow_methods=["*"],  # Allow all types of web requests
    allow_headers=["*"],  # Allow any headers in requests
)

# === Text extraction function ===  # This function pulls text out of PDF files
def extract_text(file_path: str) -> str:  # Define a function that takes a file path and gives back the text inside
    ext = file_path.split('.')[-1].lower()  # Get the file type (like 'pdf') and make it lowercase
    if ext != "pdf":  # If it's not a PDF file
        raise ValueError(f"Unsupported file type: {ext}. Only PDF files are supported.")  # Stop and say we only handle PDFs
    reader = PdfReader(file_path)  # Open the PDF with the reader tool
    text = "\n".join(page.extract_text() or "" for page in reader.pages)  # Grab text from each page and combine them with line breaks
    return text  # Give back the full text

# === Word counting function ===  # This function counts words that repeat in the text
def count_repeated_words(text: str) -> dict:  # Define a function that takes text and returns a list of repeated words
    # Clean text: lowercase, remove punctuation  # Make the text clean by removing extras and making it all lowercase
    cleaned = re.sub(r'[^\w\s]', '', text.lower())  # Use regex to strip out punctuation and lowercase everything
    words = cleaned.split()  # Break the text into individual words
    counter = Counter(words)  # Count how many times each word shows up
    repeated = {word: count for word, count in counter.items() if count > 1}  # Keep only words that appear more than once
    return repeated  # Return the list of repeated words with their counts

# === Common repeated words function ===  # This function finds common repeated words between two texts
def count_common_repeated_words(text1: str, text2: str) -> dict:  # Define a function that takes two texts and returns common repeated words
    repeated1 = count_repeated_words(text1)  # Get repeated words from first text
    repeated2 = count_repeated_words(text2)  # Get repeated words from second text
    common = {word: min(repeated1.get(word, 0), repeated2.get(word, 0)) for word in repeated1 if word in repeated2}  # Find common words with min count
    return common  # Return the common repeated words with their min counts

# === FastAPI endpoint ===  # This is the main web address (endpoint) for uploading and processing files
@app.post("/count_common_words")  # Set up a web endpoint that accepts POST requests at "/count_common_words"
async def count_common_words(file1: UploadFile = File(...), file2: UploadFile = File(...)):  # Define an async function that waits for two file uploads
    file_path1 = os.path.join(UPLOAD_FOLDER, file1.filename)  # Create the full path where the first file will be saved
    file_path2 = os.path.join(UPLOAD_FOLDER, file2.filename)  # Create the full path where the second file will be saved
    with open(file_path1, "wb") as buffer:  # Open a file to write the first uploaded data
        shutil.copyfileobj(file1.file, buffer)  # Copy the first uploaded file into the new file
    with open(file_path2, "wb") as buffer:  # Open a file to write the second uploaded data
        shutil.copyfileobj(file2.file, buffer)  # Copy the second uploaded file into the new file

    try:  # Try to do the following steps
        text1 = extract_text(file_path1)  # Pull out the text from the first PDF
        text2 = extract_text(file_path2)  # Pull out the text from the second PDF
        common_repeated_words = count_common_repeated_words(text1, text2)  # Count the common repeating words
    except Exception as e:  # If something goes wrong
        common_repeated_words = f"Error: {str(e)}"  # Set the result to an error message

    # Remove temp files  # Clean up by deleting the uploaded files since we don't need them anymore
    os.remove(file_path1)  # Delete the first temporary file
    os.remove(file_path2)  # Delete the second temporary file
    return {"filename1": file1.filename, "filename2": file2.filename, "common_repeated_words": common_repeated_words}  # Send back the file names and the list of common repeated words
