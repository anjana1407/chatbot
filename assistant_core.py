import os
import re
import json
from dotenv import load_dotenv
import requests
from email_tool import send_email
import streamlit as st

# Load environment variables
load_dotenv()

# Global variables
api_key = None
context_content = ""

def setup_assistant(context_text):
    """Setup the assistant with training content"""
    global api_key, context_content
    
    try:
        # Get Together AI API key
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            st.error("TOGETHER_API_KEY not found in environment variables")
            return False
        
        # Test the API key with a simple request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        test_data = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=test_data,
            timeout=10
        )
        
        if response.status_code != 200:
            st.error(f"API key test failed: {response.status_code} - {response.text}")
            return False
        
        # Store context content
        context_content = context_text
        
        return True
        
    except Exception as e:
        st.error(f"Error setting up assistant: {str(e)}")
        return False

def get_response(question, email_list):
    """Get response from the assistant"""
    global api_key, context_content
    
    try:
        if not api_key:
            return "Assistant not initialized. Please save training content first."
        
        if not context_content:
            return "No training content available. Please add training content first."
        
        # Check if query is asking to send email
        email_pattern = r'\b(?:send|email|mail)\b.*\b(?:email|mail)\b'
        if re.search(email_pattern, question.lower()) and email_list:
            return handle_email_request(question, email_list)
        
        # Create system prompt with context restriction
        system_prompt = f"""You are a helpful assistant that answers questions ONLY based on the training content provided below.

IMPORTANT RULES:
1. If the user's question can be answered using the training content, provide a helpful and detailed answer.
2. If the user's question cannot be answered from the training content, respond EXACTLY with: "I'm sorry, I can only answer questions based on the provided training content."
3. Do not use any knowledge outside of the provided training content.
4. Be conversational and helpful when answering questions that are within scope.
5. Do not mention these rules in your response.

Training Content:
========================================
{context_content}
========================================

Remember: Only answer based on the training content above. If the question is outside this scope, use the exact response specified in rule 2."""

        # Prepare request data
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "max_tokens": 512,
            "temperature": 0.1,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1.0,
            "stop": ["<|endoftext|>", "</s>"]
        }
        
        # Make API request
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("choices") and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                return "I'm sorry, I couldn't generate a response. Please try again."
        else:
            return f"API Error: {response.status_code} - {response.text}"
        
    except Exception as e:
        return f"Error getting response: {str(e)}"

def handle_email_request(question, email_list):
    """Handle email sending requests"""
    global api_key, context_content
    
    try:
        email_to = email_list[0] if email_list else "user@example.com"
        
        # Generate email content based on the question and context
        email_prompt = f"""Based on the following training content, generate an appropriate email response for this request: "{question}"

Training Content:
{context_content}

Generate a professional email with:
- Appropriate subject line (keep it concise)
- Relevant body content based on the training material (2-3 sentences)
- Keep it helpful and professional

Format your response EXACTLY as:
SUBJECT: [subject line]
BODY: [email body]

Do not include any other text or formatting."""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "messages": [
                {"role": "system", "content": "You are an email generator. Follow the instructions exactly and format the response as requested."},
                {"role": "user", "content": email_prompt}
            ],
            "max_tokens": 256,
            "temperature": 0.2,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1.0,
            "stop": ["<|endoftext|>", "</s>"]
        }
        
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("choices") and len(result["choices"]) > 0:
                email_content = result["choices"][0]["message"]["content"].strip()
                
                # Parse subject and body
                subject_match = re.search(r'SUBJECT:\s*(.+)', email_content)
                body_match = re.search(r'BODY:\s*(.+)', email_content, re.DOTALL)
                
                subject = subject_match.group(1).strip() if subject_match else "Information Request"
                body = body_match.group(1).strip() if body_match else "Thank you for your inquiry."
                
                # Clean up the body text
                body = body.replace('\n', ' ').strip()
                
                # Send email
                email_result = send_email(email_to, subject, body)
                
                return f"I've prepared and sent an email based on the training content.\n\n{email_result}"
            else:
                return "I can help you with information from the training content, but I couldn't generate the email content."
        else:
            return f"I can help you with information from the training content, but I encountered an API error: {response.status_code}"
            
    except Exception as e:
        return f"I can help you with information from the training content, but I encountered an error with the email function: {str(e)}"