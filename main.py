import time
import schedule
import asyncio


from kraken.kraken_bot import kraken_arb


async def bot():
    await kraken_arb()
    





# Schedule the trading logic to run at regular intervals
schedule.every(28).seconds.do(bot)
        
        
# Run the trading logic continuously
while True:
    try:
        schedule.run_pending()
        asyncio.run(bot())
        time.sleep(1)
    except Exception as e:
        print('An error occurred:', str(e))
        time.sleep(30)
        
        
