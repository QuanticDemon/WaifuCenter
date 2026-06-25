from flask import *
from flask_sqlalchemy import SQLAlchemy
import uuid
import bcrypt
import string
import secrets
from sqlalchemy import *
from datetime import *
import smtplib
from email.message import EmailMessage
import os
app = Flask(__name__)
app.secret_key = "ansdandoUAINXIAXSJALSNXASFMSKDFMKSDNFKSDNFKNJSNFSJDFN"


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///waifucenter.db"

db = SQLAlchemy(app)

def gen_token(value):

    char = string.ascii_letters + string.digits + string.punctuation

    tokenGen = ''.join(secrets.choice(char) for _ in range(value))

    return tokenGen





class Waifus(db.Model):
    id_waifu = db.Column(
            db.String(36),
            primary_key = True,
            default= lambda:str(uuid.uuid4())
            )
    name = db.Column(
            db.String(200),
            nullable = False
            )
    
    description = db.Column(
            db.Text,
            nullable = True
            )

    image = db.Column(
            db.String(500),
            nullable= True
            )

    @classmethod
    def create_waifu(cls, name, description, image):
        NewWaifu = cls(
                name = name,
                description = description,
                image = image
                )

        db.session.add(NewWaifu)
        db.session.commit()
        
        return NewWaifu


class Users(db.Model):
    id_user = db.Column(
            db.String(36),
            primary_key = True,
            default= lambda:str(uuid.uuid4())
            )
    username = db.Column(
            db.String(200),
            nullable = False
            )
    mail = db.Column(
            db.String(200),
            nullable = False,
            unique = True
            )
    password = db.Column(
            db.String(100),
            nullable = False
            )

    user_pic = db.Column(
            db.String(500),
            nullable = True,
            default = False
            )
    is_verified = db.Column(
            db.Boolean,
            nullable = False,
            default = False
            )


    @classmethod
    def create_account(cls, name, mail, password):      
        pass_hashing_encode = password.encode('utf-8')
        salts = bcrypt.gensalt(rounds=12)
        hashing = bcrypt.hashpw(pass_hashing_encode, salts)
        hashing_toString = hashing.decode('utf-8')


        NewUser = cls(
                username = name,
                mail = mail,
                password = hashing_toString
                )

        db.session.add(NewUser)
        db.session.commit()

        return NewUser

    @classmethod
    def sing_in_user(cls, userToken, password):
        existed_user = cls.query.filter(
                or_(cls.username == userToken, cls.mail==userToken)

                ).first()
        if not existed_user:
            return False,None

        try: 
            pass_input = password.encode('utf-8')
            pass_inDb = existed_user.password.encode('utf-8')
            if bcrypt.checkpw(pass_input, pass_inDb):
                return True, existed_user
            else:
                return False, None
        except (ValueError, AttributeError, TypeError):
            return False, None

        return None

class Friendships(db.Model):
    id_friendship = db.Column(
            db.String(36),
            primary_key = True,
            default=lambda:str(uuid.uuid4())
            )
    id_mc = db.Column(
            db.String(36),
            db.ForeignKey('users.id_user'),
            nullable = False

            )
    id_friend = db.Column(
            db.String(36),
            db.ForeignKey('users.id_user'),
            nullable = False
            )

    fs_status = db.Column(
            db.String(100),
            nullable = False
            )

    @classmethod
    def create_friendship(cls, id_mc, id_friend, status):
    
        
        existed_friendship = cls.query.filter_by(
                id_mc = session.get('id'),
                id_friend = id_friend,
                fs_status = "pending"
                ).first()

        if existed_friendship:
            return redirect(url_for('friends'))


        NewFriend = cls(
                id_mc = id_mc,
                id_friend = id_friend,
                fs_status = status
                )

        db.session.add(NewFriend)
        db.session.commit()
        return NewFriend

    @classmethod
    def del_fs(cls, id_mc, id_friend):
        del_fs_query = cls.query.filter(
                cls.id_mc == id_mc,
                cls.id_friend == id_friend
                ).first()

        if not del_fs_query:
            return False

        db.session.delete(del_fs_query)
        db.session.commit()

        return True

        



