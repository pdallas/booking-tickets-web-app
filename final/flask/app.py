# Created by Panagiotis I. Dallas,
# University of Piraeus, 2020

import datetime
import os
from flask import Flask, request, redirect, render_template, flash, session
from pymongo import MongoClient

# Connect to our local MongoDB
mongodb_hostname = os.environ.get("MONGO_HOSTNAME", "localhost")
client = MongoClient('mongodb://' + mongodb_hostname + ':27017/')
# Choose InfoCinemas database
db = client['InfoCinemas']
# Choose Users & Movies collections from InfoCinemas db
users = db['Users']
movies = db['Movies']

app = Flask(__name__)
# sometimes key bugs, if you confront any "keyErrors" try changing it with a random string!
app.secret_key = b'_5#y2LewrsdfF4fdsQ8n\xec]saa/'


@app.route('/')
def index():
    # assign to data category "admin"
    data = {"category": "admin"}
    # search the user collection of our db to find any existing admins
    user_ex = users.find_one({"category": data["category"]})
    # if no admin is registered, we create one so we can operate it
    if user_ex is None:
        data = {
            "name": "admin",
            "email": "admin@admin.net",
            "password": "1234",
            "movies_seen": [],
            "category": "admin"
        }
        # assign from the dictionary data values to the user
        user = {"name": data['name'], "email": data['email'], "password": data['password'],
                "movies_seen": data['movies_seen'], "category": data['category']}
        # db user insertion
        users.insert_one(user)
        # return the index.html template. (can be found in the folder "templates"
    return render_template("index.html")


# create a route, and define the methods that will be used.
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # request data that client typed.
        login_mail = request.form["lgml"]
        login_pw = request.form["lgpw"]
        # check if the user inserted all the information that is needed for login, if not retry.
        if login_mail == "":
            flash("To login you must insert a valid e-mail address! Please retry")
            return redirect("login")
        if login_pw == "":
            flash("To login you must insert a valid password! Please retry")
            return redirect("login")

        new = {
            # "name": "",
            "email": login_mail,
            "password": login_pw
            # "movies_seen": [],
            # "category":
        }
        # Search for the user's mail in our db.
        logmail = users.find_one({"email": new["email"]})
        # if mail not found, redirect to sign up.
        if logmail is None:
            # let the client know that his email doesnt belong to our db, by flashing the message:
            flash("This email is not registered in our service, please continue by signing up!")
            # redirect to /sign_up
            return redirect("sign_up")

        # create a user session that sustains mail, user category, username and movies_seen(previous bookings) info.
        session["user_mail"] = login_mail
        # the following sessions cant be opened before the above if statement, because you cannot open a session with
        # NoneType values, example; if we searched for a user mail but didnt exist, his user_name would be NoneType..
        session["user_name"] = logmail["name"]
        session["user_cat"] = logmail["category"]
        session["movies_seen"] = logmail["movies_seen"]

        # if the password that belongs to the usermail we searched before is the same as the one that client typed;
        if logmail["password"] == new["password"]:
            # let the client know that he logged in!
            flash("Successful login!")
            # from the email search in our db, we opened a session to have access to the client's category.
            # if the client's category is simple "user" redirect him to /user page.
            if logmail["category"] == "user":
                return redirect("user")
            # if the client's category is "admin" redirect him to /admin page.
            if logmail["category"] == "admin":
                return redirect("admin")
        else:
            # if the given password does not match with the password given by the client during sign-up, flash the
            # message below;
            flash("Wrong password")
            # delete the data stored in the session (because after login a new user_mail session will open.
            session.pop("user_mail", None)
            # redirect to /login page
            return redirect("login")
    # The statement below is a response to a GET request!
    else:
        # if there is a user mail in session (that means he already logged in before or he did not close his browser;
        if "user_mail" in session:
            # and if user category is "user";
            if session["user_cat"] == "user":
                flash("You are already connected " + session["user_name"])
                # redirect the client to /user .
                return redirect("user")
            # if he belongs to the "admin" category;
            if session["user_cat"] == "admin":
                flash("You are already connected " + session["user_name"])
                # redirect the client to /admin .
                return redirect("admin")
        # render our login.html file which is in templates project file.
        return render_template("login.html")


@app.route("/logout")
def logout():
    # clear all session saved data.
    session.clear()
    # redirect to /login after logging out.
    return redirect("login")


