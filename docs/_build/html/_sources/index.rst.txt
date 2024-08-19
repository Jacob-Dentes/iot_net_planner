.. iot_net_planner documentation master file, created by
   sphinx-quickstart on Mon Aug 19 15:54:59 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to iot_net_planner's documentation!
=============================================

Introduction
=============
- The iot_net_planner project is a set of tools for planning an `IoT network <https://blogs.cornell.edu/iotnetwork/what-is-a-public-iot-network/>`_.
- The project contains information for predicting packet reception rate and optimizing gateway placement.
- These docs are intended for a technical audience with knowledge of Python and Geopandas and want a high level of customization. For a less technical audience, see the `README <https://github.com/Jacob-Dentes/iot_net_planner/tree/main?tab=readme-ov-file#iot-net-planner>`_.

Installation
============
- Clone the repository
- Create and activate a `Python virtual environment <https://docs.python.org/3/library/venv.html>`_.
- Navigate to the repository's root `iot_net_planner/`
- Install the package with `pip install .`

API Reference
=============
- The geo submodule contains tools for interacting with terrain and other geographic data.
- The prediction submodule contains tools for predicting packet reception rates based on terrain data.
- The optimization submodule contains tools for determining where to place gateways based on predictions.

.. toctree::
   :maxdepth: 4

   geo
   prediction
   optimization

Examples
========
- The examples directory contains convenience scripts for a network planning pipeline.
- Follow the directions in `the README <https://github.com/Jacob-Dentes/iot_net_planner/tree/main#iot-net-planner>`_ for usage.

License
=======
- This project is under an `MIT license <https://github.com/Jacob-Dentes/iot_net_planner/tree/main?tab=MIT-1-ov-file#>`_.
