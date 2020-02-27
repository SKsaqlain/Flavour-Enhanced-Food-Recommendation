from scrapeReviews import getFoodReviews
import json


with open("uniqueDishName.txt",'r') as sourceFile:
	dishes=sourceFile.readlines()
	for dish in dishes:
		print(dish)
		dish=dish.strip("\n")
		data=getFoodReviews(dish)
		destFile=open("../dataset/yummlyReviews/"+dish.replace(" ","-")+".json","w")
		json.dump(data,destFile,indent=4)
		destFile.close()
