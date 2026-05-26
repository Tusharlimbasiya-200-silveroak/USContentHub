import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_helper import create_article

create_article({
    'title': 'Technical Analysis 101: How to Read Stock Charts Like a Pro',
    'slug': 'technical-analysis-101-read-stock-charts',
    'meta_description': 'Learn the fundamentals of technical analysis — chart types, trends, indicators, and patterns that help traders predict price movements and time entries.',
    'keywords': 'technical analysis for beginners, how to read stock charts, chart patterns trading, stock chart analysis',
    'word_count': 1180,
    'read_time': 5,
    'tags': ['technical-analysis', 'trading', 'stocks'],
    'body_html': '''
<p>Technical analysis is the study of price charts to predict future price movements. While fundamental analysis asks "what should I buy?", technical analysis answers "when should I buy it?" Every serious trader needs both — but technical analysis is your edge for timing entries and exits.</p>

<h2>The Three Core Principles</h2>
<p>Technical analysis is built on three assumptions:</p>
<ol>
<li><strong>Price discounts everything.</strong> All known information — earnings, news, sentiment — is already reflected in the stock price. You don't need to know WHY a stock is moving, only THAT it's moving.</li>
<li><strong>Prices move in trends.</strong> Once a trend starts, it's more likely to continue than reverse. Your job is to identify the trend and trade with it.</li>
<li><strong>History repeats itself.</strong> Patterns that worked in the past tend to work again because human psychology doesn't change. Fear and greed create the same chart patterns decade after decade.</li>
</ol>

<h2>Chart Types You Need to Know</h2>
<p><strong>Line Chart:</strong> Connects closing prices with a simple line. Good for seeing the big picture trend, but hides important intraday information.</p>
<p><strong>Bar Chart (OHLC):</strong> Shows Open, High, Low, and Close for each time period. More detailed than line charts but harder to read quickly.</p>
<p><strong>Candlestick Chart:</strong> The gold standard for traders. Each "candle" shows the open, high, low, and close with a colored body:</p>
<ul>
<li><strong>Green/White candle:</strong> Close was higher than open (bullish — price went up)</li>
<li><strong>Red/Black candle:</strong> Close was lower than open (bearish — price went down)</li>
<li><strong>Wicks/Shadows:</strong> The thin lines above and below show the high and low of the period</li>
<li><strong>Body size:</strong> Large bodies = strong conviction. Small bodies = indecision.</li>
</ul>

<h2>Understanding Trends</h2>
<p>Every stock is in one of three states:</p>
<ul>
<li><strong>Uptrend:</strong> Higher highs and higher lows. Buy dips to support levels.</li>
<li><strong>Downtrend:</strong> Lower highs and lower lows. Sell rallies to resistance levels or stay away.</li>
<li><strong>Sideways (Range):</strong> Price bouncing between support and resistance. Trade the range or wait for a breakout.</li>
</ul>
<p><strong>The most important rule in trading: trade WITH the trend, not against it.</strong> The saying "the trend is your friend" exists for a reason. Fighting the trend is how most beginners blow their accounts.</p>

<h2>Support and Resistance</h2>
<p>These are the most fundamental concepts in technical analysis:</p>
<ul>
<li><strong>Support:</strong> A price level where buyers consistently step in. Think of it as a "floor" — the price bounces off it. The more times a support level holds, the stronger it becomes.</li>
<li><strong>Resistance:</strong> A price level where sellers consistently appear. Think of it as a "ceiling" — the price gets rejected here. Once resistance is broken, it often becomes new support.</li>
</ul>
<p>How to identify them:</p>
<ol>
<li>Look for price levels where the stock has bounced or reversed multiple times</li>
<li>Round numbers ($50, $100, $200) often act as psychological support/resistance</li>
<li>Previous highs become resistance; previous lows become support</li>
<li>High-volume price levels are stronger than low-volume ones</li>
</ol>

<h2>Essential Indicators for Beginners</h2>
<p>Indicators are mathematical calculations plotted on charts. Start with these three:</p>

<p><strong>1. Moving Averages (MA)</strong></p>
<ul>
<li>Smooths price data to show the trend direction</li>
<li><strong>50-day MA:</strong> Medium-term trend. Price above = bullish; below = bearish.</li>
<li><strong>200-day MA:</strong> Long-term trend. Institutional investors watch this closely.</li>
<li><strong>Golden Cross:</strong> 50-day crosses above 200-day = strong bullish signal</li>
<li><strong>Death Cross:</strong> 50-day crosses below 200-day = strong bearish signal</li>
</ul>

<p><strong>2. Volume</strong></p>
<ul>
<li>Volume confirms price moves. A breakout on high volume is more likely to hold than one on low volume.</li>
<li>Rising price + rising volume = healthy trend</li>
<li>Rising price + declining volume = weakening trend (potential reversal coming)</li>
<li>Volume spikes often mark trend reversals or the start of new trends</li>
</ul>

<p><strong>3. RSI (Relative Strength Index)</strong></p>
<ul>
<li>Oscillates between 0 and 100</li>
<li><strong>Above 70:</strong> Overbought — stock may be due for a pullback</li>
<li><strong>Below 30:</strong> Oversold — stock may be due for a bounce</li>
<li>Best used in combination with support/resistance, not as a standalone signal</li>
<li><strong>Divergence:</strong> When RSI makes a lower high while price makes a higher high = bearish warning sign</li>
</ul>

<h2>Timeframes Matter</h2>
<p>The same stock can look bullish on one timeframe and bearish on another:</p>
<ul>
<li><strong>1-minute, 5-minute:</strong> Day trading. Very noisy, requires fast decisions.</li>
<li><strong>15-minute, 1-hour:</strong> Day trading and swing trading. Smoother than lower timeframes.</li>
<li><strong>Daily:</strong> Swing trading. The most commonly used timeframe for individual traders.</li>
<li><strong>Weekly, Monthly:</strong> Position trading and investing. Shows the big picture.</li>
</ul>
<p><strong>Pro tip:</strong> Always check the higher timeframe first. If the weekly chart is in a downtrend, buying on a daily chart pullback is risky — you're fighting the bigger trend.</p>

<h2>Common Beginner Mistakes with Charts</h2>
<ol>
<li><strong>Using too many indicators:</strong> 2-3 indicators is enough. More creates "analysis paralysis" and contradictory signals.</li>
<li><strong>Ignoring volume:</strong> Price without volume context is incomplete information.</li>
<li><strong>Looking for perfection:</strong> No pattern works 100% of the time. Technical analysis is about probabilities, not certainties.</li>
<li><strong>Forcing trades:</strong> If the chart isn't clear, don't trade. The best traders are patient — they wait for high-probability setups.</li>
<li><strong>Ignoring the bigger trend:</strong> A bullish pattern in a bearish market often fails. Always check the higher timeframe.</li>
</ol>

<div class="key-takeaway"><strong>🎯 Key Takeaway:</strong> Master candlestick charts first — they give you the most information per candle. Learn to identify trends (higher highs/lows = up, lower highs/lows = down), mark support and resistance levels, and use three indicators maximum (moving averages, volume, and RSI). Always check the higher timeframe before trading, and remember: technical analysis gives you probabilities, not guarantees. Start by studying charts for 30 minutes daily before placing any trades.</div>
'''
})

print('\\n✅ Article 2 done: Technical Analysis 101')
