from flask import Blueprint, jsonify, request, render_template
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

    def add_schedules(tour_id, start_time, capacity, days=60):
        for i in range(days):
            db.session.add(TourSchedule(
                tour_id=tour_id,
                date=today + timedelta(days=i),
                start_time=start_time,
                capacity=capacity
            ))

    tours_data = [
        # 既存ツアー
        {
            'name': 'Kyoto: Uji Matcha & UNESCO History Tour',
            'description': "Discover the heartland of Japan's highest quality green tea & matcha on a guided walking tour in Uji. Begin at the world's oldest teahouse (est. 1160 AD, same family for 24 generations), enjoy a hands-on tea-tasting experience with top-grade Gyokuro, visit Ujigami Shrine — Japan's oldest original Shinto shrine, stroll the historic tea merchant street, and explore Byodo-in Temple, a UNESCO World Heritage Site.",
            'duration_hours': 3, 'max_capacity': 6, 'area': 'uji', 'price': 20700, 'start_time': '09:30',
        },
        {
            'name': 'Kyoto: Fushimi Inari Night Walking Tour',
            'description': "Discover the mystical beauty of Fushimi Inari Shrine at night on a guided walking tour. Stroll through the iconic vermilion torii gates in a quiet, uncrowded atmosphere and learn about the shrine's rich history. Experience the spiritual and intimate side of one of Kyoto's most iconic locations, illuminated by lanterns at dusk.",
            'duration_hours': 2, 'max_capacity': 10, 'area': 'kyoto', 'price': 20700, 'start_time': '18:00',
        },
        {
            'name': 'Kyoto: Nijo Castle & Imperial Palace Guided Tour',
            'description': "Explore Kyoto's rich history and culture on a guided walking tour. Visit Nijo Castle and the Kyoto Imperial Palace — two of Japan's most iconic landmarks. Learn about the political intrigues and architectural wonders of the past, and discover the seasonal beauty of the Imperial Palace gardens.",
            'duration_hours': 3, 'max_capacity': 8, 'area': 'kyoto', 'price': 20700, 'start_time': '09:00',
        },
        {
            'name': 'Nara: UNESCO World Heritage & Deer Park Tour',
            'description': "Explore the cultural heart of Japan on a private tour of Nara's iconic UNESCO World Heritage Sites. Feed the friendly sacred deer, visit Kasuga Grand Shrine surrounded by an ancient primeval forest, and marvel at the world's largest bronze Buddha statue inside Todai-ji Temple.",
            'duration_hours': 3, 'max_capacity': 8, 'area': 'nara', 'price': 20700, 'start_time': '09:00',
        },
        {
            'name': 'Kanazawa Castle & Kenroku-en Garden Tour',
            'description': "Experience the beauty of Kanazawa on a private walking tour with a veteran guide. Explore Kenroku-en Garden — one of Japan's three most celebrated gardens — Kanazawa Castle, the samurai district, and tea ceremony shops. Meet local artisans and discover the hidden stories of this 'little Kyoto' of Japan.",
            'duration_hours': 3, 'max_capacity': 8, 'area': 'kanazawa', 'price': 20700, 'start_time': '09:30',
        },
        {
            'name': 'Himeji Castle: Expert Samurai History Tour',
            'description': "Explore Himeji Castle — a UNESCO World Heritage Site — on a 3-hour guided walking tour. A certified local guide will take you through the castle's hidden corners and strategic defense features, sharing stories of samurai, ninja, princesses, and spies.",
            'duration_hours': 3, 'max_capacity': 8, 'area': 'himeji', 'price': 20700, 'start_time': '10:00',
        },
        # 新規ツアー
        {
            'name': 'Kyoto, Your Way: A Personalized 4-Hour Exploration',
            'description': "Shape your half-day in Kyoto with iconic landmarks, hidden gems, and serene paths — crafted by your local host to match what excites you most. See both iconic sights and tucked-away corners, set your own rhythm, and experience Kyoto through local eyes. Explore Gion's historic streets, Ishibei-koji Alley, Ninenzaka & Sannenzaka slopes, Kodaiji Temple, and the serene Shirakawa Canal. Your multilingual host adapts in real time to match your mood.",
            'duration_hours': 4, 'max_capacity': 8, 'area': 'kyoto', 'price': 20700, 'start_time': '09:00',
        },
        {
            'name': 'Your First Day in Kyoto: City Essentials & Cultural Insights',
            'description': "Ease into Kyoto's rhythm with a thoughtful 3-hour introduction to its iconic sights, cultural nuances, and local tips — leaving you ready to explore with confidence. Master transit tips and IC card usage, visit Gion's historic streets and Tofukuji Temple, learn about geisha traditions and Zen principles, and discover famous landmarks alongside quiet lesser-known gems.",
            'duration_hours': 3, 'max_capacity': 8, 'area': 'kyoto', 'price': 20700, 'start_time': '09:00',
        },
        {
            'name': 'Your Osaka, Your Way: A 4-Hour Experience Tailored to You',
            'description': "Discover Osaka's contrasts with a half-day experience blending iconic highlights and hidden gems, all shaped around what excites you most. Explore Kuromon Ichiba Market, Hozenji Yokocho's nostalgic alleyways, Dotonbori's neon wonderland, and the hidden Namba Yasaka Shrine. Your local host curates every stop to match your interests.",
            'duration_hours': 4, 'max_capacity': 8, 'area': 'osaka', 'price': 20700, 'start_time': '09:00',
        },
        {
            'name': 'Half Day in Kobe with a Local',
            'description': "Discover Kobe's unique charm with a personalized half-day experience. Visit Ikuta Shrine — one of Japan's oldest Shinto shrines dating to the 3rd century — explore the beautiful seafront, discover hidden neighborhoods, and experience the city's famous food culture including Kobe beef. Your host tailors every moment to your interests.",
            'duration_hours': 4, 'max_capacity': 8, 'area': 'other', 'price': 20700, 'start_time': '09:00',
        },
        {
            'name': 'Essential Nara: Famous Sights & Local Stories',
            'description': "Start with Nara's famous temples and deer park, then slip into peaceful streets and local life with your host. Visit Todai-ji Temple with the Great Buddha, stroll Nara Park among sacred deer, explore Kasuga Taisha Shrine's lantern-lined forest paths, and discover Naramachi's preserved old merchant quarter. A balanced day from grand landmarks to quiet local rhythms.",
            'duration_hours': 6, 'max_capacity': 8, 'area': 'nara', 'price': 31500, 'start_time': '09:00',
        },
    ]

    added = []
    for td in tours_data:
        tour = Tour(
            name=td['name'],
            description=td['description'],
            duration_hours=td['duration_hours'],
            max_capacity=td['max_capacity'],
            area=td.get('area', 'kyoto')
        )
        db.session.add(tour)
        db.session.flush()

        opt = TourOption(tour_id=tour.id, name="Standard", description="Private guided tour")
        db.session.add(opt)
        db.session.flush()

        db.session.add(TourPricing(
            tour_id=tour.id, option_id=opt.id,
            min_people=1, max_people=td['max_capacity'],
            price_per_person=td['price']
        ))

        add_schedules(tour.id, td['start_time'], td['max_capacity'])
        added.append(td['name'])

    db.session.commit()
    return jsonify({'success': True, 'tours_added': len(added), 'tours': added})


