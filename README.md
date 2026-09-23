# UNIVERSITY DEGREE PLANNER
#### Video Demo:  https://youtu.be/wf643Lz9pko
## Description:
Since I am about to start my university journey in the next month I thought it would be great if I can make a web application of my own where my batchmates and I can plan out our degree for the next four years. This project became my CS50 final project and it is designed to help students organize their semesters, keep track of their courses,calculate gpa and see their overall progress. In this app users can make their individual accounts, login into the account, have a look at all the courses available for the computer science degree, choose courses and enter their achieved grades which are used to calculate the user's gpa.

## Features
### Login and Register page:
There are many features which I have implemented in my web application which include management of user accounts and passwords. The username and passwords are stored securely in a database but before they are stored there are multiple checks like the user should not submit an empty field, the passwords cannot be stored in text format in a database due to security reasons hence the password is hashed first and then stored in the database.
### Course Catalogue page:
The very first page displays the course catalog in which you can click on the name of the course and it's code, credits awarded on completion and description is shown in a tabulated manner. My thought process during the creation of this page was that rather than displaying the information for all the courses directly my application would become alot user friendly if the user can just scroll through the names of the courses and see the information of just the course they want.
### Semester Planner:
This is a page for planning out your degree for the span of four years where you can choose courses one by one from a dropdown for each semester. There are multiple things my web application does when you select a course, first of all it checks whether after adding this particular course the limit of 18 credits per semester is exceeded if it is then an error message is shown, then it checks if the course has already been chosen and after that it checks if the user has completed the course's prerequisite in the previous semester. If the course chosen passes all the checks then it is added in the table and the semester credit counter is updated. There is also an option to remove a course if you change your mind by clicking on the delete button. The delete button sends the information to the Flask. Flask validates the request before inserting it into SQLite and then the corresponding row from the userinfo table is deleted.
### Grades:
On this page you are shown all the courses you have chosen on the semester planner page and here you can select the grade you achieved in every course from a dropdown. After you have filled in the grades for each course you have chosen only then you will be able to calculate you semester gpa by clicking on the calculate gpa button. The calculate button runs a sql query at the backend which fetches the required information like the credits for that semester and then calculates the gpa depending on the grades entered.
### Progress:
On this page basically the users progress through out the degree is shown which includes the cgpa, credits completed so far, the best gpa they got in a semester all of this is displayed individually in a bootstrap component card and a progress bar is also present at the bottom which displays how much of the degree is remaining and it changes color depending on how much of it has been completed.

## Structure of Database:
#### There are 5 tables in the database I have created for this web application.
**people**: It stores the information about the users like username and hashed passwords.
**courses**: It contains data about the courses available such as course code, name,credits and description.
**prerequisites**: It contains the course codes of courses and their correspondng prerequisites.
**userinfo**: It stores data about the users regarding the courses they have chosen, semester in which they have chosen the course, the grade obtained.
**gpa**: It stores gpa for each user in each semester. Allowing the application to calculate cumulative GPA and other statistics.

## Technologies: Flask, SQLite, HTML, CSS, JavaScript, Python, Jinja, BootStrap.
## Challenges:
One of the most time consuming parts of this project was populating the database with course information and prerequisites. Since every course and its prerequisite had to be entered manually, ensuring that all the data was accurate and consistent required a great deal of attention to detail.
But the most challenging part of the project was implementing the semester planner. I needed to develop the logic that validates every course a user selects. The application checks whether adding the course would exceed the maximum credit limit for the semester, whether the course has already been selected, and whether all prerequisite courses have been completed in previous semesters before allowing it to be added. Designing and debugging this validation logic required careful planning and testing, but it was also the part of the project from which I learned the most about Flask, SQL queries, and application logic.
## Design Decisions:
One of the biggest design decisions was storing prerequisites in a separate table rather than placing them directly inside the courses table. This allows a course to have multiple prerequisites without duplicating course information. Another design decision was storing each selected course as its own database record linked to a user and semester. This makes it easy to calculate semester credits, GPA, and degree progress. I consulted chatgpt for suggestions when styling my web application and read the documentation for better understanding of classes, their attributes and how to use them. Bootstrap was used to create a responsive and consistent user interface while custom CSS was used to personalize the appearance.

