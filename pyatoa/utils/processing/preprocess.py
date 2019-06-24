"""
Pre processing functionality to put raw seismic waveoforms into the proper
format for use in analysis
"""
import warnings
import numpy as np

from pyatoa import logger


def zero_pad_stream(st, pad_length_in_seconds):
    """
    Zero pad the data of a stream, change the starttime to reflect the change

    :type st: obspy.stream.Stream
    :param st: stream to be zero padded
    :type pad_length_in_seconds: int
    :param pad_length_in_seconds: length of padding front and back
    :rtype st: obspy.stream.Stream
    :return st: stream with zero padded data object
    """
    for tr in st:
        array = tr.data
        pad_width = int(pad_length_in_seconds * tr.stats.sampling_rate)
        tr.data = np.pad(array, pad_width, mode='constant')
        tr.stats.starttime -= pad_length_in_seconds
    return st


def trimstreams(st_a, st_b, force=None):
    """
    Trim two streams to common start and end times, do some basic preprocessing
    before trimming. Allows user to force one stream to conform to another
    Assumes all traces in a stream have the same time.
    Precheck to make sure that the streams are actually different

    :type st_a: obspy.stream.Stream
    :param st_a: streams to be trimmed
    :type st_b: obspy.stream.Stream
    :param st_b: streams to be trimmed
    :type force: str
    :param force: "a" or "b"; force trim to the length of "st_a" or to "st_b",
        if not given, trims to the common time
    :rtype st_?: obspy.stream.Stream
    :return st_?: trimmed stream
    """
    # Check if the times are already the same
    diff = 1E-2
    if st_a[0].stats.starttime - st_b[0].stats.starttime < diff and \
            st_a[0].stats.endtime - st_b[0].stats.endtime < diff:
        warnings.warn("Streams are already the same length", UserWarning)
        return st_a, st_b

    if force:
        force = force.lower()
        if force == "a":
            start_set = st_a[0].stats.starttime
            end_set = st_a[0].stats.endtime
        elif force == "b":
            start_set = st_b[0].stats.starttime
            end_set = st_b[0].stats.endtime
    else:
        st_trimmed = st_a.copy() + st_b.copy()
        start_set, end_set = 0, 1E10
        for st in st_trimmed:
            start_hold = st.stats.starttime
            end_hold = st.stats.endtime
            if start_hold > start_set:
                start_set = start_hold
            if end_hold < end_set:
                end_set = end_hold

    for st in [st_a, st_b]:
        st.trim(start_set, end_set)
        st.detrend("linear")
        st.detrend("demean")
        st.taper(max_percentage=0.05)

    return st_a, st_b


def _is_preprocessed(st):
    """
    Small check to make sure a stream object has not yet been run through
    preprocessing. Simple, as it assumes that a fresh stream will have no
    processing attribute in their stats, or if they do, will not have been
    filtered (getting cut waveforms from FDSN appends a 'trim' stat).
    :type st: obspy.stream.Stream
    :param st: stream to check processing on
    :rtype: bool
    :return: if preprocessing has occurred
    """
    for tr in st:
        if hasattr(tr.stats, 'processing'):
            for processing in tr.stats.processing:
                # A little hacky, but processing flag will have the str
                # ..': filter(options'... to signify that a filter is applied
                if 'filter(' in processing:
                    warnings.warn("stream already preprocessed", UserWarning)
                    return True

    # If nothing found, return False
    return False


def preproc(st, inv=None, resample=None, pad_length_in_seconds=None,
            unit_output="VEL", synthetic_unit=None, back_azimuth=None,
            filter_bounds=(10,30), water_level=60, corners=4,
            taper_percentage=0.05):
    """
    Preprocess waveform data. Assumes synthetics are in units of displacement.

    :type st: obspy.stream.Stream
    :param st: stream object to process
    :type inv: obspy.core.inventory.Inventory
    :param inv: inventory containing relevant network and stations
    :type resample: int
    :param resample: sampling rate to resample to in Hz
    :type pad_length_in_seconds: int
    :param pad_length_in_seconds: length of padding front and back
    :type unit_output: str
    :param unit_output: output of response removal, available:
        'DISP', 'VEL', 'ACC'
    :type synthetic_unit: str
    :param synthetic_unit: units of synthetic traces, same available as unit
    :type back_azimuth: float
    :param back_azimuth: back azimuth in degrees
    :type filter_bounds: list of float
    :param filter_bounds: (min period, max_period)
    :type water_level: int
    :param water_level: water level for response removal
    :type corners: int
    :param corners: value of the filter corners, i.e. steepness of filter edge
    :type taper_percentage: float
    :param taper_percentage: amount to taper ends of waveform
    :rtype st: obspy.stream.Stream
    :return st: preprocessed stream object
    """
    warnings.filterwarnings("ignore", category=FutureWarning)
    if _is_preprocessed(st):
        return st

    # Resample the data if possible
    if resample:
        st.resample(resample)

    # Standard preprocessing
    st.detrend("linear")
    st.detrend("demean")
    st.taper(max_percentage=taper_percentage)

    # If inventory is given, working with observation data
    if inv:
        # Occasionally, inventory issues arise, as ValueErrors due to 
        # station availability, e.g. NZ.COVZ. Try/except to catch these.
        try:
            st.attach_response(inv)
            st.remove_response(output=unit_output,
                               water_level=water_level,
                               plot=False)
        except ValueError:
            return None
    
        logger.info("remove response, units of {}".format(unit_output))

        # Clean up streams after response removal
        st.detrend("linear")
        st.detrend("demean")
        st.taper(max_percentage=taper_percentage)

        # Rotate streams if they are not in the ZNE coordinate system
        st.rotate(method="->ZNE", inventory=inv)

    # No inventory means synthetic data
    elif not inv:
        if unit_output != synthetic_unit:
            logger.info(
                "unit output and synthetic output do not match, adjusting")
            # Determine the difference between synthetic unit and observed unit
            diff_dict = {"DISP": 1, "VEL": 2, "ACC": 3}
            difference = diff_dict[unit_output] - diff_dict[synthetic_unit]

            # Integrate or differentiate stream to retrieve correct units
            if difference == 1:
                st.integrate(method="cumtrapz")
            elif difference == 2:
                st.integrate(method="cumtrapz").integrate(method="cumtrapz")
            elif difference == -1:
                st.differentiate(method="gradient")
            elif difference == -2:
                st.differentiate(
                    method="gradient").differentiate(method="gradient")

            st.detrend("linear")
            st.detrend("demean")

        st.taper(max_percentage=taper_percentage)
    
    # Rotate the given stream from standard North East to Radial Transverse
    if back_azimuth:
        st.rotate(method="NE->RT", back_azimuth=back_azimuth)
        logger.info("rotating NE->RT by {} degrees".format(back_azimuth))
    
    # Zero pad the stream if value is given
    if pad_length_in_seconds:
        st = zero_pad_stream(st, pad_length_in_seconds)
        logger.info(
            "zero padding front and back by {}s".format(pad_length_in_seconds))
    
    # Filter data using ObsPy Butterworth filters
    if filter_bounds is not None:
        st.filter('bandpass', freqmin=1/filter_bounds[1],
                  freqmax=1/filter_bounds[0], corners=corners, zerophase=True
                  )
        msg = "filter streams {t0}s to {t1}s w/ {c} corner {f}"
        logger.info(msg.format(t0=filter_bounds[0], t1=filter_bounds[1],
                               c=corners, f="Butterworth"))

    return st