@admin_bp.route('/admin/tours')
def list_tours():
    if not check_auth(request):
        return jsonify({'error': 'Unauthorized'}), 401
    tours = Tour.query.all()
    return jsonify([{'id': t.id, 'name': t.name, 'area': t.area} for t in tours])


@admin_bp.route('/admin/tours_detail')
def tours_detail():
    if not check_auth(request):
        return jsonify({'error': 'Unauthorized'}), 401
    tours = Tour.query.all()
    result = []
    for t in tours:
        price = None
        if t.options and t.options[0].pricing:
            price = t.options[0].pricing[0].price_per_person
        result.append({
            'id': t.id, 'name': t.name, 'area': t.area,
            'duration_hours': t.duration_hours,
            'description': t.description,
            'image_url': t.image_url,
            'price_per_person': price
        })
    return jsonify(result)


@admin_bp.route('/admin/tour/<int:tour_id>', methods=['POST'])
def update_tour(tour_id):
    if not check_auth(request):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    tour = Tour.query.get_or_404(tour_id)
    tour.name = data.get('name', tour.name)
    tour.area = data.get('area', tour.area)
    tour.duration_hours = data.get('duration_hours', tour.duration_hours)
    tour.description = data.get('description', tour.description)
    tour.image_url = data.get('image_url', tour.image_url)
    if data.get('price_per_person') and tour.options and tour.options[0].pricing:
        tour.options[0].pricing[0].price_per_person = data['price_per_person']
    db.session.commit()
    return jsonify({'success': True})


@admin_bp.route('/admin')
def admin_index():
    if not check_auth(request):
        return jsonify({'error': 'Unauthorized'}), 401
    return render_template('admin_tours.html')
