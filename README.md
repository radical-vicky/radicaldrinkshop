# DrinkShop — Django drink delivery site

A Django e-commerce site for selling drinks with delivery to a customer's
apartment/doorstep, paid for via M-Pesa STK Push (Safaricom Daraja API).

## What's included

- **store** app — categories, products, session cart, saved delivery
  addresses (building, apartment number, floor, street, area, notes, GPS pin),
  registration/login via django-allauth (including Google sign-in).
- **orders** app — checkout, `Order` / `OrderItem` models, order history.
- **payments** app — M-Pesa Daraja integration: STK push, callback handler,
  live payment-status polling.
- Product images stored on **Cloudinary** (not local disk), so they survive
  redeploys on hosts with an ephemeral filesystem.
- **Google Sign-In** (and standard email/password accounts) via
  django-allauth.
- **GPS location capture** — customers can tap "Use my current location"
  when adding an address; the coordinates are saved and shown as a Google
  Maps link to you and to delivery riders.
- **Dark glassmorphism UI** in green/orange/gold — an auto-playing hero
  slider that pulls real photos from your featured products, a scrolling
  offers marquee, and voucher-style promo cards, all built with original
  inline SVG icons (no emoji, no icon-font dependency). An optional,
  admin-uploadable sitewide background image (Cloudinary-backed) sits
  dimmed behind the glass UI. Fonts load from Fontshare (Clash Display,
  Satoshi) and Google Fonts (JetBrains Mono) — an internet connection is
  needed for those to render as designed; without it, the browser falls
  back to system fonts and the layout still works.
- Django admin for managing products, orders and M-Pesa transactions.
- `seed_products` management command with sample non-alcoholic drinks.

### A note on alcohol

Kenya's NACADA regulations currently restrict online sale and home delivery
of alcohol. The `Product.is_alcoholic` flag plus the `DISALLOW_ALCOHOL_DELIVERY`
setting (on by default) prevent alcoholic products from being added to a
cart or checked out. If your legal situation differs, you can set
`DISALLOW_ALCOHOL_DELIVERY=False` in `.env` — but confirm with a local
lawyer or regulator first, this isn't legal advice.

## 1. Local setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # then fill in real values (see below)

python manage.py migrate
python manage.py seed_products    # optional: adds sample drinks
python manage.py createsuperuser  # for /admin/

python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the shop and `/admin/` to manage
products, categories, orders and stock.

## 2. Feature products in the hero slider

The homepage hero now pulls real product photos from your catalog instead
of generic art. In `/admin/` → **Store → Products**, open a product and
under **Homepage hero slider**:

