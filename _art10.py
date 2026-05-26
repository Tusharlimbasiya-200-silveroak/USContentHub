import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_helper import create_article

create_article({
    'title': '10 Candlestick Patterns Every Trader Must Know',
    'slug': 'candlestick-patterns-every-trader-must-know',
    'meta_description': 'Master the 10 most reliable candlestick patterns for trading — doji, hammer, engulfing, morning star, and more. Learn what each pattern signals and how to trade it.',
    'keywords': 'candlestick patterns trading, doji pattern, hammer candlestick, engulfing pattern, how to read candlesticks',
    'word_count': 1150,
    'read_time': 5,
    'tags': ['technical-analysis', 'trading', 'stocks'],
    'body_html': '''
<p>Candlestick patterns are the language of price action. They tell you the story of what buyers and sellers did during a specific time period — and more importantly, what they're likely to do next. Here are the 10 patterns that every trader should be able to recognize instantly.</p>

<h2>How to Read a Single Candlestick</h2>
<p>Before diving into patterns, make sure you understand the basics:</p>
<ul>
<li><strong>Body:</strong> The thick part — distance between open and close</li>
<li><strong>Upper wick/shadow:</strong> The thin line above the body — shows the high</li>
<li><strong>Lower wick/shadow:</strong> The thin line below the body — shows the low</li>
<li><strong>Green/white body:</strong> Close > Open (bullish)</li>
<li><strong>Red/black body:</strong> Close &lt; Open (bearish)</li>
<li><strong>Long body:</strong> Strong conviction in that direction</li>
<li><strong>Short body:</strong> Indecision between buyers and sellers</li>
</ul>

<h2>Bullish Reversal Patterns (Buy Signals)</h2>

<p><strong>1. Hammer</strong></p>
<ul>
<li>Small body at the TOP with a long lower wick (2x+ the body length)</li>
<li>Appears after a downtrend</li>
<li>Meaning: sellers pushed price down hard, but buyers stepped in and pushed it back up</li>
<li>Signal: potential bottom — watch for confirmation (next candle closes green above the hammer)</li>
<li>Best when it forms at a known support level</li>
</ul>

<p><strong>2. Bullish Engulfing</strong></p>
<ul>
<li>Two-candle pattern: small red candle followed by a large green candle that completely covers (engulfs) the previous candle's body</li>
<li>Appears after a downtrend</li>
<li>Meaning: buyers overwhelmed sellers — momentum is shifting</li>
<li>Stronger signal when the engulfing candle has above-average volume</li>
</ul>

<p><strong>3. Morning Star</strong></p>
<ul>
<li>Three-candle pattern: large red candle → small indecision candle (doji or spinning top) → large green candle</li>
<li>Appears at the bottom of a downtrend</li>
<li>Meaning: selling exhaustion (candle 1), indecision (candle 2), buyers taking over (candle 3)</li>
<li>One of the most reliable reversal patterns when it forms at strong support</li>
</ul>

<p><strong>4. Piercing Line</strong></p>
<ul>
<li>Two-candle pattern: large red candle followed by a green candle that opens below the red candle's low but closes above the midpoint of the red candle's body</li>
<li>Meaning: sellers gapped price down but buyers fought back strongly</li>
<li>Not as strong as bullish engulfing, but still a valid reversal signal at support</li>
</ul>

<h2>Bearish Reversal Patterns (Sell Signals)</h2>

<p><strong>5. Shooting Star</strong></p>
<ul>
<li>Small body at the BOTTOM with a long upper wick (2x+ the body length)</li>
<li>The opposite of a hammer — appears after an uptrend</li>
<li>Meaning: buyers tried to push price higher but sellers rejected it strongly</li>
<li>Signal: potential top — watch for confirmation (next candle closes red below the shooting star)</li>
</ul>

<p><strong>6. Bearish Engulfing</strong></p>
<ul>
<li>Small green candle followed by a large red candle that engulfs the previous body</li>
<li>Appears after an uptrend</li>
<li>Meaning: sellers overwhelmed buyers — momentum is reversing</li>
<li>Very reliable when it forms at resistance with high volume</li>
</ul>

<p><strong>7. Evening Star</strong></p>
<ul>
<li>The opposite of morning star: large green → small indecision → large red</li>
<li>Appears at the top of an uptrend</li>
<li>One of the strongest bearish reversal signals</li>
<li>Especially powerful at major resistance levels</li>
</ul>

<h2>Indecision Patterns</h2>

<p><strong>8. Doji</strong></p>
<ul>
<li>Open and close are virtually the same — forming a cross shape</li>
<li>Meaning: perfect balance between buyers and sellers — the market is undecided</li>
<li>A doji by itself doesn't tell you direction — it says "something is about to change"</li>
<li>After an uptrend: warns of a potential reversal down</li>
<li>After a downtrend: warns of a potential reversal up</li>
<li>Always wait for the NEXT candle to confirm direction after a doji</li>
</ul>

<p><strong>9. Spinning Top</strong></p>
<ul>
<li>Small body with upper and lower wicks of roughly equal length</li>
<li>Similar to a doji but with a small body</li>
<li>Meaning: indecision — neither side is winning</li>
<li>Often appears during consolidation before a breakout</li>
</ul>

<h2>Continuation Pattern</h2>

<p><strong>10. Three White Soldiers / Three Black Crows</strong></p>
<ul>
<li><strong>Three White Soldiers:</strong> Three consecutive long green candles, each opening within the previous body and closing at new highs. Strong bullish continuation.</li>
<li><strong>Three Black Crows:</strong> Three consecutive long red candles, each opening within the previous body and closing at new lows. Strong bearish continuation.</li>
<li>Both signal strong momentum in the current direction</li>
<li>Watch volume: increasing volume with each candle = stronger signal</li>
</ul>

<h2>Rules for Trading Candlestick Patterns</h2>
<ol>
<li><strong>Context matters most.</strong> A hammer at a 200-day moving average after a 20% decline is powerful. A hammer in the middle of nowhere is meaningless. Always check WHERE the pattern forms.</li>
<li><strong>Volume confirms.</strong> A bullish engulfing on 3x average volume is far more reliable than one on low volume.</li>
<li><strong>Wait for confirmation.</strong> Don't trade the pattern alone — wait for the NEXT candle to confirm. A hammer is only bullish if the following candle closes higher.</li>
<li><strong>Higher timeframes are more reliable.</strong> A daily chart pattern is more significant than a 5-minute chart pattern. Weekly patterns are even stronger.</li>
<li><strong>Don't memorize every pattern.</strong> Focus on these 10. Master reading the story they tell — who's winning: buyers or sellers? Is momentum shifting? Is there indecision?</li>
</ol>

<div class="key-takeaway"><strong>🎯 Key Takeaway:</strong> The most important candlestick patterns are: Hammer and Bullish Engulfing (buy signals at support), Shooting Star and Bearish Engulfing (sell signals at resistance), and Doji (indecision — something's about to change). Always consider WHERE the pattern forms (support/resistance matters more than the pattern itself), confirm with volume, and wait for the next candle before entering. Master these 10 patterns and you'll be able to read price action better than most traders.</div>
'''
})

print('\\n✅ Article 10 done: Candlestick Patterns')
