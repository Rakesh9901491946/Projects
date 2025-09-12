import streamlit as st
from app import Medical_chatbot


bot=Medical_chatbot()
def generate_output(text):
    try:
        output=bot.agent_executor.invoke({"input":text})
    except:
        output={"output":"Please ask questions related to medical or health"}
    return output["output"]


st.title("Medical Q&A Chatbot")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

inp = st.chat_input("Ask your medical query here")

if inp:
    st.session_state.chat_history.append({"role": "user", "response": inp})
    output=generate_output(inp)
    if "tool-use" in output:
        output="I am only designed to give answers related to medical and health related queries."
    st.session_state.chat_history.append({"role": "chatbot", "response": output})

for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.write(f"You: {chat['response']}")
    else:
        st.write(f"Bot: {chat['response']}")

