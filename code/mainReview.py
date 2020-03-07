from scrapeReviews import getFoodReviews
import json
import sys

#run as python mainReview.py filename.txt lastFoodItemIndex
with open(sys.argv[1],'r') as sourceFile:
	dishes=sourceFile.readlines()
	for i,dish in enumerate(dishes):
		if(i>=int(sys.argv[2])):
			print(i,dish)
			dish=dish.strip("\n")
			data=getFoodReviews(dish)
			destFile=open("../dataset/yummlyReviews/"+dish.replace(" ","-")+".json","w")
			json.dump(data,destFile,indent=4)
			destFile.close()
	# for i,dish in enumerate(dishes):
	# 	if(i>=42):
	# 		print(i,dish)
	# 		dish=dish.strip("\n")
	# 		data=getFoodReviews(dish)
	# 		destFile=open("../dataset/yummlyReviews/"+dish.replace(" ","-")+".json","w")
	# 		json.dump(data,destFile,indent=4)
	# 		destFile.close()
	# for i in range(len(dishes)-1,-1,-1):
	# 	if(i<=976):
	# 		print(i,dishes[i])
	# 		dish=dishes[i].strip("\n")
	# 		data=getFoodReviews(dish)
	# 		destFile=open("../dataset/yummlyReviews/"+dish.replace(" ","-")+".json","w")
	# 		json.dump(data,destFile,indent=4)
	# 		destFile.close()
