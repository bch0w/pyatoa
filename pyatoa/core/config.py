#!/usr/bin/env python3
"""
Configuration object for Pyatoa.

Fed into the processor class for workflow management, and also used for
information sharing between objects and functions.
"""
from pyatoa.plugins.pyflex_config import set_pyflex_config
from pyatoa.plugins.pyadjoint_config import set_pyadjoint_config


class Config:
    """
    Configuration class that controls functionalities inside pyatoa
    """
    def __init__(self, model_number=None, event_id=None, min_period=10,
                 max_period=30, filter_corners=4, rotate_to_rtz=False,
                 unit_output='DISP', pyflex_map='default', component_list=None,
                 adj_src_type='cc_traveltime_misfit', start_pad=20, end_pad=500,
                 zero_pad=0, synthetic_unit="DISP", observed_tag='observed',
                 synthetic_tag='synthetic_{model_num}', synthetics_only=False,
                 window_amplitude_ratio=0., map_corners=None, cfgpaths=None):
        """
        Allows the user to control the parameters of the packages called within
        pyatoa, as well as control where the outputs (i.e. pyasdf and plots) are
        sent after processing occurs

        Reasonable default values set on initation

        :type model_number: int or str
        :param model_number: model iteration number for annotations and tags
        :type event_id: str
        :param event_id: unique event identifier for data gathering, annotations
        :type: min_period: float
        :param min_period: minimum bandpass filter period
        :type max_period: float
        :param max_period: maximum bandpass filter period
        :type filter_corners: int
        :param filter_corners: filter steepness for obspy filter
        :type rotate_to_rtz: bool
        :param rotate_to_rtz: components from NEZ to RTZ
        :type unit_output: str
        :param unit_output: units of stream, to be fed into preprocessor for
            instrument response removal. Available: 'DISP', 'VEL', 'ACC'
        :type pyflex_map: str
        :param pyflex_map: name to map to pyflex preset config
        :type adj_src_type: str
        :param adj_src_type: method of misfit quantification for Pyadjoint
        :type start_pad: int
        :param start_pad: seconds before event origintime to grab waveform data
            for use by data gathering class
        :type end_pad: int
        :param end_pad: seconds after event origintime to grab waveform data
        :type zero_pad: int
        :type zero_pad: seconds to zero-pad data front and back, used by the
            preprocess functions, useful for very small source-receiver
            distances where there may not be much time from origin time
            to first arrival
        :type synthetic_unit: str
        :param synthetic_unit: units of Specfem synthetics, 'DISP', 'VEL', 'ACC'
        :type synthetics_only: bool
        :param synthetics_only: If the user is doing a synthetic-synthetic
            example, e.g. in a checkerboard test, this will tell the internal
            fetcher to search for observation data in the 'waveforms' path
            in the same manner that it searches for synthetic data.
        :type observed_tag: str
        :param observed_tag: Tag to use for asdf dataset to label and search
            for obspy streams of observation data. Defaults 'observed'
        :type synthetic_tag: str
        :param synthetic_tag: Tag to use for asdf dataset to label and search
            for obspy streams of synthetic data. Defaults 'synthetic_{model_num}
            Tag must be formatted before use
        :type cfgpaths: dict of str
        :param cfgpaths: any absolute paths for Pyatoa to search for
            waveforms in. If path does not exist, it will automatically be
            skipped. Allows for work on multiple machines, by giving multiple
            paths for the same set of data, without needing to change config.
            Waveforms must be saved in a specific directory structure with a
            specific naming scheme
        """
        if model_number is not None:
            # Format the model number to the way Pyatoa expects it
            if isinstance(model_number, str):
                # If e.g. model_number = "0"
                if not model_number[0] == "m":
                    self.model_number = 'm{:0>2}'.format(model_number)
                # If e.g. model_number = "m00"
                else:
                    self.model_number = model_number
            # If e.g. model_number = 0
            elif isinstance(model_number, int):
                self.model_number = 'm{:0>2}'.format(model_number)
        else:
            self.model_number = None

        self.event_id = event_id
        self.min_period = float(min_period)
        self.max_period = float(max_period)
        self.filter_corners = float(filter_corners)
        self.rotate_to_rtz = rotate_to_rtz
        self.unit_output = unit_output.upper()
        self.synthetic_unit = synthetic_unit.upper()
        self.observed_tag = observed_tag
        self.synthetic_tag = synthetic_tag.format(model_num=self.model_number)
        self.pyflex_map = pyflex_map
        self.adj_src_type = adj_src_type
        self.map_corners = map_corners
        self.synthetics_only = synthetics_only
        self.window_amplitude_ratio = window_amplitude_ratio
        self.zero_pad = int(zero_pad)
        self.start_pad = int(start_pad)
        self.end_pad = int(end_pad)
        self.component_list = component_list or ['Z', 'N', 'E'] 

        # Make sure User provided paths are list objects as they will be looped
        # on during the workflow
        if cfgpaths:
            for key in cfgpaths.keys():
                cfgpaths[key] = list(cfgpaths[key])
            self.cfgpaths = cfgpaths
        else:
            self.cfgpaths = {"waveforms": [], "synthetics": [], "responses": []}

        # Run internal functions to check the Config object
        self.pyflex_config = None
        self.pyadjoint_config = None
        self._check_config()

    def __str__(self):
        """
        string representation of class Config for print statements
        :return:
        """
        return ("CONFIG\n"
                "\tmodel_number:          {model_number}\n"
                "\tevent_id:              {event_id}\n"
                "\tmin_period:            {min_period}\n"
                "\tmax_period:            {max_period}\n"
                "\tfilter_corners:        {corner}\n"
                "\trotate_to_rtz:         {rotate}\n"
                "\tunit_output:           {output}\n"
                "\tpyflex_map:            {pyflex}\n"
                "\tadj_src_type:          {adjoint}\n"
                "\tcfgpaths['waveforms']: {paths_to_wavs}\n"
                "\tcfgpaths['synthetics']:{paths_to_syns}\n"
                "\tcfgpaths['responses']: {paths_to_resp}"
                ).format(model_number=self.model_number,
                         event_id=self.event_id, min_period=self.min_period,
                         max_period=self.max_period, corner=self.filter_corners,
                         rotate=self.rotate_to_rtz, output=self.unit_output,
                         pyflex=self.pyflex_map, adjoint=self.adj_src_type,
                         paths_to_wavs=self.cfgpaths['waveforms'],
                         paths_to_syns=self.cfgpaths['synthetics'],
                         paths_to_resp=self.cfgpaths['responses']
                         )

    def _check_config(self):
        """
        Just make sure that some of the configuration parameters are set proper
        """
        # Check period range is acceptable
        assert(self.min_period < self.max_period)

        # Check that the map corners is a dict and contains proper keys
        # Else, set to default map corners for New Zealand North Island
        if self.map_corners:
            assert(isinstance(self.map_corners, dict)), \
                "map_corners must be a dictionary object"
            acceptable_keys = ['lat_min', 'lat_max', 'lon_min', 'lon_max']
            for key in self.map_corners.keys():
                assert(key in acceptable_keys), "key should be in {}".format(
                    acceptable_keys)
        else:
            self.map_corners = {'lat_min': -42.5007, 'lat_max': -36.9488,
                                'lon_min': 172.9998, 'lon_max': 179.5077
                                }

        # Check if unit output properly set
        acceptable_units = ['DISP', 'VEL', 'ACC']
        assert(self.unit_output in acceptable_units), \
            "unit_output should be in {}".format(acceptable_units)

        assert(self.synthetic_unit in acceptable_units), \
            "synthetic_unit should be in {}".format(acceptable_units)

        # Check that paths are in the proper format
        acceptable_keys = ['synthetics', 'waveforms', 'responses']
        assert(isinstance(self.cfgpaths, dict)), "paths should be a dict"
        for key in self.cfgpaths.keys():
            assert(key in acceptable_keys), \
                "path keys can only be in {}".format(acceptable_keys)
        # Make sure that all the keys are given in the dictionary
        for key in acceptable_keys:
            if key not in self.cfgpaths.keys():
                self.cfgpaths[key] = []

        # Rotate component list if necessary
        if self.rotate_to_rtz:
            self.component_list = ['Z', 'R', 'T']

        # If all the assertions pass, set a few behind-the-scenes settings
        # Set Pyflex config as a tuple, (name, pyflex.Config)
        self.pyflex_config = set_pyflex_config(choice=self.pyflex_map,
                                               min_period=self.min_period,
                                               max_period=self.max_period
                                               )

        # Set Pyadjoint Config as a tuple, (adj source type, pyadjoint.Config)
        self.pyadjoint_config = set_pyadjoint_config(choice=self.adj_src_type,
                                                     min_period=self.min_period,
                                                     max_period=self.max_period
                                                     )

        # Check that the amplitude ratio is a reasonable number
        if self.window_amplitude_ratio > 0:
            assert(self.window_amplitude_ratio < 1), \
                "window amplitude ratio should be < 1"

    def write_to_txt(self, filename="./pyatoa_config.txt"):
        """
        write out config file to text file
        :type filename: str
        :param filename: filename to save config to
        """
        with open(filename.format(model_num=self.model_number), "w") as f:
            f.write("PYATOA CONFIGURATION FILE\n\n")
            f.write("Model Number:            {model_number}\n"
                    "Event ID:                {event_id}\n\n"
                    "PROCESSING\n"
                    "\tMinimum Filter Period: {min_period}\n"
                    "\tMaximum Filter Period: {max_period}\n"
                    "\tZero Pad:              {zero_pad}s\n"
                    "\tStart Pad:             {start_pad}s\n"
                    "\tEnd Pad:               {end_pad}s\n"
                    "\tFilter Corners:        {corner}\n"
                    "\tRotate to RTZ:         {rotate}\n"
                    "\tUnit Output:           {output}\n"
                    "\tSynthetic Unit:        {synunit}\n"
                    "ASDF Dataset\n"
                    "\tObserved Tag:          {obstag}\n"
                    "\tSynthetic Tag:         {syntag}\n"
                    "AUX. CONFIGS\n"
                    "\tPyflex Config:         {pyflex}\n"
                    "\tAdjoint Source Type:   {adjoint}\n"
                    "MISC\n"
                    "\tMap Corners            {mapcorners}\n"
                    "\tPaths to waveforms:    {paths_to_wavs}\n"
                    "\tPaths to synthetics:   {paths_to_syns}\n"
                    "\tPaths to responses:    {paths_to_resp}".format(
                        model_number=self.model_number, event_id=self.event_id,
                        min_period=self.min_period, max_period=self.max_period,
                        zero_pad=self.zero_pad, start_pad=self.start_pad,
                        end_pad=self.end_pad, corner=self.filter_corners,
                        rotate=self.rotate_to_rtz, output=self.unit_output,
                        synunit=self.synthetic_unit, obstag=self.observed_tag,
                        syntag=self.synthetic_tag, pyflex=self.pyflex_config,
                        adjoint=self.pyadjoint_config[0],
                        mapcorners=self.map_corners,
                        paths_to_wavs=self.cfgpaths['waveforms'],
                        paths_to_syns=self.cfgpaths['synthetics'],
                        paths_to_resp=self.cfgpaths['responses'])
                    )

    def read_from_asdf(self, ds, model):
        """
        Read and set config parameters from an ASDF Dataset, assumes that all
        necessary parameters are located in the auxiliary data subgroup of the
        dataset.

        :type ds: pyasdf.ASDFDataSet
        :param ds: dataset with config parameter to read
        :type model: str
        :param model: model number e.g. 'm00'
        """
        cfgin = ds.auxiliary_data.Configs[model].parameters

        self.model_number = cfgin['model_number']
        self.event_id = cfgin['event_id']
        self.min_period = float(cfgin['min_period'])
        self.max_period = float(cfgin['max_period'])
        self.filter_corners = float(cfgin['filter_corners'])
        self.rotate_to_rtz = cfgin['rotate_to_rtz']
        self.unit_output = cfgin['unit_output'].upper()
        self.synthetic_unit = cfgin['synthetic_unit'].upper()
        self.observed_tag = cfgin['observed_tag']
        self.synthetic_tag = cfgin['synthetic_tag'].format(model_num=model)
        self.pyflex_map = cfgin['pyflex_map']
        self.adj_src_type = cfgin['adj_src_type']
        self.map_corners = {'lat_min': cfgin['map_corners'][0],
                            'lat_max': cfgin['map_corners'][1],
                            'lon_min': cfgin['map_corners'][2],
                            'lon_max': cfgin['map_corners'][3]
                            }
        self.synthetics_only = cfgin['synthetics_only']
        self.window_amplitude_ratio = cfgin['window_amplitude_ratio']

        self.cfgpaths = {'synthetics': cfgin['paths_to_synthetics'],
                         'waveforms': cfgin['paths_to_waveforms'],
                         'responses': cfgin['paths_to_responses'],
                         'auxiliary_data': cfgin['paths_to_auxiliary_data']
                         }
        self.zero_pad = int(cfgin['zero_pad'])
        self.start_pad = int(cfgin['start_pad'])
        self.end_pad = int(cfgin['end_pad'])

        # Run internal functions to check the Config object
        self.component_list = ['Z', 'N', 'E']
        self._check_config()

    def write_to_asdf(self, ds):
        """
        Save the config values as a dictionary in the pyasdf data format
        for easy lookback
        """
        # Lazy imports because this function isn't always called
        from numpy import array
        from obspy import UTCDateTime

        par_dict = {"creation_time": str(UTCDateTime()),
                    "model_number": self.model_number,
                    "event_id": self.event_id,
                    "min_period": self.min_period,
                    "max_period": self.max_period,
                    "filter_corners": self.filter_corners,
                    "rotate_to_rtz": self.rotate_to_rtz,
                    "unit_output": self.unit_output,
                    "pyflex_map": self.pyflex_map,
                    "adj_src_type": self.adj_src_type,
                    "start_pad": self.start_pad,
                    "end_pad": self.end_pad,
                    "observed_tag": self.observed_tag,
                    "synthetic_tag": self.synthetic_tag,
                    "synthetics_only": self.synthetics_only,
                    "zero_pad": self.zero_pad,
                    "window_amplitude_ratio": self.window_amplitude_ratio,
                    "map_corners": [self.map_corners['lat_min'],
                                    self.map_corners['lat_max'],
                                    self.map_corners['lon_min'],
                                    self.map_corners['lon_max']],
                    "path_to_synthetics": self.cfgpaths['synthetics'],
                    "path_to_waveforms": self.cfgpaths['waveforms'],
                    "paths_to_responses": self.cfgpaths['responses'],
                    }

        ds.add_auxiliary_data(data_type="Configs", data=array([True]),
                              path="{}".format(self.model_number),
                              parameters=par_dict)

