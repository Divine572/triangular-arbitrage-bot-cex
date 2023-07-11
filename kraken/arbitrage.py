import ccxt.async_support as ccxt



kraken = ccxt.kraken()



# Fees - 0.24% - Taker


# Get coins List on Kraken
async def get_coins_list():
    tickers = await kraken.fetch_tickers()
    coins_list = []
    for symbol, values in tickers.items():
        ask = values.get('ask')
        bid = values.get('bid')
        if ask == None or bid == None:
            continue
        coins_list.append(symbol)
        
    await kraken.close()
        
    return coins_list


# Structure Arbitrage Pairs
def structure_triangular_pairs(coin_list):
    # Declare Variables
    triangular_pairs_list = []
    remove_duplicates_list = []
    pairs_list = coin_list[0:]

    # Get Pair A
    for pair_a in pairs_list:
        pair_a_split = pair_a.split('/')
        if len(pair_a_split) != 2:
            continue
        
        a_base = pair_a_split[0]
        a_quote = pair_a_split[1]
        
        # Assign A to a Box
        a_pair_box = [a_base, a_quote]

        # Get Pair B
        for pair_b in pairs_list:
            pair_b_split = pair_b.split("/")
            if len(pair_b_split) != 2:
                continue
            b_base = pair_b_split[0]
            b_quote = pair_b_split[1]

            # Check Pair B
            if pair_b != pair_a:
                if b_base in a_pair_box or b_quote in a_pair_box:

                    # Get Pair C
                    for pair_c in pairs_list:
                        pair_c_split = pair_c.split("/")
                        if len(pair_c_split) != 2:
                            continue
                        c_base = pair_c_split[0]
                        c_quote = pair_c_split[1]

                        # Count the number of matching C items
                        if pair_c != pair_a and pair_c != pair_b:
                            combine_all = [pair_a, pair_b, pair_c]
                            pair_box = [a_base, a_quote, b_base, b_quote, c_base, c_quote]

                            counts_c_base = 0
                            for i in pair_box:
                                if i == c_base:
                                    counts_c_base += 1

                            counts_c_quote = 0
                            for i in pair_box:
                                if i == c_quote:
                                    counts_c_quote += 1

                            # Determining Triangular Match
                            if counts_c_base == 2 and counts_c_quote == 2 and c_base != c_quote:
                                combined = pair_a + "," + pair_b + "," + pair_c
                                unique_item = "".join(sorted(combine_all))
                                if unique_item not in remove_duplicates_list:
                                    match_dict = {
                                        "a_base": a_base,
                                        "b_base": b_base,
                                        "c_base": c_base,
                                        "a_quote": a_quote,
                                        "b_quote": b_quote,
                                        "c_quote": c_quote,
                                        "pair_a": pair_a,
                                        "pair_b": pair_b,
                                        "pair_c": pair_c,
                                        "combined": combined
                                    }

                                    triangular_pairs_list.append(match_dict)
                                    remove_duplicates_list.append(unique_item)
        
    return triangular_pairs_list         
        
        
        
# Structure Prices
async def get_price_for_t_pair(t_pair):
    
    prices_json = await kraken.fetch_tickers()
    
    # Extract pair info
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]
    
    
    
    # Extract price info for given pairs
    pair_a_ask = float(prices_json[pair_a]["ask"])
    pair_a_bid = float(prices_json[pair_a]["bid"])
    pair_b_ask = float(prices_json[pair_b]["ask"])
    pair_b_bid = float(prices_json[pair_b]["bid"])
    pair_c_ask = float(prices_json[pair_c]["ask"])
    pair_c_bid = float(prices_json[pair_c]["bid"])
    
    await kraken.close()
    
    # Output dictionary
    return {
        "pair_a_ask": pair_a_ask,
        "pair_a_bid": pair_a_bid,
        "pair_b_ask": pair_b_ask,
        "pair_b_bid": pair_b_bid,
        "pair_c_ask": pair_c_ask,
        "pair_c_bid": pair_c_bid,
    }
    
    



async def convert_from_usd(symbol, amount, fee_percent=0.24):
    """
        Used when buying a token from USD
    """
    ticker = await kraken.fetch_ticker(symbol=symbol)
    fee = amount * (fee_percent / 100) # Calculate the fee
    amount_after_fee = amount - fee    # Deduct the fee from the original amount
    converted_token = amount_after_fee * (1 / ticker['ask'])  # Use 'ask' when buying
    await kraken.close()
    return converted_token



async def convert_to_usd(acquired_token, symbol, fee_percent=0.24):
    """
        Used when selling a token for USD  
    """
    ticker = await kraken.fetch_ticker(symbol=symbol)
    usd_amount_before_fee = acquired_token * ticker['bid']  # Use 'bid' when selling
    fee = usd_amount_before_fee * (fee_percent / 100) # Calculate the fee
    usd_amount_after_fee = usd_amount_before_fee - fee  # Deduct the fee from the total
    await kraken.close()
    return usd_amount_after_fee


def amount_after_fee(acquired_token, fee_percent=0.24):
    """
        Calculates the fees on a particular token
    """
    fee = acquired_token * (fee_percent / 100) # Calculate the fee
    amount_after_fee = acquired_token - fee  # Deduct the fee from the total
    return amount_after_fee



