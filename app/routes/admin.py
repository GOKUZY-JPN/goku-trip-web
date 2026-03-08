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

    tour = Tour(
        name="Kyoto: Uji Matcha & UNESCO History Tour",
        description="Discover the heartland of Japan's highest quality green tea & matcha on a guided walking tour in Uji. Begin at the world's oldest teahouse (est. 1160 AD, same family for 24 generations), enjoy a hands-on tea-tasting experience with top-grade Gyokuro, visit Ujigami Shrine, stroll the historic tea merchant street, and explore Byodo-in Temple — a UNESCO World Heritage Site.",
        duration_hours=3,
        max_capacity=6
    )
    db.session.add(tour)
    db.session.flush()

    opt1 = TourOption(tour_id=tour.id, name="Standard", description="Guided walking tour with tea-tasting")
    db.session.add(opt1)
    db.session.flush()

    db.session.add(TourPricing(tour_id=tour.id, option_id=opt1.id, min_people=1, max_people=6, price_per_person=8000))

    today = date.today()
    count = 0
    for i in range(90):
        d = today + timedelta(days=i)
        if d.weekday() in [1, 3, 5]:
            db.session.add(TourSchedule(tour_id=tour.id, date=d, start_time="09:30", capacity=6))
            count += 1
        if count >= 20:
            break

    db.session.commit()
    return jsonify({'success': True, 'tour_id': tour.id})

@admin_bp.route('/admin/tours')
def list_tours():
    if not check_auth(request):
        return jsonify({'error': 'Unauthorized'}), 401
    tours = Tour.query.all()
    return jsonify([{'id': t.id, 'name': t.name} for t in tours])
