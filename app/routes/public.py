from flask import Blueprint, render_template, jsonify, request
from ..models.models import Tour, TourSchedule, TourPricing, TourOption
from .. import db
from datetime import date

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    tours = Tour.query.filter_by(is_active=True).all()
    return render_template('index.html', tours=tours)


@public_bp.route('/tours/<int:tour_id>')
def tour_detail(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    options = TourOption.query.filter_by(tour_id=tour_id, is_active=True).all()
    return render_template('tour_detail.html', tour=tour, options=options)


# API: 日付ごとの残席数を返す
@public_bp.route('/api/availability/<int:tour_id>')
def availability(tour_id):
    schedules = TourSchedule.query.filter(
        TourSchedule.tour_id == tour_id,
        TourSchedule.date >= date.today()
    ).all()
    return jsonify([{
        'date': s.date.isoformat(),
        'schedule_id': s.id,
        'available': s.available_spots,
        'capacity': s.capacity,
        'start_time': s.start_time
    } for s in schedules])


# API: 人数・オプションから金額を計算して返す
@public_bp.route('/api/price')
def calculate_price():
    tour_id = request.args.get('tour_id', type=int)
    option_id = request.args.get('option_id', type=int)
    num_people = request.args.get('num_people', type=int, default=1)

    pricing = TourPricing.query.filter(
        TourPricing.tour_id == tour_id,
        TourPricing.option_id == option_id,
        TourPricing.min_people <= num_people,
        TourPricing.max_people >= num_people
    ).first()

    if not pricing:
        # option_idなしでフォールバック
        pricing = TourPricing.query.filter(
            TourPricing.tour_id == tour_id,
            TourPricing.option_id == None,
            TourPricing.min_people <= num_people,
            TourPricing.max_people >= num_people
        ).first()

    if pricing:
        total = pricing.price_per_person * num_people
        return jsonify({'price_per_person': pricing.price_per_person, 'total': total})
    return jsonify({'error': 'pricing not found'}), 404
