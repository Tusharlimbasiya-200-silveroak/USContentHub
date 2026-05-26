import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_helper import create_article

create_article({
    'title': 'Support and Resistance: How to Find Key Price Levels That Matter',
    'slug': 'support-resistance-find-key-price-levels',
    'meta_description': 'Support and resistance are the foundation of all trading strategies. Learn how to identify, draw, and trade these key price levels with real-world examples.',
    'keywords': 'support and resistance trading, how to draw support resistance, key price levels, trading levels',
    'word_count': 1000,
    'read_time': 4,
    'tags': ['technical-analysis', 'trading', 'stocks'],
    'body_html': '''
<p>If you only learn one concept in technical analysis, make it support and resistance. Every chart pattern, every indicator, every strategy ultimately comes back to these two concepts. They're where the real buying and selling happens.</p>

<h2>What Are Support and Resistance?</h2>
<p><strong>Support</strong> is a price level where demand is strong enough to prevent the price from falling further. Think of it as a floor — the price hits it and bounces up.</p>
<p><strong>Resistance</strong> is a price level where supply is strong enough to prevent the price from rising further. Think of it as a ceiling — the price hits it and gets pushed back down.</p>
<p>Why do they work? Because thousands of traders are watching the same levels. Enough people place buy orders at support (and sell orders at resistance) that these levels become self-fulfilling prophecies.</p>

<h2>How to Identify Support and Resistance</h2>

<p><strong>1. Previous Highs and Lows</strong></p>
<ul>
<li>The most basic method: look for price levels where the stock has reversed before</li>
<li>A low that held multiple times = strong support</li>
<li>A high that rejected price multiple times = strong resistance</li>
<li>The more times a level has been tested, the stronger it is</li>
</ul>

<p><strong>2. Round Numbers</strong></p>
<ul>
<li>$50, $100, $200, $500 — psychological price levels where traders cluster orders</li>
<li>AAPL at $200, TSLA at $250, SPY at $500 — these numbers attract attention</li>
<li>Not always precise, but they create zones of interest</li>
</ul>

<p><strong>3. Moving Averages as Dynamic S/R</strong></p>
<ul>
<li>The 20 EMA, 50 SMA, and 200 SMA act as moving support/resistance lines</li>
<li>In an uptrend, the 50-day MA often acts as support — price bounces off it</li>
<li>In a downtrend, the 50-day MA often acts as resistance — rallies stall at it</li>
</ul>

<p><strong>4. Volume Profile</strong></p>
<ul>
<li>Areas where high volume traded previously create strong S/R levels</li>
<li>High-volume nodes = lots of traders have positions at that price = strong reaction expected</li>
<li>Low-volume areas = price tends to move through them quickly</li>
</ul>

<h2>The Role Reversal Principle</h2>
<p>This is the most powerful concept in S/R trading:</p>
<p><strong>When support breaks, it becomes resistance. When resistance breaks, it becomes support.</strong></p>
<ul>
<li>Example: a stock bounces off $100 three times (support). On the fourth test, it breaks below $100. Now, $100 becomes resistance — the stock will likely struggle to get back above it.</li>
<li>The reverse is true: a stock fails at $150 twice (resistance), then breaks above. Now $150 becomes support — pullbacks should find buyers there.</li>
</ul>
<p>This principle is the basis for breakout trading and pullback entries.</p>

<h2>How to Draw Support and Resistance Correctly</h2>
<ol>
<li><strong>Use zones, not exact lines.</strong> S/R isn't a precise price — it's a zone. A support "level" at $50 might actually be a zone from $49.50 to $50.50. Draw rectangles, not single lines.</li>
<li><strong>Start with higher timeframes.</strong> Draw weekly levels first, then daily. Weekly levels are stronger than daily levels.</li>
<li><strong>Focus on recent, well-tested levels.</strong> A level that was tested last week is more relevant than one from 2 years ago.</li>
<li><strong>Use closing prices primarily.</strong> Wicks (intraday spikes) matter, but closes carry more weight because they represent where traders were willing to hold overnight.</li>
<li><strong>Less is more.</strong> If your chart has 20 S/R lines, you have no information. Focus on the 3-5 most significant levels.</li>
</ol>

<h2>Trading Support and Resistance</h2>

<p><strong>Strategy 1: Bounce Trading</strong></p>
<ul>
<li>Buy when price approaches strong support (with confirmation — bullish candle, RSI oversold)</li>
<li>Sell/short when price approaches strong resistance (with confirmation)</li>
<li>Stop-loss: just beyond the S/R level (if support is $50, stop at $49.50)</li>
<li>Target: the opposite S/R level</li>
</ul>

<p><strong>Strategy 2: Breakout Trading</strong></p>
<ul>
<li>Buy when price breaks ABOVE resistance with strong volume</li>
<li>Wait for a retest: price often comes back to the broken level (now support) before continuing</li>
<li>Enter on the retest with a stop-loss below the broken level</li>
<li>Target: the next higher resistance level</li>
</ul>

<p><strong>Strategy 3: Fakeout Trading</strong></p>
<ul>
<li>Price briefly breaks through S/R but immediately reverses — a "fakeout"</li>
<li>Fakeouts trap traders who entered on the breakout</li>
<li>Trade in the opposite direction of the fake breakout with a tight stop</li>
<li>Often results in fast, strong moves as trapped traders exit</li>
</ul>

<h2>Common Mistakes</h2>
<ol>
<li><strong>Drawing too many lines:</strong> If everything is S/R, nothing is. Stick to 3-5 major levels per chart.</li>
<li><strong>Treating S/R as exact:</strong> These are zones, not laser-precise lines. Give yourself a buffer.</li>
<li><strong>Ignoring volume:</strong> A breakout through resistance on low volume is more likely to fail than one on 2-3x average volume.</li>
<li><strong>Not checking higher timeframes:</strong> A resistance level on a 5-minute chart means nothing if the daily chart shows clear uptrend support.</li>
</ol>

<div class="key-takeaway"><strong>🎯 Key Takeaway:</strong> Support is a floor (price bounces up); resistance is a ceiling (price gets rejected down). Find them using previous highs/lows, round numbers, and moving averages. Remember the role reversal rule: broken support becomes resistance and vice versa. Draw S/R as zones, not precise lines, and focus on the 3-5 most important levels. Trade bounces at S/R with confirmation, or wait for breakouts with strong volume. Less is more — a clean chart with a few strong levels beats a cluttered mess.</div>
'''
})

print('✅ Article 12 done: Support and Resistance')
