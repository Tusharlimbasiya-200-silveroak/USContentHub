"""
Data migration: seed Auto & Cars publication, related tags, and the
2026 Tata Tiago Facelift article.
Uses get_or_create throughout so it is safe to run multiple times.
"""
from django.db import migrations
from django.utils import timezone


ARTICLE_CONTENT = """
<p class="lead">
On 28 May 2026, Tata Motors pulled off one of the boldest single-day launches in Indian automotive history — simultaneously unveiling the 2026 Tata Tiago Facelift and the 2026 Tata Tiago EV Facelift. The petrol/CNG version starts at a wallet-friendly <strong>₹4.69 lakh</strong>, while the electric variant kicks off at <strong>₹6.99 lakh</strong>. Together, they represent the most complete small-car offering in India right now.
</p>

<h2>Both Launches at a Glance</h2>
<table style="width:100%;border-collapse:collapse;margin:1.5rem 0;font-size:.95rem;">
  <thead>
    <tr style="background:#dc2626;color:#fff;">
      <th style="padding:12px 16px;text-align:left;">Spec</th>
      <th style="padding:12px 16px;text-align:left;">Tiago Facelift (ICE)</th>
      <th style="padding:12px 16px;text-align:left;">Tiago EV Facelift</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#fef2f2;">
      <td style="padding:10px 16px;border-bottom:1px solid #fecaca;font-weight:600;">Starting Price</td>
      <td style="padding:10px 16px;border-bottom:1px solid #fecaca;">₹4.69 lakh</td>
      <td style="padding:10px 16px;border-bottom:1px solid #fecaca;">₹6.99 lakh</td>
    </tr>
    <tr>
      <td style="padding:10px 16px;border-bottom:1px solid #fee2e2;font-weight:600;">Top Variant Price</td>
      <td style="padding:10px 16px;border-bottom:1px solid #fee2e2;">₹7.99 lakh (Creative CNG)</td>
      <td style="padding:10px 16px;border-bottom:1px solid #fee2e2;">₹9.99 lakh (est.)</td>
    </tr>
    <tr style="background:#fef2f2;">
      <td style="padding:10px 16px;border-bottom:1px solid #fecaca;font-weight:600;">Powertrain</td>
      <td style="padding:10px 16px;border-bottom:1px solid #fecaca;">1.2L Petrol + iCNG</td>
      <td style="padding:10px 16px;border-bottom:1px solid #fecaca;">Electric Motor</td>
    </tr>
    <tr>
      <td style="padding:10px 16px;border-bottom:1px solid #fee2e2;font-weight:600;">Range / Efficiency</td>
      <td style="padding:10px 16px;border-bottom:1px solid #fee2e2;">~19–20 kmpl / ~26 km/kg</td>
      <td style="padding:10px 16px;border-bottom:1px solid #fee2e2;">293 km (claimed)</td>
    </tr>
    <tr style="background:#fef2f2;">
      <td style="padding:10px 16px;border-bottom:1px solid #fecaca;font-weight:600;">Transmission</td>
      <td style="padding:10px 16px;border-bottom:1px solid #fecaca;">5-speed MT / 5-speed AMT</td>
      <td style="padding:10px 16px;border-bottom:1px solid #fecaca;">Single-speed automatic</td>
    </tr>
    <tr>
      <td style="padding:10px 16px;font-weight:600;">Key First</td>
      <td style="padding:10px 16px;">India's first CNG + AMT hatchback</td>
      <td style="padding:10px 16px;">Most affordable EV with 293 km range</td>
    </tr>
  </tbody>
</table>

<h2>Exterior Redesign: Finally, Some Visual Drama</h2>
<p>
The old Tiago had aged gracefully, but it had aged. The 2026 facelift changes that completely. Tata's designers took clear inspiration from the Altroz — the result is a front fascia that feels like it belongs in a segment above. The sleek new LED headlamps, eyebrow-style DRLs and blacked-out grille visually widen the car and make it look far more premium than its price suggests.
</p>
<p>
The bumper gets sportier detailing with pixel-style fog lamp housings, adding a touch of aggression that the Tiago never had before. In profile, the silhouette is largely unchanged — which is fine, because the Tiago's compact dimensions are one of its biggest assets in crowded Indian cities. Tata freshens things up with new dual-tone alloy wheels, blacked-out ORVMs and a contrasting black roof on higher trims.
</p>
<p>
At the rear, the biggest change is the vertical LED tail lamps connected by a gloss-black strip. While the light bar itself does not illuminate, it visually widens the hatch and modernises what was previously the weakest angle of the car.
</p>

<h2>Interior &amp; Cabin: Entry-Level No More</h2>
<p>
Step inside and the transformation is even more dramatic. The entire dashboard has been redesigned with a clean horizontal layout that makes the cabin feel significantly wider. The biggest highlight is the new free-standing digital instrument cluster — it instantly gives the cockpit a contemporary feel that rivals cars costing twice as much.
</p>
<p>
The 10.25-inch floating touchscreen continues from the outgoing model, but it is now accompanied by a revised two-spoke steering wheel, physical AC controls (replacing the touch-based HVAC panel — a very welcome change), and a rotary drive selector for AMT variants. The centre console also gains dual wireless charging trays and USB Type-C ports throughout.
</p>
<p>
Rear passengers are not forgotten either. The facelift adds rear AC vents, rear charging ports and front seatback pockets — things that were conspicuously absent before. The upholstery, dashboard textures and door pad inserts all feel a meaningful step up from the previous generation.
</p>

<h2>Features That Actually Matter</h2>
<ul style="margin:1rem 0 1.5rem 1.5rem;line-height:2;">
  <li><strong>360-degree Surround View Camera</strong> — one of the most affordable hatchbacks in India to offer this</li>
  <li><strong>Blind View Monitor</strong> — alerts you to vehicles in your blind spot</li>
  <li><strong>Wireless Android Auto &amp; Apple CarPlay</strong> — cable-free smartphone mirroring</li>
  <li><strong>iRA Connected Car Tech</strong> — 35+ connected features via Tata's app</li>
  <li><strong>Passive Entry Passive Start (PEPS)</strong> — keyless entry and push-button start</li>
  <li><strong>Automatic headlamps and rain-sensing wipers</strong> — on Pure Plus A and above</li>
  <li><strong>Cruise control</strong> — useful for highway runs</li>
  <li><strong>iTPMS (Tyre Pressure Monitoring)</strong> — real-time tyre pressure alerts</li>
  <li><strong>Auto-folding ORVMs</strong> — folds mirrors automatically on locking</li>
</ul>

<h2>Safety: 6 Airbags Standard Across Every Variant</h2>
<p>
This is perhaps the most headline-worthy decision Tata has made. Every single Tiago — even the base Smart variant at ₹4.69 lakh — now comes with <strong>6 airbags as standard</strong>. Add ABS with EBD, corner stability control, electronic stability program, hill hold control and ISOFIX child-seat mounts, and the Tiago's safety credentials are simply unmatched at this price point.
</p>
<p>
The 360-degree camera on higher trims makes tight city parking significantly safer, and the Blind View Monitor adds a layer of confidence during lane changes. The previous generation Tiago earned 4 stars in adult safety and 3 stars for child safety in the Global NCAP 2020 test — the new model has not been tested yet, but the hardware suggests it can only do better.
</p>

<h2>Engine &amp; Performance: Unchanged but Still Solid</h2>
<table style="width:100%;border-collapse:collapse;margin:1.5rem 0;font-size:.9rem;">
  <thead>
    <tr style="background:#1e293b;color:#fff;">
      <th style="padding:11px 16px;text-align:left;">Parameter</th>
      <th style="padding:11px 16px;text-align:left;">Petrol</th>
      <th style="padding:11px 16px;text-align:left;">iCNG</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#f8fafc;">
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;font-weight:600;">Engine</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">1.2L naturally aspirated</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">1.2L + factory CNG kit</td>
    </tr>
    <tr>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;font-weight:600;">Power</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">86 PS</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">75.5 PS</td>
    </tr>
    <tr style="background:#f8fafc;">
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;font-weight:600;">Torque</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">113 Nm</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">96.5 Nm</td>
    </tr>
    <tr>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;font-weight:600;">Gearbox</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">5-speed MT / 5-speed AMT</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">5-speed MT / 5-speed AMT</td>
    </tr>
    <tr style="background:#f8fafc;">
      <td style="padding:9px 16px;font-weight:600;">Claimed Efficiency</td>
      <td style="padding:9px 16px;">~19–20 kmpl</td>
      <td style="padding:9px 16px;">~26 km/kg</td>
    </tr>
  </tbody>
</table>
<p>
The CNG + AMT combination deserves a special mention. Tata is the first manufacturer to offer an AMT gearbox paired with a factory CNG kit in a hatchback — and it even comes with paddle shifters. For city buyers who want the economy of CNG without the hassle of a manual gearbox in stop-go traffic, this is genuinely exciting.
</p>

<h2>All Variant Prices — ICE Facelift (Ex-Showroom, Delhi)</h2>
<table style="width:100%;border-collapse:collapse;margin:1.5rem 0;font-size:.9rem;">
  <thead>
    <tr style="background:#dc2626;color:#fff;">
      <th style="padding:11px 16px;text-align:left;">Variant</th>
      <th style="padding:11px 16px;text-align:left;">Fuel</th>
      <th style="padding:11px 16px;text-align:left;">Gearbox</th>
      <th style="padding:11px 16px;text-align:right;">Price</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#fef2f2;">
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;font-weight:600;">Smart</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;">Petrol</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;">Manual</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;text-align:right;">₹4.69 L</td>
    </tr>
    <tr>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;font-weight:600;">Pure</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;">Petrol</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;">Manual</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;text-align:right;">₹5.49 L</td>
    </tr>
    <tr style="background:#fef2f2;">
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;font-weight:600;">Smart CNG</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;">CNG</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;">AMT</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;text-align:right;">₹5.79 L</td>
    </tr>
    <tr>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;font-weight:600;">Pure Plus</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;">Petrol</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;">Manual</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;text-align:right;">₹5.99 L</td>
    </tr>
    <tr style="background:#fef2f2;">
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;font-weight:600;">Pure CNG</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;">CNG</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;">AMT</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;text-align:right;">₹6.49 L</td>
    </tr>
    <tr>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;font-weight:600;">Pure Plus A</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;">Petrol</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;">Manual</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;text-align:right;">₹6.49 L</td>
    </tr>
    <tr style="background:#fef2f2;">
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;font-weight:600;">Creative</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;">Petrol</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;">Manual</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;text-align:right;">₹6.99 L</td>
    </tr>
    <tr>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;font-weight:600;">Pure Plus CNG</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;">CNG</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;">AMT</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;text-align:right;">₹6.99 L</td>
    </tr>
    <tr style="background:#fef2f2;">
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;font-weight:600;">Creative Plus</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;">Petrol</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;">Manual</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fecaca;text-align:right;">₹7.29 L</td>
    </tr>
    <tr>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;font-weight:600;">Pure Plus A CNG</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;">CNG</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;">AMT</td>
      <td style="padding:9px 16px;border-bottom:1px solid #fee2e2;text-align:right;">₹7.49 L</td>
    </tr>
    <tr style="background:#fef2f2;">
      <td style="padding:9px 16px;font-weight:600;">Creative CNG</td>
      <td style="padding:9px 16px;">CNG</td>
      <td style="padding:9px 16px;">AMT</td>
      <td style="padding:9px 16px;text-align:right;font-weight:700;">₹7.99 L</td>
    </tr>
  </tbody>
</table>

<h2>The Tiago EV Facelift: 293 km for ₹6.99 Lakh</h2>
<p>
The electric sibling gets the same exterior and interior refresh as the ICE version — sharper LED lighting, redesigned front fascia, new digital instrument cluster and the cleaned-up cabin. Under the skin, it carries over the proven electric powertrain with a claimed MIDC range of <strong>293 km</strong>, making it one of the longest-range affordable EVs in India.
</p>
<p>
At ₹6.99 lakh ex-showroom, the Tiago EV undercuts nearly every other EV in the market by a significant margin. If you have home charging available, the running cost works out to a fraction of the petrol version — making the ₹2.3 lakh premium over the base ICE look very justifiable over time.
</p>
<p>
Watch the official launch video below for the complete walkthrough of the Tiago EV facelift:
</p>

<h2>How It Stacks Up Against Rivals</h2>
<table style="width:100%;border-collapse:collapse;margin:1.5rem 0;font-size:.9rem;">
  <thead>
    <tr style="background:#1e293b;color:#fff;">
      <th style="padding:11px 16px;text-align:left;">Car</th>
      <th style="padding:11px 16px;text-align:right;">Starting Price</th>
      <th style="padding:11px 16px;text-align:left;">Airbags (base)</th>
      <th style="padding:11px 16px;text-align:left;">Notable Edge</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#fef2f2;">
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;font-weight:700;color:#dc2626;">Tata Tiago Facelift</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;text-align:right;font-weight:700;">₹4.69 L</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;font-weight:600;">6 (all variants)</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">360° cam, CNG+AMT</td>
    </tr>
    <tr>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">Maruti Suzuki Alto K10</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;text-align:right;">₹3.70 L</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">2</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">Cheaper entry price</td>
    </tr>
    <tr style="background:#fef2f2;">
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">Maruti Suzuki Swift</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;text-align:right;">₹5.79 L</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">6</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">Sportier drive feel</td>
    </tr>
    <tr>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">Hyundai Grand i10 Nios</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;text-align:right;">₹5.55 L</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">2</td>
      <td style="padding:9px 16px;border-bottom:1px solid #e2e8f0;">Refined cabin feel</td>
    </tr>
    <tr style="background:#fef2f2;">
      <td style="padding:9px 16px;">Citroen C3</td>
      <td style="padding:9px 16px;text-align:right;">₹4.99 L</td>
      <td style="padding:9px 16px;">2</td>
      <td style="padding:9px 16px;">European styling</td>
    </tr>
  </tbody>
</table>
<p>
The Tiago wins on safety hardware at this price point — no other car in this segment offers 6 airbags standard across every single variant. The 360-degree camera is also a segment first at this price.
</p>

<h2>Which Variant Should You Buy?</h2>
<p><strong>Tight budget, maximum safety → Smart (₹4.69L).</strong> You get 6 airbags, ABS, ESC and hill hold. Skip the infotainment, keep the safety. Solid choice for a first car.</p>
<p><strong>Best all-round value → Pure Plus (₹5.99L).</strong> This is where the Tiago gets genuinely exciting. You get the large 10.25-inch screen, 360-degree camera, iRA connected tech, LED headlamps and wireless CarPlay — for under ₹6 lakh.</p>
<p><strong>High city usage, want automatic + cheap running costs → Smart CNG AMT (₹5.79L).</strong> India's first CNG hatchback with an AMT gearbox. Crawling through traffic without pressing a clutch, on fuel that costs roughly half of petrol — this is the practical city winner.</p>
<p><strong>Want everything → Creative Plus (₹7.29L).</strong> PEPS, auto headlamps, rain-sensing wipers, blind view monitor, dual wireless charging, paddle shifters on AMT — this is a ₹10 lakh car's feature list at ₹7.29 lakh.</p>
<p><strong>EV route → Tiago EV Facelift (₹6.99L).</strong> If you have a home charger, this is the most economical choice over a 5-year ownership period. The 293 km range handles most real-world usage comfortably.</p>

<h2>Verdict: The Hatchback That Makes the Most Sense in 2026</h2>
<p>
The 2026 Tata Tiago Facelift is not a revolutionary reimagining — it is a confident, well-executed refresh that fixes every meaningful weakness of the outgoing model. The exterior now turns heads, the interior no longer feels like an entry-level compromise, and the feature list routinely embarrasses cars in segments above.
</p>
<p>
Six airbags standard. 360-degree camera available. CNG with AMT. A proper EV for under ₹7 lakh. No other hatchback in India ticks so many boxes simultaneously. If you are shopping for a small car in 2026, the Tiago — in whatever powertrain suits your life — has to be on your shortlist.
</p>
<blockquote>
<strong>Launch Day Pricing Summary:</strong> Tata Tiago Facelift (ICE) — ₹4.69 lakh to ₹7.99 lakh | Tata Tiago EV Facelift — from ₹6.99 lakh. All prices ex-showroom, New Delhi. May 28, 2026.
</blockquote>
""".strip()


