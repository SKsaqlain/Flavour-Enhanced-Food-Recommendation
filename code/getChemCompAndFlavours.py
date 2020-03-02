import sys
import urllib
import mechanize
from mechanize import urlopen,urljoin
import json
import pickle
import requests
from collections import OrderedDict 
from bs4 import BeautifulSoup


def getChemCompAndFlavours(ingredient):
    #initializing mechanize 
    br=mechanize.Browser()
    #loading the page
    response=br.open("https://cosylab.iiitd.edu.in/flavordb/search")
    br.response()
    #extracting the required form to search for chemical compound
    br.form=list(br.forms())[1]
    #filling the form with the required ingredient
    control=br.form.find_control("entity")
    control.value=ingredient
    #making request
    response=br.submit()
    
    #reading response in JSON format
    rawJsonData=response.read()
    #print(rawJsonData)
    #print(json.loads(rawJsonData))
    
    #selecting a specific ingredient from the list of all possible similar ingredients
    entity_id=None
    jsonifiedData=eval(json.loads(rawJsonData))
    #print(jsonifiedData)
    for ele in jsonifiedData:
        if(ele["entity_alias"].lower()==ingredient.lower()):
            entity_id=ele["entity_id"]
            break
    if(entity_id==None):
        entity_id=jsonifiedData[0]["entity_id"]
    print(entity_id)
    queryString="/flavordb/entity_details?id="+str(entity_id)
    print(queryString)
    url="https://cosylab.iiitd.edu.in/flavordb/search"+"/"+queryString
    print(url)
    
    #loading the chemical compound page 
    response=br.open(url)
    soup=BeautifulSoup(response.read(),'html.parser')
    table=soup.find_all('table',id="molecules")
    '''extracting all the tr from molecule table and storing the chemical compound 
    name and its corresponding flavour profile'''
    
    #extracting relavent information
    table[0].findAll("tr")
    molecules=dict()
    for tr in table[0].findAll("tr"):
        td=tr.findAll("td")
        #print(td)
        if(len(td)==4):
            chemComp=td[0].get_text(strip=True)
            molecules[chemComp]=td[2].get_text(strip=True).split(",")
    return molecules

if( __name__=='__main__'):
    print(getChemCompAndFlavours("white pepper"))