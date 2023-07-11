<!-- This note explains each functions in this codebase -->

### Kraven folder
- `arbitrage.py`: This file contains all the functions that -> 
    1. fetches the list of token pairs that exists on KRAKEN - `get_coins_list`
    2. Structure the fetched token pairs into Triangualar pairs (E.g A Triangular pair is like this: [USDT/EUR,XTZ/EUR,XTZ/USDT]) - `structure_triangular_pairs(coin_list)` (Takes in a list of the fetched token pairs from Kraken exchange)
    3. Takes in a each structured triangular Pair, and fecthes their bid and ask prices `get_price_for_t_pair(t_pair)`
    4. Coverts a USD to a particular token `convert_from_usd(symbol, amount, fee_percent=0.24)`
    5. Coverts a token to to USD `convert_to_usd(acquired_token, symbol, fee_percent=0.24)`
    6. Calculates the value of a symbol (e.g BTC/USD) after fee has been paid (Kraken charges 0.24% on each Order) `amount_after_fee`
    7. Calculates and returns the surface rate opportunity based on the triangular pairs `calc_triangular_arb_surface_rate(t_pair, prices_dict, starting_amount)`
    