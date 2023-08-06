import discord
from discord.ext import commands
from discord.flags import Intents
import asyncio
import os
import time
import requests
import json
import bs4
from dotenv import dotenv_values

env = dotenv_values(".env")

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

intents = discord.Intents.all()

times_times_anterior=0

client = commands.Bot(command_prefix = "?", intents=intents,help_command = help_command)

def return_card(nome_da_carta):
    def sub_Basic_land(nome_da_carta):
        basicos = {
            "Planicie": "Plains",
            "Planície": "Plains",
            "Ilha": "Island",
            "Pântano": "Swamp",
            "Pantano": "Swamp",
            "Montanha": "Mountain",
            "Floresta": "Forest",
            "Ermo": "Wastes",
        }
        return basicos.get(nome_da_carta, nome_da_carta)
    url="https://api.scryfall.com/cards/named?fuzzy="+sub_Basic_land(nome_da_carta.replace(":"," ").title()) 
    def rq(url):
        global times_times_anterior
        r = requests.get(url, timeout=None)
        if time.time_ns()-times_times_anterior<100000000:
            time.sleep((time.time_ns()-times_times_anterior)/1000000000)  #https://scryfall.com/docs/api  delay 100ms Rate Limits and Good Citizenship
        times_times_anterior=time.time_ns()
        return r
    r=rq(url)
    card_json=json.loads(r.text)

    url =f"https://api.scryfall.com/cards/search?order=released&q=oracleid%3A{ card_json['oracle_id'] }&unique=prints"
    r=rq(url)
    if r.status_code == requests.codes.OK:
        info_card_prints=json.loads(r.text)
        for cards_english in info_card_prints['data']:
            if (cards_english['image_status'] == "highres_scan"  or cards_english['image_status'] == "lowres" ) and cards_english['lang']=='en' and "paper" in cards_english["games"] and (cards_english["textless"]==False) and (cards_english["set"]!="sld") and (cards_english["set_type"]!="promo")  and (cards_english["set_type"]!="masterpiece")  and (cards_english["promo"]==False) and (cards_english["border_color"]!='borderless'):
                if 'frame_effects' in cards_english:
                    if  'inverted' not in cards_english['frame_effects'] and 'showcase' not in cards_english['frame_effects'] and 'extendedart' not in cards_english['frame_effects'] :
                        card_json=cards_english
                        break
                else:
                    card_json=cards_english
                    break
        else:
            url =f"https://api.scryfall.com/cards/search?order=released&q=oracleid%3A{ card_json['oracle_id'] }&unique=prints"
            r=rq(url)
            if r.status_code == requests.codes.OK:
                card_json=json.loads(r.text)
                card_json=card_json['data'][0]
    return card_json

contador_c_card=0
@client.command(name="card", aliases=['c', 'carta'],help=f"| Procura o card. ?[card | c | carta] Monastery Swiftspear")
async def card(message, *args):
    global contador_c_card
    if message.author == client.user or message.author.bot:
        return 
    nome_da_carta=''
    for i in args:
        nome_da_carta+= i + ' '
    
    card_json=return_card(nome_da_carta)
    mention = message.author.mention
    response = f"""hey {mention}
    **{card_json['name']}**
    -----------------------
    Standard: {card_json['legalities']['standard'].replace("_"," ").title()}
    Pioneer: {card_json['legalities']['pioneer'].replace("_"," ").title()}
    Modern: {card_json['legalities']['modern'].replace("_"," ").title()}
    Legacy: {card_json['legalities']['legacy'].replace("_"," ").title()}
    Pauper: {card_json['legalities']['pauper'].replace("_"," ").title()}
    Vintage: {card_json['legalities']['vintage'].replace("_"," ").title()}
    Penny: {card_json['legalities']['penny'].replace("_"," ").title()}
    Commander: {card_json['legalities']['commander'].replace("_"," ").title()}
    -----------------------
    """
    
    if card_json['layout'] == "transform" or card_json['layout'] == "modal_dfc":

        img_embed=card_json["card_faces"][0]["image_uris"]["png"]
        img_card2=card_json["card_faces"][1]["image_uris"]["png"]

    else:
        img_embed=card_json["image_uris"]["png"]
  
    tix=None
    url =f"https://api.scryfall.com/cards/search?order=released&q=oracleid%3A{ card_json['oracle_id'] }&unique=prints"
    def rq(url):
        global times_times_anterior
        r = requests.get(url, timeout=None)
        if time.time_ns()-times_times_anterior<100000000:
            time.sleep((time.time_ns()-times_times_anterior)/1000000000)  #https://scryfall.com/docs/api  delay 100ms Rate Limits and Good Citizenship
        times_times_anterior=time.time_ns()
        return r
    r=rq(url)
    info_card_prints=json.loads(r.text)
    for cards_english in info_card_prints['data']:
        if cards_english['prices']['tix']!=None:
            if tix==None:
                tix=float(cards_english['prices']['tix'])
            if float(cards_english['prices']['tix'])<tix:
                tix=float(cards_english['prices']['tix'])
    response+=f"""Cardhoarder: {tix}
    """
    
    embed=discord.Embed(color=0x3a40ee,description=response)
    embed.set_image(url=img_embed)
    await message.channel.send(embed=embed)
    embed=discord.Embed(color=0x3a40ee)
    if card_json['layout'] == "transform" or card_json['layout'] == "modal_dfc":
        embed.set_image(url=img_card2)
        await message.channel.send(embed=embed)
    contador_c_card+=1

