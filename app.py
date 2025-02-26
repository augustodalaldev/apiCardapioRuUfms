from flask import Flask
import datetime
import sqlmanipulation as sqlm

def validateDate(date: str) -> bool:
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
        return True
    except:
        return False

app = Flask(__name__)

@app.route("/")
def root():
    return """
    
    API Cardápio RU UFMS 
    <br>
    https://github.com/augustodalaldev/apiCardapioRuUfms
    
    """

@app.get("/menu/today")
def todayMenu():
    todayDate = datetime.date.today().isoformat()

    menu = sqlm.getMenuByDate(todayDate)

    if(menu == None): return {}

    return menu

@app.get("/menu/tomorrow")
def tomorrowMenu():
    tomorrowDate = (datetime.date.today() + datetime.timedelta(days=1)).isoformat() 

    menu = sqlm.getMenuByDate(tomorrowDate)

    if(menu == None): return {}

    return menu

@app.get("/menu/yesterday")
def yesterdayMenu():
    yesterdayDate = (datetime.date.today() - datetime.timedelta(days=1)).isoformat() 

    menu = sqlm.getMenuByDate(yesterdayDate)

    if(menu == None): return {}

    return menu

@app.get("/menu/<date>")
def menuByDate(date):
    if(not validateDate(date)): return {}

    menu = sqlm.getMenuByDate(date)

    if(menu == None): return {}

    return menu

if __name__ == "__main__":
    app.run(host="0.0.0.0")
