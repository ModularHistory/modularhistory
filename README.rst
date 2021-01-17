ModularHistory
==============

|integration| |coverage| |black|

.. |integration| image:: https://github.com/modularhistory/modularhistory/workflows/integration/badge.svg

.. |coverage| image:: https://raw.githubusercontent.com/modularhistory/modularhistory/main/modularhistory/static/coverage.svg
    
.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black


https://www.modularhistory.com

--------------

Installation
------------

Prerequisites
~~~~~~~~~~~~~

- Docker (https://docs.docker.com/get-docker/)
- Docker Compose (https://docs.docker.com/compose/install/)

Cloning
~~~~~~~

Clone ModularHistory to your local machine::

    git clone https://github.com/ModularHistory/modularhistory.git

Setup
~~~~~
With Docker
########

Enter the cloned project directory::

    cd modularhistory
    
Start up the application in development mode::

    docker-compose up -d dev
    
Watch the logs::

    docker-compose logs -f


Without Docker
########

NOTE: ModularHistory can only be run without Docker on MacOS or Linux operating systems.

Enter the cloned project directory::

    cd modularhistory

Execute the setup script (which should install all dependencies)::

    ./setup.sh

Run tests::

    invoke test

--------------

Contributing
------------

Please see ModularHistory's `contribution
guidelines <https://github.com/ModularHistory/modularhistory/wiki/Contribution-Guidelines>`__.

--------------

Support
-------

Reach out to ModularHistory:

-  By email: modularhistory@gmail.com
-  On Facebook: https://www.facebook.com/modularhistory
-  On Twitter: https://twitter.com/ModularHistory

--------------

Donations
---------

You can support ModularHistory through
`Patreon <https://www.patreon.com/modularhistory>`__.

--------------

License
-------

ModularHistory has an `ISC
License <https://github.com/ModularHistory/modularhistory/blob/main/LICENSE.txt>`__.
