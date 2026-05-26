import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_helper import create_article

create_article({
    'title': 'Options Trading Explained: Calls, Puts, and Strategies for Beginners',
    'slug': 'options-trading-explained-calls-puts-beginners',
    'meta_description': 'Options trading demystified. Learn what calls and puts are, how they work, basic strategies like covered calls and protective puts, and mistakes beginners make.',
    'keywords': 'options trading for beginners, what are calls and puts, options trading strategies, how to trade options',
    'word_count': 1200,
    'read_time': 5,
    'tags': ['options', 'trading', 'stocks'],
    'body_html': '''
<p>Options trading has a reputation for being complicated and risky. The complicated part is partly true — there's a learning curve. But options aren't inherently riskier than stocks when used correctly. In fact, options can be used to REDUCE risk. Here's everything you need to understand before placing your first options trade.</p>

<h2>What Is an Option?</h2>
<p>An option is a contract that gives you the <strong>right, but not the obligation</strong>, to buy or sell a stock at a specific price by a specific date.</p>
<p>Think of it like a reservation. You pay a small fee (the premium) to reserve the right to buy something at today's price within a set timeframe. If the price goes up, your reservation becomes very valuable. If it doesn't, you only lose the reservation fee.</p>

<h2>Calls vs Puts</h2>
<p><strong>Call Option — Betting the Price Goes UP</strong></p>
<ul>
<li>Gives you the right to BUY 100 shares at the strike price</li>
<li>You buy calls when you're bullish (think the stock will rise)</li>
<li>Example: AAPL is at $200. You buy a $210 call for $3. If AAPL rises to $225, your option is worth at least $15 — a 400% return on your $3 investment.</li>
<li>Maximum loss: the premium you paid ($3 × 100 = $300)</li>
<li>Maximum profit: theoretically unlimited (as high as the stock goes)</li>
</ul>

<p><strong>Put Option — Betting the Price Goes DOWN</strong></p>
<ul>
<li>Gives you the right to SELL 100 shares at the strike price</li>
<li>You buy puts when you're bearish (think the stock will fall)</li>
<li>Example: TSLA is at $250. You buy a $240 put for $5. If TSLA drops to $210, your option is worth at least $30 — a 500% return.</li>
<li>Maximum loss: the premium you paid ($5 × 100 = $500)</li>
<li>Maximum profit: substantial (stock can drop to $0)</li>
</ul>

<h2>Key Options Terms</h2>
<ul>
<li><strong>Strike Price:</strong> The price at which you can buy (call) or sell (put) the stock</li>
<li><strong>Expiration Date:</strong> The date by which you must exercise or the option becomes worthless</li>
<li><strong>Premium:</strong> The price you pay for the option contract</li>
<li><strong>In the Money (ITM):</strong> The option has intrinsic value. For calls: stock price > strike price. For puts: stock price &lt; strike price.</li>
<li><strong>Out of the Money (OTM):</strong> No intrinsic value yet. For calls: stock price &lt; strike price. For puts: stock price > strike price.</li>
<li><strong>At the Money (ATM):</strong> Stock price is right at the strike price</li>
<li><strong>Contract size:</strong> Each option contract controls 100 shares of stock</li>
</ul>

<h2>The Greeks (Simplified)</h2>
<p>The Greeks measure how an option's price changes based on different factors:</p>
<ul>
<li><strong>Delta:</strong> How much the option price moves per $1 move in the stock. Delta of 0.50 means the option gains $0.50 for every $1 the stock moves. Calls have positive delta; puts have negative delta.</li>
<li><strong>Theta:</strong> Time decay — how much value the option loses per day. Options lose value every day, accelerating as expiration approaches. <em>This is why buying options is a race against time.</em></li>
<li><strong>Vega:</strong> How much the option price changes with volatility. Higher volatility = more expensive options. Earnings announcements and news events spike volatility.</li>
<li><strong>Gamma:</strong> Rate of change of delta. Matters most for short-term options near the strike price.</li>
</ul>

<h2>4 Beginner-Friendly Strategies</h2>

<p><strong>1. Buying Calls (Bullish)</strong></p>
<ul>
<li>Simplest options strategy. Buy a call when you think a stock will go up.</li>
<li>Buy 30-60 days until expiration (DTE) to give yourself time</li>
<li>Choose a strike price slightly out of the money for the best risk/reward</li>
<li>Risk: limited to premium paid</li>
</ul>

<p><strong>2. Buying Puts (Bearish or Hedging)</strong></p>
<ul>
<li>Buy a put when you think a stock will drop, or to protect existing stock positions</li>
<li>Acts as insurance — if your stock drops, the put gains value to offset losses</li>
<li>Great for protecting profits before earnings reports or uncertain events</li>
</ul>

<p><strong>3. Covered Call (Income Strategy)</strong></p>
<ul>
<li>Own 100 shares of a stock and sell a call against them</li>
<li>You collect the premium as income</li>
<li>Trade-off: if the stock rockets past your strike price, your upside is capped</li>
<li>Best for: generating monthly income on stocks you plan to hold long-term anyway</li>
<li>Example: Own 100 shares of AAPL at $200. Sell a $215 call for $3. You collect $300 immediately. If AAPL stays below $215, you keep the premium and your shares.</li>
</ul>

<p><strong>4. Protective Put (Insurance)</strong></p>
<ul>
<li>Own shares and buy a put to protect against downside</li>
<li>Sets a "floor" on how much you can lose</li>
<li>Costs money (the put premium) but provides peace of mind</li>
<li>Best for: protecting large gains or hedging before risky events like earnings</li>
</ul>

<h2>Options Mistakes That Destroy Beginners</h2>
<ol>
<li><strong>Buying cheap, far OTM options:</strong> They're cheap for a reason — they almost never hit. You'll win occasionally but lose consistently. Stick to ATM or slightly OTM.</li>
<li><strong>Buying weekly options:</strong> Time decay is brutal on weeklies. Buy 30-60 DTE minimum to give your trade time to work.</li>
<li><strong>Not understanding time decay:</strong> You can be RIGHT about the stock's direction and still LOSE money because theta ate your option's value. Time is always working against option buyers.</li>
<li><strong>Oversizing positions:</strong> An option going to zero means you lose 100%. Never put more than 3-5% of your account in a single options trade.</li>
<li><strong>Holding through earnings without understanding IV crush:</strong> Implied volatility spikes before earnings and crashes after — even if the stock moves your way, IV crush can destroy your option's value.</li>
</ol>

<div class="key-takeaway"><strong>🎯 Key Takeaway:</strong> Options are contracts to buy (calls) or sell (puts) stock at a set price by a set date. Start with simple call buying (bullish) and put buying (bearish/hedging). Use 30-60 days to expiration, choose strikes near the money, and never risk more than 3-5% of your account per trade. Learn the Greeks — especially theta (time decay works against buyers) and delta (tells you how much you'll make per dollar move). Paper trade options for at least a month before using real money.</div>
'''
})

print('\\n✅ Article 6 done: Options Trading Explained')
