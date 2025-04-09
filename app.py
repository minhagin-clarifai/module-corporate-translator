import streamlit as st
from clarifai.client.model import Model
from PIL import Image, ImageOps
import requests
from io import BytesIO
import sys

# Constants
PAT = ""  # Replace with your actual PAT
MODEL_URL = "https://clarifai.com/meta/Llama-3/models/Llama-3_2-3B-Instruct"
BUSINESS_CAT_URL = "https://img.buzzfeed.com/buzzfeed-static/static/enhanced/terminal01/2011/2/21/11/enhanced-buzz-10470-1298306653-15.jpg"

def footer(st):
  with open('footer.html', 'r') as file:
    footer = file.read()
    st.write(footer, unsafe_allow_html=True)

def load_business_cat():
  """Load, crop, and flip the local business cat image"""
  img = Image.open('business_cat.jpg')
  
  # Crop to middle third (from the sides)
  width, height = img.size
  left = width // 3
  right = 2 * width // 3
  cropped_img = img.crop((left, 0, right, height))
  
  # Flip horizontally to face right
  flipped_img = ImageOps.mirror(cropped_img)
  
  return flipped_img

def main():
  # Set up the page with sidebar
  st.set_page_config(page_title="Corpo-fai", page_icon="💼", layout="wide")
  
  # Load business cat image
  business_cat = load_business_cat()
  
  # Create sidebar with Business Cat
  with st.sidebar:
    st.image(business_cat, use_container_width=True)
    st.markdown("""
    <div style="text-align: center; font-style: italic; margin-top: -10px;">
    "Let's circle back and leverage synergies"<br>- Business Cat
    </div>
    """, unsafe_allow_html=True)
  
  # Main content area
  col1, col2 = st.columns([3, 1])
  
  with col1:
    # Title and description
    st.title("💼 Corpo-fai")
    st.markdown("""
    Ever wondered what your boss *really* means? Or need to sound more "corporate"? 
    This tool translates between normal human speech and corporate jargon.
    """)
    
    # Translation direction toggle
    translation_direction = st.radio(
      "Translation Direction:",
      ["Normal → Corporate", "Corporate → Normal"],
      horizontal=True,
      index=0
    )
    
    # Text input area
    user_input = st.text_area(
      "Enter your text here:",
      placeholder="Type your normal human speech or corporate jargon here...",
      height=150
    )
    
    # Advanced options expander
    with st.expander("Advanced Options"):
      creativity = st.slider("Jargon Intensity", 0.1, 1.0, 0.7, 
                 help="Higher values make translations more corporate/absurd")
    
    # Output container
    output_container = st.container()
    
    # Translate button
    if st.button("Translate", type="primary") and user_input:
      with st.spinner("Consulting the corporate jargon database..."):
        try:
          # Generate the prompt
          prompt = generate_prompt(user_input, translation_direction)
          print("\n=== SENDING PROMPT ===\n", prompt, "\n", file=sys.stderr)
          
          # Initialize the Clarifai model
          model = Model(url=MODEL_URL, pat=PAT)
          
          # For storing the complete response
          complete_response = ""
          
          # Create output elements
          with output_container:
            st.markdown("**Translation Output:**")
            streaming_placeholder = st.empty()
            
            # Stream the response and print to terminal
            response_stream = model.generate_by_bytes(
              prompt.encode('utf-8'),
              input_type="text",
              inference_params={"temperature": creativity}
            )
            
            print("=== STREAMING RESPONSE ===", file=sys.stderr)
            for response in response_stream:
              if response.outputs and response.outputs[0].data.text:
                chunk = response.outputs[0].data.text.raw
                
                if chunk:
                  complete_response += chunk
                  streaming_placeholder.markdown(
                    f'<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 4px solid #4e79a7;">{complete_response}</div>',
                    unsafe_allow_html=True
                  )
          
          print("\n=== COMPLETE RESPONSE ===\n", complete_response, "\n", file=sys.stderr)
          st.success("Translation complete!")
          
        except Exception as e:
          error_msg = f"Translation failed: {str(e)}"
          print("=== ERROR ===", error_msg, file=sys.stderr)
          st.error(error_msg)
          with output_container:
            st.markdown("**Error:**")
            st.error(str(e))
    
    # Add some fun examples
    if not user_input:
      with st.expander("Need inspiration? Try these examples:"):
        st.write("**Normal → Corporate Examples:**")
        st.code('''"This project is late because we didn't have clear requirements"''')
        st.code('''"I don't understand what you're asking for"''')
        
        st.write("**Corporate → Normal Examples:**")
        st.code('''"Let's leverage our core competencies to optimize the synergy moving forward"''')
        st.code('''"We need to ideate a paradigm shift to disrupt the current market space"''')

def generate_prompt(text, direction):
  """Generate the appropriate prompt based on translation direction"""
  if "Normal → Corporate" in direction:
    return f"""You are an expert at translating plain English into persuasive corporate jargon. 
    Transform this message into something that would impress executives at a Fortune 500 company.
    
    Guidelines:
    - Only response with the translation; no need for contextualizing it with "here's your translation" or anyting like that
    - Use natural-sounding business language (not a parody)
    - Incorporate appropriate corporate buzzwords naturally
    - Maintain the core meaning but make it sound more strategic
    - Use professional tone but avoid being overly verbose
    - Match the seriousness of the original message
    
    Input: "{text}"
    
    Corporate Translation:"""
  else:
    return f"""You are a skilled interpreter of corporate speak. 
    Convert this business jargon into clear, straightforward English that a normal person would understand.
    
    Guidelines:
    - Only response with the translation; no need for contextualizing it with "here's your translation" or anyting like that
    - Extract the actual meaning from the corporate language
    - Remove all unnecessary buzzwords
    - If the original is vague, reveal what the speaker is likely trying to say
    - Keep it concise but preserve all important information
    
    Input: "{text}"
    
    Plain English Translation:"""

main()
footer(st)