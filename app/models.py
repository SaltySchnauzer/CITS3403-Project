from app import db 


# Table stores account user information such as a user id, username and password. 
class Accounts(db.Model): 
    user_id = db.Column(db.Integer, primary_key=True) 
    user_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False) 

 
