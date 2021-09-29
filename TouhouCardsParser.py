# Parse every card
# Lay it out as a HTML list of links

import os, aiohttp, asyncio, socket, urllib, json, jsonpickle
import cloudscraper

scraper = cloudscraper.create_scraper()

jsonpickle.set_preferred_backend('json')

trading_cards = []

good_cards = 0
bad_cards = 0

use_old_wiki = True

class TradingCard:
    name = ""
    raw_name = ""
    link = ""
    character_image = ""

    type1 = ""
    type2 = ""

    hp = 0
    attack = 0
    defense = 0
    special_attack = 0
    special_defense = 0
    speed = 0
    total = 0
    #rarity = ""
    #rarity_message = ""
    #rarity_string = ""
    #price = ""

class RarityResponse:
    rarity = ""
    rarity_symbol = ""

def write(file, contents):
    open(os.path.dirname(os.path.realpath(__file__)) + '\\' +  file, 'a').write(contents)

def read(file):
    return open(os.path.dirname(os.path.realpath(__file__)) + '\\' +  file, 'r').read()

def read_raw(file):
    return open (os.path.dirname(os.path.realpath(__file__)) + '\\' +  file, 'rb').read()

def mkdir(directory):
    if os.path.exists(os.path.dirname(os.path.realpath(__file__)) + '\\' + directory):
        return
    else:
         os.makedirs(os.path.dirname(os.path.realpath(__file__)) + '\\' + directory)

async def get_aio_connector():
    conn = aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=True)
    return conn

async def get(url):
    global scraper
    
    #async with aiohttp.ClientSession(connector=await get_aio_connector()) as session:
        #async with session.get(url) as resp:
            #return await resp.text()
    return scraper.get(url).text

'''
async def GetImage(query):
    json = await get("https://en.touhouwiki.net/wiki/" + query)
    file = ""

    try:
        json = json[json.index('infobox'):]
        json = json[json.index('<a href="/wiki/File:') + 9:]
        json = json[:json.index("</a>")]
        file = json[json.index('File:'):json.index('"')]

        json = await get("https://en.touhouwiki.net/api.php?action=query&titles=" + file + "&prop=imageinfo&iiprop=url&format=json")

        json = json[json.index('"url":"') + 7:]
        file = json[:json.index('"')]
    except:
        return False

    if not file == "":
        return file

    return False
'''

async def GetNames():
    if use_old_wiki:
        html = await get("https://en.touhouwiki.net/api.php?action=parse&prop=wikitext&format=json&page=Touhoudex_2/Touhoudex_2")
    else:
        #html = await get("https://touhou.fandom.com/wiki/Touhoudex_2/Touhoudex_2")
        html = await get("https://touhou.fandom.com/api.php?action=parse&prop=wikitext&format=json&page=Touhoudex_2/Touhoudex_2")

    raw_names = []

    #if use_old_wiki:
    keep_parsing = True
    while keep_parsing:
        try:
            html = html[html.index('}}') + 4:]
            html = html[html.index('{{Touhoudex 2/DexEntry') + 22:]
            for i in range(0, 2):
                html = html[html.index('|') + 1:]
            name = html[:html.index('|')]

            if '<!--' in name:
                name = name[:name.index('<!--')]

            if not name == "None":
                raw_names.append(name)
                #print(name)
        except:
            keep_parsing = False

    if use_old_wiki:
        raw_names = raw_names[:-19] # Cut off misc. characters

        # Okay but add a few more back in though because they're pretty cool
        raw_names.append("TensokuG")
        raw_names.append("Kasen")
        raw_names.append("Satsuki")
        raw_names.append("EMarisa")
        raw_names.append("JKSanae")
        raw_names.append("MPSuika")
        raw_names.append("Ayakashi")
    else:
        raw_names = raw_names[:-7] # Cut off misc. dex
        raw_names = raw_names[:-1] # Cut off hidden dex

    '''
    else:
        while True:
            try:
                html = html[html.index('rowspan'):]
                html = html[html.index('Touhoudex 2/') + 12:]
                name = html[:html.index('"')]

                print(name)
                raw_names.append(name)
            except:
                break
    '''

    #print("DONE")
    #input()
    return raw_names