@app.route("/sign_up", methods=["POST", "GET"])
def sign_up():
    if request.method == "POST":
        # request mail,name and password from the form that client filed.
        sign_up_mail = request.form["lgml"]
        sign_up_name = request.form["lgnm"]
        sign_up_pw = request.form["lgpw"]
        # check if the user inserted all the information that is needed for sign up.
        if sign_up_mail == "":
            flash("To complete the sign up you must insert a valid e-mail address! Please retry")
            return redirect("sign_up")
        if sign_up_name == "":
            flash("To complete the sign up you must insert valid a name! Please retry!")
            return redirect("sign_up")
        if sign_up_pw == "":
            flash("To complete the sign up you must insert a valid password! Please retry")
            return redirect("sign_up")

        new = {
            "name": sign_up_name,
            "email": sign_up_mail,
            "password": sign_up_pw,
            "movies_seen": [],
            "category": "user"
        }

        mail = users.find_one({"email": new["email"]})
        # if mail not found in our database, insert the new member.
        if mail is None:
            users.insert_one({"email": sign_up_mail, "name": sign_up_name, "password": sign_up_pw,
                              "movies_seen": new["movies_seen"], "category": new["category"]})
            flash('You were successfully signed up')
            # after a successful sign-up, redirect the client to the login page.
            return redirect("login")
        else:
            # if the email that the client typed during sign-up already exist, redirect to login page.
            flash("Already signed up! Continue by logging in")
            return redirect("login")
    # The statement below is a response to a GET request! Explained in the /login route.
    else:
        if "user_mail" in session:
            if session["user_cat"] == "user":
                return redirect("user")
            else:
                return redirect("admin")
        return render_template("sign_up.html")


@app.route("/admin")
def admin_home():
    # The statement below is a response to a GET request! Explained in the /login route.
    if "user_mail" in session:
        allscreeningsav = movies.find({})
        sav = []
        for cursor in allscreeningsav:
            titlenew = cursor.get("title")
            yornew = cursor.get("year_of_release")
            datenew = cursor.get("dateOfScreening")
            timenew = cursor.get("timeOfScreening")
            descnew = cursor.get("description")
            avseatsnew = cursor.get("available_tickets")
            # create a list with the movie attributes of each movie
            k = [titlenew, yornew, datenew, timenew, descnew, avseatsnew]
            # add it to a new list
            sav.append(k)
        login_name = session["user_name"]
        flash("User " + login_name + " connected ")
        # while rendering our template, pass a value login_name to our html file.
        return render_template("admin_home.html", login_name=login_name, sav=sav, q=len(sav))
    else:
        return redirect("login")


@app.route("/add_movie", methods=["POST", "GET"])
def add_movie():
    if request.method == "POST":
        # request title, year of release, date, time and description from the form that the user administrator filed.
        add_movie_title = request.form["addt"]
        add_movie_yearofrelease = request.form["amvyor"]
        add_movie_date = request.form["amvd"]
        add_movie_time = request.form["amvt"]
        add_movie_descr = request.form["amvds"]

        new = {
            "title": add_movie_title,
            "year_of_realese": add_movie_yearofrelease,
            "description": add_movie_descr,
            "dateOfScreening": add_movie_date,
            "timeOfScreening": add_movie_time,
            # default number of tickets is set to 50 per screening.
            "available_tickets": 50
        }
        # to add a movie to the system, admin has to give all the information asked.
        # if not, redirect to /add_movie and try again!
        if new["title"] == "":
            flash("Please, fill all the information asked!")
            return redirect("add_movie")
        if new["year_of_realese"] == "":
            flash("Please, fill all the information asked!")
            return redirect("add_movie")
        if new["description"] == "":
            flash("Please, fill all the information asked!")
            return redirect("add_movie")
        if new["dateOfScreening"] == "":
            flash("Please, fill all the information asked!")
            return redirect("add_movie")
        if new["timeOfScreening"] == "":
            flash("Please, fill all the information asked!")
            return redirect("add_movie")

        # if the admin completed everything, insert the movie in our database collection "Movies".
        movies.insert_one({"title": add_movie_title, "year_of_release": add_movie_yearofrelease,
                           "description": add_movie_descr, "dateOfScreening": add_movie_date,
                           "timeOfScreening": add_movie_time, "available_tickets": new["available_tickets"]})
        flash('You successfully added the movie ' + new["title"] + "  (" + new["year_of_realese"] + ")")
        return redirect("add_movie")
    # The statement below is a response to a GET request! Explained in the /login route.
    else:
        if "user_mail" in session:
            if session["user_cat"] == "admin":
                return render_template("add_movie.html")
            if session["user_cat"] == "user":
                return redirect("login")
        return redirect("login")


