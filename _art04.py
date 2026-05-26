import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_helper import create_article

create_article({
    'title': 'Risk Management: The #1 Skill Every Trader Needs to Master',
    'slug': 'risk-management-trading-skill-master',
    'meta_description': 'Risk management separates profitable traders from blown accounts. Learn position sizing, stop-losses, the 1% rule, and risk-reward ratios that protect your capital.',
    'keywords': 'risk management trading, position sizing, stop loss strategy, 1 percent rule trading, risk reward ratio',
    'word_count': 1150,
    'read_time': 5,
    'tags': ['trading', 'risk-management', 'stocks'],
    'body_html': '''
<p>You can have the best trading strategy in the world and still blow your account without proper risk management. The uncomfortable truth: risk management isn't exciting, it isn't flashy, and nobody on social media brags about it. But it's the single biggest factor that separates traders who survive from those who don't.</p>

<h2>Why Risk Management Matters More Than Strategy</h2>
<p>Consider this scenario:</p>
<ul>
<li>Trader A wins 70% of trades but risks 10% of account per trade</li>
<li>Trader B wins 45% of trades but risks 1% of account per trade</li>
</ul>
<p>After a losing streak of 5 trades (which happens to everyone):</p>
<ul>
<li><strong>Trader A:</strong> Down 50% — needs a 100% return just to break even. Account is effectively destroyed.</li>
<li><strong>Trader B:</strong> Down 5% — a minor setback. Back to break-even with a few good trades.</li>
</ul>
<p>Trader B survives the inevitable bad streaks. Trader A doesn't. That's why risk management beats strategy every single time.</p>

<h2>The 1% Rule: Your Account's Life Insurance</h2>
<p>The most important rule in trading: <strong>never risk more than 1-2% of your total account on any single trade.</strong></p>
<p>Here's what that looks like in practice:</p>
<ul>
<li><strong>$10,000 account:</strong> Maximum risk per trade = $100-$200</li>
<li><strong>$25,000 account:</strong> Maximum risk per trade = $250-$500</li>
<li><strong>$50,000 account:</strong> Maximum risk per trade = $500-$1,000</li>
</ul>
<p>This means even 10 consecutive losses (extremely rare) only costs you 10-20% of your account. You live to trade another day.</p>

<h2>Position Sizing: How Much to Buy</h2>
<p>Position sizing is how you control risk. The formula is simple:</p>
<p><strong>Position Size = Risk Amount ÷ (Entry Price - Stop-Loss Price)</strong></p>
<p>Example with a $25,000 account risking 1%:</p>
<ul>
<li>Risk amount: $25,000 × 1% = $250</li>
<li>Stock entry price: $50.00</li>
<li>Stop-loss price: $47.50 (a $2.50 risk per share)</li>
<li>Position size: $250 ÷ $2.50 = 100 shares</li>
<li>Total position value: 100 × $50 = $5,000 (20% of account)</li>
</ul>
<p>Notice: you're NOT buying $25,000 worth of stock. Position sizing ensures your RISK stays at 1%, regardless of the position's total dollar value.</p>

<h2>Stop-Loss Orders: Your Safety Net</h2>
<p>A stop-loss order automatically sells your position when the price drops to a predetermined level. Rules for setting stop-losses:</p>
<ul>
<li><strong>Set it BEFORE you enter the trade</strong> — never enter without knowing your exit</li>
<li><strong>Place it at a logical level</strong> — below support, below a moving average, or below the most recent swing low</li>
<li><strong>Never move it further away</strong> — widening your stop = increasing your risk after the fact</li>
<li><strong>It's okay to tighten it</strong> — move your stop-loss UP as the trade moves in your favor to lock in profits</li>
</ul>

<p><strong>Types of stop-losses:</strong></p>
<ul>
<li><strong>Fixed percentage:</strong> Sell if price drops 5-8% from entry (simple, works for beginners)</li>
<li><strong>Technical:</strong> Place below key support level or moving average (more precise)</li>
<li><strong>Trailing stop:</strong> Moves up with the price, locking in gains — e.g., always 5% below the highest price reached</li>
<li><strong>Time-based:</strong> Exit if the trade hasn't moved in your favor after X days (prevents dead money)</li>
</ul>

<h2>Risk-Reward Ratio: Making Math Work for You</h2>
<p>The risk-reward ratio compares how much you could lose to how much you could gain:</p>
<p><strong>Risk-Reward = Potential Profit ÷ Potential Loss</strong></p>
<p>Example:</p>
<ul>
<li>Entry: $50, Stop-loss: $48, Target: $56</li>
<li>Risk: $2 per share, Reward: $6 per share</li>
<li>Risk-Reward Ratio: 1:3 (risking $1 to make $3)</li>
</ul>
<p><strong>Why this matters:</strong> With a 1:3 risk-reward ratio, you only need to win 25% of your trades to break even. Win 40% and you're very profitable. This is how traders make money even with more losing trades than winners.</p>

<p><strong>Minimum acceptable ratios:</strong></p>
<ul>
<li><strong>1:2</strong> — minimum for most trades (risk $1 to make $2)</li>
<li><strong>1:3</strong> — ideal for swing trades</li>
<li><strong>1:1 or worse</strong> — skip the trade unless you have an extremely high win rate</li>
</ul>

<h2>Portfolio-Level Risk Management</h2>
<p>Individual trade risk isn't enough. You also need to manage overall portfolio risk:</p>
<ul>
<li><strong>Maximum total exposure:</strong> Don't have more than 5-6 open positions at once when starting out</li>
<li><strong>Correlated risk:</strong> Owning 5 tech stocks isn't diversified — if tech drops, they all drop together</li>
<li><strong>Daily loss limit:</strong> If you lose 3% of your account in one day, stop trading. Come back tomorrow with a clear head.</li>
<li><strong>Weekly loss limit:</strong> If you're down 5-6% for the week, take the rest of the week off. Preventing tilt is essential.</li>
<li><strong>Drawdown limit:</strong> If your account drops 15-20% from its peak, stop trading live. Go back to paper trading until you figure out what's wrong.</li>
</ul>

<h2>The Risk Management Checklist</h2>
<p>Before every trade, ask yourself:</p>
<ol>
<li>Where is my stop-loss? (Must have an answer BEFORE entering)</li>
<li>How many shares should I buy? (Use position sizing formula)</li>
<li>What's my risk-reward ratio? (Minimum 1:2)</li>
<li>Am I risking more than 1-2% of my account? (If yes, reduce size)</li>
<li>How many other positions do I have open? (Don't over-concentrate)</li>
<li>Am I trading emotionally right now? (If upset, angry, or euphoric — don't trade)</li>
</ol>

<div class="key-takeaway"><strong>🎯 Key Takeaway:</strong> Never risk more than 1-2% of your account per trade. Use the position sizing formula (Risk Amount ÷ Distance to Stop-Loss) to calculate exactly how many shares to buy. Always set stop-losses BEFORE entering, aim for at least a 1:2 risk-reward ratio, and have a daily loss limit (3%) and weekly loss limit (5-6%). Risk management isn't optional — it's the foundation everything else is built on. A mediocre strategy with excellent risk management beats a great strategy with no risk management every time.</div>
'''
})

print('\\n✅ Article 4 done: Risk Management')
