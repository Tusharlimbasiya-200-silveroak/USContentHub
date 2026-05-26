"""
Create a comprehensive blog article on the US-Iran conflict:
Why the war happened, consequences, markets, gold, rupee, and more.
"""
import os, sys, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "writeflow.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
from blog.models import Article, Publication, Tag


def get_or_create_tags(tag_names):
    tags = []
    for name in tag_names:
        tag, _ = Tag.objects.get_or_create(name=name.strip().lower())
        tags.append(tag)
    return tags


pub = Publication.objects.get(slug="usa-news-digest")

TITLE = "The US-Iran War Explained: Why It Happened, Why Markets Crashed, Why Gold Soared, and What Comes Next"
SLUG = "us-iran-war-explained-markets-gold-rupee-oil-consequences-2026"
SUBTITLE = "A complete breakdown of the 2026 US-Iran conflict — from the first strikes to oil at $100, stock market turmoil, gold's record run, the rupee's plunge, and the uncertain path to peace."
META = "Complete guide to the 2026 US-Iran war: why it started, its global consequences on oil, stock markets, gold prices, the Indian rupee, and what a peace deal could mean."
COVER = "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1200"
TAGS = [
    "news", "us iran war 2026", "iran conflict explained", "oil prices",
    "gold prices 2026", "stock market crash", "indian rupee", "geopolitics",
    "economy", "strait of hormuz", "iran peace deal"
]

