import nltk
nltk.download('punkt')
from dotenv import load_dotenv
load_dotenv()

import os
from lxml import etree

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv('LANGCHAIN_API_KEY')
os.environ["Gemini_API_key"] = os.getenv('Gemini_API_key')
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')
os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')

from langchain.agents import AgentExecutor
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.google_palm import GooglePalmEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.agents import create_tool_calling_agent


class Medical_chatbot():
    total_info=""

    main_directory_path = 'MedQuAD-master'
    for root, dirs, files in os.walk(main_directory_path):
        for file in files:
            if file.endswith('.xml'):  
                file_path = os.path.join(root, file)
                
                try:
                    tree = etree.parse(file_path)
                    root_element = tree.getroot()
                    topic = root_element.find('.//Focus')
                    if topic is not None:
                        total_info=total_info +" \n " +topic.text+ " \n "
                    
                    for specific_element in root_element.iter("QAPair"):
                        quest = specific_element.find('.//Question')
                        answ= specific_element.find('.//Answer')
                        question_text = quest.text
                        answer_text = answ.text
                        qtype = quest.attrib.get('qtype', 'No qtype found')
                        if topic is not None:
                            total_info=total_info +" (Question Type: "+qtype+") Question: "+question_text+ " Answer: "+answer_text 
                    
                    total_info = total_info+" \n "
                except etree.XMLSyntaxError as e:
                    print(f"Error parsing {file_path}: {e}")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=60)
    documents=text_splitter.create_documents([total_info])
    palm_embeddings=GooglePalmEmbeddings()

    vector = FAISS.from_documents(documents, palm_embeddings)

    retriever = vector.as_retriever()

    retriever_tool = create_retriever_tool(
        retriever,
        "medical_tool",
        "searches the medical documents"
    )

    tools = [retriever_tool]

    model = ChatGroq(model="llama3-8b-8192")

    model_with_tools = model.bind_tools(tools)

    prompt=PromptTemplate.from_template(
    """
    You are a mecial chatbot and answer the user query in short based on the tool. If some other questions 
    are asked other than medical then say something like you are only designed to answer medical questions only.
    question: {input}
    answer:''
    {agent_scratchpad}
    """
    )

    agent = create_tool_calling_agent(model, tools, prompt)

    agent_executor = AgentExecutor(agent=agent, tools=tools, output_parser=StrOutputParser())


