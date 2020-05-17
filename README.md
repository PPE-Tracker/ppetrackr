# PPETrackr

This is the codebase for the Personal Protective Equipment Tracker being built
to help address COVID-19. 

If you're a government agency or healthcare provider looking to use https://www.ppetrackr.org/ without deploying your own code, [learn more here.](#learn-more)



## Table of Contents
- [Development Setup](#dev-setup)
- [Database](#db-setup)
    - [Seeding](#db-seeding)
    - [Superuser](#db-superuser)
- [Email Server](#email)
- [Acknowledgements](#acknowledgements)
- [Copyright](#copyright)


## Development Setup <a name="dev-setup"></a>

```
# create a virtualenv
python3 -m venv env
source env/bin/activate

# inside env
pip3 install -r requirements.txt

# runs the database migration schemas
# and creates a db.sqlite3 file
python3 manage.py migrate

# runs localhost server
python3 manage.py runserver
```

You can also use handy shortcuts in the `Makefile`.


## Database <a name="db-setup"></a>

Django settings currently default to using a sqlite db in development mode, and
it picks up on AWS RDS postgres db when deployed.

Using sqlite in development mode makes it easier to get started for now.

Thanks to Django Migrations and ORM we don't need to worry about this while
writing code.

When you make changes to models be sure to "create migration files" for those changes:

```
python3 manage.py makemigrations
# or shortcut: make makemigrations
```
New migration files will be created which needs to be commited to the repo.

It's best to avoid creating multiple migration files, and club all migrations
into one file per django app per pull-request.

You have now created the migration, but to actually make any changes in the database, you have to apply it with the management command:

```
# apply changes
python3 manage.py migrate
```

#### Seeding database with PPE data <a name="db-seeding"></a>

PPE data is customizable. We have provided a `ppe.json` file with all the PPE data, brands, and sizes that we're currently using. Please note, if you want to add different PPE, you may need to modify provider's homepage views and inventory forms to make the app compatible with PPE beyond the PPE we have included as default. To seed your PPEType table, you can simply modify `ppe.json` as you see fit and run:

```python3 manage.py loaddata ppe.json```

#### Creating a superuser <a name="db-superuser"></a>

One of Django’s prominent features is the admin interface, which is a built-in app that automatically generates a user interface to add and modify a site’s content. To create a superuser, run the following command and enter your username, email, and password as prompted:

```python3 manage.py createsuperuser```

Setting up a superuser is crucial for using this app in it's current state. Our `Organization` table uses  `MPTT`, a library that manages a database table as a tree structure and provides tools for working with trees of model instances. Through the admin panel, you must set up the organization hierarchy that . You can do this by heading to `/admin` --> Organizations --> click on organization name you want to assign a parent to --> select parent organization from the dropdown.

## Setting up email <a name="email"></a>

PPETrackr sends organization codes to users. Python comes with a very basic and integrated SMTP server you can use to send emails from Django during development. To start it just open a terminal and type the following. You will see the email directly in the terminal.

```python3 -m smtpd -n -c DebuggingServer localhost:1025```

## Getting Started on PPETrackr.org <a name="learn-more"></a>
If you want to use PPETrackr immediately, you can sign up on ppetrackr.org. 

After siging up you will be prompted to register an organization or connect to one. Follow the instructions below to figure out what's right for you:
- If you're working with a government agency or hospital system, and you want to *oversee* data of healthcare providers:
    - If you have an organization code from another member of your organization who already created an organization on PPETrackr, you must click "Connect using Organization Code" to access your organization.
    - If you're the first member of your organization to use PPETrackr, you must first click "Register as Parent Organization." You will receive an organization code via email and you can share this code with other members of your organization who also want to oversee inventory of faciliites within your jurisdiction/organization. 
- If you're a healthcare provider and you want to *report* PPE inventory for your facility:
    - If you have an organization code from another member of your organization who already created an organization on PPETrackr, you must click "Connect using Organization Code" to access your organization.
    - If you're the first member of your healthcare facility to use PPETrackr, you must first click "Register as Provider Organization." You will receive an organization code via email and you can share this code with other members of your organization who also want to report inventory for your facility. 

- For more detailed instructions on how to sign up, checkout our [manual guide](https://docs.google.com/document/d/1OPUSyuqkTjsJiqlidwb8absWwi9lDBK6RLluHFYUHKQ/edit) and [video tutorials](https://www.youtube.com/channel/UCaFMZdqjR8D0ra4Qpfgp6FA?view_as=subscriber)!

### PPETrackr.org FAQ 

#### Should I sign up as myself or my organization?
It is important to note that organizations and users distinct entities. A user can join an organization, and an organization can have many users associated with it. When a user signs up, they should register as themself, not as their organization.

#### Is information submitted by one provider facility visible to other provider facilities?
No, submissions are private between provider facilities. Each facility will only be able to submit forms and will not be able to see the form submissions of other facilities. Only authorized individuals (associated parent organizations) will have access to provider data information.

#### If I do not know the answer to a question, should I estimate the answer or guess?
Please only provide exact, known answers for ALL questions. If you do not know the answer to a question, leave the field blank.  Erroneous guesses will negatively impact data analysis.

#### How can I associate my hospital/ healthcare facility underneath a larger administration (Parent Organization) so that they see my data?
If you are a hospital/ healthcare facility and would like to be associated with a parent organization in the system so that the parent organization has visibility over your data, please email help@ppetrackr.org clearly stating the name of the Parent Organization. After cross-verification, the PPETrackr team will enable this relationship.

#### How can I allow my parent organization to oversee provider organizations I have jurisdiction over so that I can gain visibility over their data?
If you are a government body/ parent organization and would like provider organizations in the system to be associated with you so that you have visibility over their data, please email help@ppetrackr.org clearly stating the name of the relevant Provider Organizations. After cross-verification, the PPETrackr team will enable this relationship.

## Acknowledgements <a name="acknowledgements"></a>
PPETrackr was built through the support of many volunteers. We'd like to take a moment to acknowledge some of these individuals: Nathaniel Raymond, Tony Formica, Devin Osborne, Evie Schumann, Katie Taylor, Alvaro Perpuly, Eric Etsey, Anirudh Krishnan, Sidharth Krishnan, Rotem Weizman, Samuel Corden,  Nathanael McLaughlin, and Sean O'Brien.

## Copyright <a name="copyright"></a>

### Authors

* Varsha Raghavan <varsha.g.raghavan@yale.edu>
* Rachel Sterneck <rachel.sterneck@yale.edu>
* Mitesh Shah
* Meit Shah
* Flynn Chen
* Jake Tae
* Clayton Barnes
* Austin Scott

See ``AUTHORS`` file for details.

### License

This project is licensed under the [GNU Affero General Public License 3.0](https://www.gnu.org/licenses/gpl-3.0.en.html) or any later version - see ``LICENSE`` file for details.