# Calculate Surface Rate Arbitrage Opportunity
async def calc_triangular_arb_surface_rate(t_pair, prices_dict, starting_amount):

    # Set Variables
    fee_percent=0.24
    starting_amount_in_usd = starting_amount
    min_surface_rate = 0
    surface_dict = {}
    contract_2 = ""
    contract_3 = ""
    direction_trade_1 = ""
    direction_trade_2 = ""
    direction_trade_3 = ""
    acquired_coin_t2 = 0
    acquired_coin_t3 = 0
    calculated = 0

    # Extract Pair Variables
    a_base = t_pair["a_base"]
    a_quote = t_pair["a_quote"]
    b_base = t_pair["b_base"]
    b_quote = t_pair["b_quote"]
    c_base = t_pair["c_base"]
    c_quote = t_pair["c_quote"]
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]

    # Extract Price Information
    a_ask = prices_dict["pair_a_ask"]
    a_bid = prices_dict["pair_a_bid"]
    b_ask = prices_dict["pair_b_ask"]
    b_bid = prices_dict["pair_b_bid"]
    c_ask = prices_dict["pair_c_ask"]
    c_bid = prices_dict["pair_c_bid"]

    # Guard - return zero if non divisible items
    if a_ask == 0 or a_bid == 0 or b_ask == 0 or b_bid == 0 or c_ask == 0 or c_bid == 0:
        return []
        
    

    # Set directions and loop through
    direction_list = ["forward", "reverse"]
    for direction in direction_list:

        # Set additional variables for swap information
        swap_1 = 0
        swap_2 = 0
        swap_3 = 0
        swap_1_rate = 0
        swap_2_rate = 0
        swap_3_rate = 0


        """
            If we are swapping the coin on the left (Base) to the right (Quote) then * (1 / Ask)
            If we are swapping the coin on the right (Quote) to the left (Base) then * Bid
        """

        # Assume starting with a_base and swapping for a_quote
        if direction == "forward":
            swap_1 = a_base
            swap_2 = a_quote
            swap_1_rate = 1 / a_ask
            direction_trade_1 = "base_to_quote"

        # Assume starting with a_base and swapping for a_quote
        if direction == "reverse":
            swap_1 = a_quote
            swap_2 = a_base
            swap_1_rate = a_bid
            direction_trade_1 = "quote_to_base"

        # ***************** Token Coversion before First Trade *******************
        
        pair_a_split = pair_a.split('/')
        if direction_trade_1 == "base_to_quote" and pair_a_split[0] != "USD":
            symbol = f"{pair_a_split[0]}/USD"
            starting_amount = await convert_from_usd(symbol=symbol, amount=starting_amount, fee_percent=fee_percent)
        if direction_trade_1 == "quote_to_base" and pair_a_split[1] != "USD":
            symbol = f"{pair_a_split[1]}/USD"
            starting_amount = await convert_from_usd(symbol=symbol, amount=starting_amount, fee_percent=fee_percent)
            
            
        # *************************************************************
            
        # Place first trade
        contract_1 = pair_a
        acquired_coin_t1 = starting_amount * swap_1_rate
        
        
        
        """  FORWARD """
        # SCENARIO 1 Check if a_quote (acquired_coin) matches b_quote
        if direction == "forward":
            if a_quote == b_quote and calculated == 0:
                swap_2_rate = b_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                acquired_coin_t2 = amount_after_fee(acquired_coin_t2, fee_percent)
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_b

                # If b_base (acquired coin) matches c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # If b_base (acquired coin) matches c_quote
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                acquired_coin_t3 = amount_after_fee(acquired_coin_t3, fee_percent)
                calculated = 1

        # SCENARIO 2 Check if a_quote (acquired_coin) matches b_base
        if direction == "forward":
            if a_quote == b_base and calculated == 0:
                swap_2_rate = 1 / b_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                acquired_coin_t2 = amount_after_fee(acquired_coin_t2, fee_percent)
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_b

                # If b_quote (acquired coin) matches c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # If b_quote (acquired coin) matches c_quote
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                acquired_coin_t3 = amount_after_fee(acquired_coin_t3, fee_percent)
                calculated = 1

        # SCENARIO 3 Check if a_quote (acquired_coin) matches c_quote
        if direction == "forward":
            if a_quote == c_quote and calculated == 0:
                swap_2_rate = c_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                acquired_coin_t2 = amount_after_fee(acquired_coin_t2, fee_percent)
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_c

                # If c_base (acquired coin) matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # If c_base (acquired coin) matches b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                acquired_coin_t3 = amount_after_fee(acquired_coin_t3, fee_percent)
                calculated = 1

        # SCENARIO 4 Check if a_quote (acquired_coin) matches c_base
        if direction == "forward":
            if a_quote == c_base and calculated == 0:
                swap_2_rate = 1 / c_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                acquired_coin_t2 = amount_after_fee(acquired_coin_t2, fee_percent)
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_c

                # If c_quote (acquired coin) matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # If c_quote (acquired coin) matches b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                acquired_coin_t3 = amount_after_fee(acquired_coin_t3, fee_percent)
                calculated = 1

        """  REVERSE """
        # SCENARIO 1 Check if a_base (acquired_coin) matches b_quote
        if direction == "reverse":
            if a_base == b_quote and calculated == 0:
                swap_2_rate = b_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                acquired_coin_t2 = amount_after_fee(acquired_coin_t2, fee_percent)
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_b

                # If b_base (acquired coin) matches c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # If b_base (acquired coin) matches c_quote
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                acquired_coin_t3 = amount_after_fee(acquired_coin_t3, fee_percent)
                calculated = 1

        # SCENARIO 2 Check if a_base (acquired_coin) matches b_base
        if direction == "reverse":
            if a_base == b_base and calculated == 0:
                swap_2_rate = 1 / b_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                acquired_coin_t2 = amount_after_fee(acquired_coin_t2, fee_percent)
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_b

                # If b_quote (acquired coin) matches c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # If b_quote (acquired coin) matches c_quote
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                acquired_coin_t3 = amount_after_fee(acquired_coin_t3, fee_percent)
                calculated = 1

        # SCENARIO 3 Check if a_base (acquired_coin) matches c_quote
        if direction == "reverse":
            if a_base == c_quote and calculated == 0:
                swap_2_rate = c_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                acquired_coin_t2 = amount_after_fee(acquired_coin_t2, fee_percent)
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_c

                # If c_base (acquired coin) matches b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # If c_base (acquired coin) matches b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                acquired_coin_t3 = amount_after_fee(acquired_coin_t3, fee_percent)
                calculated = 1

        # SCENARIO 4 Check if a_base (acquired_coin) matches c_base
        if direction == "reverse":
            if a_base == c_base and calculated == 0:
                swap_2_rate = 1 / c_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                acquired_coin_t2 = amount_after_fee(acquired_coin_t2, fee_percent)
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_c

                # If c_quote (acquired coin) matches b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # If c_quote (acquired coin) matches b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                acquired_coin_t3 = amount_after_fee(acquired_coin_t3, fee_percent)
                calculated = 1
                
            
        # ***************** Token Coversion before First Trade *******************
        
        last_pair_split = contract_3.split('/')
        if direction_trade_3 == "base_to_quote" and last_pair_split[0] != "USD":
            symbol = f"{last_pair_split[0]}/USD"
            balance_in_usd = await convert_to_usd(symbol=symbol, acquired_token=acquired_coin_t3, fee_percent=fee_percent)
        if direction_trade_3 == "quote_to_base" and last_pair_split[1] != "USD":
            symbol = f"{last_pair_split[1]}/USD"
            balance_in_usd = await convert_to_usd(symbol=symbol, acquired_token=acquired_coin_t3, fee_percent=fee_percent)
        if swap_3 == "USD":
            balance_in_usd = acquired_coin_t3
            
            
        # *************************************************************
        


        """ PROFIT LOSS OUTPUT """
        
        # Profit and Loss Calculation
        # print(f"Acquired {swap_3} {acquired_coin_t3}")
        # print(f"Starting amount {starting_amount}")
        profit_loss = acquired_coin_t3 - starting_amount
        profit_loss_perc = (profit_loss / starting_amount) * 100 if profit_loss != 0 else 0
        
        
        # Trade Descriptions
        trade_description_1 = f"Start with {swap_1} of {starting_amount}. Swap at {swap_1_rate} for {swap_2} acquiring {acquired_coin_t1}."
        trade_description_2 = f"Swap {acquired_coin_t1} of {swap_2} at {swap_2_rate} for {swap_3} acquiring {acquired_coin_t2}."
        trade_description_3 = f"Swap {acquired_coin_t2} of {swap_3} at {swap_3_rate} for {swap_1} acquiring {acquired_coin_t3}."
        final_description = f"Started with USD of {starting_amount_in_usd} || Balance in USD after Trade {balance_in_usd}"
        
        
        
        # Output Results
        if profit_loss_perc > min_surface_rate:
            
            surface_dict = {
                "exchange": "KRAKEN",
                "swap_1": swap_1,
                "swap_2": swap_2,
                "swap_3": swap_3,
                "contract_1": contract_1,
                "contract_2": contract_2,
                "contract_3": contract_3,
                "direction_trade_1": direction_trade_1,
                "direction_trade_2": direction_trade_2,
                "direction_trade_3": direction_trade_3,
                "starting_amount": starting_amount,
                "acquired_coin_t1": acquired_coin_t1,
                "acquired_coin_t2": acquired_coin_t2,
                "acquired_coin_t3": acquired_coin_t3,
                "swap_1_rate": swap_1_rate,
                "swap_2_rate": swap_2_rate,
                "swap_3_rate": swap_3_rate,
                "profit_loss": profit_loss,
                "profit_loss_perc": profit_loss_perc,
                "direction": direction,
                "trade_description_1": trade_description_1,
                "trade_description_2": trade_description_2,
                "trade_description_3": trade_description_3,
                "final_description": final_description
            }
            
            return surface_dict
    return surface_dict
        



