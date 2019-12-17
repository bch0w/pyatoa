## Python's Adjoint Tomography Operations Assitant
### A misfit quantification package for the modern tomographer
![Logo](pyatoa/docs/pyatoa_logo.png)

Pyatoa provides abstraction over a few Python based tools, which are useful in the adjoint tomography problem:

**[Obspy:](https://github.com/obspy/obspy/wiki)** for seismic data fetching, handling, processing and organization.    
**[Pyflex:](https://krischer.github.io/pyflex/)** a Python port of Flexwin, an automatic time window selection algorithm.  
**[Pyadjoint:](http://krischer.github.io/pyadjoint/)** a package for calculating misfit and creating adjoint sources.  
**[PyASDF:](https://seismicdata.github.io/pyasdf/)** heirarchical data storage for seismic data.  
**[Matplotlib:](https://matplotlib.org/)** 2D plotting library for visualization of waveforms, statistics, misfit etc.  
**[Basemap:](https://matplotlib.org/basemap/)** A mapping library for source receiver distributions, raypaths, etc. (deprecated, Cartopy in the future).  

Pyatoa provides pre-fabricated classes and functions which allow for streamlined misfit quantification workflows that can be used bog-standard, or customized to a researchers needs with simple Python scripting.

The design philosophy of Pyatoa follows closely with Obspy; that is, flexible classes and functions that can be used for rapid development, quick data handling and simple but powerful visualization, while still leaving room for easy transition to more detailed scientific research. 

Pyatoa has been developed in conjunction with [Seisflows](https://github.com/rmodrak/seisflows), an automated workflow for seismic inversions. Included are plugin scripts that allow Pyatoa to be slotted in neatly to a Seisflows workflow template.

Detailed documentation coming soon!
