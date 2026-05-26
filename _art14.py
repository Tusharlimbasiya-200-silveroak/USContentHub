import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_helper import create_article

create_article({
    'title': '12 Common Trading Mistakes That Destroy Accounts (And How to Fix Them)',
    'slug': 'common-trading-mistakes-destroy-accounts',
    'meta_description': 'Most traders fail because of the same repeated mistakes. Here are the 12 most common trading errors — from overtrading to ignoring stop-losses — and how to fix each one.',
    'keywords': 'common trading mistakes, why traders lose money, trading errors to avoid, beginner trading mistakes',
    'word_count': 1050,
    'read_time': 4,
    'tags': ['trading', 'stocks', 'risk-management'],
    'body_html': '''
<p>Studies consistently show that 70-90% of retail traders lose money. Not because the market is rigged, not because they picked the wrong stocks — but because they make the same preventable mistakes over and over. Here are the 12 most common account-destroying mistakes and exactly how to avoid each one.</p>

<h2>1. Trading Without a Plan</h2>
<p><strong>The mistake:</strong> Entering trades on gut feeling, tips from social media, or because "the chart looks good."</p>
<p><strong>The fix:</strong> Write a trading plan with specific entry criteria, exit rules, and position sizing BEFORE you trade. If a setup doesn't meet your criteria, skip it — no matter how tempting.</p>

<h2>2. Risking Too Much Per Trade</h2>
<p><strong>The mistake:</strong> Putting 10-20% of your account into a single trade. One bad trade wipes out weeks of gains.</p>
<p><strong>The fix:</strong> Never risk more than 1-2% of your account per trade. Use position sizing formulas. A string of 5 losses at 1% risk each only costs 5% — totally recoverable.</p>

<h2>3. Not Using Stop-Losses</h2>
<p><strong>The mistake:</strong> "I'll just watch it and sell if it drops." You won't. You'll hope, pray, and watch a small loss become a disaster.</p>
<p><strong>The fix:</strong> Set a stop-loss order the moment you enter every trade. Make it automatic — remove the human element. A planned loss is a small loss. An unplanned loss is a catastrophe.</p>

<h2>4. Moving Stop-Losses Further Away</h2>
<p><strong>The mistake:</strong> Price approaches your stop, so you move it lower to avoid getting stopped out. This turns a small planned loss into a much larger one.</p>
<p><strong>The fix:</strong> Never widen your stop. If anything, tighten it. If the trade hits your stop, your analysis was wrong — accept it and move on.</p>

<h2>5. Overtrading</h2>
<p><strong>The mistake:</strong> Taking 10-20 trades per day, most of which are mediocre setups. Commissions and slippage eat your profits. Decision fatigue degrades your judgment.</p>
<p><strong>The fix:</strong> Quality over quantity. 2-3 high-quality trades per day (or per week for swing traders) beats 20 average ones. The best traders spend more time waiting than trading.</p>

<h2>6. Chasing Stocks That Already Ran</h2>
<p><strong>The mistake:</strong> A stock is up 40% today and you buy because you don't want to miss out (FOMO). By the time you see it, the move is over.</p>
<p><strong>The fix:</strong> If you missed the move, let it go. There will always be another trade tomorrow. Chasing leads to buying at the top — the worst possible entry. Wait for a pullback or find a different setup.</p>

<h2>7. Averaging Down Without a Plan</h2>
<p><strong>The mistake:</strong> Your stock drops from $50 to $40. Instead of cutting the loss, you buy more to "lower your average cost." The stock drops to $30. Now you've doubled your loss.</p>
<p><strong>The fix:</strong> Only add to positions if it was part of your original plan (scaling in at predetermined levels). If you're adding because you're losing and hoping for a bounce, you're compounding a mistake.</p>

<h2>8. Ignoring the Bigger Trend</h2>
<p><strong>The mistake:</strong> Buying a stock in a strong downtrend because it "looks cheap" or a single indicator says oversold.</p>
<p><strong>The fix:</strong> Check the weekly chart first. If the stock is below its 200-day moving average and making lower highs, don't try to catch the bottom. Trade WITH the trend, not against it.</p>

<h2>9. Trading Based on Tips and Hype</h2>
<p><strong>The mistake:</strong> Buying because someone on Reddit, TikTok, or Discord said "this stock is going to 10x!" By the time retail hears about it, the smart money has already positioned.</p>
<p><strong>The fix:</strong> Do your own analysis. If you can't explain why you're buying in two sentences using YOUR OWN research, don't buy it. Social media is entertainment, not investment advice.</p>

<h2>10. Not Keeping a Trading Journal</h2>
<p><strong>The mistake:</strong> Trading for months without tracking your results. You have no idea what's working, what's not, or what patterns in your behavior are costing you money.</p>
<p><strong>The fix:</strong> Journal every trade — entry, exit, reason, emotion, result. Review weekly. After 50+ trades, your journal will reveal patterns you can't see in real-time.</p>

<h2>11. Switching Strategies Too Often</h2>
<p><strong>The mistake:</strong> A strategy loses 3 trades in a row, so you abandon it for a new one. That loses too, so you switch again. You never give any strategy enough trades to prove itself.</p>
<p><strong>The fix:</strong> Commit to one strategy for at least 50-100 trades before evaluating it. Random variance means even great strategies have losing streaks. Three losses doesn't mean the strategy is broken — it might mean you hit normal variance.</p>

<h2>12. Trading with Money You Can't Afford to Lose</h2>
<p><strong>The mistake:</strong> Trading with rent money, emergency funds, credit card cash advances, or borrowed money. The pressure to perform makes rational decision-making impossible.</p>
<p><strong>The fix:</strong> Only trade with money that, if you lost 100% of it tomorrow, wouldn't change your lifestyle. Build an emergency fund first (3-6 months expenses), eliminate high-interest debt, THEN fund your trading account with surplus money.</p>

<h2>Self-Assessment: How Many Are You Making?</h2>
<p>Be honest with yourself. Count how many of the 12 mistakes you're currently making:</p>
<ul>
<li><strong>0-2 mistakes:</strong> You have good habits. Focus on consistency.</li>
<li><strong>3-5 mistakes:</strong> These are costing you significant money. Fix them one at a time, starting with risk management (#2, #3, #4).</li>
<li><strong>6+ mistakes:</strong> Stop live trading immediately. Go back to paper trading, build a written plan, and address each issue before risking real money again.</li>
</ul>

<div class="key-takeaway"><strong>🎯 Key Takeaway:</strong> The 3 most critical mistakes to fix FIRST: not using stop-losses (turns small losses into catastrophic ones), risking too much per trade (1-2% max), and overtrading (quality beats quantity). Fix these three and you'll immediately stop the bleeding. Then work on the psychological mistakes — revenge trading, FOMO/chasing, and switching strategies. Track everything in a journal. The traders who survive long enough to become profitable are the ones who fix these common mistakes early.</div>
'''
})

print('✅ Article 14 done: Common Trading Mistakes')
