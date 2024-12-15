import streamlit as st
import uuid
import sys
import kendra_chat_llama_2 as llama2
from dotenv import load_dotenv
import os
import logging
import boto3
from botocore.exceptions import ClientError

load_dotenv()

# Load environment variables from .env file

USER_ICON = "images/user-icon.png"
AI_ICON = "images/ai-icon.png"
MAX_HISTORY_LENGTH = os.environ.get("MAX_HISTORY_LENGTH", 10)
PROVIDER_MAP = {"llama2": "Llama 2"}
KENDRA_INDEX_ID = os.environ.get("KENDRA_INDEX_ID")
KENDRA_DATA_SOURCE_ID = os.environ.get("KENDRA_DATA_SOURCE_ID")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
AWS_REGION = os.environ.get("AWS_REGION")


# function to upload a file to an S3 bucket


def upload_file_to_s3(file_name, bucket, object_name=None):
    """
    Upload a file to an S3 bucket.

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client("s3", AWS_REGION)
    try:
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def start_kendra_data_source_sync_job(data_source_id, index_id):
    """
    Start a data source sync job in Amazon Kendra.

    :param data_source_id: The identifier of the data source connector to synchronize.
    :param index_id: The identifier of the index used with the data source connector.
    :return: Execution ID of the sync job if successful, else None
    """

    kendra_client = boto3.client("kendra",AWS_REGION)

    try:
        response = kendra_client.start_data_source_sync_job(
            Id=data_source_id, IndexId=index_id
        )
        return response.get("ExecutionId")
    except ClientError as e:
        logging.error(e)
        return None


# function to read a properties file and create environment variables
def read_properties_file(filename):
    """
    The function reads a properties file and sets the properties as environment variables.

    :param filename: The filename parameter is a string that represents the name of the properties file
    that you want to read
    """
    import os
    import re

    with open(filename, "r") as f:
        for line in f:
            m = re.match(r"^\s*(\w+)\s*=\s*(.*)\s*$", line)
            if m:
                os.environ[m.group(1)] = m.group(2)


# Check if the user ID is already stored in the session state
if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]

# If the user ID is not yet stored in the session state, generate a random UUID
else:
    user_id = str(uuid.uuid4())
    st.session_state["user_id"] = user_id


if "llm_chain" not in st.session_state:
    if len(sys.argv) > 1:
        if sys.argv[1] == "llama2":
            st.session_state["llm_app"] = llama2
            st.session_state["llm_chain"] = llama2.build_chain()

        else:
            raise Exception("Unsupported LLM: ", sys.argv[1])
    else:
        raise Exception("Usage: streamlit run app.py llama2")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "chats" not in st.session_state:
    st.session_state.chats = [{"id": 0, "question": "", "answer": ""}]

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = []

if "input" not in st.session_state:
    st.session_state.input = ""


st.markdown(
    """
        <style>
               .block-container {
                    padding-top: 32px;
                    padding-bottom: 32px;
                    padding-left: 0;
                    padding-right: 0;
                }
                .element-container img {
                    background-color: #000000;
                }

                .main-header {
                    font-size: 24px;
                }
        </style>
        """,
    unsafe_allow_html=True,
)


def write_logo():
    """
    The `write_logo` function displays an image of an AI icon using the `st.image` function from the
    `streamlit` library.
    """
    col1, col2, col3 = st.columns([5, 1, 5])
    with col2:
        st.image(AI_ICON, use_column_width="always")


def write_top_bar():
    """
    The function `write_top_bar()` creates a top bar for an AI app, displaying an AI icon, the name of
    the selected provider, and a button to clear the chat.
    :return: the "clear" button.
    """
    col1, col2, col3 = st.columns([1, 10, 2])
    with col1:
        st.image(AI_ICON, use_column_width="always")
    with col2:
        selected_provider = sys.argv[1]
        if selected_provider in PROVIDER_MAP:
            provider = PROVIDER_MAP[selected_provider]
        else:
            provider = selected_provider.capitalize()
        header = f"An AI App powered by Amazon Kendra and {provider}!"
        st.write(f"<h3 class='main-header'>{header}</h3>", unsafe_allow_html=True)
    with col3:
        clear = st.button("Clear Chat")
    return clear


clear = write_top_bar()

if clear:
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.input = ""
    st.session_state["chat_history"] = []


def handle_input():
    """
    The `handle_input` function takes user input, adds it to the list of questions, runs it through a
    language model chain, stores the answer and relevant source documents, and resets the input field.
    """
    input = st.session_state.input
    question_with_id = {"question": input, "id": len(st.session_state.questions)}
    st.session_state.questions.append(question_with_id)

    chat_history = st.session_state["chat_history"]
    if len(chat_history) == MAX_HISTORY_LENGTH:
        chat_history = chat_history[:-1]

    llm_chain = st.session_state["llm_chain"]
    chain = st.session_state["llm_app"]
    result = chain.run_chain(llm_chain, input, chat_history)
    answer = result["answer"]
    chat_history.append((input, answer))

    document_list = []
    if "source_documents" in result:
        for d in result["source_documents"]:
            if not (d.metadata["source"] in document_list):
                document_list.append((d.metadata["source"]))

    st.session_state.answers.append(
        {
            "answer": result,
            "sources": document_list,
            "id": len(st.session_state.questions),
        }
    )
    st.session_state.input = ""


def write_user_message(md):
    """
    The function `write_user_message` displays a user message with a warning icon.

    :param md: A dictionary containing the message details. The dictionary should have a key "question"
    which contains the text of the user's question
    """
    col1, col2 = st.columns([1, 12])

    with col1:
        st.image(USER_ICON, use_column_width="always")
    with col2:
        st.warning(md["question"])


def render_result(result):
    """
    The `render_result` function takes a `result` as input and renders the answer and sources in
    separate tabs.

    :param result: The `result` parameter is a dictionary that contains the information to be rendered.
    It should have the following structure:
    """
    answer, sources = st.tabs(["Answer", "Sources"])
    with answer:
        render_answer(result["answer"])
    with sources:
        if "source_documents" in result:
            render_sources(result["source_documents"])
        else:
            render_sources([])


def render_answer(answer):
    """
    The `render_answer` function takes an answer as input and displays it in a two-column layout with an
    image in the first column and the answer text in the second column.

    :param answer: The `answer` parameter is a dictionary that contains the information to be rendered.
    It likely has a key called "answer" which holds the actual answer to be displayed
    """
    col1, col2 = st.columns([1, 12])
    with col1:
        st.image(AI_ICON, use_column_width="always")
    with col2:
        st.info(answer["answer"])


def render_sources(sources):
    """
    The function `render_sources` takes a list of sources and displays them in an expandable section.

    :param sources: The `sources` parameter is a list of sources that you want to render. Each source in
    the list can be a string or any other data type that can be converted to a string
    """
    col1, col2 = st.columns([1, 12])
    with col2:
        with st.expander("Sources"):
            for s in sources:
                st.write(s)


# Each answer will have context of the question asked in order to associate the provided feedback with the respective question
def write_chat_message(md, q):
    """
    The function `write_chat_message` renders a chat message with an answer and sources.

    :param md: A dictionary containing the chat message data. It should have two keys: "answer" and
    "sources". The value of the "answer" key should be a string representing the answer to the user's
    question. The value of the "sources" key should be a list of strings representing the sources or
    :param q: The parameter `q` represents the user's question or input in the chat message
    """
    chat = st.container()
    with chat:
        render_answer(md["answer"])
        render_sources(md["sources"])


with st.container():
    for q, a in zip(st.session_state.questions, st.session_state.answers):
        write_user_message(q)
        write_chat_message(a, q)

st.markdown("---")

# Optional file uploader integration
uploaded_file = st.file_uploader(
    "Attach a file (optional)", accept_multiple_files=False
)
if uploaded_file is not None:
    # Save the uploaded file temporarily
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    # Assume bucket, data_source_id, and index_id are provided or determined elsewhere
    bucket = BUCKET_NAME
    data_source_id = KENDRA_DATA_SOURCE_ID
    index_id = KENDRA_INDEX_ID
    # Upload to S3 and trigger Kendra data source sync
    if upload_file_to_s3(uploaded_file.name, bucket):
        st.success("File uploaded to S3 successfully.")
        if start_kendra_data_source_sync_job(data_source_id, index_id):
            st.success("Kendra data source sync job started.")
        else:
            st.error("Failed to start Kendra sync job.")
    else:
        st.error("Failed to upload file to S3.")
st.markdown("---")
input = st.text_input(
    "You are talking to an AI, ask any question.", key="input", on_change=handle_input
)