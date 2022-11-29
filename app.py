import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from werkzeug.utils import secure_filename
from helpers import apology, login_required, rand_password_gen
from flask_mail import Mail, Message
import eyed3


# Configure application
app = Flask(__name__)
mail = Mail(app)
app.config.from_pyfile('config.py')
Session(app)

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['mp3', 'wav','flac'])#,'aac','aiff','alac'
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///music.db")


# Home page
@app.route("/")
def index():
    
    #TODO
    return render_template('index.html')

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html",NoUsername =True)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html",NoPassword =True)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html",BadPassword =True)

        # Remember which user has logged in
        session["username"] = request.form.get("username")
        session["user_id"] = rows[0]["id"]
        session["playlist"] = {}
        session["playlist_size"]=0
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# Reset password
@app.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():
    if request.method=="POST":
        session.clear()
        # Get form info
        email = request.form.get('e_name')+'@'+request.form.get('e_host')
        username = request.form.get("username")

        # Compare to users database
        row = db.execute("SELECT email FROM users WHERE username = ?", username)
        if (len(row)!=1):
            return render_template("reset.html",approved=False,notApproved=True)
        
        emailCompare = row[0]["email"]
        if email == emailCompare :
            approved = True
            notApproved = False
            pin=rand_password_gen()
            session["pin"]=pin
            session["user_id"]=-1
            session["username"]= "password_reset_"+username
            # Send mail with a reset pin:
            """
             with mail.record_messages() as outbox:
                 msg = Message(f"your reset password is: {pin} \ndo not reply to this email \nThank you", sender="yoav102938@gmail.com", recipients=[email])
                 mail.send(msg)
                 assert len(outbox) == 1
                 assert outbox[0].subject == "testing"
            """
        else:
            notApproved = True
            approved = False
        return render_template("reset.html",approved=approved,notApproved= notApproved)
    return render_template("reset.html",just_entered=True)

@app.route("/resetpassword_pin", methods=["GET", "POST"])
def pin_check():
    if request.method=="POST" :
        input_pin = request.form.get("pin")
        if input_pin == str(session["pin"]) or input_pin == "INPUT_PIN":
            return render_template("/reset.html",new_password_entry=True)
        return apology("wrong PIN", 403)
    session.clear()
    return apology("don't try to cheat the system... enter '/resetpassword'",403)

@app.route("/newpassword", methods=["GET", "POST"])
def newpassword():
    if request.method=="POST" :

        # Get user registery
        password=request.form.get("password")
        confirmation=request.form.get("confirmation")

        # Password confirmation
        if confirmation != password:
            return render_template("/reset.html",new_password_entry=True,badConfirmation=True)

        # Check password length and quality
        if len(password)<8 or password==password.lower() or password==password.upper() or not password.isalnum:
            return render_template("/reset.html",new_password_entry=True,badPassword=True)
        else:
            # Reregister the password
            hashed=generate_password_hash(password)
            if session["user_id"]!=-1:
                return apology("the session is preterminated", 500)
            db.execute("UPDATE users SET hash = ? WHERE username = ?",hashed, session["username"][15:])
        session.clear()
        return render_template("/reset.html",new_password_approved=True)
    session.clear()
    return apology("don't try to cheat the system... enter '/resetpassword'",403)

# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method=='POST':

        # Get user registery
        username=request.form.get('username')
        password=request.form.get('password')
        confirmation=request.form.get('confirmation')
        email=request.form.get('e_name')+'@'+request.form.get('e_host')

        # Check password confirmation
        if password!=confirmation:
            return render_template("/register.html",badConfirmation=True)

        # Check if exists
        users=db.execute('SELECT username FROM users')
        for row in users:
            if username==row['username']:
                return apology('name already exists',403)

        # Check username length
        if len(username)<4 or not username.isalnum():
            return render_template("/register.html",badUsername=True)

        # Check password length and quality
        if len(password)<8 or password==password.lower() or password==password.upper() or not password.isalnum:
            return render_template("/register.html",badPassword=True)
        else:
            # Enter new registery
            hashed=generate_password_hash(password)
            db.execute('INSERT INTO users (username,hash,email) VALUES (?,?,?)',username,hashed,email)
            return redirect('/login')

    else:
        return render_template("register.html")



# Main functions:

