ModularHistory
==============

|integration| |coverage| |black|

.. |integration| image:: https://github.com/modularhistory/modularhistory/workflows/integration/badge.svg

.. |coverage| image:: https://raw.githubusercontent.com/modularhistory/modularhistory/main/static/coverage.svg
    
.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    
.. _modularhistory.orega.org: https://modularhistory.orega.org/
.. _wiki: https://github.com/ModularHistory/modularhistory/wiki


This repository powers the ModularHistory web application.

--------------

Mission
------------

ModularHistory's mission and purpose is to help people to learn about and understand history, view current events in their historical context, avoid errors of the past, and contribute to the future. To accomplish this purpose, our volunteers gather and organize historical information regarding the patterns of human moral and intellectual progress, highlighting the roles and contributions of scientists, scholars, statespersons, philosophers, and religious leaders; gather and transcribe the contents of historical documents; contribute to our database of modularized historical information; and make all gathered information accessible at ModularHistory.com.

ModularHistory is a 501(c)(3) nonprofit organization.

--------------

Tech stack
------------
ModularHistory.com is a web application built with a tech stack including Django, Next.js, PostgreSQL, Nginx, and Docker.

* `Django <https://www.djangoproject.com/>`_, a Python web framework, powers ModularHistory's back end and much of its current front end. Django is used to power the API that makes ModularHistory's data accessible to its front-end Next.js application (which powers interactive pages on the website).
* `Next.js <https://nextjs.org/docs>`_, a `React <https://reactjs.org/>`_ framework, is used for some of ModularHistory's interactive pages. ModularHistory's Nginx server determines whether to route a request to the Django server or the Next.js server. When the Next.js server receives requests, it in turn makes requests to ModularHistory's (Django) API to retrieve data. Eventually, when Django templates and JavaScript files are converted to JSX/TSX files, Next.js will power most of ModularHistory's front end.
* `PostgreSQL <https://www.postgresql.org/>`_ is ModularHistory's database engine. Django interacts with the database.
* `Nginx <https://www.nginx.com/>`_ is used as a reverse proxy to serve static files (JS, CSS, media files, etc.) and route other requests to ModularHistory's Django and Next.js servers.
* `Docker <https://www.docker.com/>`_ is used to reliably connect the processes that power ModularHistory, in both development and production environments.

--------------

Contributing
------------

Please see ModularHistory's `contribution
guidelines <https://github.com/ModularHistory/modularhistory/wiki/Contribution-Guidelines>`__.

--------------

Support
-------

Reach out to ModularHistory:

-  By email: support@modularhistory.orega.org
-  On Facebook: https://www.facebook.com/modularhistory
-  On Twitter: https://twitter.com/ModularHistory

--------------

Donations
---------

You can support ModularHistory through
`Patreon <https://www.patreon.com/modularhistory>`__.

--------------
