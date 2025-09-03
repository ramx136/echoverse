import streamlit as st
import os
import time

# --- Dependency and Model Loading ---

try:
    from gtts import gTTS
except ImportError:
    st.error("Required libraries are not installed. Please run: pip install gtts")
    st.stop()

# --- Backend Functions ---

def rewrite_text_with_tone(text, tone):
    """
    Rewrites the text with a simple, rule-based tone.
    """
    if tone == "Suspenseful":
        return f"Suddenly... {text}... But what if? No one knows for sure."
    elif tone == "Inspiring":
        return f"Imagine a world where... {text}... You can achieve anything you set your mind to!"
    else:  # Neutral
        return text

def generate_audio_gtts(text, lang_code, output_path):
    """
    Converts text to speech and saves it as an MP3 file using gTTS.
    """
    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save(output_path)
        return True
    except Exception as e:
        st.error(f"Error generating audio. Please check your internet connection. Error: {e}")
        return False

# --- Frontend Streamlit App ---

st.title("EchoVerse – An AI-Powered Audiobook Creation Tool")
st.markdown("Transform your written content into natural-sounding audio with a customizable tone.")

# 1. Input Section
st.header("1. Provide Your Text")
input_option = st.radio("Choose input method:", ("Paste Text", "Upload .txt File"))

original_text = ""
if input_option == "Paste Text":
    original_text = st.text_area("Paste your text here:", height=200)
else:
    uploaded_file = st.file_uploader("Choose a .txt file", type="txt")
    if uploaded_file is not None:
        try:
            original_text = uploaded_file.read().decode("utf-8")
            st.text_area("Uploaded Text:", value=original_text, height=200, disabled=True)
        except Exception as e:
            st.error(f"Failed to read the uploaded file. Please ensure it is a valid .txt file. Error: {e}")

# 2. Options and Processing
if original_text:
    st.header("2. Customize and Generate")
    
    tone = st.selectbox(
        "Select the desired tone for your narration:",
        ("Neutral", "Suspenseful", "Inspiring")
    )
    
    accent_map = {"Standard English": "en", "Indian English": "en-in"}
    selected_accent = st.selectbox(
        "Select an accent:",
        options=list(accent_map.keys())
    )

    if st.button("Generate Audiobook"):
        if not original_text.strip():
            st.warning("Please enter or upload some text to proceed.")
        else:
            with st.status("Processing your request...", expanded=True) as status:
                
                final_text = original_text
                
                status.update(label="Rewriting text for tone...", state="running")
                rewritten_text = rewrite_text_with_tone(final_text, tone)
                
                status.update(label="Text processing complete!", state="complete", expanded=False)
                st.success("Successfully processed the text!")
                
                st.subheader("3. Result")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### Original Text")
                    st.info(original_text)
                with col2:
                    st.markdown("### Tone-Adapted Text")
                    st.success(rewritten_text)
                
                status.update(label="Generating audio...", state="running")
                audio_filename = f"narration_{int(time.time())}.mp3"
                lang_code = accent_map[selected_accent]
                if generate_audio_gtts(rewritten_text, lang_code, audio_filename):
                    status.update(label="Audio generation complete!", state="complete")
                    
                    st.subheader("Listen and Download")
                    st.audio(audio_filename, format="audio/mpeg")
                    
                    with open(audio_filename, "rb") as file:
                        st.download_button(
                            label="Download Audio as MP3",
                            data=file,
                            file_name=audio_filename,
                            mime="audio/mpeg"
                        )
                    
                    try:
                        os.remove(audio_filename)
                    except OSError:
                        pass
                else:
                    status.update(label="Audio generation failed.", state="error")