@app.route("/delete_movie", methods=["POST", "GET"])
def delete_movie():
    if request.method == "POST":
        titletodel = request.form["ttd"]

        new = {
            "title": titletodel
        }

        if titletodel == "":
            flash("Please, insert a movie!")
            return redirect("delete_movie")
        else:
            # retrive current year
            x = datetime.datetime.now()
            # add 10 to adjust the max release date possible
            possible_year = x.year + 10

            titles = movies.find({"title": new["title"]})
            if titles is None:
                flash("Movie not found! Retry")
                return redirect("delete_movie")
            else:
                for movie in titles:
                    # movie['_id'] = None
                    i = int(movie["year_of_release"])
                    # if year of release of the exact movie < max release year possible,
                    # save the id of that movie
                    if i < possible_year:
                        _id = movie["_id"]
                new2 = {
                    "_id": _id
                }
                movies.find_one_and_delete({"_id": new2["_id"]})
                flash("Movie successfully deleted")
                return redirect("delete_movie")
    else:
        if "user_mail" in session:
            if session["user_cat"] == "admin":
                return render_template("delete_movie.html")
            if session["user_cat"] == "user":
                return redirect("login")
        return redirect("login")


@app.route("/find_update_movie", methods=["POST", "GET"])
def find_update_movie():
    if request.method == "POST":
        find_movietitle_to_upd = request.form["fmvtupd"]
        find_movieyor_to_upd = request.form["fmvyorupd"]

        new = {
            "title": find_movietitle_to_upd,
            "year_of_realese": find_movieyor_to_upd,
            #   "description": ,
            #   "dateOfScreening": ,
            #   "timeOfScreening":
        }
        if new["title"] == "":
            flash("Please, fill all the information asked!")
            return redirect("find_update_movie")
        if new["year_of_realese"] == "":
            flash("Please, fill all the information asked!")
            return redirect("find_update_movie")

        session["movie_title"] = find_movietitle_to_upd
        session["movie_yor"] = find_movieyor_to_upd

        lookmovie = movies.find_one({"title": new["title"], "year_of_release": new["year_of_realese"]})
        # if movie doenst exist in db, try again
        if lookmovie is None:
            flash("Movie not found, try again")
            return redirect("find_update_movie")
        else:
            flash("Insert new values for movie " + new["title"] + " (" + new["year_of_realese"] + ")")
            flash("Check the boxes that you want to be updated!")
            return redirect("update_movie")

    else:
        if "user_mail" in session:
            if session["user_cat"] == "admin":
                return render_template("find_update_movie.html")
            if session["user_cat"] == "user":
                return redirect("login")
        return redirect("login")


@app.route("/update_movie", methods=["POST", "GET"])
def update_movie():
    if request.method == "POST":
        # retrieve selected movie for update
        titleselected = session["movie_title"]
        yorselected = session["movie_yor"]
        # find the movie based on title & year of release.
        mov = movies.find_one({"title": titleselected, "year_of_release": yorselected})
        # get movie id of the movie selected
        movselected_id = mov["_id"]

        # retrive form data
        new_title = request.form["pp"]
        new_yearofrelease = request.form["pd"]
        new_date = request.form["pf"]
        new_time = request.form["pg"]
        new_descr = request.form["ph"]

        # json
        updt = {
            "title": new_title,
            "year_of_release": new_yearofrelease,
            "description": new_descr,
            "dateOfScreening": new_date,
            "timeOfScreening": new_time
        }
        checkedlist = request.form.getlist("checkbx")
        checkedlistlength = len(checkedlist)
        if not checkedlist:
            flash("Nothing selected to update.")
            return redirect("update_movie")

        for i in range(checkedlistlength):
            # 0 refers to title checkbox
            if checkedlist[i] == "0":
                flash("Title successfully updated!")
                movies.find_one_and_update({"_id": movselected_id}, {"$set": {'title': updt["title"]}})
            # 1 refers to year of release checkbox
            if checkedlist[i] == "1":
                flash("Year of release successfully updated!")
                movies.find_one_and_update({"_id": movselected_id},
                                           {"$set": {'year_of_release': updt["year_of_release"]}})
            # 2 refers to date checkbox
            if checkedlist[i] == "2":
                flash("Date of screening successfully updated!")
                movies.find_one_and_update({"_id": movselected_id},
                                           {"$set": {'dateOfScreening': updt["dateOfScreening"]}})
            # 3 refers to time checkbox
            if checkedlist[i] == "3":
                flash("Time of screening successfully updated!")
                movies.find_one_and_update({"_id": movselected_id},
                                           {"$set": {'timeOfScreening': updt["timeOfScreening"]}})
            # 4 refers to description checkbox
            if checkedlist[i] == "4":
                flash("Description successfully updated!")
                movies.find_one_and_update({"_id": movselected_id}, {"$set": {'description': updt["description"]}})
        # pop the sessions after update is completed.
        session.pop("movie_title", None)
        session.pop("movie_yor", None)
        return redirect("find_update_movie")
    else:
        if "user_mail" in session:
            if session["user_cat"] == "admin":
                return render_template("update_movie.html")
            if session["user_cat"] == "user":
                return redirect("login")
        return redirect("login")


