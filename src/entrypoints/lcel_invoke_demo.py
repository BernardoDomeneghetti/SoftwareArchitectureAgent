from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from rag.rag_search import search

user_message = "Quais são as melhores práticas para implementar resiliência em microserviços?"

similarities = search(user_message)
technical_terms = [term for term, _ in similarities]

chain_input = {
    "user_message": user_message,
    "technical_terms": technical_terms
}


prompt = ChatPromptTemplate.from_template(
    "Dado o contexto de arquitetura de software e o tema :{technical_terms} responda:{user_message}"
)

model = ChatOpenAI(model_name="gpt-4o-mini")

parser = StrOutputParser()

chain = prompt|model|parser

response = chain.invoke(chain_input)

print ("Termos técnicos encontrados:", technical_terms)
print ("Resposta do modelo:", response)