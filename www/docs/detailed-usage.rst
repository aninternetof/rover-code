Detailed Usage
===============

Testing and Linting
----------------------

Run the tests like this:

.. code-block:: bash

    $ pwd
    > ~/rovercode
    $ py.test

Or, if you're using Docker, make sure the container is running (the `sudo docker run ...` command above), then do:

.. code-block:: bash

    $ sudo docker exec -it rovercode bash -c "cd ../; py.test"  # run the tests
    $ sudo docker exec -it rovercode bash -c "cd ../; prospector" # run the linter

Building the Docs
--------------------

.. code-block:: bash

    $ cd docs 
    $ make html

Or, if you're using Docker, make sure the container is running (the `sudo docker run ...` command above), then do:

.. code-block:: bash

    sudo docker exec -it rovercode bash -c "cd docs; make html"


Getting a Bash Shell Inside the Docker Container
-------------------------------------------------

If you're using Docker to develop, and you'd like to try out some
commands within the Docker container, get a bash shell like this:

.. code-block:: bash

    sudo docker exec -it rovercode bash

Using rovercode with a rovercode-web Hosted Somewhere Other than rovercode.com
-------------------------------------------------------------------------------

Read about this `over on the rovercode-web docs 
<https://contributor-docs.rovercode.com/rovercode-web/development/detailed-usage.html#using-rovercode-with-a-rovercode-web-hosted-somewhere-other-than-rovercode-com>`_.
