import requests
URL_MENUS = "https://proaes.ufms.br/category/restaurante-universitario/"
URL_FILES = "https://proaes.ufms.br/files"

#faz um request na página que compila todos os cardápios e busca pela url do cardápio mais recente e a retorna
def getNewestUrlPdf():
    page = requests.get(URL_MENUS)
    pageText = page.text

    indexNewestUrlMenu = pageText.find(URL_FILES)
    if(indexNewestUrlMenu == -1): return 

    newestUrlMenu = pageText[indexNewestUrlMenu:].split(chr(39))[0]

    return newestUrlMenu