def seed_forward(apps, schema_editor):
    Publication = apps.get_model('blog', 'Publication')
    Tag = apps.get_model('blog', 'Tag')
    Article = apps.get_model('blog', 'Article')

    # ── Publication ───────────────────────────────────────────
    pub, _ = Publication.objects.get_or_create(
        slug='auto-cars',
        defaults={
            'name': 'Auto & Cars',
            'description': (
                'Latest car launches, reviews, pricing, and auto news '
                'from India and around the world.'
            ),
            'icon': '🚗',
            'color': '#dc2626',
        },
    )

    # ── Tags ──────────────────────────────────────────────────
    tag_names = [
        'cars', 'hatchback', 'tata', 'auto-news', 'india',
        'new-launch-2026', 'electric-vehicle', 'ev', 'tata-tiago', 'cng',
    ]
    tags = []
    for name in tag_names:
        t, _ = Tag.objects.get_or_create(name=name)
        tags.append(t)

    # ── Article ───────────────────────────────────────────────
    SLUG = 'tata-tiago-facelift-2026-launched-4-69-lakh'
    if Article.objects.filter(slug=SLUG).exists():
        return  # already seeded — skip

    article = Article(
        title=(
            '2026 Tata Tiago & Tiago EV Facelift Launched: '
            'ICE from \u20b94.69L, EV from \u20b96.99L \u2014 Complete Guide'
        ),
        subtitle=(
            '6 airbags standard, 360\u00b0 camera, CNG+AMT first, '
            '293km EV range \u2014 everything you need to know about both launches'
        ),
        slug=SLUG,
        content=ARTICLE_CONTENT,
        cover_image=(
            'https://images.unsplash.com/photo-1494976388531-d1058494cdd8'
            '?w=1200&h=630&fit=crop&q=80'
        ),
        video_url='https://www.youtube.com/watch?v=MN-ZszUS2Cg',
        publication=pub,
        status='published',
        read_time=8,
        word_count=1650,
        meta_description=(
            '2026 Tata Tiago Facelift starts at \u20b94.69L with 6 airbags standard, '
            '360\u00b0 camera and India\u2019s first CNG+AMT hatchback. '
            'Tiago EV from \u20b96.99L with 293km range. '
            'Full pricing, specs and variant guide.'
        ),
        published_at=timezone.now(),
    )
    article.save()
    article.tags.set(tags)


def seed_reverse(apps, schema_editor):
    Article = apps.get_model('blog', 'Article')
    Article.objects.filter(
        slug='tata-tiago-facelift-2026-launched-4-69-lakh'
    ).delete()
    # Leave publication and tags intact (other articles may use them later)


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_newslettersubscriber_article_video_url_userprofile_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_forward, seed_reverse),
    ]