@app.route("/manage_admins", methods=["POST", "GET"])
def manage_admins():
    if request.method == "POST":
        # request mail,name and pw from form
        admin_mail = request.form["adm_mail"]
        admin_name = request.form["adm_name"]
        admin_pw = request.form["adm_pw"]
        # check if the user inserted all the information that is needed for sign up
        if admin_mail == "":
            flash("To complete the sign up you must insert a valid e-mail address! Please retry")
            return redirect("manage_admins")
        if admin_name == "":
            flash("To complete the sign up you must insert valid a name! Please retry!")
            return redirect("manage_admins")
        if admin_pw == "":
            flash("To complete the sign up you must insert a valid password! Please retry")
            return redirect("manage_admins")

        new = {
            "name": admin_name,
            "email": admin_mail,
            "password": admin_pw,
            "movies_seen": [],
            "category": "admin"
        }
        mail = users.find_one({"email": new["email"]})

        if mail is None:
            users.insert_one({"email": admin_mail, "name": admin_name, "password": admin_pw,
                              "movies_seen": new["movies_seen"], "category": new["category"]})
            flash('You successfully created an admin!')
            return redirect("manage_admins")
        else:
            flash("Already signed up!")
            return redirect("manage_admins")
    else:
        if "user_mail" in session:
            if session["user_cat"] == "user":
                return redirect("user")
            else:
                return render_template("manage_admins.html")
        return redirect("login")


@app.route("/user")
def user_home():
    if "user_mail" in session:
        allscreenings = movies.find({})
        scren = []
        for cursor in allscreenings:
            titlenew = cursor.get("title")
            yornew = cursor.get("year_of_release")
            datenew = cursor.get("dateOfScreening")
            timenew = cursor.get("timeOfScreening")
            descnew = cursor.get("description")
            avseatsnew = cursor.get("available_tickets")
            # create a list with the movie attributes of each movie
            j = [titlenew, yornew, datenew, timenew, descnew, avseatsnew]
            # add it to a new list
            scren.append(j)
        login_name = session["user_name"]
        flash("User " + login_name + " connected ")
        return render_template("user_home.html", login_name=login_name, scren=scren, t=len(scren))
    else:
        return redirect("login")


@app.route("/search_movies", methods=["POST", "GET"])
def search_movies():
    if request.method == "POST":
        search_movie_title = request.form["smov"]

        new = {
            "title": search_movie_title,
            # "year_of_realese": find_movieyor_to_upd,
            #   "description": [],
            #   "dateOfScreening": ,
            #   "timeOfScreening":
        }
        if new["title"] == "":
            flash("Please, fill all the information asked!")
            return redirect("search_movies")

        session["search_title"] = search_movie_title
        amovie = movies.find_one({"title": new["title"]})
        # if movie doenst exist in db, try again
        if amovie is None:
            flash("Movie not found, try another title!")
            return redirect("search_movies")
        else:
            output = []
            # find all the movies available with the same title
            smovie = movies.find({"title": new["title"]})
            for cursor in smovie:
                titlenew = cursor.get("title")
                yornew = cursor.get("year_of_release")
                datenew = cursor.get("dateOfScreening")
                timenew = cursor.get("timeOfScreening")
                descnew = cursor.get("description")
                avseatsnew = cursor.get("available_tickets")
                # create a list with the movie attributes of each movie
                ls1 = [titlenew, yornew, datenew, timenew, descnew, avseatsnew]
                # add it to a new list
                output.append(ls1)
            # debugging mode: print(len(output))
            # alert user that the movie he/she is looking for exists
            flash("Movie " + new["title"] + " found.")
            flash("Please select one of the following to book.")
            # open a session which has all the movies available with the same title
            session["movdata"] = output
            # redirect to movie_info_book in which user can choose a movie with the extra information that is provided.
            return redirect("movie_info_book")

    else:
        if "user_mail" in session:
            if session["user_cat"] == "admin":
                return redirect("login")
            if session["user_cat"] == "user":
                return render_template("search_movie.html")
        return redirect("login")


