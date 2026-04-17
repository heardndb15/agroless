from flask import Blueprint, jsonify, request
from models import db, Field, Expense, Harvest, User
import requests
import os
import google.generativeai as genai
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email уже зарегистрирован'}), 400
    
    user = User(email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Успешная регистрация', 'user': {'email': user.email}}), 201

@api.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data.get('email')).first()
    if user and user.check_password(data.get('password')):
        # В реальной жизни тут возвращается JWT токен
        return jsonify({'message': 'Успешный вход', 'user': {'email': user.email}})
    return jsonify({'error': 'Неверный email или пароль'}), 401

@api.route('/fields', methods=['GET', 'POST'])
def handle_fields():
    if request.method == 'POST':
        data = request.json
        new_field = Field(
            name=data['name'], area_ha=data['area_ha'],
            crop=data['crop'], lat=data['lat'], lon=data['lon'],
            planted_at=datetime.strptime(data['planted_at'], '%Y-%m-%d').date()
        )
        db.session.add(new_field)
        db.session.commit()
        return jsonify({"message": "Поле добавлено"}), 201
    
    fields = Field.query.all()
    return jsonify([{
        "id": f.id, "name": f.name, "area_ha": f.area_ha, "crop": f.crop,
        "lat": f.lat, "lon": f.lon, "planted_at": f.planted_at.isoformat()
    } for f in fields])

@api.route('/expenses', methods=['GET', 'POST'])
def handle_expenses():
    if request.method == 'POST':
        data = request.json
        new_exp = Expense(
            field_id=data['field_id'], category=data['category'],
            amount=data['amount'], unit_price=data['unit_price'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date()
        )
        db.session.add(new_exp)
        db.session.commit()
        return jsonify({"message": "Расход добавлен"}), 201
        
    expenses = Expense.query.all()
    return jsonify([{
        "id": e.id, "field_id": e.field_id, "category": e.category,
        "amount": e.amount, "unit_price": e.unit_price, "date": e.date.isoformat(),
        "total": e.amount * e.unit_price
    } for e in expenses])

@api.route('/harvests', methods=['GET', 'POST'])
def handle_harvests():
    if request.method == 'POST':
        data = request.json
        new_harvest = Harvest(
            field_id=data['field_id'], yield_tons=data['yield_tons'],
            sell_price_per_ton=data['sell_price_per_ton'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date()
        )
        db.session.add(new_harvest)
        db.session.commit()
        return jsonify({"message": "Урожай добавлен"}), 201
        
    harvests = Harvest.query.all()
    return jsonify([{
        "id": h.id, "field_id": h.field_id, "yield_tons": h.yield_tons,
        "sell_price_per_ton": h.sell_price_per_ton, "date": h.date.isoformat(),
        "revenue": h.yield_tons * h.sell_price_per_ton
    } for h in harvests])

@api.route('/dashboard', methods=['GET'])
def get_dashboard():
    expenses = Expense.query.all()
    harvests = Harvest.query.all()
    
    total_expenses = sum(e.amount * e.unit_price for e in expenses)
    total_revenue = sum(h.yield_tons * h.sell_price_per_ton for h in harvests)
    profit = total_revenue - total_expenses
    roi = (profit / total_expenses * 100) if total_expenses > 0 else 0
    
    expense_by_cat = {}
    for e in expenses:
        cat = e.category
        expense_by_cat[cat] = expense_by_cat.get(cat, 0) + (e.amount * e.unit_price)

    return jsonify({
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "profit": profit,
        "roi": roi,
        "expense_by_category": expense_by_cat
    })

@api.route('/recommendations/weather/<int:field_id>', methods=['GET'])
def get_weather(field_id):
    field = db.session.get(Field, field_id)
    if not field:
        return jsonify({"error": "Field not found"}), 404
        
    url = f"https://api.open-meteo.com/v1/forecast?latitude={field.lat}&longitude={field.lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        daily = data.get('daily', {})
        precip = daily.get('precipitation_sum', [])
        
        recommendation = "Прогноз благоприятный."
        if precip and sum(precip[:7]) > 10:
            recommendation = "Ожидаются дожди, отложите полив."
        elif precip and sum(precip[:7]) < 2:
            recommendation = "Сухая неделя, запланируйте полив."
            
        return jsonify({
            "daily": daily,
            "recommendation": recommendation
        })
    return jsonify({"error": "Failed to fetch weather"}), 500

@api.route('/analytics/ai', methods=['POST'])
def ai_analytics():
    data = request.json
    question = data.get("question", "Проанализируй мои данные")
    
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "dummy"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    fields = Field.query.all()
    expenses = Expense.query.all()
    harvests = Harvest.query.all()
    
    # --- АГЕНТ 1: Метеоролог (Прогноз погоды) ---
    weather_reports = []
    for f in fields:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={f.lat}&longitude={f.lon}&daily=precipitation_sum,temperature_2m_max&timezone=auto"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                daily = resp.json().get('daily', {})
                precip = sum(daily.get('precipitation_sum', [0][:7]))
                temp_max = sum(daily.get('temperature_2m_max', [0][:7])) / 7 # средняя макс температура
                weather_reports.append(f"Поле '{f.name}': Осадки за 7 дней = {precip:.1f} мм, Ср. макс температура = {temp_max:.1f}°C.")
        except:
            continue
    agent1_weather = " ".join(weather_reports) if weather_reports else "Нет данных о погоде."

    # --- АГЕНТ 2: Агро-Бухгалтер (Калькуляция и Вычеты) ---
    total_expenses = sum(e.amount * e.unit_price for e in expenses)
    total_revenue = sum(h.yield_tons * h.sell_price_per_ton for h in harvests)
    profit = total_revenue - total_expenses
    roi = (profit / total_expenses * 100) if total_expenses > 0 else 0
    cost_per_ha = total_expenses / sum(f.area_ha for f in fields) if fields else 0
    agent2_finance = f"Всего расходов: {total_expenses} ₸. Выручка: {total_revenue} ₸. Чистая прибыль: {profit} ₸. Рентабельность (ROI): {roi:.1f}%. Траты на 1 гектар: {cost_per_ha:.1f} ₸/га."

    # --- ГЛАВНЫЙ ОРКЕСТРАТОР: Gemini ИИ ---
    context = f"""
Ты Главный Агроном. К тебе поступили отчеты от твоих субагентов по хозяйству:
1. ИНФОРМАЦИЯ О ПОЛЯХ: {[f"{f.name} ({f.area_ha} га, {f.crop})" for f in fields]}
2. ОТЧЕТ АГЕНТА-МЕТЕОРОЛОГА: {agent1_weather}
3. ОТЧЕТ АГЕНТА-БУХГАЛТЕРА: {agent2_finance}

Задача: Проанализируй эти отчеты. Сделай конкретные вычеты (например, если мало дождей и низкая рентабельность, предложи оптимизацию полива или смену культуры). НЕ выдумывай данные, опирайся строго на отчеты агентов. Ответь на запрос фермера.

Запрос фермера: {question}
    """

    try:
        response = model.generate_content(context)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
