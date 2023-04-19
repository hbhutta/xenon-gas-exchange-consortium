"""Base configuration file."""
import sys

import numpy as np
from ml_collections import config_dict

# parent directory
sys.path.append("..")

from utils import constants


class Config(config_dict.ConfigDict):
    """Base config file.

    Attributes:
        data_dir: str, path to the data directory
        manual_seg_filepath: str, path to the manual segmentation nifti file
        remove_contamination: bool, whether to remove gas contamination
        remove_noisy_projections: bool, whether to remove noisy projections
        processes: Process, the evaluation processes
        params: Params, the important parameters
        platform: Platform, the scanner vendor platform
        scan_type: str, the scan type
        segmentation_key: str, the segmentation key
        site: str, the scan site
        subject_id: str, the subject id
        rbc_m_ratio: float, the RBC to M ratio
    """

    def __init__(self):
        """Initialize config parameters."""
        super().__init__()
        self.data_dir = ""
        self.manual_seg_filepath = ""
        self.manual_reg_filepath = ""
        self.processes = Process()
        self.recon = Recon()
        self.params = Params()
        self.platform = constants.Platform.SIEMENS.value
        self.scan_type = constants.ScanType.NORMALDIXON.value
        self.segmentation_key = constants.SegmentationKey.CNN_VENT.value
        self.registration_key = constants.RegistrationKey.SKIP.value
        self.bias_key = constants.BiasfieldKey.N4ITK.value
        self.site = constants.Site.DUKE.value
        self.subject_id = "test"
        self.rbc_m_ratio = 0.0
        self.remove_contamination = False
        self.remove_noisy_projections = False


class Process(object):
    """Define the evaluation processes.

    Attributes:
        gx_mapping_recon: bool, whether to perform gas exchange mapping
            with reconstruction
        gx_mapping_readin: bool, whether to perform gas exchange mapping
            by reading in the mat file
    """

    def __init__(self):
        """Initialize the process parameters."""
        self.gx_mapping_recon = True
        self.gx_mapping_readin = False


class Recon(object):
    """Define reconstruction configurations.

    Attributes:
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
        self.kernel_sharpness_lr = 0.14
        self.kernel_sharpness_hr = 0.32
        self.n_skip_start = 60
        self.n_skip_end = 0
        self.recon_size = 64
        self.matrix_size = 128
        self.recon_proton = True


class Params(object):
    """Define important parameters.

    Attributes:
        threshold_oscillation: np.ndarray, the oscillation amplitude thresholds for
            binning
        threshold_rbc: np.ndarray, the RBC thresholds for binning
    """

    def __init__(self):
        """Initialize the reconstruction parameters."""
        self.threshold_vent = np.array([0.185, 0.418, 0.647, 0.806, 0.933])
        self.threshold_rbc = np.array([0.066, 0.250, 0.453, 0.675, 0.956])
        self.threshold_membrane = np.array(
            [0.180, 0.458, 0.736, 1.014, 1.292, 1.57, 1.848]
        )


def get_config() -> config_dict.ConfigDict:
    """Return the config dict. This is a required function.

    Returns:
        a ml_collections.config_dict.ConfigDict
    """
    return Config()
