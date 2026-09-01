"""
Simple Streamlit Chatbot powered by a Hugging Face open-source model.

How it works:
1. Streamlit renders the chat UI and keeps chat history in st.session_state.
2. Every time the user sends a message, we call the Hugging Face Inference
   API (via huggingface_hub's InferenceClient) with the full conversation.
3. The model's reply is shown in the chat and saved to history.
"""

import os
import streamlit as st
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 1. Setup
# ---------------------------------------------------------------------------
load_dotenv()  # reads HF_TOKEN from a local .env file if present

st.set_page_config(page_title="HF Chatbot", page_icon="🤖")
st.title("🤖 Chat with Buddy")

# List of open chat models that currently have an active Inference Provider
# (Hugging Face routes requests to partners like Together, Novita, Fireworks,
# Nebius, etc. — not every model on the Hub has one hosting it for free).
# If one of these ever stops working, check which models are live at:
# https://huggingface.co/models?inference_provider=all&pipeline_tag=text-generation
MODEL_OPTIONS = [
    "meta-llama/Llama-3.1-8B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "deepseek-ai/DeepSeek-R1",
    "openai/gpt-oss-120b",
]

# ---------------------------------------------------------------------------
# 2. Sidebar controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")

    hf_token = st.text_input(
        "Hugging Face API Token",
        value=os.getenv("HF_TOKEN", ""),
        type="password",
        help="Get a free token from https://huggingface.co/settings/tokens",
    )

    model_name = st.selectbox("Model", MODEL_OPTIONS, index=0)
    custom_model = st.text_input(
        "...or type any other model ID from huggingface.co/models",
        value="",
        help="Only works if the model has an active Inference Provider. "
        "Check huggingface.co/models?inference_provider=all&pipeline_tag=text-generation",
    )
    if custom_model.strip():
        model_name = custom_model.strip()

    system_prompt = st.text_area(
        "System prompt (sets the bot's personality/behavior)",
        value="You are a helpful, friendly assistant. Keep answers concise.",
        height=100,
    )

    temperature = st.slider("Temperature (creativity)", 0.0, 1.5, 0.7, 0.1)
    max_tokens = st.slider("Max response length (tokens)", 64, 1024, 512, 64)

    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------------------
# 3. Chat history (kept in Streamlit's session state so it survives reruns)
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"assistant", "content": str}

# Render past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# 4. Handle new user input
# ---------------------------------------------------------------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    if not hf_token:
        st.error("⚠️ Please enter your Hugging Face API token in the sidebar first.")
        st.stop()

    # Show and store the user's message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build the full message list (system prompt + history) for the API call
    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages.extend(st.session_state.messages)

    # Call the Hugging Face Inference API
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("▌ thinking...")
        try:
            client = InferenceClient(model=model_name, token=hf_token, provider="auto")

            # Stream the response token-by-token for a nice chat feel
            full_reply = ""
            stream = client.chat_completion(
                messages=api_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream:
                if not chunk.choices:
                    continue  # some providers send a final chunk with no choices (usage stats etc.)
                delta = chunk.choices[0].delta.content or ""
                full_reply += delta
                placeholder.markdown(full_reply + "▌")

            placeholder.markdown(full_reply)

        except Exception as e:
            err_text = str(e)
            if "model_not_supported" in err_text or "not supported by any provider" in err_text:
                full_reply = (
                    f"❌ **`{model_name}`** isn't hosted by any Hugging Face Inference "
                    "Provider right now. Pick a different model from the sidebar, or "
                    "browse currently-live models at "
                    "https://huggingface.co/models?inference_provider=all&pipeline_tag=text-generation"
                )
            else:
                full_reply = f"❌ Error calling Hugging Face API: {e}"
            placeholder.markdown(full_reply)

    # Save assistant reply to history
    st.session_state.messages.append({"role": "assistant", "content": full_reply})