@app.route("/movie_info_book", methods=["POST", "GET"])
def movie_info_book():
    if request.method == "POST":
        # request a list that has information about our checkboxes
        checkedlist = request.form.getlist("checkbxs")
        # request number of tickets
        tickets = int(request.form["ticketnum"])
        checkedlistlength = len(checkedlist)

        # User cant continue his book if he has chosen 0 or less tickets to book.
        if tickets <= 0:
            flash("Please elect the number of tickets you want to book.")
            return redirect("movie_info_book")
        # if nothing is inside our checkbox list, retry!
        if not checkedlist:
            flash("Nothing selected to book.")
            return redirect("movie_info_book")
        # for this version, client can only book for 1 movie at a single time.
        if checkedlistlength > 1:
            flash("Please make one booking at a time.")
            return redirect("movie_info_book")
        else:
            # get the value of the checkbox selected (which is dynamically produced in movie_info_book.html)
            # Because we let the user choose only one checkbox to proceed, getlist will only have the selected checkbox
            # so we know that it can be found at potition "0" of the list checkedList.
            movie_selected = int(checkedlist[0])
            # retrieve movies found in search_movie func
            getsession = session["movdata"]
            # from session movdata (which has all the movies available with the same title that user searched)
            # find which movie was selected based on the movie_selected (which has the value of the checkbox selected)
            movie_info = getsession[movie_selected]
            # calculate the remaining tickets after the booking.
            ticketsAfterBook = int(movie_info[5]) - tickets

            if ticketsAfterBook < 0:
                flash("There are not " + str(tickets) + " tickets available. Select less to proceed!")
                return redirect("movie_info_book")
            else:
                # find the movie and update tickets
                movies.find_one_and_update(
                    {"title": movie_info[0], "year_of_release": movie_info[1], "dateOfScreening": movie_info[2],
                     "timeOfScreening": movie_info[3], "description": movie_info[4]},
                    {"$set": {"available_tickets": ticketsAfterBook}})

                # retrieve movies_seen from the session created during login.
                movseen = session["movies_seen"]
                # append the movie that the client booked to the list.
                movseen.append(movie_info[0])
                a = session["user_mail"]
                # find the user's profile through the session user_mail, and update the movies_seen list
                users.find_one_and_update({"email": a}, {"$set": {"movies_seen": movseen}})
                # let the client know that his booking was completed.
                flash("Tickets were successfully booked!")
        return redirect("book_ticket")

    else:
        if "user_mail" in session:
            if session["user_cat"] == "admin":
                return redirect("login")
            if session["user_cat"] == "user":
                # get movies found in search_movie func
                htmldata = session["movdata"]
                # pass the movie information in the html file movie_info_book.html
                return render_template("movie_info_book.html", htmldata=htmldata, b=len(session["movdata"]))
        return redirect("login")


@app.route("/book_ticket")
def book_ticket():
    if "user_mail" in session:
        if session["user_cat"] == "admin":
            return redirect("login")
        if session["user_cat"] == "user":
            return render_template("book_ticket.html")
    return redirect("login")


@app.route("/user_bookings")
def user_bookings():
    if "user_mail" in session:
        if session["user_cat"] == "admin":
            return redirect("login")
        if session["user_cat"] == "user":
            htmlmovseendata = session["movies_seen"]
            return render_template("user_bookings.html", htmlmovseendata=htmlmovseendata)
    return redirect("login")


# @app.route("/<usr>")
# def user(usr):
#   return f"<h1>{usr}</h1>"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
