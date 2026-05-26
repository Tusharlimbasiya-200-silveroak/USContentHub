import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_helper import create_article

create_article({
    'title': 'How to Build a Trading Plan That Actually Works',
    'slug': 'build-trading-plan-that-works',
    'meta_description': 'A trading plan is your blueprint for consistent profits. Learn exactly what to include — from market selection to risk rules — with a free template you can use today.',
    'keywords': 'trading plan template, how to create a trading plan, trading plan for beginners, stock trading plan',
    'word_count': 1050,
    'read_time': 4,
    'tags': ['trading', 'stocks'],
    'body_html': '''
<p>Trading without a plan is gambling. Trading with a plan is a business. Every consistently profitable trader has a written plan that defines what they trade, when they trade, how much they risk, and when they exit. Here's how to build yours.</p>

<h2>Why You Need a Written Plan</h2>
<p>A trading plan removes emotion from decision-making. When you're in the heat of the moment — watching your position swing up and down — you can't think clearly. Your plan was written when you were calm, rational, and not influenced by live P&L swings. It's your anchor.</p>
<p>Without a plan, you'll:</p>
<ul>
<li>Enter trades on impulse</li>
<li>Change your strategy every week</li>
<li>Risk too much on exciting trades and too little on boring ones</li>
<li>Have no way to measure if you're actually improving</li>
</ul>

<h2>The 8 Components of a Complete Trading Plan</h2>

<p><strong>1. Trading Goals</strong></p>
<p>Be specific and realistic:</p>
<ul>
<li>Bad goal: "Make lots of money trading"</li>
<li>Good goal: "Achieve 3-5% monthly return on a $10,000 account while keeping maximum drawdown under 10%"</li>
<li>Better: Break it into weekly targets. 3% monthly = roughly 0.75% per week.</li>
</ul>

<p><strong>2. Markets and Instruments</strong></p>
<p>Define exactly what you'll trade:</p>
<ul>
<li>Stocks only? Which sectors or market cap range?</li>
<li>Options? Which strategies (calls, puts, spreads)?</li>
<li>Forex? Which pairs?</li>
<li>Crypto? Which coins?</li>
</ul>
<p>Specialization beats diversification when learning. Master one market first.</p>

<p><strong>3. Trading Style and Timeframe</strong></p>
<ul>
<li>Day trading, swing trading, or position trading?</li>
<li>What chart timeframes will you use? (e.g., daily charts for entries, weekly for trend confirmation)</li>
<li>How many hours per day will you dedicate?</li>
<li>Which trading sessions? (Pre-market, regular hours, after-hours?)</li>
</ul>

<p><strong>4. Entry Rules (Setup Criteria)</strong></p>
<p>Define exactly what must be true before you enter a trade. Example for a swing trade long setup:</p>
<ul>
<li>Stock is above its 50-day moving average (uptrend)</li>
<li>Price has pulled back to a support level or rising trendline</li>
<li>RSI is between 30-50 (not overbought)</li>
<li>Volume is declining during the pullback (no panic selling)</li>
<li>A bullish candlestick pattern forms at support (hammer, engulfing, etc.)</li>
<li>ALL five conditions must be met — no exceptions</li>
</ul>

<p><strong>5. Exit Rules</strong></p>
<p>Define three exits before you enter:</p>
<ul>
<li><strong>Stop-loss:</strong> Where you'll exit if wrong (mandatory). Example: below the most recent swing low or 2× ATR below entry.</li>
<li><strong>Profit target:</strong> Where you'll take profits. Example: next resistance level, or when risk-reward of 1:2 or 1:3 is reached.</li>
<li><strong>Time stop:</strong> How long you'll hold if nothing happens. Example: exit if the trade hasn't moved in 5 trading days.</li>
</ul>

<p><strong>6. Position Sizing and Risk Rules</strong></p>
<ul>
<li>Maximum risk per trade: 1% of account (or 2% for high-conviction setups)</li>
<li>Maximum number of open positions: 3-5</li>
<li>Maximum daily loss: 3% of account → stop trading for the day</li>
<li>Maximum weekly loss: 5% of account → stop for the week and review</li>
<li>Maximum drawdown: 15% from peak → stop live trading, go back to paper</li>
</ul>

<p><strong>7. Trading Schedule</strong></p>
<p>Define your routine:</p>
<ul>
<li><strong>Pre-market:</strong> Review watchlist, check news, identify setups (30-60 min)</li>
<li><strong>Market hours:</strong> Execute trades, manage positions</li>
<li><strong>Post-market:</strong> Journal trades, review what worked and what didn't (15-30 min)</li>
<li><strong>Weekend:</strong> Weekly review, plan next week's watchlist (1-2 hours)</li>
</ul>

<p><strong>8. Review and Improvement Process</strong></p>
<ul>
<li>Review trading journal every Friday</li>
<li>Track key metrics: win rate, average win vs. average loss, profit factor, maximum drawdown</li>
<li>Monthly performance review: what's working, what's not, what needs adjustment</li>
<li>Only change your plan based on data from 30+ trades, not individual wins/losses</li>
</ul>

<h2>Sample Trading Plan Template</h2>
<div class="tip-box">
<p><strong>📋 My Trading Plan</strong></p>
<p><strong>Goal:</strong> 3-5% monthly return, max 10% drawdown</p>
<p><strong>Markets:</strong> US stocks, large-cap ($10B+), daily chart</p>
<p><strong>Style:</strong> Swing trading, 2-10 day holds</p>
<p><strong>Setup:</strong> Pullback to 20 EMA in an uptrend with bullish reversal candle + increasing volume</p>
<p><strong>Entry:</strong> Limit order at previous candle's close</p>
<p><strong>Stop-loss:</strong> Below the pullback low (or 2× ATR)</p>
<p><strong>Target:</strong> 1:2 risk-reward minimum, trail stop after 1:1 reached</p>
<p><strong>Position size:</strong> 1% risk per trade using formula</p>
<p><strong>Max positions:</strong> 4 open at any time</p>
<p><strong>Daily loss limit:</strong> 3% → done for the day</p>
<p><strong>Schedule:</strong> Scan 8-9 PM, review 4:30 PM, full review Sundays</p>
</div>

<h2>Common Mistakes with Trading Plans</h2>
<ol>
<li><strong>Making it too complicated:</strong> Your plan should fit on one page. If it's 10 pages long, you won't follow it.</li>
<li><strong>Not following it:</strong> A plan you don't follow is worthless. If you find yourself deviating, figure out why — adjust the plan, don't abandon it.</li>
<li><strong>Changing it too often:</strong> Give your plan at least 30-50 trades before making changes. Random variance can make even good plans look bad in small samples.</li>
<li><strong>No review process:</strong> A plan without regular review never improves. Schedule weekly and monthly reviews.</li>
</ol>

<div class="key-takeaway"><strong>🎯 Key Takeaway:</strong> Your trading plan should define 8 things: goals, markets, style/timeframe, entry rules, exit rules, position sizing, schedule, and review process. Keep it to one page. Follow it religiously — deviating from your plan is the #1 sign of emotional trading. Review weekly, adjust monthly, but only based on data from 30+ trades. The plan isn't about being right on every trade — it's about having a repeatable process that makes money over time.</div>
'''
})

print('\\n✅ Article 9 done: Build a Trading Plan')