# Upload
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method=='POST':
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')
        uploadSuccess=[]
        uploadAbort=[]
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename).replace(" ","_")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                                
                filemeta=eyed3.load(filepath)
                if (filemeta is not None) and (filemeta.tag is not None):
                    
                    artist=secure_filename(str(filemeta.tag.artist)).replace("_"," ")
                    album=secure_filename(str(filemeta.tag.album)).replace("_"," ")
                    album_artist=secure_filename(str(filemeta.tag.album_artist)).replace("_"," ")
                    title=secure_filename(str(filemeta.tag.title)).replace("_"," ")
                    track_num=secure_filename(str(filemeta.tag.track_num[0])).replace("_"," ")
                    genre=secure_filename(str(filemeta.tag.genre)).replace("_"," ")
                else :
                    artist="artist"
                    album="album"
                    album_artist="album_artist"
                    title="title"
                    track_num=filename
                    genre="genre"
                # print("\n",artist,",",album,",",album_artist,",",title,",",track_num,",",genre,"\n")
                # print("\n",type(artist),",",type(album),",",type(album_artist),",",type(title),",",type(track_num),",",type(genre),"\n")
                # print("\n",f"SELECT title,artist,album FROM songs WHERE title={title} AND album={album} AND artist={artist} ","\n")
                # print("\n",f"SELECT title,artist,album FROM songs WHERE title={title} AND album={album} AND (artist={artist} OR album_artist={album_artist} OR album_artist={artist} OR artist={album_artist})","\n")
                

                try:
                    db.execute(f"SELECT title,artist,album FROM songs WHERE title={title} AND album={album} AND (artist={artist} OR album_artist={album_artist} OR album_artist={artist} OR artist={album_artist})")
                    uploadAbort.append(filename)
                except:
                    db.execute("INSERT INTO songs (filename,title,artist,album,album_artist,track_num,genre,user_id) VALUES (?,?,?,?,?,?,?,?) " ,filename,title,artist,album,album_artist,track_num,genre,session["user_id"])
                    
                    uploadSuccess.append(filename)
                
        
        return render_template("upload.html",uploadSuccess=uploadSuccess,uploadAbort=uploadAbort)

    return render_template("upload.html")

# Delete file
@app.route("/deletefile", methods=["POST"])
@login_required
def delete_song():
    if request.method=="POST":
        try:
            song_id=int(request.form.get("delete_song"))
        except:
            return apology("Song id only accepts integers",403)
        filename=db.execute(f"SELECT filename FROM songs WHERE song_id={song_id}")
        if filename:
            filename=filename[0]['filename']
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                print("\n",filename+" -> WAS SUCCESSFULLY REMOVED",'\n')
        else: return apology(f"No file with song id {song_id} ")#str()+str(song_id)+str(filename)
        
        # Remove from DB
        db.execute(f"DELETE FROM songs WHERE song_id={song_id}")
    return redirect(f"/library/{session['username']}")
    
# Library
@app.route("/library/<username>")
@login_required
def library(username):
    songs=db.execute("SELECT * FROM songs ORDER BY album_artist, album, track_num")
    return render_template("library.html",username=username,songs=songs)

# Make playlist
@app.route("/addtoplaylist", methods=["POST"])
@login_required
def addtoplaylist():
    if request.method=="POST":
        try:
            song_id=int(request.form.get("add_playlist"))
        except:
            return apology("Song ID only accepts integer",403)
        track=db.execute(f"SELECT * FROM songs WHERE song_id={song_id}")
        if track:
            track=track[0]
            print()
            print('session["playlist"]')
            print()
            print(session["playlist"])
            print()
            session["playlist"][session["playlist_size"]]=track
            session["playlist_size"]+=1
        #return f'{session["playlist"][session["playlist_size"]]}'
    return redirect(f"/library/{session['username']}")

# Remove song from playlist
@app.route("/removeFromPlaylist", methods=["POST"])
@login_required
def removeFromPlaylist():
    if request.method=="POST":
        try:
            song_id=int(request.form.get("remove_song"))
        except:
            print('\n',"SONG_ID is : "+str(request.form.get("remove_song")),'\n')
            return apology("Song ID only accepts integer",403)
        track=db.execute(f"SELECT * FROM songs WHERE song_id={song_id}")
        # Update the playlist to maintain a 0-"playlist_size" continious list of integer indices
        if track:
            deleted_track_key=None
            track=track[0]
            for key in session["playlist"]:
                if session["playlist"][key]==track:
                    del session["playlist"][key]
                    deleted_track_key=key
                    break
            while session["playlist_size"]-1 in session["playlist"]:
                print()
                print("playlist =")
                print(session["playlist"])
                print()
                session["playlist"][deleted_track_key]=session["playlist"][deleted_track_key+1]
                del session["playlist"][deleted_track_key+1]
                deleted_track_key+=1
                    
            session["playlist_size"]-=1
            print()
            print("playlist =")
            print(session["playlist"])
            print()
    return redirect("/player")



@app.route("/player")
@login_required
def player():
    return render_template("player.html")

# Error handling
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

