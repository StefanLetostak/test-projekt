from flask import Flask, render_template, redirect, url_for, request, jsonify, Response, stream_with_context
from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired
import openai

app = Flask(__name__)
app.secret_key = 'tajny_kluc'  # Potrebné pre WTForms

class WeatherForm(FlaskForm):
    mesiac = SelectField('Mesiac', choices=[('1', 'Január'), ('2', 'Február'), ('3', 'Marec'), ('4', 'Apríl'), ('5', 'Máj'), ('6', 'Jún'), ('7', 'Júl'), ('8', 'August'), ('9', 'September'), ('10', 'Október'), ('11', 'November'), ('12', 'December')], validators=[DataRequired()])
    teplota = FloatField('Teplota (°C)', validators=[DataRequired()])
    smer = SelectField('Smer vetra', choices=[('S', 'Sever'), ('J', 'Juh'), ('V', 'Východ'), ('Z', 'Západ')], validators=[DataRequired()])
    rychlost = FloatField('Rýchlosť vetra (m/s)', validators=[DataRequired()])
    tlak = FloatField('Tlak vzduchu (hPa)', validators=[DataRequired()])
    oblacnost = IntegerField('Oblačnosť (%)', validators=[DataRequired()])
    vlhkost = IntegerField('Vlhkosť (%)', validators=[DataRequired()])
    submit = SubmitField('Predpovedať zrážky')

# Chatbot OpenAI client a história
client = openai.OpenAI(
    api_key="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"
)

chat_history = [
    {"role": "system", "content": "Si chat ktorý je odborník na otázku ohľadom ľudských generácii a odpovedáš na otázky na projekt o generáciách X,Y,Z a alpha"},
]

@app.route('/<int:page>')
def show_page(page):
    # Definuj obsah pre každú stranu
    pages = {
        1: {
            'img': 'obrazky/strana_navrh.png',
            'video': None,
            'prev': None,
            'next': 2
        },
        2: {
            'img': 'obrazky/druha_strana.png',
            'video': None,
            'prev': 1,
            'next': 3
        },
        3: {
            'img': None,
            'video': 'videa/video_test.mp4',
            'prev': 2,
            'next': 'form'
        },
        4: {
            'img': None,
            'video': None,
            'prev': 3,
            'next': 'chatbot'
        }
    }
    data = pages.get(page)
    if not data:
        return "Stránka neexistuje", 404
    return render_template('page.html', page=page, **data)

@app.route('/form', methods=['GET', 'POST'])
def show_form():
    form = WeatherForm()
    zrazky_predpoved = None
    if form.validate_on_submit():
        # Tu by bola logika predikcie zrážok, zatiaľ len príklad
        zrazky_predpoved = round(float(form.teplota.data) * 0.1 + float(form.vlhkost.data) * 0.05, 2)
    return render_template('form.html', form=form, zrazky_predpoved=zrazky_predpoved)

@app.route('/chatbot', methods=['GET'])
def show_chatbot():
    return render_template('index.html', chat_history=chat_history)

@app.route('/chat', methods=['POST'])
def chat():
    content = request.json["message"]
    chat_history.append({"role": "user", "content": content})
    return jsonify(success=True)

@app.route('/stream', methods=['GET'])
def stream():
    def generate():
        assistant_response_content = ""
        with client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=chat_history,
            stream=True,
            max_tokens=500,
        ) as stream:
            for chunk in stream:
                if chunk.choices[0].delta and chunk.choices[0].delta.content:
                    assistant_response_content += chunk.choices[0].delta.content
                    yield f"data: {chunk.choices[0].delta.content}\n\n"
                if chunk.choices[0].finish_reason == "stop":
                    break
        chat_history.append({"role": "assistant", "content": assistant_response_content})
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route('/reset', methods=['POST'])
def reset_chat():
    global chat_history
    chat_history = [{"role": "system", "content": "Si chat ktorý je odborník na otázku ohľadom ľudských generácii a odpovedáš na otázky na projekt o generáciách X,Y,Z a alpha"}]
    return jsonify(success=True)

@app.route('/')
def index():
    return show_page(1)

@app.route('/zaver')
def zaver():
    return render_template('zaver.html', img='obrazky/zaver.png', video=None)


if __name__ == '__main__':
    app.run(debug=True)