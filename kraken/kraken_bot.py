import ccxt.async_support as ccxt
import asyncio
import json
import schedule

# from arbitrage import (
#     get_coins_list,
#     structure_triangular_pairs,
#     get_price_for_t_pair,
#     calc_triangular_arb_surface_rate
# )


from kraken import arbitrage 

from signal_messaging import send_signal_message



kraken = ccxt.kraken()


""" Save List of Triangualr Arbitrage Pairs as JSON and run on schedule """
async def save_triangular_pairs():
    coins_list = await arbitrage.get_coins_list()
    structured_list = arbitrage.structure_triangular_pairs(coins_list)
    # Save Structued List 
    with open("structured_triangular_piars.json", "w") as f:
        json.dump(structured_list, f)




""" Calculate Surface Rates & Real Rates of Each Triangular Pair """
async def calc_surface_and_real_rates():
    
    # Get Structured Pairs 
    with open("structured_triangular_piars.json") as json_file:
        structured_pairs = json.load(json_file)
        
    
    # Loop through and get structured price info
    for t_pair in structured_pairs:
        prices_dict = await arbitrage.get_price_for_t_pair(t_pair)        
        surface_rate_arb = await arbitrage.calc_triangular_arb_surface_rate(t_pair, prices_dict, 100)
        if len(surface_rate_arb) > 0:
            print(2 * "\n" + 100* "-")
            print("*************** NEW TRADE SIGNAL (Surface Rate) ✅ *******************")
            print(f' 🟢 {surface_rate_arb["exchange"]} EXCHANGE ARBITRAGE SIGNAL')
            print(f' 🤖 {surface_rate_arb["trade_description_1"]}')
            print(f' 🤖 {surface_rate_arb["trade_description_2"]}')
            print(f' 🤖 {surface_rate_arb["trade_description_3"]}')
            print(f' 🚀 {surface_rate_arb["final_description"]}')
            print(f' ✅ Profit & Loss  -> {surface_rate_arb["profit_loss"]}')
            print(f' ✅ Profit & Loss Percentage -> {surface_rate_arb["profit_loss_perc"]}%')
            print(100 * "-" + "\n")
            


            message = f'*************** NEW TRADE SIGNAL (Surface Rate) ✅ *******************\n'\
            f' 🟢 {surface_rate_arb["exchange"]} EXCHANGE ARBITRAGE SIGNAL\n'\
                    f' 🤖 {surface_rate_arb["trade_description_1"]}\n'\
                        f' 🤖 {surface_rate_arb["trade_description_2"]}\n'\
                        f' 🤖 {surface_rate_arb["trade_description_3"]}\n'\
                            f' 🚀 {surface_rate_arb["final_description"]}\n'\
                                f' ✅ Profit & Loss  -> {surface_rate_arb["profit_loss"]}\n'\
                                    f' ✅ Profit & Loss Percentage -> {surface_rate_arb["profit_loss_perc"]}%\n'\
                                        
            
            send_signal_message(message)
        
        


schedule.every().day.do(save_triangular_pairs)


async def kraken_arb():
    await save_triangular_pairs()
    await calc_surface_and_real_rates()
    

