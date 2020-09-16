import os
import random
from discord.ext import commands, tasks
from scraping import get_product_info_flipkart
import sqlite3
from discord.utils import find

TOKEN = "NzUxNDAyNzYxNzg2MjI4NzY4.X1IkWg.VdNrZeITZm6w3Z0D3hSuCj4DzL8"

bot = commands.Bot(command_prefix='sb!')

bot.remove_command("help")


@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('Hello {}!'.format(guild.name))
        await general.send("**This is a bot used to track products' price and stock status on flipkart.**\nUsage:`sb!<command>`\nValid Commands:\n\n1.`sb!add` *<link to product on flipkart>.*\n2.`sb!remove` *(To stop tracking of a product)*\n3.`sb!list` *(To list all the products you are tracking.)*\n4.`sb!check_now` *(To check the price and stock status at that moment)*\n\n**The bot will track the product every 6 hours.**\n")
        await general.send("__**Use sb!add <flipkart link> to get started.**__\nThe Bot will dm you instead of replying on server.")


@bot.command(name='help')
async def help(ctx):
    await ctx.message.author.send("**This is the bot used to track products' price and stock status on flipkart.**\n\nUsage:`sb!<command>`\n\nValid Commands:\n\n1.`sb!add` *<link to product on flipkart>.*\n2.`sb!remove` *(To stop tracking of a product)*\n3.`sb!list` *(To list all the products you are tracking.)*\n4.`sb!check_now` *(To check the price and stock status at that moment)*\n\n**The bot will track the product every 6 hours.**\n")


def gather_name_list(user_id):
    conn = sqlite3.connect("discord_tracking.db")
    c = conn.cursor()

    table_name = "_" + str(user_id)

    c.execute(
        'create table if not exists ' + table_name + ' (link text,name text,price_with_currency text,price real,in_stock text)')
    c.execute('SELECT * FROM ' + table_name)
    lis = c.fetchall()
    product_names = []
    for j in lis:
        product_names.append(j[1])
    print(product_names)
    product_names.sort()
    list_message = "__**You are tracking the following products:**__\n\n**"
    for i in enumerate(product_names):
        list_message += str(i[0] + 1) + ". " + i[1] + "\n\n"
    list_message = list_message.strip() + "**"
    conn.commit()
    conn.close()
    return (list_message, product_names)


@bot.command(name='add')
async def add(ctx, link: str = ''):
    # print(ctx.args)
    print(link)
    if link == '':
        await ctx.message.author.send(
            "Please enter a flipkart product link.\nEnter `sb!help` command to view all commands")
        return

    if "flipkart.com" not in link:
        await ctx.message.author.send("`" + link + "`\n **Doesn't seem to be a valid flipkart link**")
        return
    conn = sqlite3.connect('discord_tracking.db')
    c = conn.cursor()

    table_name = "_" + str(ctx.message.author.id)
    c.execute(
        'create table if not exists ' + table_name + ' (link text,name text,price_with_currency text,price real,in_stock text)')
    try:
        # {"name":"product_name"}
        product_info = get_product_info_flipkart(link)

    except IndexError:
        await ctx.message.author.send("`" + link + "`** is not a link to any product.**\n*Enter `sb!help` to view all commands and their formats.*")
        return

    c.execute('SELECT * FROM ' + table_name +
              ' WHERE name=?', (product_info["name"],))
    match = c.fetchone()

    if match:
        await ctx.message.author.send("You are already tracking **" + match[1] + "**")
    else:
        c.execute('INSERT INTO ' + table_name + ' values (?,?,?,?,?)', (link,
                                                                        product_info['name'], product_info["price_with_currency"], product_info["price_in_num"], product_info['availability']))

        await ctx.message.author.send("You just added **" + product_info["name"] + "** for tracking.\n```Currently:\n   Price:" + product_info["price_with_currency"].rjust(10) + "\nIn Stock:" + product_info["availability"].rjust(10) + "```")

    conn.commit()
    conn.close()


@bot.command(name='list')
async def list_names(ctx):
    list_message, product_names = gather_name_list(ctx.message.author.id)
    if len(product_names) == 0:
        await ctx.message.author.send("**You are not tracking any items.**")
        return
    await ctx.message.author.send(list_message)


@bot.command(name='remove')
async def remove(ctx, num: int = 0):
    list_message, product_names = gather_name_list(ctx.message.author.id)
    if len(product_names) == 0:
        await ctx.message.author.send("**You are not tracking any items**")
        return
    if not num:
        await ctx.message.author.send(list_message)
        await ctx.message.author.send(
            "\n*Select the product to remove*.\n**Enter `sb!remove <no. corresponding to the product>` to remove the product.**")
        return

    if num > len(product_names) or num < 0:
        await ctx.message.author.send("**No product with that number.**")
        return

    conn = sqlite3.connect("discord_tracking.db")
    c = conn.cursor()
    table_name = "_" + str(ctx.message.author.id)
    c.execute("DELETE FROM " + table_name +
              " WHERE name=?", (product_names[num - 1],))
    await ctx.message.author.send("You removed **" + product_names[num - 1] + "** from tracking.")
    conn.commit()
    conn.close()


