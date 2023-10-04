"""Base configuration file."""
import sys

import numpy as np
from ml_collections import config_dict

from config import config_utils

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
        segmentation_key: str, the segmentation key
        hb_correction_key: str, hemoglobin correction key
        hb: float, subject hb value in g/dL
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
        self.segmentation_key = constants.SegmentationKey.CNN_VENT.value
        self.registration_key = constants.RegistrationKey.SKIP.value
        self.bias_key = constants.BiasfieldKey.N4ITK.value
        self.hb_correction_key = constants.HbCorrectionKey.NONE.value
        self.hb = constants.HbCorEqs.HB_REF
        self.site = constants.Site.DUKE.value
        self.subject_id = "test"
        self.rbc_m_ratio = 0.0


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
        self.recon_key = constants.ReconKey.ROBERTSON.value
        self.scan_type = constants.ScanType.NORMALDIXON.value
        self.kernel_sharpness_lr = 0.14
        self.kernel_sharpness_hr = 0.32
        self.n_skip_start = config_utils.get_n_skip_start(self.scan_type)
        self.n_skip_end = 0
        self.recon_size = 64
        self.matrix_size = 128
        self.recon_proton = True
        self.remove_contamination = False
        self.remove_noisy_projections = True


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
        self.mean_membrane = 0.736
        self.std_membrane = 0.278
        self.mean_rbc = 0.471
        self.std_rbc = 0.259
        self.reference_stats = {
            "vent_defect_avg": "5",
            "vent_defect_std": "3",
            "vent_low_avg": "16",
            "vent_low_std": "8",
            "vent_high_avg": "15",
            "vent_high_std": "5",
            "membrane_defect_avg": "1",
            "membrane_defect_std": "<1",
            "membrane_low_avg": "8",
            "membrane_low_std": "2",
            "membrane_high_avg": "1",
            "membrane_high_std": "1",
            "rbc_defect_avg": "4",
            "rbc_defect_std": "2",
            "rbc_low_avg": "14",
            "rbc_low_std": "6",
            "rbc_high_avg": "15",
            "rbc_high_std": "10",
            "rbc_m_ratio_avg": "0.57",
            "rbc_m_ratio_std": "0.07",
            "inflation_avg": "3.4",
            "inflation_std": "0.33",
        }


def get_config() -> config_dict.ConfigDict:
    """Return the config dict. This is a required function.

    Returns:
        a ml_collections.config_dict.ConfigDict
    """
    return Config()