CONTENT = """
<p>Since late February 2026, the world has been gripped by the <strong>US-Iran military conflict</strong> — a war that has reshaped global energy markets, sent gold to record highs, battered stock markets, weakened currencies from the Indian rupee to the Turkish lira, and raised the specter of a wider Middle Eastern conflagration.</p>

<p>Nearly three months in, the conflict shows signs of winding down with peace talks in Qatar, but the damage to the global economy has been profound. Whether you're an investor watching your portfolio, a driver wincing at gas prices, or simply trying to understand why the world feels more unstable — this is the complete guide to what happened, why, and what comes next.</p>

<hr>

<h2>Part 1: Why Did the US Go to War With Iran?</h2>

<h3>The Deep Roots (1953–2025)</h3>

<p>US-Iran tensions didn't start in 2026. They trace back over seven decades:</p>

<ul>
<li><strong>1953:</strong> The CIA-backed coup overthrew Iran's democratically elected Prime Minister Mohammad Mosaddegh, installing Shah Mohammad Reza Pahlavi. This planted seeds of anti-American sentiment that persist today</li>
<li><strong>1979:</strong> The Islamic Revolution toppled the Shah. Radical students seized the US Embassy in Tehran, holding 52 Americans hostage for 444 days. Diplomatic relations were severed</li>
<li><strong>1980–1988:</strong> The Iran-Iraq War — the US backed Iraq's Saddam Hussein against Iran, deepening Iranian resentment</li>
<li><strong>2002:</strong> President George W. Bush named Iran part of the "Axis of Evil," accusing it of pursuing nuclear weapons</li>
<li><strong>2015:</strong> The JCPOA (Iran Nuclear Deal) — a landmark agreement where Iran limited its nuclear program in exchange for sanctions relief. Seen as a diplomatic triumph</li>
<li><strong>2018:</strong> President Trump withdrew the US from the JCPOA, reimposing crippling sanctions on Iran. Iran gradually resumed uranium enrichment</li>
<li><strong>2020:</strong> The US assassinated Iranian General Qasem Soleimani via drone strike. Iran retaliated with missile attacks on US bases in Iraq</li>
<li><strong>2023–2025:</strong> Iran's nuclear program advanced significantly. Intelligence agencies reported Iran was approaching weapons-grade uranium enrichment. Proxy conflicts intensified across the region</li>
</ul>

<h3>The Immediate Trigger (February 2026)</h3>

<p>Multiple factors converged to push the situation from cold war to hot war:</p>

<ol>
<li><strong>Nuclear threshold:</strong> US and Israeli intelligence concluded Iran was weeks away from having enough weapons-grade enriched uranium for a nuclear device. This crossed a "red line" that both nations had set</li>
<li><strong>Israeli pressure:</strong> Israel, viewing an Iranian nuclear weapon as an existential threat, pushed hard for military action and indicated it would act alone if necessary</li>
<li><strong>Regional provocations:</strong> Iranian-backed Houthi rebels continued attacking shipping in the Red Sea, and Hezbollah escalated attacks on Israel's northern border</li>
<li><strong>Strait of Hormuz threats:</strong> Iran threatened to close the Strait of Hormuz — through which 20% of the world's oil flows — if subjected to further sanctions pressure</li>
<li><strong>Political calculation:</strong> The Trump administration, facing domestic pressures, framed military action as necessary to prevent nuclear proliferation</li>
</ol>

<h3>How the War Unfolded</h3>

<p>The conflict began on <strong>February 28, 2026</strong>, with coordinated US and Israeli airstrikes on Iranian nuclear facilities, military bases, and missile sites. Key phases:</p>

<ul>
<li><strong>Week 1 (Feb 28 – Mar 6):</strong> Massive aerial bombardment of nuclear facilities at Natanz, Fordow, and Isfahan. Iran's air defenses were suppressed. First US service members were killed by Iranian missile retaliation</li>
<li><strong>Weeks 2-4 (Mar 7–28):</strong> Iran retaliated with ballistic missiles against US bases in the Gulf region. The IRGC Navy harassed shipping in the Strait of Hormuz. Oil prices spiked above $90 per barrel</li>
<li><strong>Weeks 5-8 (Mar 29 – Apr 20):</strong> Escalation as US struck Iranian infrastructure, including power grid targets. Iran fired missiles at Israel. A Lebanon-Israel ceasefire was negotiated. International outcry grew as civilian casualties mounted</li>
<li><strong>Weeks 9-12 (Apr 21 – May 26):</strong> De-escalation attempts. Peace talks began in Qatar. Intermittent strikes continued. Oil surged past $100 as Strait of Hormuz disruptions intensified. Trump shifted messaging toward a deal</li>
</ul>

<hr>

<h2>Part 2: The Economic Consequences — Why Everything Got More Expensive</h2>

<h3>Why Oil Prices Exploded</h3>

<p>Brent crude oil went from roughly <strong>$75/barrel before the war to over $100/barrel</strong> by late May 2026. The reasons:</p>

<ol>
<li><strong>Iranian supply offline:</strong> Iran was producing approximately 3.2 million barrels per day before the conflict. Sanctions and physical destruction knocked most of this offline</li>
<li><strong>Strait of Hormuz disruption:</strong> Even partial disruption to this chokepoint — through which roughly 21 million barrels per day flow — created panic in energy markets. Iran's mining of certain shipping lanes forced tankers to take longer, more expensive routes</li>
<li><strong>Insurance costs:</strong> War-risk insurance premiums for tankers transiting the Gulf skyrocketed, adding $2-5 per barrel to shipping costs</li>
<li><strong>Speculative premium:</strong> Traders added a "war premium" of $10-20 per barrel, betting on further escalation</li>
<li><strong>OPEC+ response:</strong> Other oil producers were slow to increase output to compensate, partly due to limited spare capacity and partly due to political reluctance to undermine a fellow OPEC member</li>
</ol>

<p><strong>Real-world impact:</strong> US gasoline prices rose from roughly $3.40/gallon to $3.85-$4.10/gallon, with further increases expected if the conflict persists through summer driving season.</p>

<h3>Why Stock Markets Tumbled</h3>

<p>Global equity markets experienced significant turbulence:</p>

<ul>
<li><strong>The S&P 500</strong> dropped sharply in the initial days of the conflict, though tech stocks have since recovered somewhat on AI optimism. As of late May, the Nasdaq has actually reached new highs, driven by Micron and semiconductor stocks — but broader market indices remain volatile</li>
<li><strong>Energy-dependent sectors</strong> (airlines, shipping, chemicals, consumer discretionary) have been hit hardest</li>
<li><strong>Defense stocks</strong> (Lockheed Martin, Raytheon, Northrop Grumman) have surged — an uncomfortable rally that always accompanies war</li>
</ul>

<p>The market turbulence stems from several interconnected fears:</p>

<ol>
<li><strong>Inflation resurgence:</strong> Higher oil prices feed into transportation, manufacturing, and food costs, threatening the progress made in taming post-pandemic inflation</li>
<li><strong>Federal Reserve response:</strong> If oil-driven inflation re-accelerates, the Fed may delay or reverse planned interest rate cuts, keeping borrowing costs elevated</li>
<li><strong>Supply chain disruption:</strong> CNBC analysts warn of a potential "supply chain correction" in August 2026 if shipping disruptions persist</li>
<li><strong>Consumer spending squeeze:</strong> Higher gas and grocery prices reduce discretionary spending, potentially slowing economic growth</li>
<li><strong>Geopolitical uncertainty:</strong> Markets hate uncertainty, and the constantly shifting US timeline for ending the conflict ("2-3 weeks," "when I feel it in my bones," "soon") has kept investors on edge</li>
</ol>

<h3>Why Gold Hit Record Highs</h3>

<p>Gold has surged to levels above <strong>$3,300-$3,500 per ounce</strong> during the conflict, reaching all-time highs. Here's why:</p>

<ul>
<li><strong>Safe-haven demand:</strong> When wars erupt, investors flee to gold — the oldest store of value. It's the ultimate "fear trade." Unlike stocks or bonds, gold has no counterparty risk — it can't go bankrupt or default</li>
<li><strong>Inflation hedge:</strong> Rising oil prices create inflation. Gold has historically been the premier inflation hedge because its supply is limited and it can't be printed like currency</li>
<li><strong>Dollar uncertainty:</strong> Despite being the world's reserve currency, the dollar has shown weakness amid fiscal deficit concerns and the geopolitical instability the US itself created. When dollar confidence wavers, gold benefits</li>
<li><strong>Central bank buying:</strong> China, India, and other nations have been aggressively buying gold reserves to reduce dependence on the US dollar — a trend the Iran war has accelerated</li>
<li><strong>De-dollarization trend:</strong> The weaponization of the financial system through sanctions has pushed countries to seek alternatives to dollar-denominated assets. Gold is the primary alternative</li>
</ul>

<p><strong>The bottom line:</strong> Gold is rising because the world is scared, inflation is climbing, and trust in traditional financial systems is eroding. It's a barometer of global anxiety — and that barometer is flashing red.</p>

<h3>Why the Indian Rupee Is Falling</h3>

<p>The Indian rupee has weakened significantly against the US dollar during the conflict, and India is particularly vulnerable for several reasons:</p>

<ol>
<li><strong>Oil import dependency:</strong> India imports approximately <strong>85% of its crude oil</strong>. It's the world's third-largest oil importer. Every $10/barrel increase in oil prices widens India's trade deficit by roughly $15-17 billion annually</li>
<li><strong>Current account deficit:</strong> Higher oil imports drain India's foreign exchange reserves and widen the current account deficit, putting downward pressure on the rupee</li>
<li><strong>Capital flight:</strong> Foreign institutional investors (FIIs) pull money out of emerging markets during geopolitical crises, preferring the safety of US Treasuries and gold. India loses billions in portfolio investment outflows</li>
<li><strong>Inflation transmission:</strong> Rising oil prices feed directly into Indian inflation — from transportation costs to cooking fuel (LPG) to petrochemical-based goods. The Reserve Bank of India faces pressure to raise rates, which can slow economic growth</li>
<li><strong>Iran was India's oil supplier:</strong> Before US sanctions, Iran was a major oil supplier to India at discounted prices. The war has eliminated this option entirely, forcing India to buy more expensive oil from other sources</li>
<li><strong>Fertilizer costs:</strong> India's agricultural sector depends heavily on imported fertilizers, which are energy-intensive to produce. Higher global energy prices raise farming costs, affecting food prices for 1.4 billion people</li>
</ol>

<p><strong>The ripple effect:</strong> A weaker rupee makes everything India imports more expensive — oil, electronics, gold (which Indians buy heavily for weddings and festivals), and industrial equipment. This creates a vicious cycle of inflation and currency weakness.</p>

<hr>

<h2>Part 3: The Human Cost</h2>

<p>Behind the market charts and oil prices are human beings. While exact figures are difficult to verify in an active conflict zone:</p>

<ul>
<li>Multiple US service members have been killed in action — the first American combat deaths in a new theater since the withdrawal from Afghanistan</li>
<li>Iranian civilian casualties have mounted, particularly after strikes on infrastructure including power generation</li>
<li>Iran's internet was shut down for months, only recently being partially restored — cutting 88 million people off from the world</li>
<li>Humanitarian organizations warn of a growing crisis as sanctions, war damage, and infrastructure destruction limit access to food, medicine, and clean water</li>
<li>A majority of Americans oppose the war, according to polling — yet Senate resolutions to invoke War Powers and limit the conflict have been blocked four times</li>
</ul>

<hr>

<h2>Part 4: The Peace Deal — Is It Coming?</h2>

<p>As of late May 2026, there are cautious signs of progress:</p>

<ul>
<li><strong>Qatar talks:</strong> Iranian negotiators are in Qatar for discussions, though 21 hours of talks recently ended without agreement</li>
<li><strong>Rubio's statement:</strong> Secretary of State Marco Rubio has said a deal could take "a few more days" — though Trump's shifting timelines have made such predictions unreliable</li>
<li><strong>Trump's Camp David meeting:</strong> The President is hosting a Cabinet meeting at Camp David to discuss Iran strategy, suggesting high-level decisions are imminent</li>
<li><strong>Strait of Hormuz:</strong> Signs of a deal to reopen the Strait have briefly calmed oil markets, with Brent dropping when positive signals emerge, only to spike again on new strikes</li>
<li><strong>Abraham Accords linkage:</strong> Trump has linked the Iran deal to a broader Abraham Accords expansion, potentially including Saudi Arabia's normalization with Israel</li>
</ul>

<h3>What a Peace Deal Could Mean for Markets</h3>

<ul>
<li><strong>Oil:</strong> Could drop $15-25/barrel rapidly if Iranian supply returns to market and Strait of Hormuz shipping normalizes</li>
<li><strong>Gold:</strong> Likely to pull back from highs but remain elevated due to persistent inflation and central bank buying</li>
<li><strong>Stocks:</strong> A relief rally is probable, particularly in energy-dependent sectors and emerging market equities</li>
<li><strong>Rupee:</strong> Would strengthen as oil import costs fall and foreign investment flows resume</li>
<li><strong>Gas prices:</strong> Could fall back below $3.50/gallon by late summer if a deal holds</li>
</ul>

<hr>

<h2>Part 5: What Should You Do?</h2>

<h3>As an Investor</h3>
<ul>
<li><strong>Don't panic sell:</strong> Wars create volatility, but markets have historically recovered after every conflict. Selling at the bottom locks in losses</li>
<li><strong>Diversify globally:</strong> Don't be concentrated in any single market or sector. Broad index funds spread risk</li>
<li><strong>Consider commodities exposure:</strong> Gold, oil, and commodity ETFs can hedge against geopolitical risk</li>
<li><strong>Watch the peace talks:</strong> A deal will trigger rapid repricing. Being positioned before it happens is more important than timing it perfectly</li>
</ul>

<h3>As a Consumer</h3>
<ul>
<li><strong>Lock in fuel-intensive purchases:</strong> If you need to buy a car, book flights, or plan travel, factor in the possibility of sustained higher fuel costs</li>
<li><strong>Build an emergency fund:</strong> Economic uncertainty makes savings buffers more important than ever</li>
<li><strong>Buy store brands:</strong> Grocery inflation is real. Switching to store brands saves 20-30% with equivalent quality</li>
<li><strong>Use gas price apps:</strong> GasBuddy and similar tools can save 20-40 cents per gallon by finding the cheapest stations nearby</li>
</ul>

<h3>As a Citizen</h3>
<ul>
<li><strong>Stay informed from multiple sources:</strong> The fog of war makes reliable information critical. Cross-reference claims from official sources, independent journalists, and international media</li>
<li><strong>Understand the stakes:</strong> This conflict affects everything from your gas bill to global food security to the risk of nuclear proliferation</li>
<li><strong>Engage democratically:</strong> Contact your representatives about the War Powers issue. Regardless of your position, democratic accountability in matters of war and peace is foundational</li>
</ul>

<hr>

<h2>The Bottom Line</h2>

<p>The 2026 US-Iran war is the most significant American military engagement since the Iraq War. Its consequences ripple across every aspect of global life — from the price of bread in Cairo to the value of your 401(k) to the cost of your morning commute.</p>

<p>The conflict exposes deep vulnerabilities in the global economic system: our dependence on Middle Eastern oil, the fragility of shipping chokepoints, the interconnectedness of financial markets, and the limits of military force in achieving political objectives.</p>

<p>Whether peace comes in days or months, the world that emerges from this conflict will be different. Energy diversification, de-dollarization, defense spending, and a recalibration of Middle Eastern alliances are already underway. Understanding these shifts isn't optional — it's essential for anyone navigating the economy, markets, and geopolitics of the years ahead.</p>

<p>We'll continue updating this article as the situation develops. Bookmark this page for the latest analysis.</p>
"""

if Article.objects.filter(slug=SLUG).exists():
    print(f"⏭  Already exists: {SLUG}")
else:
    words = len(CONTENT.split())
    article = Article.objects.create(
        title=TITLE,
        subtitle=SUBTITLE,
        slug=SLUG,
        content=CONTENT,
        cover_image=COVER,
        publication=pub,
        status="published",
        read_time=14,
        word_count=words,
        meta_description=META,
        published_at=timezone.now(),
    )
    article.tags.set(get_or_create_tags(TAGS))
    print(f"✅ Created: {TITLE}")
    print(f"   Words: {words} | Read time: 14 min")
    print(f"   Slug: {SLUG}")