@tasks.loop(hours=6.0)
async def daily_checker():
    conn = sqlite3.connect("discord_tracking.db")
    c = conn.cursor()
    c.execute('SELECT name from sqlite_master where type= "table"')
    all_users = c.fetchall()
    for j in all_users:    # send_changes(int(i[0][1:]))
        c.execute("SELECT * FROM "+j[0])
        all_items = c.fetchall()

        user = bot.get_user(int(j[0][1:]))
        print("Doing "+str(user)+"'s Tracking.")
        # print(dic)
        for i in all_items:
            dic = get_product_info_flipkart(i[0])
            # print(dic)
            current_price = dic['price_in_num']
            current_in_stock = dic['availability']
            price_change = current_price - i[3]
            # price_change= -1000
            # print(dic['name'])
            if price_change > 0:
                await user.send("**"+dic['name']+"**:\n"+"*6 hours back*:\n```   Price:"+i[2].rjust(10)+"\nIn Stock:"+i[4].rjust(10)+"```\n*Now*:\n```   Price:"+dic["price_with_currency"].rjust(10)+"\nIn Stock:"+dic["availability"].rjust(10)+"```")
                await user.send("```diff\n-Price has increased by "+dic["price_with_currency"][0]+str(price_change)+"```")

            elif price_change < 0:
                await user.send("**"+dic['name']+"**:\n"+"*6 hours back*:\n```   Price:"+i[2].rjust(10)+"\nIn Stock:"+i[4].rjust(10)+"```\n*Now*:\n```   Price:"+dic["price_with_currency"].rjust(10)+"\nIn Stock:"+dic["availability"].rjust(10)+"```")
                await user.send("```yaml\nPrice has decreased by "+dic["price_with_currency"][0]+str(abs(price_change))+"```")
            else:
                print("No change in price for "+dic['name'])

            if dic['availability'] == 'Yes' and i[4] == 'No':
                if price_change != 0:
                    await user.send("```yaml\nProduct is in stock.```")
                else:
                    await user.send("**"+dic['name']+"**:\n"+"*6 hours back*:\n```   Price:"+i[2].rjust(10)+"\nIn Stock:"+i[4].rjust(10)+"```\n*Now*:\n```   Price:"+dic["price_with_currency"].rjust(10)+"\nIn Stock:"+dic["availability"].rjust(10)+"```")
                    await user.send("```yaml\nProduct is in stock.```")
            if price_change < 0 and dic['availability'] == "No":
                await user.send("```diff\n-But the product is out of stock.```")

            if price_change != 0:
                await user.send("*Link:*\n"+i[0])
            # Updating the database with the current values.
            c.execute("UPDATE "+j[0]+" SET price_with_currency='" +
                      dic['price_with_currency']+"' WHERE link=?", (i[0],))
            c.execute("UPDATE "+j[0]+" SET price=" +
                      str(dic["price_in_num"])+" WHERE link=?", (i[0],))
            c.execute("UPDATE "+j[0]+" SET in_stock='" +
                      dic["availability"]+"' WHERE link=?", (i[0],))
    conn.commit()
    conn.close()


@bot.command(name="check_now")
async def check_now(ctx, num: int = 0):
    conn = sqlite3.connect("discord_tracking.db")
    c = conn.cursor()
    table_name = "_"+str(ctx.message.author.id)
    c.execute('create table if not exists ' + table_name +
              ' (link text,name text,price_with_currency text,price real,in_stock text)')
    c.execute("SELECT * FROM "+table_name)
    all_items = c.fetchall()
    user = bot.get_user(ctx.message.author.id)
    print("Doing "+str(user)+"'s Tracking.")
    if num == 0:
        message = "__**You are tracking the following items.**__\n"
        for j in enumerate(all_items):
            message += str(j[0]+1)+". "+j[1][1]+"\n\n"
        message += "-1. All Items\n" + \
            "Enter `sb!check_now <no. corresponding to product>` to check that product."
        await user.send(message)
    else:
        if num > len(all_items) or num < -2:
            await user.send("**No Product with that number.**")
            return
        else:
            if num == -1:
                for i in all_items:
                    dic = get_product_info_flipkart(i[0])
                    current_price = dic['price_in_num']
                    current_in_stock = dic['availability']
                    await user.send("**"+dic['name']+"**:\n"+"*Last Time Checked*:\n```   Price:"+i[2].rjust(10)+"\nIn Stock:"+i[4].rjust(10)+"```\n*Now*:\n```   Price:"+dic["price_with_currency"].rjust(10)+"\nIn Stock:"+dic["availability"].rjust(10)+"```"+"*Link:*\n"+i[0])
                    # await user.send()
            else:
                dic = get_product_info_flipkart(all_items[num-1][0])
                current_price = dic['price_in_num']
                current_in_stock = dic['availability']
                await user.send("**"+dic['name']+"**:\n"+"*Last Time Checked*:\n```   Price:"+all_items[num-1][2].rjust(10)+"\nIn Stock:"+all_items[num-1][4].rjust(10)+"```\n*Now*:\n```   Price:"+dic["price_with_currency"].rjust(10)+"\nIn Stock:"+dic["availability"].rjust(10)+"```"+"*Link:*\n"+all_items[num-1][0])


@daily_checker.before_loop
async def before_daily_checker():
    print("waiting")
    await bot.wait_until_ready()

daily_checker.start()
bot.run(TOKEN)
