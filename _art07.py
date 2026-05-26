import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_helper import create_article

create_article({
    'title': 'Forex Trading Basics: Currency Pairs, Pips, and How to Start',
    'slug': 'forex-trading-basics-currency-pairs-pips',
    'meta_description': 'A beginner-friendly guide to forex trading. Learn how currency pairs work, what pips and lots are, how leverage works, and how to start trading forex in 2026.',
    'keywords': 'forex trading for beginners, what are pips forex, currency pairs explained, how to trade forex',
    'word_count': 1100,
    'read_time': 5,
    'tags': ['forex', 'trading'],
    'body_html': '''
<p>The forex (foreign exchange) market is the largest financial market in the world — over $7.5 trillion traded daily. Unlike the stock market, forex trades 24 hours a day, 5 days a week. It's where currencies are exchanged, and it offers unique opportunities for traders who understand how it works.</p>

<h2>How Forex Trading Works</h2>
<p>In forex, you always trade currencies in <strong>pairs</strong>. When you buy one currency, you're simultaneously selling another.</p>
<p>Example: EUR/USD = 1.0850</p>
<ul>
<li><strong>EUR</strong> is the base currency (first)</li>
<li><strong>USD</strong> is the quote currency (second)</li>
<li>The price means 1 euro costs 1.0850 US dollars</li>
<li>If you "buy" EUR/USD, you're betting the euro will strengthen against the dollar</li>
<li>If you "sell" EUR/USD, you're betting the dollar will strengthen against the euro</li>
</ul>

<h2>Major Currency Pairs</h2>
<p>Start with the majors — they have the tightest spreads and most liquidity:</p>
<ul>
<li><strong>EUR/USD:</strong> Euro vs US Dollar — the most traded pair in the world</li>
<li><strong>GBP/USD:</strong> British Pound vs US Dollar — called "Cable"</li>
<li><strong>USD/JPY:</strong> US Dollar vs Japanese Yen</li>
<li><strong>USD/CHF:</strong> US Dollar vs Swiss Franc</li>
<li><strong>AUD/USD:</strong> Australian Dollar vs US Dollar — commodity-linked</li>
<li><strong>USD/CAD:</strong> US Dollar vs Canadian Dollar — oil-influenced</li>
</ul>
<p><strong>Tip:</strong> As a beginner, stick to EUR/USD and GBP/USD. They're the most liquid, have the tightest spreads, and the most predictable behavior.</p>

<h2>Understanding Pips</h2>
<p>A <strong>pip</strong> (percentage in point) is the smallest standard price movement in forex — the fourth decimal place for most pairs.</p>
<ul>
<li>EUR/USD moves from 1.0850 to 1.0851 = 1 pip move</li>
<li>EUR/USD moves from 1.0850 to 1.0900 = 50 pip move</li>
<li>Exception: JPY pairs use 2 decimal places (USD/JPY moves from 155.50 to 155.51 = 1 pip)</li>
</ul>

<p><strong>What's a pip worth?</strong></p>
<ul>
<li><strong>Standard lot</strong> (100,000 units): 1 pip = $10</li>
<li><strong>Mini lot</strong> (10,000 units): 1 pip = $1</li>
<li><strong>Micro lot</strong> (1,000 units): 1 pip = $0.10</li>
</ul>
<p>Most beginners should trade micro or mini lots to keep risk manageable.</p>

<h2>Leverage: The Double-Edged Sword</h2>
<p>Forex brokers offer leverage — the ability to control large positions with small amounts of money. US brokers offer up to 50:1 leverage for major pairs.</p>
<p><strong>Example with 50:1 leverage:</strong></p>
<ul>
<li>You deposit $1,000</li>
<li>You can control a position worth $50,000</li>
<li>A 1% move in your favor = $500 profit (50% return on your $1,000)</li>
<li>A 1% move against you = $500 loss (50% of your capital — gone)</li>
</ul>
<p><strong>Critical rule:</strong> Just because you CAN use 50:1 leverage doesn't mean you should. Experienced forex traders typically use 5:1 to 10:1 effective leverage. Beginners should use 2:1 to 3:1 maximum.</p>

<h2>Forex Trading Sessions</h2>
<p>The forex market trades 24/5, but not all hours are equal:</p>
<ul>
<li><strong>Sydney Session:</strong> 5 PM – 2 AM ET — lowest volume, smallest moves</li>
<li><strong>Tokyo Session:</strong> 7 PM – 4 AM ET — moderate volume, JPY pairs most active</li>
<li><strong>London Session:</strong> 3 AM – 12 PM ET — highest volume session, GBP and EUR pairs move the most</li>
<li><strong>New York Session:</strong> 8 AM – 5 PM ET — second highest volume, USD pairs dominate</li>
<li><strong>London-New York Overlap (8 AM – 12 PM ET):</strong> The most active period — best time to trade</li>
</ul>

<h2>What Moves Currency Prices?</h2>
<ul>
<li><strong>Interest rates:</strong> Higher rates attract foreign capital → currency strengthens. Central bank decisions (Fed, ECB, BOJ) are the biggest movers.</li>
<li><strong>Economic data:</strong> GDP, employment reports, inflation (CPI), manufacturing data</li>
<li><strong>Geopolitical events:</strong> Wars, elections, trade agreements, sanctions</li>
<li><strong>Risk sentiment:</strong> In "risk-off" environments, traders flock to safe havens (USD, JPY, CHF). In "risk-on," they buy commodity currencies (AUD, NZD, CAD).</li>
</ul>

<h2>Getting Started: Step by Step</h2>
<ol>
<li><strong>Choose a regulated US broker:</strong> OANDA, Forex.com (GAIN Capital), or Interactive Brokers. Avoid unregulated offshore brokers.</li>
<li><strong>Open a demo account:</strong> Practice with virtual money for at least 2-3 months</li>
<li><strong>Learn 1-2 pairs:</strong> Focus on EUR/USD to start. Understand its behavior, typical daily range, and what moves it.</li>
<li><strong>Start with micro lots:</strong> When you go live, trade the smallest size possible. A micro lot risks about $0.10 per pip.</li>
<li><strong>Use proper risk management:</strong> Risk 1% per trade maximum. Set stop-losses on every position.</li>
<li><strong>Keep a trading journal:</strong> Record every trade — entry, exit, reason, result, and what you learned.</li>
</ol>

<h2>Forex vs Stocks: Key Differences</h2>
<table>
<thead><tr><th>Factor</th><th>Forex</th><th>Stocks</th></tr></thead>
<tbody>
<tr><td>Market hours</td><td>24/5</td><td>9:30 AM – 4 PM ET</td></tr>
<tr><td>Leverage (US)</td><td>Up to 50:1</td><td>Up to 2:1 (4:1 day trading)</td></tr>
<tr><td>Minimum to start</td><td>$50-$100</td><td>$0 (no minimum)</td></tr>
<tr><td>Number of instruments</td><td>~50 main pairs</td><td>5,000+ stocks</td></tr>
<tr><td>What you trade</td><td>Currencies</td><td>Company ownership</td></tr>
<tr><td>Dividends</td><td>No (swap rates)</td><td>Yes</td></tr>
</tbody>
</table>

<div class="key-takeaway"><strong>🎯 Key Takeaway:</strong> Forex trading is currency pair trading — buying one currency while selling another. Start with EUR/USD, use micro lots to keep risk tiny, and limit leverage to 2:1-3:1 even though brokers offer 50:1. Trade during the London-New York overlap (8 AM–12 PM ET) for the best moves. Demo trade for 2-3 months before going live, use a regulated US broker (OANDA, Forex.com, or IBKR), and never risk more than 1% per trade. Forex rewards patience and discipline above all.</div>
'''
})

print('\\n✅ Article 7 done: Forex Trading Basics')
