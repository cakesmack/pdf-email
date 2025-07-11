import streamlit as st
import PyPDF2
import smtplib
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Configuration (UPDATE THESE) ---
SENDER_EMAIL = "thosecommybastards@gmail.com"
SENDER_PASSWORD = "dyuy elhu cmqy ixkm" # Use app-specific passwords if available (e.g., for Gmail)
RECEIVER_EMAIL = "cmack6189@gmail.com"
SMTP_SERVER = "smtp.gmail.com" # e.g., "smtp.gmail.com" for Gmail
SMTP_PORT = 587 # or 465 for SSL

PDF_FILE_NAME = "Manifesto.pdf" # Make sure this file is in the same directory or provide full path
START_PAGE = 14 # Page numbers are 1-indexed for users, but often 0-indexed in libraries
LINES_PER_EMAIL = 1 # Send one line at a time
DELAY_MINUTES = 3

# --- Email Sending Function ---
def send_email(subject, body, to_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Upgrade connection to secure
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

# --- Streamlit App ---
st.title("PDF Email Sender")
st.write("This script will send lines from a PDF file via email, one line at a time, every 3 minutes, starting from page 14.")

if not os.path.exists(PDF_FILE_NAME):
    st.error(f"Error: The file '{PDF_FILE_NAME}' was not found in the current directory.")
    st.info("Please upload the PDF file to the same directory as this script, or provide its full path.")
else:
    st.success(f"'{PDF_FILE_NAME}' found.")

    st.subheader("Email Configuration (Please Update in Script)")
    st.text(f"Sender: {SENDER_EMAIL}")
    st.text(f"Recipient: {RECEIVER_EMAIL}")

    if st.button("Start Sending Emails"):
        st.info("Starting the email sending process. Please do not close this tab or refresh.")

        try:
            with open(PDF_FILE_NAME, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)

                if START_PAGE > total_pages:
                    st.error(f"Start page ({START_PAGE}) is greater than total pages ({total_pages}). Aborting.")
                else:
                    st.write(f"PDF has {total_pages} pages. Starting from page {START_PAGE}.")
                    current_line_count = 0
                    email_sent_count = 0

                    # Adjust for 0-indexed page access in PyPDF2
                    for page_num in range(START_PAGE - 1, total_pages):
                        page = reader.pages[page_num]
                        text = page.extract_text()
                        if text:
                            lines = text.split('\n')
                            st.write(f"Processing Page {page_num + 1} with {len(lines)} lines...")
                            for line in lines:
                                if line.strip(): # Only send non-empty lines
                                    current_line_count += 1
                                    subject = f"Karl and Friedrich here, thought this might interest you. {page_num + 1}, Line {current_line_count})"
                                    body = line.strip()

                                    st.write(f"Attempting to send email for Page {page_num + 1}, Line {current_line_count}: '{body[:50]}...'")
                                    if send_email(subject, body, RECEIVER_EMAIL):
                                        email_sent_count += 1
                                        st.success(f"Email sent successfully for Page {page_num + 1}, Line {current_line_count}. Total sent: {email_sent_count}")
                                    else:
                                        st.warning(f"Failed to send email for Page {page_num + 1}, Line {current_line_count}. Retrying next line after delay.")

                                    # Introduce the delay
                                    st.write(f"Waiting for {DELAY_MINUTES} minutes before sending next line...")
                                    time.sleep(DELAY_MINUTES * 60)
                                    st.empty() # Clear previous "Waiting" message (optional)
                        else:
                            st.warning(f"Page {page_num + 1} is empty or could not extract text.")

                    st.success(f"Process completed! Sent {email_sent_count} lines in total.")

        except PyPDF2.errors.PdfReadError:
            st.error("Error reading PDF file. It might be corrupted or encrypted.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")