'''
async def CalculateRarity(power):
    rarity_remaining = float(power) - 330

    rarity = 0
    rarity_symbol = ":large_blue_circle:"

    while rarity_remaining >= 39:
        rarity_remaining = rarity_remaining - 39
        rarity = rarity + 1

    if rarity >= 4:
        rarity_symbol = ":red_circle:"
    if rarity >= 9:
        rarity_symbol = ":white_circle:"

    #rarity = rarity - 1

    rarity_response = RarityResponse()
    rarity_response.rarity = rarity
    rarity_response.rarity_symbol = rarity_symbol

    return rarity_response
'''

async def GetCard(raw_name):
    raw_name_link = raw_name.replace(".", "")

    if use_old_wiki:
        #character_html = await get("https://en.touhouwiki.net/wiki/Touhoudex_2/" + raw_name)
        raw_name_link = raw_name_link.replace('Shikieiki', 'Eiki')
        character_html = await get("https://en.touhouwiki.net/api.php?action=parse&prop=wikitext&format=json&page=Touhoudex_2/" + raw_name_link)
    else:
        character_html = await get("https://touhou.fandom.com/api.php?action=parse&prop=wikitext&format=json&page=Touhoudex_2/" + raw_name_link)

    card = TradingCard()

    if use_old_wiki:
        card.raw_name = raw_name
        print("RawName='" + raw_name + "'")

        #character_html = character_html.replace(' |', ' |')
        character_html = character_html.replace('\\n|', ' |')
        character_html = character_html.replace(' \\n|', ' |')

        character_html = character_html[character_html.index('name') + 4:]
        character_html = character_html[character_html.index('=') + 1:]

        character_name = character_html[:character_html.index(' |')]

        link_is_name = False
        character_link = ""
        if '[' in character_name:
            if '|' in character_name:
                character_link = character_name[character_name.index('[['):character_name.index('|') + 1]
            else:
                character_link = character_name[character_name.index('[['):character_name.index(']]') + 1]
                link_is_name = True
            link = character_link[2:-1].replace(' ', '_')
        else:
            link = ""

        card.link = link
        print("Link='" + link + "'")

        if link_is_name:
            character_name = character_name.replace('[[', '')
            character_name = character_name.replace(']', '')
        else:
            character_name = character_name.replace(character_link, '')

        while '[' in character_name:
            if '|' in character_name:
                character_link = character_name[character_name.index('[['):character_name.index('|') + 1]
            else:
                character_link = character_name[character_name.index('[['):character_name.index(']]') + 2]
            character_name = character_name.replace(character_link, '')

        name = character_name.replace(']]', '')

        true_name = name
        if true_name[0].isupper() and true_name[1].isupper():
            if true_name[0] == 'A':
                true_name = "Attack " + name[1:]
            if true_name[0] == 'D':
                true_name = "Defense " + name[1:]
            if true_name[0] == 'H':
                true_name = "Helper " + name[1:]
            if true_name[0] == 'S':
                true_name = "Speed " + name[1:]
            if true_name[0] == 'T':
                true_name = "Technician " + name[1:]
        if true_name.startswith("Ad") and true_name[2].isupper():
            true_name = "Advent " + name[2:]

        if true_name.endswith(" "):
            true_name = true_name[:-1]

        if raw_name.startswith("Chibi ") and (not true_name.startswith("Chibi ")):
            true_name = "Chibi " + true_name

        card.name = true_name
        print("Name='" + true_name + "'")

        #character_image = "Touhoudex 2/" + raw_name
        #character_image = await GetImage(character_image)

        character_html = character_html[character_html.index('image') + 5:]
        file = character_html[character_html.index('=') + 1:character_html.index(' |')]
        if file.endswith(" "):
            file = file[:-1]
        file = file.replace(" ", "_")
        if '\\' in file:
            file = file[:file.index('\\')]
        file = "File:" + file
        print("DEBUG FILE '" + file + "'")

        character_image = await get("https://en.touhouwiki.net/api.php?action=query&titles=" + file + "&prop=imageinfo&iiprop=url&format=json")
        character_image = character_image[character_image.index('"url":"') + 7:]
        character_image = character_image[:character_image.index('"')]

        card.character_image = character_image
        print("CharacterImage='" + character_image + "'")

        character_html = character_html[character_html.index('type1') + 5:]
        type1 = character_html[character_html.index('=') + 1:character_html.index(' |')]
        if type1.endswith(" "):
            type1 = type1[:-1]
        card.type1 = type1
        print("Type1='" + type1 + "'")

        type2 = ""
        if 'type2' in character_html:
            character_html = character_html[character_html.index('type2') + 5:]
            type2 = character_html[character_html.index('=') + 1:character_html.index(' |')]
            if type2.endswith(" "):
                type2 = type2[:-1]
        card.type2 = type2
        print("Type2='" + type2 + "'")

        character_html = character_html[character_html.index('BaseStats'):]

        character_html = character_html[character_html.index('HP=') + 3:]
        hp = int(character_html[:character_html.index(' |')])
        card.hp = hp
        print("Hp=" + str(hp))
        #Lowest: 1
        #Highest: 255

        character_html = character_html[character_html.index('Attack=') + 7:]
        attack = int(character_html[:character_html.index(' |')])
        card.attack = attack
        print("Attack=" + str(attack))
        #Lowest: 10
        #Highest: 255

        character_html = character_html[character_html.index('Defense=') + 8:]
        defense = int(character_html[:character_html.index(' |')])
        card.defense = defense
        print("Defense=" + str(defense))
        #Lowest: 5
        #Highest: 220

        character_html = character_html[character_html.index('SplAtk=') + 7:]
        special_attack = int(character_html[:character_html.index(' |')])
        card.special_attack = special_attack
        print("SpAttack=" + str(special_attack))
        #Lowest: 10
        #Highest: 200

        character_html = character_html[character_html.index('SplDef=') + 7:]
        special_defense = int(character_html[:character_html.index(' |')])
        card.special_defense = special_defense
        print("SpDefense=" + str(special_defense))
        #Lowest: 5
        #Highest: 220

        character_html = character_html[character_html.index('Speed=') + 6:]
        speed = int(character_html[:character_html.index(' |')])
        card.speed = speed
        print("Speed=" + str(speed))
        #Lowest: 5
        #Highest: 180

        character_html = character_html[character_html.index('Total=') + 6:]
        total = int(character_html[:character_html.index('\\')])
        card.total = total
        print("Total=" + str(total))
        #Lowest: 280
        #Highest: 720

        #Old Lowest: 330

        return card
        '''
        try: # New Template Parser
            character_name = character_html[character_html.index("vcard") + 4:]
            character_html = character_name
            character_name = character_name[character_name.index("<b>") + 3:character_name.index("</b>")]
            if character_name.endswith("</a>"):
                character_name = character_name[:-4]

            #card.character_name = character_name
            card.raw_name = raw_name

            try:
                link = character_name[character_name.index("href=") + 6:]
                link = link[1:link.index('"')]
                link = link[link.index("/") + 1:]
            except:
                link = ""

            card.link = link

            name = character_name
            try:
                while '<' in name:
                    bad_name = name[name.index("<"):name.index(">") + 1]
                    name = name.replace(bad_name, "")
            except:
                #name = character_name
                pass

            #card.name = name

            true_name = name
            if true_name[0].isupper() and true_name[1].isupper():
                if true_name[0] == 'A':
                    true_name = "Attack " + name[1:]
                if true_name[0] == 'D':
                    true_name = "Defense " + name[1:]
                if true_name[0] == 'H':
                    true_name = "Helper " + name[1:]
                if true_name[0] == 'S':
                    true_name = "Speed " + name[1:]
                if true_name[0] == 'T':
                    true_name = "Technician " + name[1:]
            if true_name.startswith("Ad"):
                true_name = "Advent " + name[2:]

            card.name = true_name

            character_image = "Touhoudex 2/" + raw_name
            character_image = await GetImage(character_image)

            card.character_image = character_image

            power = character_html[character_html.index("Base Stats"):]
            #power = power[power.index("</tr>") + 5:power.index("</table>")]
            power = power[:power.index("</table>")]
            power = power[power.rfind("<td>") + 4:]
            power = power[:power.index("<") - 1]
            power = int(power)

            card.power = power



            #Lowest: 330
            #Highest: 720

            response = await CalculateRarity(power)

            card.rarity = response.rarity
            rarity_symbol = response.rarity_symbol

            rarity_message = ""
            for i in range(0, 10):
                if i <= response.rarity:
                    rarity_message = rarity_message + response.rarity_symbol
                else:
                    rarity_message = rarity_message + ":black_circle:"

            card.rarity_message = rarity_message

            rarity_string = "Common"
            #if card.rarity >= 4:
                #rarity_string = "Rare"
            if card.rarity >= 1:
                rarity_string = "Uncommon"
            if card.rarity >= 4:
                rarity_string = "Rare"
            if card.rarity >= 6:
                rarity_string = "Epic"
            if card.rarity == 10:
                rarity_string = "LEGENDARY"

            card.rarity_string = rarity_string

            #price = int((int(power)*int(power)*int(power)*int(power)/2)/100000000) * (rarity + 1)
            #price = int((int(power)*int(power)*int(power)*2)/1000000) * (rarity + 1)
            #price = int((int(power)*int(power)*int(power)*2)/1000000)
            price = int((power*power*power*2)/1000000)

            if response.rarity >= 7:
                for i in range(7, 10):
                    if response.rarity >= i:
                        price = price * 2

            card.price = price

            return card
        except: # Outdated Template Parser
            return False
        '''

