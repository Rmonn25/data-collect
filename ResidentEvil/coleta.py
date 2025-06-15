# %%
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd 

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.residentevildatabase.com/personagens/',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    # 'cookie': '_gid=GA1.2.1927814430.1750006044; __gpi=UID=000010d410da9f94:T=1750006022:RT=1750006022:S=ALNI_Mbk4gKOCmMOnkk2aw7bOCuBK3VRsQ; __gads=ID=7e742d3fa2c9821f:T=1750006022:RT=1750013129:S=ALNI_MZjfusS_9kioo8o3XwehGu_Fcfmbw; __eoi=ID=2f7867b2d5fc0bf8:T=1750006022:RT=1750013129:S=AA-AfjZ9pRH_vxzVw_Nc5EwK4NiS; _ga=GA1.2.1885018565.1750006044; _ga_DJLCSW50SC=GS2.1.s1750013150$o2$g1$t1750013206$j4$l0$h0; _ga_D6NF5QC4QT=GS2.1.s1750013150$o2$g1$t1750013206$j4$l0$h0; FCNEC=%5B%5B%22AKsRol8ngilnOJc5Kllapw6tUhqZ7agRdYEbzPoSsubaoJeGCe_BpltgnBvxe6wNE2S2F4lvRayJJxeX4e0J0PgKgvn6_OOAmnb-NyEO9eKNtwLKvkqvOLylykhWDtRoUJPA0PU5yWqK130xfoHRXk4c2wAEJx0LPQ%3D%3D%22%5D%5D',
}

def get_content(url):
    resp = requests.get(url, headers=headers)
    return resp

# pega informações basicas do personagem
def get_basic_infos(soup):
    div_page = soup.find("div", class_ ="td-page-content")
    paragrafo = div_page.find_all("p")[1]
    ems = paragrafo.find_all("em")
    
    data = {}
    
    for i in ems:
        print(i)
        chave, valor, *_ = i.text.split(":")
        chave = chave.strip(" ")
        data[chave] = valor.strip(" ") 

    return data 

# pega as paricoes que o personagem teve nos jogos
def get_aparicoes(soup):
    lis = (soup.find("div", class_ ="td-page-content")
            .find("h4")
            .find_next()
            .find_all("li"))

    aparicoes = [i.text for i in lis]
    return aparicoes

# obtem os dados 
def get_personagem_infos(url):
    resp = get_content(url)
    if resp.status_code != 200:
        print("Não foi possivel obter os dados")
        return {}
    else:
        soup = BeautifulSoup(resp.text)
        data = get_basic_infos(soup)
        data["Aparicoes"] = get_aparicoes(soup)
        return data

# obtem os links das paginas dos personagens    
def get_links():
    url = "https://www.residentevildatabase.com/personagens/"
    resp = requests.get(url, headers=headers)
    soup_personagens = BeautifulSoup(resp.text)
    ancoras = (soup_personagens.find("div", class_="td-page-content")
                               .find_all("a"))
    
    links = [i["href"] for i in ancoras]
    return links

# %%

links = get_links()
data = []

for i in tqdm(links):
    print(i)
    d = get_personagem_infos(i)
    d["link"] = i
    nome = i.strip("/").split("/")[-1].replace("-", " ").title()
    d["Nome"] = nome
    data.append(d)

# %%

df = pd.DataFrame(data)
df
# %%

df.to_parquet("dados_re.parquet", index=False)
# %%

df_new = pd.read_parquet("dados_re.parquet")

df_new
# %%

df