contador_c_meta=0
@client.command(name="meta", aliases=['m', 'field'],help=f"| Decks do metagame. ?[meta | m | field] [FORMATO] {os.linesep}{os.linesep}[standard | t2 | s | padrao |padrão]{os.linesep}[modern | m | moderno ]{os.linesep}[pioneer | pi | pioneiro]{os.linesep}[historic | h | histórico | historico]{os.linesep}[explorer | e | explorador]{os.linesep}[alchemy | a | alquimia]{os.linesep}[pauper | p | pobre]{os.linesep}[legacy | t1.5 | t1,5 | l | legado]{os.linesep}[vintage | t1 | v]{os.linesep}[penny preadful | pd | penny]{os.linesep}[duel commander | duel | d | cx1 | c1x1 | commander 1v1 | commander 1x1 | commander x1]{os.linesep}[commander | c | edh]{os.linesep}[historic brawl | hb]{os.linesep}[braw | b | briga]")
async def meta(message, *args):
    global contador_c_meta
    if message.author == client.user or message.author.bot:
        return 
    argumento=''
    for i in args:
        argumento+= i + ' '

    def q_formato(arg):
        formatos = {
            't2':'standard',
            'standard':'standard',
            'padrao':'standard',
            'padrão':'standard',
            's':'standard',
            
            'modern':'modern',
            'm':'modern',
            'moderno':'modern',

            'pioneer':'pioneer',
            'pi':'pioneer',
            'pioneiro':'pioneer',

            'historic':'historic',
            'h':'historic',
            'histórico':'historic',
            'historico':'historic',

            'explorer':'explorer',
            'e':'explorer',
            'explorador':'explorer',

            'alchemy':'alchemy',
            'a':'alchemy',
            'alquimia':'alchemy',

            'pauper':'pauper',
            'p':'pauper',
            'pobre':'pauper',

            't1.5':'legacy',
            't1,5':'legacy',
            'legacy':'legacy',
            'l':'legacy',
            'legado':'legacy',

            'vintage':'vintage',
            'v':'vintage',
            't1':'vintage',

            'penny preadful':'penny_dreadful',
            'penny':'penny_dreadful',
            'pd':'penny_dreadful',

            'duel commander':'commander_1v1',
            'duel':'commander_1v1',
            'd':'commander_1v1',
            'cx1':'commander_1v1',
            'c1v1':'commander_1v1',
            'c1x1':'commander_1v1',
            'commander 1v1':'commander_1v1',
            'commander 1x1':'commander_1v1',
            'commander x1':'commander_1v1',

            'commander':'commander',
            'c':'commander',
            'edh':'commander',

            'historic brawl':'historic_brawl',
            'hb':'historic_brawl',

            'braw':'braw',
            'b':'braw',
            'briga':'braw',

        }
        return formatos.get(arg.strip(), arg)
    url =f"https://www.mtggoldfish.com/metagame/{q_formato(argumento.lower())}/full#online"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 OPR/94.0.0.0'}

    res = requests.get(url, headers=headers)
    ObjS=bs4.BeautifulSoup(res.text, 'html.parser')

    mention = message.author.mention
    response = f"""hey {mention}
    **[{q_formato(argumento.lower()).title()} Metagame]({url})**
    -----------------------
    """
    i=0
    for item in ObjS.find_all("div", {"class": "archetype-tile"}):
        decks=[]

        link=item.find_all("a", {"class": "card-image-tile-link-overlay"})[0]['href']
        for item2 in item.find_all("div", {"class": "archetype-tile-description-wrapper"}):
            decks.append(item2.get_text())
        aa=decks[0].split("\n")
        while 1:
            if '' in aa:
                aa.remove("")
            else:
                break     
        response += f"""[{aa[0]} | {aa[6]} | {aa[11]}](http://www.mtggoldfish.com{link})
        """
        i+=1
        if i>30:
            break
    embed=discord.Embed(color=0x3a40ee,description=response)
    await message.channel.send(embed=embed)
    contador_c_meta+=1

@commands.command(name="help",aliases=['ajuda', 'h'],help=f"| Comando de ajuda. ?[help | ajuda | h]")
async def help(message):
    helptxt = ''
    for command in client.commands:
        helptxt += f'**{command}** - {command.help}\n'
    embedhelp = discord.Embed(
        description=helptxt,
        colour = 0x3a40ee,#grey
        title=f'Comandos do {client.user.name}',
        #description = helptxt+'\n[Crie seu próprio Bot de Música](https://youtu.be/YGx0xNHzjgE)'
    )
    #embedhelp.set_thumbnail(url=self.client.user.avatar_url)
    await message.channel.send(embed=embedhelp)
client.run(env['token'])