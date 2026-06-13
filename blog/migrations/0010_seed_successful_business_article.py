from datetime import datetime

from django.db import migrations
from django.utils.timezone import make_aware


SLUG = "successful-business-stories-founder-lessons"

ARTICLE_CONTENT = """
<p>Successful business stories often look simple after they become famous. A founder sees an opportunity, builds a product, grows fast, and becomes a household name. But the real story is usually harder and more useful: years of rejection, small improvements, customer listening, risk, and patience.</p>

<p>The best founder stories are not just inspirational. They show repeatable lessons. Whether someone wants to start a local service business, an online brand, a technology startup, or a family company, the pattern is similar: solve a real problem, serve customers better than others, stay consistent, and adapt when the market changes.</p>

<h2>1. Amazon: Jeff Bezos Started With One Clear Bet</h2>
<p>Amazon did not begin as the everything store. Jeff Bezos started with books because they were easy to catalog, easy to ship, and had a huge selection problem. A physical bookstore could only hold limited inventory. An online bookstore could offer far more choice.</p>

<p>The founder lesson is focus. Many new entrepreneurs try to launch too many things at once. Bezos started with one category, proved the model, improved logistics, earned customer trust, and then expanded. Amazon's early success came from customer obsession: lower prices, more selection, faster delivery, and a buying experience that kept improving.</p>

<p><strong>Business lesson:</strong> Start with one clear problem. Win trust in a narrow area before trying to become big.</p>

<h2>2. Apple: Steve Jobs Built Around Experience, Not Just Technology</h2>
<p>Apple's story is not only about computers and phones. Steve Jobs understood that people do not just buy specifications. They buy design, simplicity, emotion, and confidence. Apple products became powerful because the company connected hardware, software, packaging, retail, and brand into one experience.</p>

<p>Jobs was also forced out of Apple before returning years later. That part of the story matters. Failure did not end his career. It gave him new perspective. When he came back, Apple reduced product confusion, focused on fewer products, and made each one easier to understand.</p>

<p><strong>Business lesson:</strong> A great product is more than features. The customer experience around the product can become the strongest advantage.</p>

<h2>3. Nike: Phil Knight Sold Shoes From a Car Trunk</h2>
<p>Before Nike became one of the world's biggest sports brands, Phil Knight was selling imported running shoes from the trunk of his car. The company started small, close to runners, coaches, and athletes. That closeness helped Nike understand what serious customers wanted.</p>

<p>Nike's growth came from product quality, bold branding, and athlete partnerships. But the foundation was simple: serve a specific group deeply. Runners needed better shoes, and Nike worked to become part of their identity.</p>

<p><strong>Business lesson:</strong> You do not need to start big. Start close to your customer. Learn their language, needs, and habits.</p>

<h2>4. Starbucks: Howard Schultz Sold a Feeling</h2>
<p>Starbucks did not become famous only because of coffee. Howard Schultz saw coffee shops as a third place between home and work. The product mattered, but the feeling mattered too: comfort, routine, community, and a small daily reward.</p>

<p>This is why Starbucks could charge more than ordinary coffee shops. The company was not just selling caffeine. It was selling a repeatable experience people wanted in their daily lives.</p>

<p><strong>Business lesson:</strong> Customers often pay for identity, convenience, comfort, and emotion, not just the physical product.</p>

<h2>5. Spanx: Sara Blakely Turned a Personal Problem Into a Brand</h2>
<p>Sara Blakely started Spanx after facing a practical clothing problem herself. She did not have a fashion empire, major funding, or a big team at the beginning. She had a clear pain point, persistence, and the ability to explain the product in a way customers understood quickly.</p>

<p>One of the strongest parts of the Spanx founder story is resourcefulness. Blakely researched patents, pitched stores, handled rejection, and kept going until the product found its audience. The brand grew because it solved a real problem in a simple way.</p>

<p><strong>Business lesson:</strong> Your own frustration can be a business idea if many other people share the same problem.</p>

<h2>6. Tesla: Elon Musk Made a Hard Market Feel Possible</h2>
<p>Tesla's founder story is different because it involved a massive, expensive industry. Electric vehicles existed before Tesla, but many people saw them as slow, boring, or impractical. Tesla changed the story by making electric cars desirable, fast, and technology-driven.</p>

<p>The lesson is not that every founder should take huge risks. The lesson is that markets can change when a company changes customer belief. Tesla made people imagine a different future for cars, energy, and software updates.</p>

<p><strong>Business lesson:</strong> If you are entering a difficult market, you need more than a product. You need a story that helps customers believe change is worth it.</p>

<h2>What These Founder Stories Have in Common</h2>
<p>These companies are different, but the founder lessons overlap. None of them succeeded only because of luck. They found a real customer need, created a strong point of view, and kept improving when the first version was not perfect.</p>

<ul>
    <li><strong>They started with a clear problem.</strong> Books were hard to browse online, running shoes needed improvement, coffee could become an experience, and customers needed better everyday solutions.</li>
    <li><strong>They built trust over time.</strong> Great founders understand that brand trust is earned through repeated delivery.</li>
    <li><strong>They stayed close to customers.</strong> Feedback, behavior, complaints, and repeat purchases all guided the next move.</li>
    <li><strong>They used focus before expansion.</strong> Most great companies became broad only after becoming excellent at something specific.</li>
    <li><strong>They turned setbacks into information.</strong> Rejection, cash pressure, competition, and product mistakes became signals, not endings.</li>
</ul>

<h2>How to Use These Lessons in Your Own Business</h2>
<p>You do not need to copy Amazon, Apple, Nike, Starbucks, Spanx, or Tesla. A small business should not behave exactly like a global company. But the principles work at every size.</p>

<p>If you are starting a business, ask three simple questions. What exact problem am I solving? Who feels this problem strongly enough to pay for a solution? Why would they choose me instead of another option?</p>

<p>Then keep the first version simple. Talk to customers. Improve the offer. Make buying easy. Deliver consistently. A business becomes strong when customers can clearly explain why it exists and why it is useful.</p>

<h2>The Real Meaning of a Successful Business Story</h2>
<p>A successful business story is not only about becoming rich or famous. It is about creating value that lasts. Founders become memorable when they solve problems in a way that changes customer habits, improves lives, or creates a new standard in the market.</p>

<p>The inspiring part is that most big companies started with small, uncertain steps. A bookstore website, a computer in a garage, shoes sold from a car trunk, a coffee shop idea, a personal clothing problem, or a belief that electric cars could be better. The start was not perfect. The persistence made the story.</p>

<div class="key-takeaway"><strong>Key Takeaway:</strong> Successful business stories are built on clear problems, customer trust, focused execution, and founder persistence. The best founders do not just chase money. They understand people, solve real problems, and keep improving until the market believes in their solution.</div>
"""


