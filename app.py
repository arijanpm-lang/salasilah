from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'secretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ======================
# Models
# ======================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class FamilyMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    birth_date = db.Column(db.String(50))
    father_id = db.Column(db.Integer, db.ForeignKey('family_member.id'), nullable=True)
    mother_id = db.Column(db.Integer, db.ForeignKey('family_member.id'), nullable=True)

    # Relationship betul untuk self-referential
    children_father = db.relationship(
        'FamilyMember',
        backref=db.backref('father', remote_side=[id]),
        foreign_keys=[father_id],
        lazy='dynamic'
    )
    children_mother = db.relationship(
        'FamilyMember',
        backref=db.backref('mother', remote_side=[id]),
        foreign_keys=[mother_id],
        lazy='dynamic'
    )

# ======================
# Login Manager
# ======================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ======================
# Routes
# ======================
@app.route('/')
def index():
    return redirect(url_for('login'))

# ---------- Login ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Username atau password salah')
    return render_template('login.html')

# ---------- Register ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan')
            return redirect(url_for('register'))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Register berjaya! Sila login')
        return redirect(url_for('login'))
    return render_template('register.html')

# ---------- Logout ----------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ---------- Dashboard ----------
@app.route('/dashboard')
@login_required
def dashboard():
    members = FamilyMember.query.all()
    
    # Kumpul pasangan (father + mother) dan anak-anak mereka
    pairs_dict = {}
    singles = []
    for member in members:
        if not member.father_id and not member.mother_id:
            singles.append(member)
        else:
            key = (member.father_id, member.mother_id)
            if key not in pairs_dict:
                pairs_dict[key] = []
            pairs_dict[key].append(member)

    paired_roots = []
    for (father_id, mother_id), children in pairs_dict.items():
        father = FamilyMember.query.get(father_id) if father_id else None
        mother = FamilyMember.query.get(mother_id) if mother_id else None
        paired_roots.append((father, mother, children))

    return render_template('dashboard.html', paired_roots=paired_roots, singles=singles)

# ---------- Add Member ----------
@app.route('/add_member', methods=['GET', 'POST'])
@login_required
def add_member():
    members = FamilyMember.query.all()
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form.get('birth_date') or None
        father_id = request.form.get('father_id') or None
        mother_id = request.form.get('mother_id') or None

        member = FamilyMember(
            name=name,
            birth_date=birth_date,
            father_id=father_id,
            mother_id=mother_id
        )
        db.session.add(member)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_member.html', members=members)

# ---------- Edit Member ----------
@app.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
@login_required
def edit_member(member_id):
    member = FamilyMember.query.get_or_404(member_id)
    members = FamilyMember.query.filter(FamilyMember.id != member_id).all()
    if request.method == 'POST':
        member.name = request.form['name']
        member.birth_date = request.form.get('birth_date') or None
        member.father_id = request.form.get('father_id') or None
        member.mother_id = request.form.get('mother_id') or None
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_member.html', member=member, members=members)

# ======================
# Run App
# ======================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)