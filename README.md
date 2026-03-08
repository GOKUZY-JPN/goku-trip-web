# GOKU TRIP Web — Tour Booking Site

## 構成
- **Flask** (Python) — バックエンド
- **PostgreSQL** — DB（Railway提供）
- **Stripe Checkout** — 決済
- **Railway** — ホスティング

## ローカルで動かす

```bash
# 1. 依存関係インストール
pip install -r requirements.txt

# 2. 環境変数設定
cp .env.example .env
# .envを編集してStripeキー等を入力

# 3. DB初期化
flask db init
flask db migrate -m "init"
flask db upgrade

# 4. 起動
python run.py
```

## Railwayへのデプロイ手順

1. https://railway.app にアクセスしてGitHubでログイン
2. **New Project** → **Deploy from GitHub repo** → このリポジトリを選択
3. **Add Plugin** → **PostgreSQL** を追加
4. **Variables** タブで以下を設定：
   ```
   DATABASE_URL  → RailwayのPostgreSQL URLを自動入力（${{Postgres.DATABASE_URL}}）
   SECRET_KEY    → ランダムな文字列
   STRIPE_SECRET_KEY      → sk_live_xxxx
   STRIPE_PUBLISHABLE_KEY → pk_live_xxxx
   STRIPE_WEBHOOK_SECRET  → whsec_xxxx（後で設定）
   YOUR_DOMAIN   → https://your-app.up.railway.app
   ```
5. デプロイ後、コンソールで：
   ```
   flask db upgrade
   ```
6. StripeのWebhook URLに登録：
   `https://your-domain.com/booking/webhook`

## ドメイン紐付け

Railwayの **Settings → Domains** からカスタムドメインを追加できる。
DNSのCNAMEレコードをRailwayの指定先に向けるだけ。

## DBにツアーデータを入れる

Railwayコンソールで：

```python
from app import create_app, db
from app.models.models import Tour, TourOption, TourPricing, TourSchedule
from datetime import date

app = create_app()
with app.app_context():
    # ツアー追加
    tour = Tour(name="Kyoto Private Tour", description="...", duration_hours=6, max_capacity=8)
    db.session.add(tour)
    db.session.flush()

    # オプション追加
    opt = TourOption(tour_id=tour.id, name="Lunch included", description="Traditional kaiseki lunch")
    db.session.add(opt)
    db.session.flush()

    # 価格設定（1-4人: 15000円/人、5人以上: 12000円/人）
    db.session.add(TourPricing(tour_id=tour.id, option_id=opt.id, min_people=1, max_people=4, price_per_person=15000))
    db.session.add(TourPricing(tour_id=tour.id, option_id=opt.id, min_people=5, max_people=15, price_per_person=12000))

    # スケジュール追加
    db.session.add(TourSchedule(tour_id=tour.id, date=date(2025, 4, 1), start_time="09:00", capacity=8))

    db.session.commit()
```

## フェーズ2：ガイド管理統合

`Guide` と `GuideAssignment` テーブルはすでにDBに存在。
`app/routes/guide.py` を追加して `/guide/*` ルートを実装するだけ。
