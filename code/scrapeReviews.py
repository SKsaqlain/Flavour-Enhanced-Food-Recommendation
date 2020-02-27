import mechanize
from bs4 import BeautifulSoup
br = mechanize.Browser()


def getFoodReviews(food):
    url="https://www.yummly.com/recipes?q="+food+"&taste-pref-appended=true"
    response=br.open(url)
    soup = BeautifulSoup(response.read(), 'html.parser')
    recipeContainer=soup.find_all("div",class_="RecipeContainer")
    #recipeContainer=soup.find_all("div",class_="recipe-card ingredients-hover single-recipe visible")
    #print(len(recipeContainer))

    foodContainer=recipeContainer[0].find_all("a")
    #print(foodContainer)
    print(len(foodContainer))
    reviews=[]
    id=1
    for i in range(0,len(foodContainer),2):
        #print(foodContainer)
        foodCode=foodContainer[i]["href"]
        if(not foodCode.startswith("/recipe/")):
            continue
        #print(foodCode)
        #print(foodContainer[i]["data-url"])
        url="https://www.yummly.com"+foodCode
        response=br.open(url)
        soup=BeautifulSoup(response.read(),'html.parser')
        cookbookDetails=soup.find(class_="recipe-details")
        
        reviewUrl="https://www.yummly.com"+foodCode+"#reviews"
        response=br.open(reviewUrl)
        soup=BeautifulSoup(response.read(),'html.parser')
        allReviews=soup.find_all("div",class_="review media")
        if(len(allReviews)==0):
        	continue

        for eachReview in allReviews:
            body=dict()
            body["id"]=id
            body["food_item"]=food
            body["name"]=eachReview.find(class_="review-name").find("a").get_text()
        #     reviewName=reviews[0].find_all("div",class_="review-name")
            stars=eachReview.find(class_="review-rating").find_all("span")
            cnt=0
        #     print(stars)
            for st in stars:
                #print(st["class"])
                if(st["class"][1].startswith("full-star")):
                    cnt+=1
            body["rating"]=cnt
            body["review"]=eachReview.find(class_="review-text font-normal p2-text").get_text()
            reviews.append(body)
        id+=1

        #print(reviews)
    return reviews

if(__name__=="__main__"):
	x=getFoodReviews("Roasted chickpeas")
	print(x)