- Tick **Is featured** to include it in the hero.
- Optionally set a **Hero tagline** (small badge text, e.g. "20% off
  today"), **Hero headline** (big text — defaults to the product name),
  and **Hero description** (defaults to the product's normal description).
- Upload a product **image** (stored on Cloudinary — see below) so the
  hero shows an actual photo. Without one, it falls back to a simple line
  icon so the layout never breaks.

Feature 2–4 products for a good slider. If nothing is marked featured yet,
the hero shows a few of your most recent in-stock products automatically
so a fresh install never looks empty.

## 3. Set a sitewide background image

In `/admin/` → **Store → Site settings**, upload a **Background image**
(any image you have the rights to use — your own photography, or a stock
photo you've properly licensed) and make sure **Is active** is checked.
It's stored on Cloudinary and shown dimmed behind the glass UI sitewide.
Leave it blank to keep the plain dark background. Only one active row is
used at a time (the most recently created).

**Note:** don't hot-link images from stock photo marketplaces (Depositphotos,
Shutterstock, Getty, etc.) — their preview URLs are copyrighted and using
them on a live site without a purchased license and/or attribution per
their terms is copyright infringement. Upload a properly licensed image
here instead.

## 4. Set up Cloudinary (product images)

1. Create a free account at https://cloudinary.com and open the Console —
   it shows your **Cloud name**, **API key**, and **API secret**.
2. Put them in `.env`:
   ```
   CLOUDINARY_CLOUD_NAME=...
   CLOUDINARY_API_KEY=...
   CLOUDINARY_API_SECRET=...
   ```
3. That's it — any image uploaded through `/admin/` (Product → image) now
   goes to Cloudinary automatically. If these are left blank, the site
   falls back to storing images on local disk (fine for quick local dev,
   not for production).

## 5. Set up Google Sign-In

1. Go to https://console.cloud.google.com/apis/credentials and create an
   **OAuth 2.0 Client ID** (Application type: Web application).
2. Add an **Authorized redirect URI**:
   `https://<your-domain>/accounts/google/login/callback/`
   (for local testing: `http://127.0.0.1:8000/accounts/google/login/callback/`)
3. Put the client ID/secret in `.env`:
   ```
   GOOGLE_OAUTH_CLIENT_ID=...
   GOOGLE_OAUTH_CLIENT_SECRET=...
   ```
4. Log into `/admin/` → **Sites** → edit the default site (id=1) so its
   **Domain name** matches where you're running the app (e.g.
   `127.0.0.1:8000` locally, or `yourdomain.com` in production). Google
   login won't work until this matches.
5. Restart the server. "Sign in with Google" now appears on the
   login/signup pages. Regular username+password accounts still work too.

## 6. GPS delivery location

On the "Add delivery address" page, customers can tap **📍 Use my current
location** to capture GPS coordinates via their browser (`navigator.geolocation`
— requires HTTPS in production, works on `http://127.0.0.1` for local dev).
The coordinates are saved on the address and shown as a **View pinned
location on map** link on the addresses page, checkout, and order detail —
handy for your delivery rider to find the exact spot instead of relying on
the typed address alone. If the customer declines the browser's location
permission, they can still fill in the address fields manually.

## 7. Set delivery zones & pricing

Delivery fees are per-neighbourhood, not one flat rate. In `/admin/` under
**Store → Delivery zones**, add a zone per estate/neighbourhood with its own
fee and estimated delivery time (e.g. Kilimani — KES 100 — 30 min).

- Matching is by case-insensitive substring against the customer's saved
  `area` field, so a zone named "Kilimani" matches an address with area
  "Kilimani, near Yaya Centre".
- Any address whose area doesn't match a configured zone falls back to the
  flat `DELIVERY_FEE` from `.env`.
- Set a zone's **is_active** to off to temporarily stop deliveries there —
  it'll show as unavailable at checkout instead of being charged the
  default fee.
- `seed_products` adds a few sample Nairobi zones (Kilimani, Westlands,
  Lavington, Kileleshwa, South B, South C) to get you started.

## 8. Add your own products

Easiest: log into `/admin/`, add **Categories**, then **Products** (upload
an image, set price in KES, stock, and whether it's alcoholic).

## 9. Set up M-Pesa (Daraja API)

1. Create a free account at https://developer.safaricom.co.ke
2. Create a new app → this gives you a **Consumer Key** and **Consumer Secret**.
3. For testing, use the sandbox **Lipa Na M-Pesa Online** shortcode `174379`
   and the sandbox passkey shown on the Daraja "Test Credentials" page.
4. Put these in your `.env`:
   ```
   MPESA_ENV=sandbox
   MPESA_CONSUMER_KEY=...
   MPESA_CONSUMER_SECRET=...
   MPESA_SHORTCODE=174379
   MPESA_PASSKEY=...
   MPESA_CALLBACK_URL=https://<your-public-url>/payments/mpesa/callback/
   ```
5. Safaricom must be able to reach `MPESA_CALLBACK_URL` over the public
   internet. For local dev, run `ngrok http 8000` and use the ngrok HTTPS
   URL + `/payments/mpesa/callback/`.
6. Sandbox test phone number: `254708374149` (any amount works).
7. When you're ready to go live, apply for a production shortcode/paybill
   from Safaricom, set `MPESA_ENV=production`, and update the three
   credentials plus `MPESA_CALLBACK_URL` to your real domain.

### How the payment flow works

1. Customer checks out → an `Order` (status `pending_payment`) and
   `OrderItem`s are created.
2. The server calls `stk_push()`, which prompts the customer's phone for
   their M-Pesa PIN, and stores a matching `MpesaTransaction`.
3. Customer is shown a "waiting for confirmation" page that polls
   `/payments/status/<order_id>/` every 3 seconds.
4. Safaricom calls back to `/payments/mpesa/callback/` with the result.
   On success, the transaction is marked `success` and the order `paid`.

## 10. Deploying

- Set `DJANGO_DEBUG=False`, a strong `DJANGO_SECRET_KEY`, and real
  `DJANGO_ALLOWED_HOSTS` / `DJANGO_CSRF_TRUSTED_ORIGINS` in `.env`.
- Swap SQLite for Postgres in production (edit `DATABASES` in
  `drinkshop/settings.py`, or wire up `dj-database-url`).
- Serve static files with `python manage.py collectstatic` behind
  nginx/whitenoise, and run the app with `gunicorn drinkshop.wsgi`.
- Put the app behind HTTPS — required for the M-Pesa callback URL anyway.
- Consider a proper delivery-zone/rider-assignment system once volume
  grows; the current delivery fee is a flat rate from `DELIVERY_FEE`.

## 11. The design system

Everything lives in `static/css/style.css` as CSS custom properties at the
top of the file (`:root`), so re-theming doesn't require hunting through
templates:

```css
--void: #060907;      /* page background */
--green: #2FA66B;     /* primary brand / CTAs */
--orange: #FF8A3D;    /* secondary accent */
--gold: #E8B93C;      /* offers, vouchers, premium accents */
--panel: rgba(22, 30, 25, 0.55);  /* glass card fill */
```

Icons are inline SVG `<symbol>` defs in `templates/includes/icons.html`,
referenced elsewhere as `<svg><use href="#icon-name"/></svg>` — add a new
`<symbol>` there to add an icon anywhere in the site without a new
dependency. The hero slider's product art is original line-art SVG (not
stock photography), so there's nothing to license — swap in real product
photos via `product.image` (Cloudinary) once you've got your own.

## 12. Project layout

```
drinkshop/
├── manage.py
├── requirements.txt
├── .env.example
├── drinkshop/        # project settings & URLs
├── store/             # products, cart, addresses, auth
├── orders/            # checkout, orders
├── payments/           # M-Pesa Daraja integration
├── templates/          # base.html + shared templates
└── static/css/         # styling
```
