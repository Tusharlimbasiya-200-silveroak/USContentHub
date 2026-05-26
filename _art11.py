import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_helper import create_article

create_article({
    'title': 'Moving Averages Explained: SMA vs EMA Trading Strategies',
    'slug': 'moving-averages-sma-vs-ema-trading-strategies',
    'meta_description': 'Learn how to use Simple Moving Average (SMA) and Exponential Moving Average (EMA) for trading — crossover strategies, trend identification, and dynamic support.',
    'keywords': 'moving averages trading, SMA vs EMA, moving average crossover, 50 day moving average, 200 day moving average',
    'word_count': 1000,
    'read_time': 4,
    'tags': ['technical-analysis', 'trading', 'stocks'],
    'body_html': '''
<p>Moving averages are the most widely used indicator in technical analysis. They smooth out price noise, reveal the underlying trend, and generate clear buy/sell signals. If you can only learn one indicator, make it moving averages.</p>

<h2>SMA vs EMA: What's the Difference?</h2>
<p><strong>Simple Moving Average (SMA)</strong></p>
<ul>
<li>Calculates the average closing price over a set number of periods</li>
<li>Example: 20-day SMA = average of the last 20 closing prices</li>
<li>Treats all data points equally — each of the 20 days has the same weight</li>
<li>Smoother, slower to react to price changes</li>
<li>Best for: identifying long-term trends, reducing false signals</li>
</ul>

<p><strong>Exponential Moving Average (EMA)</strong></p>
<ul>
<li>Gives MORE weight to recent prices, less to older ones</li>
<li>Example: 20-day EMA reacts faster to recent price moves than the 20-day SMA</li>
<li>More responsive to new information</li>
<li>Best for: short-term trading, catching trend changes earlier</li>
</ul>

<p><strong>Which should you use?</strong> For swing trading and daily charts, EMAs are generally preferred because they react faster. For longer-term investing and weekly charts, SMAs work well because you want to filter out noise. Many traders use both — EMAs for entries and SMAs for trend context.</p>

<h2>The Most Important Moving Averages</h2>
<ul>
<li><strong>9 EMA / 10 EMA:</strong> Short-term momentum. Day traders and scalpers use this. Price above = short-term bullish.</li>
<li><strong>20 EMA / 21 EMA:</strong> The "institutional" short-term average. Swing traders' favorite. Stocks in strong uptrends tend to bounce off the 20 EMA on pullbacks.</li>
<li><strong>50 SMA / 50 EMA:</strong> Medium-term trend. The most watched moving average by active traders. Stocks above the 50 MA are generally in uptrends.</li>
<li><strong>100 SMA:</strong> Intermediate-term. Often used as a filter between the 50 and 200.</li>
<li><strong>200 SMA:</strong> Long-term trend. The most important MA on Wall Street. Institutional investors use this as a line between bull and bear markets. Price above 200 SMA = bullish. Below = bearish.</li>
</ul>

<h2>Moving Average Trading Strategies</h2>

<p><strong>1. Trend Following: Price Above/Below the MA</strong></p>
<ul>
<li>The simplest strategy: only buy stocks trading ABOVE their 50-day or 200-day MA</li>
<li>Only short (or avoid) stocks trading BELOW their 50-day or 200-day MA</li>
<li>This single filter eliminates most losing trades by keeping you on the right side of the trend</li>
</ul>

<p><strong>2. Moving Average Bounce (Pullback Entry)</strong></p>
<ul>
<li>In an uptrend, wait for price to pull back to a key MA (20 EMA or 50 SMA)</li>
<li>Look for a bullish candlestick pattern at the MA (hammer, engulfing)</li>
<li>Enter long with stop-loss below the MA</li>
<li>This gives you low-risk entries in the direction of the trend</li>
<li>Works best when multiple MAs are stacked bullishly (price > 20 EMA > 50 SMA > 200 SMA)</li>
</ul>

<p><strong>3. Moving Average Crossover</strong></p>
<ul>
<li><strong>Golden Cross:</strong> 50-day MA crosses ABOVE the 200-day MA = bullish signal. Historically, stocks gain an average of 7-10% in the 6 months following a golden cross.</li>
<li><strong>Death Cross:</strong> 50-day MA crosses BELOW the 200-day MA = bearish signal. Often precedes significant declines.</li>
<li><strong>Shorter crossover:</strong> 9 EMA crossing above 21 EMA = shorter-term buy signal for swing trades</li>
<li><strong>Warning:</strong> Crossovers are lagging signals. The move often starts before the crossover confirms. Use them for confirmation, not as standalone entry triggers.</li>
</ul>

<p><strong>4. Multiple Moving Average System</strong></p>
<p>Use three MAs together to see the full picture:</p>
<ul>
<li><strong>Short (20 EMA):</strong> Entry timing and short-term trend</li>
<li><strong>Medium (50 SMA):</strong> Main trend direction</li>
<li><strong>Long (200 SMA):</strong> Overall market regime (bull vs bear)</li>
</ul>
<p>Best setup: all three stacked bullishly (price > 20 > 50 > 200). When they're tangled or inverted, stay cautious or sit out.</p>

<h2>Moving Average Mistakes to Avoid</h2>
<ol>
<li><strong>Using MAs in choppy/sideways markets:</strong> Moving averages work in trending markets. In a range, they'll generate constant false signals (whipsaws). Wait for a clear trend to develop.</li>
<li><strong>Using too many MAs:</strong> 2-3 MAs is plenty. Having 5+ MAs on your chart creates clutter and confusion.</li>
<li><strong>Treating crossovers as instant signals:</strong> Crossovers confirm trends — they don't predict them. By the time the golden cross fires, the stock has often already moved 10-15% off the bottom.</li>
<li><strong>Using the same MA for all timeframes:</strong> A 50 SMA on a 5-minute chart covers about 4 hours. A 50 SMA on a daily chart covers 2.5 months. Same indicator, vastly different meaning.</li>
</ol>

<div class="key-takeaway"><strong>🎯 Key Takeaway:</strong> Start with three moving averages: 20 EMA (short-term entries), 50 SMA (trend direction), and 200 SMA (bull vs bear). When all three are stacked bullishly, buy pullbacks to the 20 EMA with stop-losses below. The Golden Cross (50 above 200) and Death Cross (50 below 200) are powerful trend-confirmation signals. Avoid using moving averages in sideways markets — they only work when prices are trending. Simple beats complex: two or three MAs tell you everything you need to know.</div>
'''
})

print('✅ Article 11 done: Moving Averages SMA vs EMA')
