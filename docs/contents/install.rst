=============
Installation
=============


Machine Learning Layer
-----------------------
Copy files under giotto folder to a server where Building Depot is installed and add the directory to python's search path.

External Libraries
---------------------
The machine learning layer requires NumPy, SciPy, and Scikit-Learn. Install these
libraries if not installed yet. In Ubuntu, you can install these libraries with the following commands.

.. code-block:: bash

   $ sudo apt-get install python-numpy python-scipy python-sklearn

Run!!
-----------
Run a Flask server that provides REST APIs for others to interact with this
machine learning layer.

.. code-block:: bash

   $ python <giotto root directory>/ml/server/rest_api.py	


