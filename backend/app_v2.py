from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emailsender.db'
db = SQLAlchemy(app)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Sender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    opened = db.Column(db.Integer, default=0)
    clicked = db.Column(db.Integer, default=0)

# CRUD Operations for Campaigns
@app.route('/campaigns', methods=['GET', 'POST'])
def manage_campaigns():
    if request.method == 'POST':
        data = request.get_json()  
        new_campaign = Campaign(name=data['name'])
        db.session.add(new_campaign)
        db.session.commit()
        return jsonify({'id': new_campaign.id}), 201
    else:
        campaigns = Campaign.query.all()
        return jsonify([{'id': c.id, 'name': c.name} for c in campaigns])

@app.route('/campaigns/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'id': campaign.id, 'name': campaign.name})
    elif request.method == 'PUT':
        data = request.get_json()
        campaign.name = data['name']
        db.session.commit()
        return jsonify({'message': 'Campaign updated'})
    elif request.method == 'DELETE':
        db.session.delete(campaign)
        db.session.commit()
        return jsonify({'message': 'Campaign deleted'})

# CRUD Operations for Templates
@app.route('/templates', methods=['GET', 'POST'])
def manage_templates():
    if request.method == 'POST':
        data = request.get_json()  
        new_template = Template(content=data['content'])
        db.session.add(new_template)
        db.session.commit()
        return jsonify({'id': new_template.id}), 201
    else:
        templates = Template.query.all()
        return jsonify([{'id': t.id, 'content': t.content} for t in templates])

@app.route('/templates/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_template(id):
    template = Template.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'id': template.id, 'content': template.content})
    elif request.method == 'PUT':
        data = request.get_json()
        template.content = data['content']
        db.session.commit()
        return jsonify({'message': 'Template updated'})
    elif request.method == 'DELETE':
        db.session.delete(template)
        db.session.commit()
        return jsonify({'message': 'Template deleted'})

# CRUD Operations for Leads
@app.route('/leads', methods=['GET', 'POST'])
def manage_leads():
    if request.method == 'POST':
        data = request.get_json()  
        new_lead = Lead(email=data['email'])
        db.session.add(new_lead)
        db.session.commit()
        return jsonify({'id': new_lead.id}), 201
    else:
        leads = Lead.query.all()
        return jsonify([{'id': l.id, 'email': l.email} for l in leads])

@app.route('/leads/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_lead(id):
    lead = Lead.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'id': lead.id, 'email': lead.email})
    elif request.method == 'PUT':
        data = request.get_json()
        lead.email = data['email']
        db.session.commit()
        return jsonify({'message': 'Lead updated'})
    elif request.method == 'DELETE':
        db.session.delete(lead)
        db.session.commit()
        return jsonify({'message': 'Lead deleted'})

# CRUD Operations for Senders
@app.route('/senders', methods=['GET', 'POST'])
def manage_senders():
    if request.method == 'POST':
        data = request.get_json()  
        new_sender = Sender(name=data['name'])
        db.session.add(new_sender)
        db.session.commit()
        return jsonify({'id': new_sender.id}), 201
    else:
        senders = Sender.query.all()
        return jsonify([{'id': s.id, 'name': s.name} for s in senders])

@app.route('/senders/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_sender(id):
    sender = Sender.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'id': sender.id, 'name': sender.name})
    elif request.method == 'PUT':
        data = request.get_json()
        sender.name = data['name']
        db.session.commit()
        return jsonify({'message': 'Sender updated'})
    elif request.method == 'DELETE':
        db.session.delete(sender)
        db.session.commit()
        return jsonify({'message': 'Sender deleted'})

# CRUD Operations for Analytics
@app.route('/analytics', methods=['GET', 'POST'])
def manage_analytics():
    if request.method == 'POST':
        data = request.get_json()  
        new_analytics = Analytics(campaign_id=data['campaign_id'], opened=data['opened'], clicked=data['clicked'])
        db.session.add(new_analytics)
        db.session.commit()
        return jsonify({'id': new_analytics.id}), 201
    else:
        analytics = Analytics.query.all()
        return jsonify([{'id': a.id, 'campaign_id': a.campaign_id, 'opened': a.opened, 'clicked': a.clicked} for a in analytics])

@app.route('/analytics/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_analytics(id):
    analytics = Analytics.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'id': analytics.id, 'campaign_id': analytics.campaign_id, 'opened': analytics.opened, 'clicked': analytics.clicked})
    elif request.method == 'PUT':
        data = request.get_json()
        analytics.opened = data['opened']
        analytics.clicked = data['clicked']
        db.session.commit()
        return jsonify({'message': 'Analytics updated'})
    elif request.method == 'DELETE':
        db.session.delete(analytics)
        db.session.commit()
        return jsonify({'message': 'Analytics deleted'})

if __name__ == '__main__':
    db.create_all()  # create database tables if they don't exist
    app.run(debug=True)