async def PopulateTree():
    mkdir('cards_root')
    for i in range(0, len(trading_cards)):
        folder = trading_cards[i].raw_name.replace(' ', '_')
        write("cards_root\\index.html", '<li><a href="' + folder + '//index.html">' + trading_cards[i].raw_name + "</a></li>\n")
        mkdir('cards_root//' + folder)

        print(trading_cards[i].raw_name + " - Image")
        urllib.request.urlretrieve(trading_cards[i].character_image, 'cards_root//' + folder + '//0.jpg')
        write('cards_root//' + folder + '//index.html', '<img src="0.png"><br>\n')

        print(trading_cards[i].raw_name + " - Card Info")
        link = trading_cards[i].link.replace('_', ' ')
        if trading_cards[i].link != "":
            link = '<a href="https://en.touhouwiki.net/wiki/' + trading_cards[i].link + '">' + link + '</a>'
        write('cards_root//' + folder + '//index.html', trading_cards[i].raw_name + '/' + trading_cards[i].true_name + ' (' + name + ')')
        print()
    print("Finished!")

async def Start():
    global trading_cards

    global good_cards
    global bad_cards

    if os.path.exists(os.path.dirname(os.path.realpath(__file__)) + '\\cards_pickle.json'):
        print("Using existing Cards JSON File!")
        trading_cards = read('cards_pickle.json')
        trading_cards = jsonpickle.decode(trading_cards)
        '''
        print("Populating 'Card List' HTML Structure in 'root' in 5 seconds...")
        await asyncio.sleep(5)
        print("Now creating 'Card List' HTML Structure in 'root'...\n")
        await PopulateTree()
        '''

        '''
        for i in range(0, 11):
            number = 0
            for ii in range(0, len(trading_cards)):
                rarity = await CalculateRarity(trading_cards[ii].power)
                rarity = rarity.rarity
                if rarity == i:
                    number = number + 1
            print(str(i) + " Rarity Cards: " + str(number))
        '''
        '''
        for i in range(330, 721):
            number = 0
            for ii in range(0, len(trading_cards)):
                #print(str(i) + " - " + str(trading_cards[ii].power))
                if trading_cards[ii].power == i:
                    number = number + 1
            if number > 0:
                print(str(i) + " - " + str(number))
        '''
        lowest = trading_cards[0].total
        highest = trading_cards[0].total
        print("Lowest: " + str(lowest))
        print("Highest: " + str(highest))
        for i in range(0, len(trading_cards)):
            if trading_cards[i].total < lowest:
                lowest = trading_cards[i].total
                print("New Lowest: " + str(lowest))
            if trading_cards[i].total > highest:
                highest = trading_cards[i].total
                print("New Highest: " + str(highest))

        print("Lowest: " + str(lowest))
        print("Highest: " + str(highest))
    else:
        names = await GetNames()

        for i in range(0, len(names)):
            card = await GetCard(names[i])
            if card == False:
                print("[" + str(i) + "/" + str(len(names)) + "] " + names[i] + " = ERROR")
                bad_cards  = bad_cards + 1
            else:
                print("[" + str(i) + "/" + str(len(names)) + "] " + names[i] + " = SUCCESS")
                good_cards = good_cards + 1

                trading_cards.append(card)

        print("Finished in 'trading_cards' Array!\n" + str(good_cards) + " Good Cards\n" + str(bad_cards) + " Bad Cards\nNow saving JSON....")
        json_output = jsonpickle.encode(trading_cards, unpicklable=False)
        json_output_pickle = jsonpickle.encode(trading_cards, unpicklable=True)
        write('cards.json', json_output)
        write('cards_pickle.json', json_output_pickle)
        print("Finished!")

loop = asyncio.get_event_loop()
loop.run_until_complete(Start())
loop.close()
