"""Demo configuration file."""

import os
import sys

from ml_collections import config_dict

# parent directory
sys.path.append("..")

import numpy as np

from config import base_config, config_utils
from utils import constants


class Config(base_config.Config):
    """Demo config file.

    Inherit from base_config.Config and override the parameters.
    """

    def __init__(self):
        """Initialize config parameters."""
        super().__init__()
        self.data_dir = "assets/demo/"  # define directory containing subject image data
        self.subject_id = "test"  # define subject ID
        self.rbc_m_ratio = 0.57  # set RBC to membrane ratio

        # set what kind of segmentation to use
        self.segmentation_key = constants.SegmentationKey.MANUAL_VENT.value
        # define path of manual segmentation
        self.manual_seg_filepath = os.path.join(self.data_dir, "mask.nii")

        # set what kind of hemoglobin correction to use
        self.hb_correction_key = constants.HbCorrectionKey.RBC_AND_MEMBRANE.value
        # define subject hemoglobin in g/dL
        self.hb = 15.0

        # override specific reconstruction parameters, as set in Recon class below
        self.recon = Recon()

        # set reference data distribution: manual or automatic
        self.reference_data_key = constants.ReferenceDataKey.DUKE_REFERENCE.value

        self.multi_echo = False;


class Recon(base_config.Recon):
    """Define reconstruction configurations.

    Attributes:
        recon_key: str, the reconstruction key
        scan_type: str, the scan type
        kernel_sharpness_lr: float, the kernel sharpness for low resolution, higher
            SNR images
        kernel_sharpness_hr: float, the kernel sharpness for high resolution, lower
            SNR images
        n_skip_start: int, the number of frames to skip at the beginning
        n_skip_end: int, the number of frames to skip at the end
        key_radius: int, the key radius for the keyhole image
    """

    def __init__(self):
        """Initialize the reconstruction parameters."""
        super().__init__()
        # override default scan type
        self.scan_type = constants.ScanType.FASTDIXON.value
        # override default number of views to skip
        self.n_skip_start = config_utils.get_n_skip_start(self.scan_type)
        self.del_x = 0
        self.del_y = 0
        self.del_z = 0
        self.recon_proton = False


def get_config() -> config_dict.ConfigDict:
    """Return the config dict. This is a required function.

    Returns:
        a ml_collections.config_dict.ConfigDict
    """
    return Config()

