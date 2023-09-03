
from selenium import webdriver

from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

import json

driver = webdriver.Edge()
wait = WebDriverWait(driver,3)

#urls
genshingg_url = "https://genshin.gg/characters/"

#All genshin characters
characters = ['alhaitham','hutao','kazuha','kokomi','nahida','nilou','raiden','yelan','zhongli','bennett','xiangling','xingqiu','albedo','ayaka','childe','ganyu','mona','shenhe','tighnari','yaemiko','yoimiya','baizhu','lyney','faruzan','fischl','gorou','kukishinobu','sara','yunjin','ayato','cyno','itto','jean','keqing','traveler(dendro)','venti','wanderer','xiao','beidou','collei','diona','layla','rosaria','sucrose','yaoyao','mika','kirara','diluc','eula','klee','qiqi','traveler(electro)','barbara','candace','chongyun','heizou','lisa','sayu','yanfei','kaveh','lynette','aloy','traveler(anemo)','traveler(geo)','dehya','amber','dori','kaeya','ningguang','noelle','razor','thoma','xinyan']

data = {}




for character in characters:
    url =genshingg_url+character
    driver.get(url)#Goes to the character's page
    
    try:
        wait.until(EC.url_to_be(url))
    except:
        print("I timed out! call me out!")
    
    soup = BeautifulSoup(driver.page_source, features ="html.parser")
    
    
    #Informacoes basicas
    info = {
        'element':soup.find('img',class_="character-element")['src'],
        'role':soup.find('div',class_="character-role").text,
        'weapon': soup.find('img',class_="character-path-icon")['alt'],
        'portrait': soup.find('img',class_="character-portrait")['src']
        }
    

    #Separo a seção de artefatos da seção de armas
    build_tags = soup.findAll("div",class_="character-build-section")

    #Obtendo informacoes das armas
    weapon_tags=build_tags[0].findAll("div",class_="character-build-weapon")
    best_weapons = []
    for weapon_tag in weapon_tags:
        weapon = {
            'name':weapon_tag.find('img',class_='character-build-weapon-icon')['alt'] ,
            'img':weapon_tag.find('img',class_='character-build-weapon-icon')['src']
        }
        best_weapons.append(weapon)

    #Obtendo informacoes dos artefatos
    artifact_tags = build_tags[1].findAll("div",class_="character-build-weapon")

    best_artifacts = []
    for artifact_tag in artifact_tags:
        artifacts_set_tags = artifact_tag.findAll("div",class_="character-build-weapon-content")
        artifacts = []
        for artifact_set_tag in artifacts_set_tags:
            artifacts.append( {
                'name': artifact_set_tag.find("div",class_="character-build-weapon-name").text,
                'img': artifact_set_tag.find("img",class_="character-build-weapon-icon")['src']
            })
        best_artifacts.append(artifacts)
    
    #Obtendo informações dos melhores status

    stats_tags = soup.findAll('div',class_="character-stats-item")

    #Remove as tags b dos status
    for stat_tag in stats_tags:
        stat_tag.b.decompose()

    #Remove o texto antes de dizer os substatus
    substats = stats_tags[3].text
    substats.replace("Substats:",'')
    substats.lstrip()

    best_stats = {
        'sands': stats_tags[0].text.lstrip(),
        'goblet':stats_tags[1].text.lstrip(),
        'circlet' : stats_tags[2].text.lstrip(),
        'substats': substats
    }
    
    
    data[character] = {
        'info' : info,
        'best_weapons':best_weapons,
        'best_artifacts':best_artifacts,
        'best_stats':best_stats
    }
#Exporta tudo no final
with open("data.json","w") as outfile:
    json.dump(data,outfile)