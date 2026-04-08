from flask import Blueprint, jsonify, request
from ..models.models import Tour, TourOption, TourPricing, TourSchedule
from .. import db
from datetime import date, timedelta
import os

admin_bp = Blueprint('admin', __name__)

def check_auth(req):
    token = req.args.get('token') or req.headers.get('X-Admin-Token')
    return token == os.environ.get('ADMIN_TOKEN', 'gokutrip-admin')

@admin_bp.route('/admin/seed')
def seed():
    if not check_auth(request):
        return jsonify({'error': 'Unauthorized'}), 401

    TourSchedule.query.delete()
    TourPricing.query.delete()
    TourOption.query.delete()
    Tour.query.delete()
    db.session.commit()

    today = date.today()

    # ツアー1: Uji Matcha Tour
    t1 = Tour(
        name="Kyoto: Uji Matcha & UNESCO History Tour",
        description="Discover the heartland of Japan's highest quality green tea & matcha on a guided walking tour in Uji. Begin at the world's oldest teahouse (est. 1160 AD, same family for 24 generations), enjoy a hands-on tea-tasting experience with top-grade Gyokuro, visit Ujigami Shrine (Japan's oldest original Shinto shrine), stroll the historic tea merchant street, and explore Byodo-in Temple — a UNESCO World Heritage Site.",
        duration_hours=3,
        max_capacity=6
    )
    db.session.add(t1)
    db.session.flush()

    o1 = TourOption(tour_id=t1.id, name="Standard", description="Guided walking tour with tea-tasting")
    db.session.add(o1)
    db.session.flush()
    db.session.add(TourPricing(tour_id=t1.id, option_id=o1.id, min_people=1, max_people=6, price_per_person=20700))

    for i in range(60):
        db.session.add(TourSchedule(tour_id=t1.id, date=today + timedelta(days=i), start_time="09:30", capacity=6))

    # ツアー2: Your First Day in Kyoto (3時間)
    t2 = Tour(
        name="Your First Day in Kyoto: City Essentials & Cultural Insights",
        description="Ease into Kyoto's rhythm with a thoughtful 3-hour introduction to its iconic sights, cultural nuances, and local tips — leaving you ready to explore with confidence. Master transit tips, visit Gion's historic streets and Tofukuji Temple, learn about geisha traditions and Zen principles, and discover famous landmarks alongside quiet, lesser-known gems.",
        duration_hours=3,
        max_capacity=8
    )
    db.session.add(t2)
    db.session.flush()

    o2 = TourOption(tour_id=t2.id, name="Standard", description="Private guided walking tour")
    db.session.add(o2)
    db.session.flush()
    db.session.add(TourPricing(tour_id=t2.id, option_id=o2.id, min_people=1, max_people=8, price_per_person=20700))

    for i in range(60):
        db.session.add(TourSchedule(tour_id=t2.id, date=today + timedelta(days=i), start_time="09:00", capacity=8))

    # ツアー3: Kyoto Your Way (4時間)
    t3 = Tour(
        name="Kyoto, Your Way: A Personalized 4-Hour Exploration",
        description="Shape your half-day in Kyoto with iconic landmarks, hidden gems, and serene paths — crafted by your local host to match what excites you most! See both iconic sights and tucked-away corners, set your own rhythm, and experience Kyoto through local eyes. Your multilingual host adapts in real time to match your mood and interests.",
        duration_hours=4,
        max_capacity=8
    )
    db.session.add(t3)
    db.session.flush()

    o3 = TourOption(tour_id=t3.id, name="Standard", description="Private personalized walking tour")
    db.session.add(o3)
    db.session.flush()
    db.session.add(TourPricing(tour_id=t3.id, option_id=o3.id, min_people=1, max_people=8, price_per_person=20700))

    for i in range(60):
        db.session.add(TourSchedule(tour_id=t3.id, date=today + timedelta(days=i), start_time="09:00", capacity=8))

    db.session.commit()
    return jsonify({'success': True, 'tours_added': 3})

@admin_bp.route('/admin/tours')
def list_tours():
    if not check_auth(request):
        return jsonify({'error': 'Unauthorized'}), 401
    tours = Tour.query.all()
    return jsonify([{'id': t.id, 'name': t.name} for t in tours])
