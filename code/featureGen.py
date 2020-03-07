import json
from getChemCompAndFlavours import *



def genVecList(foodName,ingrFile,destPath):
    uniChemComp=list()
    with open(ingrFile,"r") as f:
        ingr=[ele.strip("\n") for ele in f.readlines()]
        for i in ingr:
            temp=getChemCompAndFlavours(i)
            if(len(temp)>=1):
                uniChemComp.extend(list(temp.keys()))
        uniChemComp=list(set(uniChemComp))
    with open(destPath+"foodName"+".json","w") as f:
    	json.dump(uniChemComp,f)

if(__name__=='__main__'):        
	chem=genVecList("veg-spring-roll","../dataset/sample/Veg Spring Roll.txt","../dataset/sample/")
	with open("../dataset/sample/veg-spring-roll-chem.json","w") as f:
	    json.dump(chem,f)