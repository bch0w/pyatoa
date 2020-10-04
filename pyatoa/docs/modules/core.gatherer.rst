Gatherer
===========================

.. currentmodule:: pyatoa.core.gatherer

.. automodule:: pyatoa.core.gatherer

--------------

.. autoclass:: Gatherer

    .. rubric:: Methods
    
    .. automethod:: gather_event
    .. automethod:: append_focal_mechanism
    .. automethod:: gather_station
    .. automethod:: gather_observed
    .. automethod:: gather_synthetic


.. rubric:: External Data Gathering 
.. autoclass:: ExternalGetter

    .. rubric:: Methods
     
    .. automethod:: event_get
    .. automethod:: station_get
    .. automethod:: obs_waveform_get

.. rubric:: Internal Data Gathering
.. autoclass:: InternalFetcher

    .. rubric:: Methods
    
    .. automethod:: fetch_resp_by_dir
    .. automethod:: fetch_obs_by_dir
    .. automethod:: fetch_syn_by_dir
    .. automethod:: obs_waveform_fetch
    .. automethod:: syn_waveform_fetch
    .. automethod:: station_fetch
    .. automethod:: asdf_event_fetch
    .. automethod:: asdf_station_fetch
    .. automethod:: asdf_waveform_fetch