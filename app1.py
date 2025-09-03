import streamlit as st
import os
import time

# --- Dependency and Model Loading ---

try:
    import pyttsx3
except ImportError:
    st.error("Required libraries are not installed. Please run: pip install pyttsx3 pypiwin32")
    st.stop()

# --- Backend Functions ---

@st.cache_resource(show_spinner=False)
def get_tts_engine_and_voices():
    """
    Initializes the pyttsx3 engine and retrieves available voices.
    """
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        voice_map = {}
        for voice in voices:
            # Simple check to categorize voices
            if "male" in voice.name.lower():
                voice_map["Male Voice"] = voice.id
            elif "female" in voice.name.lower():
                voice_map["Female Voice"] = voice.id
            else:
                voice_map[f"Other Voice ({voice.name})"] = voice.id
        
        # Ensure we have at least one voice
        if not voice_map:
            st.warning("No TTS voices were found on your system. Audio generation will not work.")
            return None, [], {}

        return engine, list(voice_map.keys()), voice_map
    except Exception as e:
        st.error(f"Failed to initialize the Text-to-Speech engine. Error: {e}")
        return None, [], {}

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

def generate_audio_pyttsx3(engine, text, voice_id, output_path):
    """
    Converts text to speech and saves it as an MP3 file using pyttsx3.
    """
    try:
        engine.setProperty('voice', voice_id)
        engine.setProperty('rate', 150)
        
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True
        else:
            st.error("Audio file was not created. This may be due to a system configuration error.")
            return False
    except Exception as e:
        st.error(f"Error generating audio with pyttsx3. Error: {e}")
        return False

# --- Frontend Streamlit App ---

st.title("EchoVerse – An AI-Powered Audiobook Creation Tool")
st.markdown("Transform your written content into natural-sounding audio with a customizable tone.")

engine, voice_names, voice_map = get_tts_engine_and_voices()

if engine is None or not voice_names:
    st.stop()

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
    
    selected_voice_name = st.selectbox(
        "Select a voice:",
        options=voice_names
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
                selected_voice_id = voice_map.get(selected_voice_name)
                if generate_audio_pyttsx3(engine, rewritten_text, selected_voice_id, audio_filename):
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