class Tokens(db.Model):
    id_token = db.Column(
            db.String(36),
            primary_key = True,
            default = lambda:str(uuid.uuid4())
    )

    token = db.Column(
            db.String(6),
            nullable = False,
            default = lambda:gen_token(6)
            )

    type_token = db.Column(
            db.String(100),
            nullable = False
            )

    creation_datetime = db.Column(
            db.DateTime,
            nullable = False,
            default=datetime.utcnow
            )
    expiration_datetime = db.Column(
            db.DateTime,
            nullable = True,
            default = datetime.utcnow() + timedelta(minutes=15)
            )

    @classmethod
    def create_token(cls, type_token):
        NewToken = cls(
                type_token = type_token
                )

        db.session.add(NewToken)
        db.session.commit()

        return NewToken

class Messages(db.Model):
    id_message = db.Column(
            db.String(36),
            primary_key = True,
            default=lambda:str(uuid.uuid4())

            )
    id_emisor = db.Column(
            db.String(36),
            
            )
    id_receptor = db.Column(
            db.String(36)
            )

    text_content = db.Column(
            db.Text,
            nullable = False
            )
    send_date = db.Column(
            db.DateTime,
            nullable = False,
            default = datetime.utcnow
            )

    @classmethod
    def send(cls, id_emisor, id_receptor, content):

        new_message = cls(
                id_emisor = id_emisor,
                id_receptor = id_receptor,
                text_content = content
                )

        db.session.add(new_message)
        db.session.commit()

        return new_message

class Chats(db.Model):
    id_chat= db.Column(
            db.String(36),
            primary_key=True,
            default=lambda:str(uuid.uuid4())
            )

    id_user = db.Column(
            db.String(36),
            db.ForeignKey('messages.id_emisor'),
            nullable=False
            )
    id_friend = db.Column(
            db.String(36),
            db.ForeignKey('messages.id_receptor'),
            nullable=False
            )
    id_message = db.Column(
            db.String(36),
            db.ForeignKey('messages.id_message'),
            )

    status = db.Column(
            db.String(100),
            nullable=False
            )

    @classmethod
    def new_chat(cls, id_user, id_friend):
        existed_chat = cls.query.filter_by(id_user = id_user, id_friend = id_friend).first()

        if existed_chat:
            return redirect(url_for('priv_chat', chat_id_friend=id_friend))

        NewChat = cls(
                id_user = id_user,
                id_friend = id_friend,
                status = "Active"
                )
        db.session.add(NewChat)
        db.session.commit()

        return NewChat

        

class Bridge(db.Model):
    id_bridge = db.Column(
            db.String(36),
            primary_key = True,
            default=lambda:str(uuid.uuid4())

    )

    id_user = db.Column(
            db.String(36),
            db.ForeignKey('users.id_user'),
            nullable = False
    )

    id_token = db.Column(
            db.String(36),
            db.ForeignKey('tokens.id_token'),
            nullable = True
            )

    id_waifu = db.Column(
            db.String(36),
            db.ForeignKey('waifus.id_waifu'),
            )


    user = db.relationship('Users')
    token = db.relationship('Tokens')
    waifu = db.relationship('Waifus')
    
    @classmethod
    def create_bridge_account(cls, id_user, id_token):
        NewBridge = cls(
                id_user = id_user,
                id_token = id_token
                )
        db.session.add(NewBridge)
        db.session.commit()

        return NewBridge

    @classmethod
    def create_bridge_waifu(cls, id_user, id_waifu):
        NewBridge = cls(
                id_user = id_user,
                id_waifu = id_waifu
                )

        db.session.add(NewBridge)
        db.session.commit()

        return NewBridge








@app.context_processor
def inject():
    mail = session.get('mail')
    username = session.get('username')
    user_id = session.get('id')

    user = Users.query.filter_by(id_user = user_id).first()

    if not user:
        return {}

    return{
            "mail":user.mail,
            "username":user.username,
            "id":user_id,
            "picture":user.user_pic
            }

@app.route('/home', methods=["GET", "POST"])
def home():
  
  if "id" not in session:
    return redirect(url_for('login'))

  
  tables = (
          Waifus.query.join(Bridge, Waifus.id_waifu == Bridge.id_waifu).filter(Bridge.id_user == session.get('id')).all()

          )


  return render_template("home.html", tables=tables) 
