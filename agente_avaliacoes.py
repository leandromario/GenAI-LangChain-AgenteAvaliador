import requests
import json
import time

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from os import getenv

http_reviews = requests.get("https://apis.codante.io/api/reviews-api/reviews")
dict_reviews = json.loads(http_reviews.content.decode("utf-8"))
list_review = []

for review in dict_reviews["data"]:
  list_review.append(review["description"])

#Desenvolva, a partir daqui, um chain para um agente que avalia se as revisões recebidas são positivas ou negativas.
#Utilize todos os componentes do LangChain que trabalhamos até este momento para isso.

load_dotenv()
API_KEY = getenv("GROQ_API_KEY")

llm = ChatGroq(
    groq_api_key = API_KEY,
    model        = "qwen/qwen3.8-27b",
    temperature  = 0,                     #Classificação deve ser o mais determinística possível
    max_tokens   = 200,                   #Limite de saída por requisição (plano on_demand: 1000 OTPM)
    max_retries  = 5                      #Repete a chamada com espera ao receber 429
)

output_parser = StrOutputParser()

#Chain 1: classifica a avaliação como positiva ou negativa
classify_prompt = ChatPromptTemplate([("system", "Você classifica avaliações de clientes sobre um produto. Responda exclusivamente com uma única palavra: Positiva ou Negativa. Não escreva mais nada."),\
                                      ("human", "{review}")])

classify_chain = classify_prompt | llm | output_parser

#Chains 2 e 3: respondem ao comentário de acordo com a classificação obtida
positive_prompt = ChatPromptTemplate([("system", "Você é o atendimento de uma loja de fones de ouvido. Escreva uma resposta curta (até 3 frases), cordial e agradecida a uma avaliação positiva de um cliente."),\
                                      ("human", "{review}")])

negative_prompt = ChatPromptTemplate([("system", "Você é o atendimento de uma loja de fones de ouvido. Escreva uma resposta curta (até 3 frases), empática e que peça desculpas e ofereça ajuda a uma avaliação negativa de um cliente."),\
                                      ("human", "{review}")])

reply_chains = {"positiva": positive_prompt | llm | output_parser,
                "negativa": negative_prompt | llm | output_parser}

for review in list_review:
  sentiment = classify_chain.invoke({"review": review}).strip().lower().rstrip(".")

  print("Avaliação: " + review)
  print("Classificação: " + sentiment)

  if sentiment in reply_chains:
    print("Resposta: " + reply_chains[sentiment].invoke({"review": review}).strip())
  else:
    print("Resposta: (classificação não reconhecida, nenhuma resposta gerada)")
  print()

  time.sleep(10)                          #Espaça as chamadas para respeitar o limite de tokens por minuto
