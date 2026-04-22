from datetime import datetime
from . import db


class Tour(db.Model):
    __tablename__ = 'tours'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_hours = db.Column(db.Float)
    max_capacity = db.Column(db.Integer, default=10)
    image_url = db.Column(db.String(500))
    area = db.Column(db.String(50), default="kyoto")  # kyoto/osaka/nara/kanazawa/himeji/other
    area = db.Column(db.String(50), default="kyoto")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    options = db.relationship('TourOption', backref='tour', lazy=True)
    schedules = db.relationship('TourSchedule', backref='tour', lazy=True)


class TourOption(db.Model):
    __tablename__ = 'tour_options'
    id = db.Column(db.Integer, primary_key=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tours.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)   # e.g. "昼食あり", "昼食なし"
    description = db.Column(db.String(300))
    area = db.Column(db.String(50), default="kyoto")
    is_active = db.Column(db.Boolean, default=True)

    pricing = db.relationship('TourPricing', backref='option', lazy=True)


class TourPricing(db.Model):
    __tablename__ = 'tour_pricing'
    id = db.Column(db.Integer, primary_key=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tours.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('tour_options.id'), nullable=True)
    min_people = db.Column(db.Integer, nullable=False, default=1)
    max_people = db.Column(db.Integer, nullable=False, default=99)
    price_per_person = db.Column(db.Integer, nullable=False)  # JPY (円)


class TourSchedule(db.Model):
    __tablename__ = 'tour_schedules'
    id = db.Column(db.Integer, primary_key=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tours.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(10))   # "09:00"
    capacity = db.Column(db.Integer, nullable=False)
    booked_count = db.Column(db.Integer, default=0)

    @property
    def available_spots(self):
        return self.capacity - self.booked_count

    @property
    def is_available(self):
        return self.available_spots > 0


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tours.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('tour_schedules.id'), nullable=True)
    option_id = db.Column(db.Integer, db.ForeignKey('tour_options.id'), nullable=True)

    # お客さん情報
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(200), nullable=False)
    num_people = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)  # JPY

    # どこからの予約か
    source = db.Column(db.String(50), default='own_site')
    # 'own_site' | 'gyg' | 'airbnb' | 'viator' | 'manual'

    # Stripe
    stripe_session_id = db.Column(db.String(200))
    stripe_payment_intent = db.Column(db.String(200))
    payment_status = db.Column(db.String(50), default='pending')
    # 'pending' | 'paid' | 'cancelled' | 'refunded'

    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tour = db.relationship('Tour', backref='bookings')
    schedule = db.relationship('TourSchedule', backref='bookings')
    option = db.relationship('TourOption', backref='bookings')


# ガイド向け（フェーズ2統合用 - テーブルだけ先に作っておく）
class Guide(db.Model):
    __tablename__ = 'guides'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200))
    languages = db.Column(db.String(200))  # "ja,en,es"
    area = db.Column(db.String(50), default="kyoto")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assignments = db.relationship('GuideAssignment', backref='guide', lazy=True)


class GuideAssignment(db.Model):
    __tablename__ = 'guide_assignments'
    id = db.Column(db.Integer, primary_key=True)
    guide_id = db.Column(db.Integer, db.ForeignKey('guides.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('tour_schedules.id'), nullable=False)
    status = db.Column(db.String(50), default='assigned')  # 'assigned' | 'confirmed' | 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