@app.route('/register', methods=["GET", "POST"])
def register_user():
    session.clear()
    if request.method == "POST":
       data = request.get_json();
       username = data.get('username')
       mail = data.get('mail')
       password = data.get('pass')

       mail =mail.replace(" ","")
       password = password.replace(" ","")
       user = Users.create_account(username, mail, password)
       
       

       if user:
           token = Tokens.create_token('email_verification')
           sender = EmailMessage()
           sender['From'] = 'g2jyostin@gmail.com'
           sender['To'] = user.mail
           sender['Subject'] = "Verification Code Waifu Center"
           sender.set_content(
                f"Verification Code is: {token.token}"
                   )
           server_connex = smtplib.SMTP_SSL(
                   "smtp.gmail.com",
                   465
                   )
           server_connex.login(
                   "g2jyostin@gmail.com",
                   "xfqo kmjo vctz tras"
                   )
           server_connex.send_message(sender)
           server_connex.quit()

           bridge = Bridge.create_bridge_account(user.id_user, token.id_token)
           
           session['id'] = user.id_user
           session['username'] = user.username
           session['mail'] =user.mail
            
           return {
                   "success":True
                   }



    return render_template('register.html')

@app.route('/register/verification', methods=["GET", "POST"])
def verification():
    temp_mail = session.get('mail')
    if request.method == "GET":
         return render_template('verification.html', temp_mail = temp_mail)


    
    if request.method == "POST":
        data = request.get_json()
        code = data.get('code')
        print("DATA:", data)
        print("CODE:", code)

        bridge = Bridge.query.filter_by(id_user = session.get('id')).first()
        
        if not bridge:
             return {"success": False, "error": "bridge_not_found"}, 400
        token = Tokens.query.filter_by(id_token = bridge.id_token).first()
        user = Users.query.filter_by(id_user = session.get('id')).first()

        if token and code == token.token:
            user.is_verified = True
            db.session.commit()
            return {
                    "success":True,


                    }
        else:
            return {
                    "success":False
                    }

@app.route('/sign-in', methods=["GET","POST"])
def login():
    session.clear()
    

    if request.method == "POST":
       data = request.get_json()

       userToken = data.get('user')
       password = data.get('pass')

       verification,user = Users.sing_in_user(userToken, password)
       if user and verification:
           session['id'] = user.id_user
           session['username'] = user.username
           session['mail'] = user.mail
           return {
                   "success":True
                   }
       else:
            return {
                   "success":False
                   }


               



    return render_template('login.html')

@app.route('/home/add-waifu', methods=["POST"])
def process_waifu_data():
    
    name_waifu = request.form.get('waifu-name')
    description_waifu = request.form.get('waifu-description')
    image_waifu = request.files.get('waifu-image')

    if not image_waifu:
        image_waifu = None
    filename, extension = os.path.splitext(image_waifu.filename)
    filename = str(uuid.uuid4()) + extension
    path = os.path.join(upload_images, filename)
    image_waifu.save(path)

    waifu = Waifus.create_waifu(name_waifu, description_waifu, filename)

    if waifu:
        bridge = Bridge.create_bridge_waifu(session.get('id'), waifu.id_waifu)
        return {
                "success":True
                }
    else:
         return {
                "success":False
                }


@app.route('/home/friends', methods=["GET", "POST"])
def friends():
    if 'id' not in session:
        active = False
        return redirect(url_for('login'))

    active = True

    my_id=session.get('id')
    solicitudes = Friendships.query.all()
    user_solicitudes = (Friendships.query.filter(Friendships.id_friend == my_id, Friendships.fs_status == "pending").join(Users, Friendships.id_mc ==Users.id_user).add_entity(Users).all())

    user_solicitudes_enviadas = (Friendships.query.filter(Friendships.id_mc == session.get('id'), Friendships.fs_status == "pending").join(Users, Friendships.id_friend == Users.id_user).add_entity(Users).all())
        
    enviadas_raw = Friendships.query.filter_by(id_mc=my_id, fs_status="pending").all()
    all_users = Users.query.all()
    users_show = []
    users_ids_env = [friend.id_friend for friend in enviadas_raw]


    friends_user = (Friendships.query.filter(        Friendships.id_friend == my_id, Friendships.fs_status=="friends"
        ).join(Users, Friendships.id_mc == Users.id_user).add_entity(Users).all())

    friends_friends =  (Friendships.query.filter(        Friendships.id_mc == my_id, Friendships.fs_status=="friends"
        ).join(Users, Friendships.id_friend == Users.id_user).add_entity(Users).all())


    
    for user in all_users:
        if user.id_user != session.get('id'):
            users_show.append({
                "id":user.id_user,
                "pic":user.user_pic,
                "username":user.username
                })

      

    


    return render_template('friends.html', users= users_show, user_solicitudes = user_solicitudes, user_solicitudes_enviadas = user_solicitudes_enviadas, users_ids_env = users_ids_env, friends_user = friends_user, friends_friends = friends_friends, active = active)

