from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from ..models.models import Booking, TourSchedule, Tour
from .. import db
import stripe
import os

booking_bp = Blueprint('booking', __name__)
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
YOUR_DOMAIN = os.environ.get('YOUR_DOMAIN', 'http://localhost:5000')


@booking_bp.route('/checkout', methods=['POST'])
def create_checkout():
    data = request.get_json()
    tour_id = data.get('tour_id')
    schedule_id = data.get('schedule_id')
    option_id = data.get('option_id')
    num_people = data.get('num_people', 1)
    customer_name = data.get('customer_name')
    customer_email = data.get('customer_email')
    total_price = data.get('total_price')  # フロントで計算済みの金額（円）

    tour = Tour.query.get_or_404(tour_id)
    schedule = TourSchedule.query.get(schedule_id)

    if schedule and schedule.available_spots < num_people:
        return jsonify({'error': 'Not enough availability'}), 400

    # Stripe Checkout セッション作成
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'jpy',
                'product_data': {
                    'name': tour.name,
                    'description': f'{num_people}名 / {schedule.date.strftime("%Y-%m-%d") if schedule else ""}',
                },
                'unit_amount': total_price,
            },
            'quantity': 1,
        }],
        mode='payment',
        customer_email=customer_email,
        success_url=YOUR_DOMAIN + '/booking/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=YOUR_DOMAIN + f'/tours/{tour_id}',
        metadata={
            'tour_id': tour_id,
            'schedule_id': schedule_id or '',
            'option_id': option_id or '',
            'num_people': num_people,
            'customer_name': customer_name,
        }
    )

    # 仮予約レコード作成
    booking = Booking(
        tour_id=tour_id,
        schedule_id=schedule_id,
        option_id=option_id,
        customer_name=customer_name,
        customer_email=customer_email,
        num_people=num_people,
        total_price=total_price,
        source='own_site',
        stripe_session_id=session.id,
        payment_status='pending'
    )
    db.session.add(booking)
    db.session.commit()

    return jsonify({'checkout_url': session.url})


@booking_bp.route('/success')
def success():
    session_id = request.args.get('session_id')
    booking = Booking.query.filter_by(stripe_session_id=session_id).first()
    return render_template('booking_success.html', booking=booking)


@booking_bp.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except Exception:
        return '', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        booking = Booking.query.filter_by(stripe_session_id=session['id']).first()
        if booking:
            booking.payment_status = 'paid'
            booking.stripe_payment_intent = session.get('payment_intent')

            # 残席を減らす
            if booking.schedule_id:
                schedule = TourSchedule.query.get(booking.schedule_id)
                if schedule:
                    schedule.booked_count += booking.num_people

            db.session.commit()

    return '', 200
