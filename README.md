# My First Hugging Face Chatbot 🤖

A simple chatbot with a Streamlit UI that talks to open-source LLMs hosted on
Hugging Face's Inference API.

## Project structure

```
hf-chatbot/
├── app.py              # the Streamlit app (all the UI + logic)
├── requirements.txt    # Python packages needed
├── .env.example        # template for your secret token
├── .gitignore
└── README.md           # this guide
```

---

## Step-by-step setup

### 1. Get a Hugging Face account + API token
1. Go to https://huggingface.co/join and create a free account (if you don't have one).
2. Once logged in, go to https://huggingface.co/settings/tokens
3. Click **"New token"** → name it anything (e.g. `chatbot`) → role **"Read"** is enough.
4. Copy the token (it starts with `hf_...`). Keep it secret, like a password.

### 2. Install Python
Make sure you have Python 3.9+ installed. Check with:
```bash
python3 --version
```

### 3. Set up the project folder
Put `app.py`, `requirements.txt`, `.env.example`, and `.gitignore` in one folder,
e.g. `hf-chatbot/`, then open a terminal inside that folder.

### 4. Create a virtual environment (recommended)
This keeps this project's packages separate from other Python projects on your machine.
```bash
python3 -m venv venv

# Activate it:
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 5. Install the dependencies
```bash
pip install -r requirements.txt
```

### 6. Add your token
Copy the example env file and paste in your real token:
```bash
cp .env.example .env
```
Then open `.env` in any text editor and replace `hf_your_token_here` with your
actual token from Step 1.

*(You can also skip this and just paste the token directly into the sidebar
when the app is running — the `.env` file just saves you from retyping it
every time.)*

### 7. Run the app
```bash
streamlit run app.py
```
This opens the chatbot in your browser, usually at `http://localhost:8501`.

### 8. Chat!
- Pick a model from the sidebar dropdown (they're all free, open-source instruct models).
- Optionally tweak the system prompt, temperature, and max response length.
- Type a message in the box at the bottom and hit Enter.

---

## How it works (in plain English)

1. **Streamlit** draws the web page: title, sidebar settings, chat bubbles, and
   the input box at the bottom.
2. **Session state** (`st.session_state.messages`) is Streamlit's way of
   "remembering" things between interactions — it stores your whole
   conversation so it doesn't get wiped out every time you send a message
   (Streamlit reruns the whole script on every interaction!).
3. When you send a message, the app:
   - Adds your message to the history.
   - Sends the **entire conversation** (system prompt + all messages so far)
     to the Hugging Face model via `InferenceClient.chat_completion(...)`.
   - Streams the model's reply back token-by-token so it feels like it's
     "typing."
   - Saves the reply into history too, so it's part of the context for your
     next message.

## Common issues

| Problem | Fix |
|---|---|
| `401 Unauthorized` error | Your token is missing/invalid — check the sidebar or `.env` |
| `Model is loading` / timeout | Some models "cold start" on first use — wait ~20s and retry |
| Very slow responses | Try a smaller model (e.g. the 3B Llama option) |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again inside your activated venv |

## Ideas to extend this project
- Add a dropdown to let users pick response "personas" (system prompts).
- Save/export chat history to a file.
- Add file upload so the bot can answer questions about a document (RAG).
- Swap the sidebar model list for **any** model ID from https://huggingface.co/models?pipeline_tag=text-generation
- Deploy it for free on [Streamlit Community Cloud](https://streamlit.io/cloud).
