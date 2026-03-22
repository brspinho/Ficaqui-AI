import requests
from bs4 import BeautifulSoup
import re

url = "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Previa_da_Populacao/"
# Wait, let's just look at the master directory
url = "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/"
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
for link in soup.find_all('a'):
    print(link.get('href'))
