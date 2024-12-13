## tools
import os, sys
from typing import Optional
from langchain_core.tools import tool
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from fpdf import FPDF
from src.constants import *
from src.agents.sql_agent import SqlAgent


sql_agent_getter = SqlAgent()
sql_agent = sql_agent_getter.get_sql_agent()

def format_as_points(text):
    """
    Converts a text into numbered points by splitting at each condition or clause.

    Args:
        text (str): The input text containing terms and conditions.

    Returns:
        str: A string formatted as numbered points.
    """
    # Split the text into clauses based on commas, semicolons, or periods.
    clauses = [clause.strip() for clause in text.replace('\n', '').split(',') if clause.strip()]

    # Format each clause as a numbered point.
    points = "\n".join(f"{i+1}. {clause}" for i, clause in enumerate(clauses))

    return points        
        
@tool
def sql_agent_tool(input):
    """Use this tool to interact with the SQLite database to retrieve tenant and lease data.
    This tool could be used to do all the database related activities including CRUD. 

    """
    return sql_agent.invoke({"input": input})


@tool
def generate_lease_agreement_tool(tenant_name: str, 
    apartment_number: str, 
    tenant_email: str, 
    tenant_phone: str, 
    owner_name: str, 
    owner_email: str, 
    owner_contact: str, 
    property_name: str, 
    city: str, 
    zip_code: str, 
    lease_start: str, 
    lease_end: str, 
    rent_amount: str,
    lease_terms_conditions:str,
    renewal_terms_conditions:str
    ) -> str:
    """Generates a professional lease agreement based on tenant and lease data."""
    try:
        

        agreement = f"""
        LEASE AGREEMENT
        Tenant Name: {tenant_name}
        Tenant Apartment: {apartment_number}
        Tenant Email: {tenant_email}
        Tenant Contact: {tenant_phone}

        Owner Name: {owner_name}
        Owner Email: {owner_email}
        Owner Contact: {owner_contact}

        Property: {property_name}
        Property City: {city}
        Property Zip Code: {zip_code}

        Basic Terms and Conditions:
        1. Lease Term: Start Date: {lease_start}, End Date: {lease_end}
        2. Rent: ${rent_amount} per month, due on the 5th of each month. Payment methods include cheque or online payment.
        3. Security Deposit: A security deposit of ${rent_amount} is required and refundable subject to property condition.
        4. Maintenance and Repairs: Tenant handles minor repairs; landlord handles major repairs unless caused by tenant negligence.
        5. Utilities: Tenant pays for electricity, water, and gas.
        6. Default: Landlord may terminate the lease and seek damages for breaches or non-payment of rent.
        7. Governing Law: This lease is governed by the laws of the property location.

        Lease Terms and Conditions:
        {lease_terms_conditions}
        
        Renewal Terms:
        {format_as_points(renewal_terms_conditions)}

        Signed By:
        Tenant Signature: _____________________   Date: ___________
        Owner Signature: ______________________   Date: ___________
        """
        
        # Initialize PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Add content to the PDF
        for line in agreement.strip().split("\n"):
            pdf.cell(200, 10, txt=line.strip(), ln=True)

        # Define file path
        file_name = f"Lease_Agreement_{tenant_name.replace(' ', '_')}.pdf"
        file_path = os.path.join("generated_leases", file_name)
        
        # Ensure the directory exists
        os.makedirs("generated_leases", exist_ok=True)

        # Save PDF
        pdf.output(file_path)

        return file_path
    except Exception as e:
        return f"Error generating lease agreement: {str(e)}"
    
    
    


@tool
def send_email_tool(
    tenant_first_name:str,
    recipient_email: str,
    subject: str,
    attachment_path: Optional[str] = None,
    include_payment_link: bool = False,
) -> str:
    
    
    """Send an email with optional attachment and payment link. Find out the recipient/tenant mail id from the database or previous chats.
    The email is sensitive so make sure you send the mail to the correct recipient.

    Args:
        recipient_email (str): Email address of the recipient
        subject (str): Subject line of the email
        email_body (str): Main body of the email
        attachment_path (str, optional): Path to the file to be attached
        include_payment_link (bool, optional): Whether to include a payment link
        payment_link (str, optional): Payment link to be included in the email

    Returns:
        str: Confirmation message about email sending status
    
    
    """
    
    try:
        # Retrieve email credentials from environment variables
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_APP_PASSWORD")

        if not sender_email or not sender_password:
            raise ValueError("Email credentials not found in environment variables")

        # SMTP server configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Compose email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        greeting_body = f"""Hi {tenant_first_name},\nThank you for contacting us. """
        # Prepare email body
        if include_payment_link:
            email_body = greeting_body+"PLease follow below link for payment -   abc.xyz@Pqr"

            msg.attach(MIMEText(email_body, 'plain'))
        else:
            email_body = greeting_body+"Please find the lease agreement below."
            msg.attach(MIMEText(email_body, 'plain'))

            # Attach file if provided
            if attachment_path and os.path.exists(attachment_path):
                try:
                    with open(attachment_path, 'rb') as file:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(file.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition', 
                            f'attachment; filename="{os.path.basename(attachment_path)}"'
                        )
                        msg.attach(part)
                except Exception as attach_error:
                    print(f"Error attaching file: {attach_error}")
                # Continue sending email even if attachment fails

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"Email sent successfully to {recipient_email}")

        return f"Email successfully sent to {recipient_email}"

    except smtplib.SMTPException as smtp_error:
        print(f"SMTP error occurred: {smtp_error}")
        return f"Failed to send email: SMTP error - {smtp_error}"
    except Exception as error:
        print(f"Unexpected error occurred: {error}")
        return f"Failed to send email: Unexpected error - {error}"

    
