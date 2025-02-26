'''
Arquivo responsável por fazer as manipulações no banco de dados
'''

import sqlite3
import json
import os
from dotenv import load_dotenv
load_dotenv()

#path para a base de dados
DATABASE_PATH = os.getenv('DATABASE_PATH')

#cria a tabela que armazenará os menus, verificando caso sua existencia previamente
def createTable():
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS menus(date TEXT PRYMARY KEY, content TEXT)")

    con.close()

#TODO: verificar se data está no modelo 'YYYY-MM-DD'
#recebe como parametro um dia (str) e o menu do dia (dict), e os insere na base de dados
def insertDayMenu(date: str, dayMenu: dict):
    menuJson = json.dumps(dayMenu)

    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO menus VALUES (?, ?)", (date, menuJson))
    con.commit()

    con.close()

#recebe um dict no modelo retornado pelo arquivo "pdfmenuextract", e insere dia a dia na base de dados
def insertWeek(weekMenu: dict):
    for date in weekMenu:
        insertDayMenu(date, json.dumps(weekMenu[date]))

#converte o conteudo armazenado na base de dados em um objeto do python (dict)
def convertContentObject(content: str) -> dict:
    try:
        #TODO: entender porque é necessário fazer a conversão duas vezes seguidas (provavelmente pelo modo em que o content é armazenado)
        return json.loads(json.loads(content))
    except:
        return None

#recebe uma data no formato 'YYYY-MM-DD' e retorna o menu daquele dia
def getMenuByDate(date: str) -> dict:
    try:
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()

        res = cur.execute("SELECT content FROM menus WHERE date = ?", (date, ))
        menu = res.fetchone()

        con.close()

        return {date: convertContentObject(menu[0])}
    except:
        return None

def getAll() -> list:
    try:
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        res = cur.execute("SELECT * FROM menus")
        allMenus = res.fetchall()
        con.close()

        allMenus = [{e[0]: convertContentObject(e[1]) for e in allMenus}]

        return allMenus
    except:
        return None