@app.route('/profile-user/changes/userpic', methods=["GET", "POST"])
def change_picture():
    if request.method == "POST":
        image = request.files.get('userpic')

       
        filename, extension = os.path.splitext(image.filename)

        filename = str(uuid.uuid4()) + extension

        path = os.path.join(upload_images_user, filename)

        image.save(path)

        user = Users.query.filter_by(id_user = session.get('id')).first()

        if not user:
            return{
                    "succces":False
                    }

        user.user_pic = filename
        db.session.commit()
        return{
                "success":True
                }


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/profile-user/changes', methods=["GET", "POST"])
def change_userdata():
    data = request.get_json()
    name = data.get('new-name')
    mail = data.get('new-mail')
    user = Users.query.filter_by(id_user = session.get('id')).first()
    
    if not user:
        return {"success":False}

    if name:
        user.username = name
        db.session.commit()
    if mail:
        user.mail = mail 
        db.session.commit()
    return {
            "success":True
            }

@app.route('/fs-manager', methods=["POST", "GET"])
def fs_manager():
    data = request.get_json()
    if data is None:
        return None
    id_user = session.get('id')
    type_sol = data.get('type_solicitude')
    id_friend = data.get('id_friend')

    if type_sol == 'pending':
        newFS = Friendships.create_friendship(id_user, id_friend, type_sol)
        if not newFS:
                return{
                        "success":False
                        }
    if type_sol == 'cancel':
        cancelSol = Friendships.del_fs(id_user, id_friend).first()

        if not cancelSol:
            return{
                    "succes":False
                    }

    if type_sol == 'accept':
        acceptSol = Friendships.query.filter(Friendships.id_mc == id_friend, Friendships.id_friend == id_user).first()

        if not acceptSol:
            return{
                    "success":False
                    }

        acceptSol.fs_status = "friends"
        db.session.commit()
    return{
            "success":True
            }
@app.route('/home/friends/c/<chat_id_friend>', methods=["GET", "POST"])
def priv_chat(chat_id_friend):

    if 'id' not in session:
        return redirect(url_for('login'))
    friend = Users.query.filter_by(id_user = chat_id_friend).first()
    user = Users.query.filter_by(id_user=session.get('id')).first()
    if not friend:
        return {}
    if not user: 
        return {}
    if request.method == "GET":
         return render_template('chats.html', chat_id_friend=chat_id_friend, friend = friend, user = user)
    data = request.get_json()

    from_ms = data.get('from')
    message = data.get('message')

    save_send_message = Messages.send(from_ms, chat_id_friend, message)

    if save_send_message:
        new_chatt = Chats.new_chat(save_send_message.id_emisor, save_send_message.id_receptor)
        return {
                "success":True,
                "message": save_send_message.text_content,
                "date":save_send_message.send_date
                }
    else:
        return{
                "success":False
                }


@app.route('/home/friends/c', methods=["POST", "GET"])
def chat_menu():
    if 'id' not in session:
        return redirect(url_for('login'))
    user_id = session.get('id')
    chat_user = Chats.query.filter_by(id_user=user_id).all()
    chats_user = (Chats.query.filter(Chats.id_user==user_id, Chats.status == "Active").join(Users, Chats.id_friend == Users.id_user).add_entity(Users).all())
    if not chat_user:
        return {}
    return render_template('chatmenu.html', chat_user= chat_user, chats_user = chats_user)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    upload_images = os.path.join(base_dir, "static", "uploads_waifus_images")
    upload_images_user = os.path.join(base_dir, "static", "uploads_userpic")

    os.makedirs(upload_images, exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)


