'''
Arquivo responsável por compilar todas as funções referentes a extração de conteúdo do cardápio

As funções foram pensadas para serem utilizadas com a biblioteca PyMuPdf, com a função .get_text()
aplicada nas páginas, e passadas para a função getWeekMenu(page1Text, page2Text)

'''


#recebe o texto da página um, e o sanitiza, extraindo apenas o conteúdo referente as calorias 
def __sanitizeCaloriesText(caloriesPageText: str) -> list[str]:
    calories = []

    caloriesPageText = caloriesPageText.lower()

    indexCalorico = caloriesPageText.find("calórico")

    if(indexCalorico == -1): return []

    caloriesTextCut = caloriesPageText[indexCalorico:]

    indexSobremesa1 = caloriesTextCut.find("sobremesa")
    indexSobremesa2 = caloriesTextCut.find("sobremesa", indexSobremesa1 + 1) #pegando o index da segunda "sobremesa"

    if(indexSobremesa1 == -1 or indexSobremesa2 == -1): return []

    caloriesProteico = caloriesTextCut[indexSobremesa1:indexSobremesa2].split("\n")
    caloriesVegetariano = caloriesTextCut[indexSobremesa2:].split("\n")

    for i in [1, 2, 3, 4, 5, 6]:
        calories.append(caloriesProteico[i].replace(",", "."))

    for i in [1, 2, 3, 4, 5, 6]:
        calories.append(caloriesVegetariano[i].replace(",", "."))

    return calories

#converte o texto (valor) de calorias para float
def __convertCalorieTextFloat(calorieText: str) -> float:
    #esperando texto no formato "1234.46 calorias" ou algo diferente
    if(calorieText.split(".")[0].isnumeric()):
        return float(calorieText.split(" ")[0].strip())
    return None

#recebe  o texto da página de calorias e extrai as calorias em formato de dicionário
def __extractWeekCalories(caloriesPageText: str) -> dict:
    calories = __sanitizeCaloriesText(caloriesPageText)

    caloriesPerDayWeek = {}
    caloriesPerDayWeek["prato_proteico"] = {"segunda": None, "terça": None, "quarta": None, "quinta": None, "sexta": None, "sábado": None}
    caloriesPerDayWeek["opcao_vegetariana"] = {"segunda": None, "terça": None, "quarta": None, "quinta": None, "sexta": None, "sábado": None}

    for i, dWeek in enumerate(["segunda", "terça", "quarta", "quinta", "sexta", "sábado"]):
        j = i + 6

        caloriesMeat = __convertCalorieTextFloat(calories[i])
        caloriesVeg = __convertCalorieTextFloat(calories[j])

        caloriesPerDayWeek["prato_proteico"][dWeek] = caloriesMeat
        caloriesPerDayWeek["opcao_vegetariana"][dWeek] = caloriesVeg

    return caloriesPerDayWeek

#recebe o texto da segunda página do cardápio (com ingredientes) e o retorna sanitizado (cada item e ingrediente em apenas uma linha)
def __sanitizeIngredientsText(ingredientPageText: str) -> str:
    textSanitized = []
    for i, c in enumerate(ingredientPageText):
        if(i == len(ingredientPageText) - 1): 
            textSanitized.append(c)
            break

        #caso o proximo caractere de linha seja minusculo, sabemos que a linha foi indevidamente pulada
        if c == "\n":
            nextChr = ingredientPageText[i + 1]
            asciiNext = ord(nextChr) #proximo caractere em ascii

            if((asciiNext >= 65 and asciiNext <= 90) or (nextChr in ["\n", " ", ""])):
                textSanitized.append(c)
            else:
                continue
        else:
            textSanitized.append(c)

    return "".join(textSanitized)

#recebe o texto da segunda pagina do cardapio, e retorna um dicionário na estrutura dia da semana (chave), texto referente ao dia no cardapio (valor)
def __extractWeekIngredients(ingredientPageText: str) -> dict:
    ingredientsText = __sanitizeIngredientsText(ingredientPageText)

    weekMenuIngredients = {"segunda": [], "terça": [], "quarta": [], "quinta": [], "sexta": [], "sábado": []}

    ingrTextLower = ingredientsText.lower()

    for dWeek in ["segunda", "terça", "quarta", "quinta", "sexta", "sábado"]:
        index = ingrTextLower.find(dWeek)

        if(index == -1):
            weekMenuIngredients[dWeek] = None
            continue

        contN = 0 #quantidade de linhas (\n)

        while(index < len(ingrTextLower) - 1 and contN < 9): 
            if(ingrTextLower[index] == "\n"): 
                contN+=1
                if(contN == 9): break

            weekMenuIngredients[dWeek].append(ingrTextLower[index])
            index+=1

        weekMenuIngredients[dWeek] = "".join(weekMenuIngredients[dWeek])

    return weekMenuIngredients

#recebe uma data no formato '01/02/3456' e retorna no formato '3456-02-01'
def __formatDate(date: str) -> str:
    date = date.split("/")
    date = date[::-1]
    return "-".join(date)

#recebe os dicionários gerados pelas funções acima, e retorna um dicionário com tudo compilado e organizado, focado na conversão futura para json
def __extractMenuWeek(weekMenuIngredients: dict, weekCalories: dict) -> dict:
    weekMenu = {}
    for dWeek in ["segunda", "terça", "quarta", "quinta", "sexta", "sábado"]:

        lines = []

        if(weekMenuIngredients[dWeek] != None):
            
            lines = weekMenuIngredients[dWeek].split("\n")
            
            #extrai a data, sempre contida na primeira linha
            date = lines[0].split(":")[1].strip()
            date = __formatDate(date)

            weekMenu[date] = {}

            for i, line in enumerate(lines):
                indexPattern = ["", "arroz", "arroz", "acompanhamento", "prato_proteico", "opcao_vegetariana", "guarnicao", "salada", "salada", "sobremesa"]

                if(i == 0): continue

                if(line != None):
                    #extrai o item do cardapio, e os seus ingredientes
                    item, ingredients = line.split(":")
                    item = item.strip()
                    ingredients = ingredients.strip()

                    #checar se a chave já existe no dicionario
                    if(not(indexPattern[i] in weekMenu[date].keys())):
                        weekMenu[date][indexPattern[i]] = {}

                    weekMenu[date][indexPattern[i]][item] = ingredients

            #adicionando as calorias ao dict
            weekMenu[date]["calorias"] = {}
            weekMenu[date]["calorias"]["prato_proteico"] = weekCalories["prato_proteico"][dWeek]
            weekMenu[date]["calorias"]["opcao_vegetariana"] = weekCalories["opcao_vegetariana"][dWeek]

                
    return weekMenu
        
#recebe a primeira pagina e segunda pagina do cardapio, e retorna um dicionario com todas as informacoes relevantes
def getWeekMenu(page1Text: str, page2Text: str) -> dict:

    weekCalories = __extractWeekCalories(page1Text)
    weekMenuIngredients = __extractWeekIngredients(page2Text)
    
    return __extractMenuWeek(weekMenuIngredients, weekCalories)
    





