from flask import Flask, redirect, url_for, render_template, session
from flask_login import LoginManager, login_required, current_user
from config import Config
from extensions import db  # ✅ Now from extensions
from models import User, SiteStat
from auth import auth_bp
from tools.routes import tools_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(tools_bp)

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ✅ Ensure this is defined correctly
@app.before_first_request
def initialize_database():
    with app.app_context():
        db.create_all()

# ✅ Inject site stats into all templates
@app.context_processor
def inject_site_stats():
    stat = SiteStat.query.first()
    if not stat:
        stat = SiteStat(visitors=0, files_converted=0)
        db.session.add(stat)
        db.session.commit()
    return dict(total_visitors=stat.visitors, total_conversions=stat.files_converted)

# ✅ Homepage Route
@app.route('/')
def home():
    stat = SiteStat.query.first()
    if not stat:
        stat = SiteStat(visitors=1, files_converted=0)
    else:
        stat.visitors += 1
    db.session.add(stat)
    db.session.commit()
    return render_template('home.html')

# ✅ Dashboard Route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

# ✅ Reset session for guest uses (for testing only)
@app.route('/reset-guest-uses')
def reset_guest_uses():
    session['guest_uses'] = 0
    return redirect(url_for('home'))

# ✅ Entry point (for local development)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