def seed_article(apps, schema_editor):
    Publication = apps.get_model("blog", "Publication")
    Tag = apps.get_model("blog", "Tag")
    Article = apps.get_model("blog", "Article")

    publication, _ = Publication.objects.get_or_create(
        slug="usa-news-digest",
        defaults={
            "name": "USA News Digest",
            "description": "Breaking down US news, trends, and issues that matter to Americans",
            "color": "#6366f1",
            "icon": "📰",
        },
    )

    article, _ = Article.objects.update_or_create(
        slug=SLUG,
        defaults={
            "title": "Successful Business Stories: Founder Lessons That Built Great Companies",
            "subtitle": "Successful business stories are not just about money. Learn how founders built companies through clear problems, customer focus, patience, and smart risk-taking.",
            "content": ARTICLE_CONTENT.strip(),
            "cover_image": "https://picsum.photos/seed/successful-business-stories-founder-lessons/1200/630",
            "publication": publication,
            "status": "published",
            "read_time": 5,
            "word_count": 1162,
            "meta_description": "Successful business stories are not just about money. Learn how founders built companies through clear problems, customer focus, patience, and smart risk-taking.",
            "published_at": make_aware(datetime(2026, 6, 11)),
        },
    )

    tag_names = [
        "news",
        "trends",
        "business",
        "successful business stories",
        "founder stories",
        "entrepreneur lessons",
    ]
    tags = []
    for name in tag_names:
        tag, _ = Tag.objects.get_or_create(name=name[:100])
        tags.append(tag)
    article.tags.set(tags)


def remove_article(apps, schema_editor):
    Article = apps.get_model("blog", "Article")
    Article.objects.filter(slug=SLUG).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0009_alter_article_title"),
    ]

    operations = [
        migrations.RunPython(seed_article, remove_article),
    ]
