# Simple movie theater booking system
This web application is built with python's Flask framework, and MongoDB. Both services run in one composed docker container.
To run the docker containers run the command “(sudo) docker-compose up –build -d”.
After a couple of seconds, with the containers up and running, open a browser and go to "http://localhost:5000/login".
For the shake of simplicity, when the application boots for the first time, an admin user is created with the following credentials:

email : admin@admin.net

password : 1234

### Functionality walkthrough

Initially a user can log-in or sign-up. Checks are always made on whether the service user leaves something unfinished and displays the corresponding message.
If the user logs in and the mail does not exist in the database, it automatically redirects it to /sign_up to register in infocinemas. If the user tries to sign-up with an email that already exists in our database, it redirects the user to / login.


The simple user (user) after logging in redirects to user_home, where all the movies that are currently available are displayed ("What is being played now").

The simple user options are 3:
 
**1. Movie search:**

In which the user searches for views for a movie. If the movie the user is looking for is in the database, the movie information as well as the available tickets are displayed. From there, after selecting the number of tickets but also ticking the movie of intrest, the user can proceed to booking. If he selects a screening that does not have tickets available or if he declares more than the available ones, the corresponding message is displayed.


**2. Booking history:**

By clicking on the booking history the user can see the previous reservations he has made in the past.


**3. Logout:** 

By pressing the logout the user logs out of the system and the session ends.


**4. Home:** 

By pressing home, the user gets redirected back to homepage.

The system administrator (admin) after logging in is in admin_home, where all the available views are displayed.

The administrator options are 6:


**1. Add_movie:**

In which the administrator adds a movie view to the database, after filling in all the required fields.


**2. Delete_movie:**

By clicking delete movie, the administrator can search for a movie and delete it.


**3. Update_movie:**

By clicking update movie, the administrator can search for the movie of interes, by giving title and year of release. After finding the movie, right next to each field there is a checkbox, with which the administrator chooses which fields he wants to update. When the update button is pressed, the movie entry gets updated in the database.


**4. Manage admins:**

By selecting manage admins the administrator can fill in a registration form (as in sign up) and the added member will get the administrator privileges.


**5. Logout:**

Same as a normal user.

**6. Home:**

Same as a normal user.

