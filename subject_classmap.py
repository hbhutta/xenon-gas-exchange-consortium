"""Module for oscillation imaging subject."""
import glob
import logging
import os
import pdb

import nibabel as nib
import numpy as np

import biasfield
import oscillation_binning as ob
import preprocessing as pp
import reconstruction
import registration
import segmentation
from config import base_config
from utils import (
    binning,
    constants,
    img_utils,
    io_utils,
    metrics,
    plot,
    recon_utils,
    report,
    spect_utils,
    traj_utils,
)


class Subject(object):
    """Module to for processing oscillation imaging.

    Attributes:
        config (config_dict.ConfigDict): config dict
        data_dissolved (np.array): dissolved-phase data of shape
            (n_projections, n_points)
        data_gas (np.array): gas-phase data of shape (n_projections, n_points)
        data_ute (np.array): UTE proton data of shape (n_projections, n_points)
        dict_dis (dict): dictionary of dissolved-phase data and metadata
        dict_dyn (dict): dictionary of dynamic spectroscopy data and metadata
        dict_ute (dict): dictionary of UTE proton data and metadata
        image_dissolved (np.array): dissolved-phase image
        image_gas_highreso (np.array): high-resolution gas-phase image
        image_gas_highsnr (np.array): high-SNR gas-phase image
        image_membrane (np.array): membrane image
        image_membrane2gas (np.array): membrane image normalized by gas-phase image
        image_rbc (np.array): RBC image
        image_rbc2gas (np.array): RBC image normalized by gas-phase image
        image_proton (np.array): UTE proton image
        mask (np.array): thoracic cavity mask
        rbc_m_ratio (float): RBC to M ratio
        stats_dict (dict): dictionary of statistics
        traj_dissolved (np.array): dissolved-phase trajectory of shape
            (n_projections, n_points, 3)
        traj_gas (np.array): gas-phase trajectory of shape
            (n_projections, n_points, 3)
        traj_ute (np.array): UTE proton trajectory of shape
    """

    def __init__(self, config: base_config.Config):
        """Init object."""
        logging.info("Initializing oscillation imaging subject.")
        self.config = config
        self.data_dissolved = np.array([])
        self.data_gas = np.array([])
        self.dict_dis = {}
        self.dict_dyn = {}
        self.image_biasfield = np.array([0.0])
        self.image_dissolved = np.array([0.0])
        self.image_gas_highreso = np.array([0.0])
        self.image_gas_highsnr = np.array([0.0])
        self.image_gas_cor = np.array([0.0])
        self.image_gas_binned = np.array([0.0])
        self.image_membrane = np.array([0.0])
        self.image_membrane2gas = np.array([0.0])
        self.image_membrane2gas_binned = np.array([0.0])
        self.image_proton = np.array([0.0])
        self.image_rbc = np.array([0.0])
        self.image_rbc2gas = np.array([0.0])
        self.image_rbc2gas_binned = np.array([0.0])
        self.mask = np.array([0.0])
        self.rbc_m_ratio = 0.0
        self.stats_dict = {}
        self.traj_dissolved = np.array([])
        self.traj_gas = np.array([])

    def read_twix_files(self):
        """Read in twix files to dictionary.

        Read in the dynamic spectroscopy (if it exists) and the dissolved-phase image
        data.
        """
        self.dict_dyn = io_utils.read_dyn_twix(
            io_utils.get_dyn_twix_files(str(self.config.data_dir))
        )
        self.dict_dis = io_utils.read_dis_twix(
            io_utils.get_dis_twix_files(str(self.config.data_dir))
        )
        if self.config.recon.recon_proton:
            self.dict_ute = io_utils.read_ute_twix(
                io_utils.get_ute_twix_files(str(self.config.data_dir))
            )

    def read_mrd_files(self):
        """Read in mrd files to dictionary.

        Read in the dynamic spectroscopy (if it exists) and the dissolved-phase image
        data.
        """
        self.dict_dyn = io_utils.read_dyn_mrd(
            io_utils.get_dyn_mrd_files(str(self.config.data_dir))
        )
        self.dict_dis = io_utils.read_dis_mrd(
            io_utils.get_dis_mrd_files(str(self.config.data_dir))
        )

    def read_mat_file(self):
        """Read in mat file of reconstructed images.

        Note: The mat file variable names are matched to the instance variable names.
        Thus, if the variable names are changed in the mat file, they must be changed.
        """
        mdict = io_utils.import_mat(io_utils.get_mat_file(str(self.config.data_dir)))
        self.dict_dis = io_utils.import_matstruct_to_dict(mdict["dict_dis"])
        self.dict_dyn = io_utils.import_matstruct_to_dict(mdict["dict_dyn"])
        if "dict_ute" in mdict.keys():
            logging.info("UTE proton data found.")
            self.dict_ute = io_utils.import_matstruct_to_dict(mdict["dict_ute"])
        self.data_dissolved = mdict["data_dissolved"]
        self.data_gas = mdict["data_gas"]
        self.image_dissolved = mdict["image_dissolved"]
        self.image_gas_highreso = mdict["image_gas_highreso"]
        self.image_gas_highsnr = mdict["image_gas_highsnr"]
        self.image_gas_cor = mdict["image_gas_cor"]
        self.image_proton = mdict["image_proton"]
        self.mask = mdict["mask"].astype(bool)
        self.rbc_m_ratio = float(mdict["rbc_m_ratio"])
        self.traj_dissolved = mdict["traj_dissolved"]
        self.traj_gas = mdict["traj_gas"]

    def calculate_rbc_m_ratio(self):
        """Calculate RBC:M ratio using static spectroscopy.

        If a manual RBC:M ratio is specified, use that instead.
        """
        if self.config.rbc_m_ratio > 0:  # type: ignore
            self.rbc_m_ratio = float(self.config.rbc_m_ratio)  # type: ignore
            logging.info("Using manual RBC:M ratio of {}".format(self.rbc_m_ratio))
        else:
            logging.info("Calculating RBC:M ratio from static spectroscopy.")
            self.rbc_m_ratio, _ = spect_utils.calculate_static_spectroscopy(
                fid=self.dict_dyn[constants.IOFields.FIDS_DIS],
                dwell_time=self.dict_dyn[constants.IOFields.DWELL_TIME],
                tr=self.dict_dyn[constants.IOFields.TR],
                center_freq=self.dict_dyn[constants.IOFields.FREQ_CENTER],
                rf_excitation=self.dict_dyn[constants.IOFields.FREQ_EXCITATION],
                plot=False,
            )

    def preprocess(self):
        """Prepare data and trajectory for reconstruction.

        Also, calculates the scaling factor for the trajectory.
        """
        generate_traj = not constants.IOFields.TRAJ in self.dict_dis.keys()
        if self.config.remove_contamination:
            self.dict_dis = pp.remove_contamination(self.dict_dyn, self.dict_dis)
        (
            self.data_dissolved,
            self.traj_dissolved,
            self.data_gas,
            self.traj_gas,
        ) = pp.prepare_data_and_traj_interleaved(
            self.dict_dis,
            generate_traj=generate_traj,
            remove_noise=self.config.remove_noisy_projections,
        )
        self.data_dissolved, self.traj_dissolved = pp.truncate_data_and_traj(
            self.data_dissolved,
            self.traj_dissolved,
            n_skip_start=int(self.config.recon.n_skip_start),
            n_skip_end=int(self.config.recon.n_skip_end),
        )
        self.data_gas, self.traj_gas = pp.truncate_data_and_traj(
            self.data_gas,
            self.traj_gas,
            n_skip_start=0,
            n_skip_end=int(self.config.recon.n_skip_end),
        )
        self.traj_scaling_factor = traj_utils.get_scaling_factor(
            recon_size=int(self.config.recon.recon_size),
            n_points=self.data_gas.shape[1],
            scale=True,
        )
        self.traj_dissolved *= self.traj_scaling_factor
        self.traj_gas *= self.traj_scaling_factor
        if self.config.recon.recon_proton:
            (
                self.data_ute,
                self.traj_ute,
            ) = pp.prepare_data_and_traj(self.dict_ute)
            self.data_ute, self.traj_ute = pp.truncate_data_and_traj(
                self.data_ute,
                self.traj_ute,
                n_skip_start=0,
                n_skip_end=0,
            )
            self.traj_ute *= self.traj_scaling_factor

    def reconstruction_ute(self):
        """Reconstruct the UTE image."""
        self.image_proton = reconstruction.reconstruct(
            data=(recon_utils.flatten_data(self.data_ute)),
            traj=recon_utils.flatten_traj(self.traj_ute),
            kernel_sharpness=float(self.config.recon.kernel_sharpness_hr),
            kernel_extent=9 * float(self.config.recon.kernel_sharpness_hr),
            image_size=int(self.config.recon.recon_size),
        )
        self.image_proton = img_utils.interp(
            self.image_proton,
            self.config.recon.matrix_size // self.config.recon.recon_size,
        )
        self.image_proton = img_utils.flip_and_rotate_image(
            self.image_proton, orientation=self.dict_dis[constants.IOFields.ORIENTATION]
        )

    def reconstruction_gas(self):
        """Reconstruct the gas phase image."""
        self.image_gas_highsnr = reconstruction.reconstruct(
            data=(recon_utils.flatten_data(self.data_gas)),
            traj=recon_utils.flatten_traj(self.traj_gas),
            kernel_sharpness=float(self.config.recon.kernel_sharpness_lr),
            kernel_extent=9 * float(self.config.recon.kernel_sharpness_lr),
            image_size=int(self.config.recon.recon_size),
        )
        self.image_gas_highreso = reconstruction.reconstruct(
            data=(recon_utils.flatten_data(self.data_gas)),
            traj=recon_utils.flatten_traj(self.traj_gas),
            kernel_sharpness=float(self.config.recon.kernel_sharpness_hr),
            kernel_extent=9 * float(self.config.recon.kernel_sharpness_hr),
            image_size=int(self.config.recon.recon_size),
        )
        self.image_gas_highreso = img_utils.interp(
            self.image_gas_highreso,
            self.config.recon.matrix_size // self.config.recon.recon_size,
        )
        self.image_gas_highsnr = img_utils.interp(
            self.image_gas_highsnr,
            self.config.recon.matrix_size // self.config.recon.recon_size,
        )
        self.image_gas_highsnr = img_utils.flip_and_rotate_image(
            self.image_gas_highsnr,
            orientation=self.dict_dis[constants.IOFields.ORIENTATION],
        )
        self.image_gas_highreso = img_utils.flip_and_rotate_image(
            self.image_gas_highreso,
            orientation=self.dict_dis[constants.IOFields.ORIENTATION],
        )

    def reconstruction_dissolved(self):
        """Reconstruct the dissolved phase image."""
        self.image_dissolved = reconstruction.reconstruct(
            data=(recon_utils.flatten_data(self.data_dissolved)),
            traj=recon_utils.flatten_traj(self.traj_dissolved),
            kernel_sharpness=float(self.config.recon.kernel_sharpness_lr),
            kernel_extent=9 * float(self.config.recon.kernel_sharpness_lr),
            image_size=int(self.config.recon.recon_size),
        )
        self.image_dissolved = img_utils.interp(
            self.image_dissolved,
            self.config.recon.matrix_size // self.config.recon.recon_size,
        )
        self.image_dissolved = img_utils.flip_and_rotate_image(
            self.image_dissolved,
            orientation=self.dict_dis[constants.IOFields.ORIENTATION],
        )

    def segmentation(self):
        """Segment the thoracic cavity."""
        if self.config.segmentation_key == constants.SegmentationKey.CNN_VENT.value:
            logging.info("Performing neural network segmenation.")
            self.mask = segmentation.predict(self.image_gas_highreso, erosion=5)
        elif self.config.segmentation_key == constants.SegmentationKey.SKIP.value:
            self.mask = np.ones_like(self.image_gas_highreso)
        elif (
            self.config.segmentation_key == constants.SegmentationKey.MANUAL_VENT.value
        ):
            logging.info("loading mask file specified by the user.")
            try:
                self.mask = np.squeeze(
                    np.array(nib.load(self.config.manual_seg_filepath).get_fdata())
                ).astype(bool)
            except ValueError:
                logging.error("Invalid mask nifti file.")
        else:
            raise ValueError("Invalid segmentation key.")

    def registration(self):
        """Register moving image to target image.

        Uses ANTs registration to register the proton image to the xenon image.
        """
        if self.config.registration_key == constants.RegistrationKey.MASK2GAS.value:
            logging.info("Run registration algorithm, vent is fixed, mask is moving")
            _, self.image_proton_reg = np.abs(
                registration.register_ants(
                    abs(self.image_gas_highreso), self.mask, self.image_proton
                )
            )
        elif self.config.registration_key == constants.RegistrationKey.PROTON2GAS.value:
            logging.info("Run registration algorithm, vent is fixed, proton is moving")
            self.image_proton_reg, mask = np.abs(
                registration.register_ants(
                    abs(self.image_gas_highreso), self.image_proton, self.mask
                )
            )
            if (
                self.config.segmentation_key
                == constants.SegmentationKey.CNN_PROTON.value
                or self.config.segmentation_key
                == constants.SegmentationKey.MANUAL_PROTON.value
            ):
                self.mask = mask
        elif self.config.registration_key == constants.RegistrationKey.MANUAL.value:
            # Load a file specified by the user
            try:
                proton_reg = glob.glob(self.config.manual_reg_filepath)[0]
                self.image_proton_reg = np.squeeze(
                    np.array(nib.load(proton_reg).get_fdata())
                )
            except ValueError:
                logging.error("Invalid proton nifti file.")
        elif self.config.registration_key == constants.RegistrationKey.SKIP.value:
            logging.info("No registration, setting registered proton to proton")
            self.image_proton_reg = self.image_proton
        else:
            raise ValueError("Invalid registration key.")

    def biasfield_correction(self):
        """Correct ventilation image for bias field."""
        if self.config.bias_key == constants.BiasfieldKey.SKIP.value:
            logging.info("Skipping bias field correction.")
            self.image_gas_cor = abs(self.image_gas_highreso)
            self.image_biasfield = np.ones(self.image_gas_highreso.shape)
        elif self.config.bias_key == constants.BiasfieldKey.N4ITK.value:
            logging.info("Performing N4ITK bias field correction.")
            (
                self.image_gas_cor,
                self.image_biasfield,
            ) = biasfield.correct_biasfield_n4itk(
                image=abs(self.image_gas_highreso),
                mask=self.mask.astype(bool),
            )
        else:
            raise ValueError("Invalid bias field correction key.")

    def dixon_decomposition(self):
        """Perform Dixon decomposition on the dissolved-phase images."""
        self.image_rbc, self.image_membrane = img_utils.dixon_decomposition(
            image_gas=self.image_gas_highsnr,
            image_dissolved=self.image_dissolved,
            mask=self.mask,
            rbc_m_ratio=self.rbc_m_ratio,
        )

    def dissolved_analysis(self):
        """Calculate the dissolved-phase images relative to gas image."""
        self.image_rbc2gas = img_utils.divide_images(
            image1=self.image_rbc, image2=np.abs(self.image_gas_highsnr), mask=self.mask
        )
        self.image_membrane2gas = img_utils.divide_images(
            image1=self.image_membrane,
            image2=np.abs(self.image_gas_highsnr),
            mask=self.mask,
        )

    def gas_binning(self):
        """Bin gas images to colormap bins."""
        self.image_gas_binned = binning.linear_bin(
            image=img_utils.normalize(self.image_gas_cor, self.mask),
            mask=self.mask,
            thresholds=self.config.params.threshold_vent,
        )

    def dissolved_binning(self):
        """Bin dissolved images to colormap bins."""
        self.image_rbc2gas_binned = binning.linear_bin(
            image=self.image_rbc2gas,
            mask=self.mask,
            thresholds=self.config.params.threshold_rbc,
        )
        self.image_membrane2gas_binned = binning.linear_bin(
            image=self.image_membrane2gas,
            mask=self.mask,
            thresholds=self.config.params.threshold_membrane,
        )

    def get_statistics(self):
        """Calculate image statistics."""
        self.stats_dict = {
            constants.StatsIOFields.SUBJECT_ID: self.config.subject_id,
            constants.StatsIOFields.INFLATION: metrics.inflation_volume(
                self.mask, self.dict_dis[constants.IOFields.FOV]
            ),
            constants.StatsIOFields.RBC_M_RATIO: self.rbc_m_ratio,
            constants.StatsIOFields.SCAN_DATE: self.dict_dis[
                constants.IOFields.SCAN_DATE
            ],
            constants.StatsIOFields.PROCESS_DATE: metrics.process_date(),
            constants.StatsIOFields.SNR_RBC: metrics.snr(self.image_rbc, self.mask)[0],
            constants.StatsIOFields.SNR_MEMBRANE: metrics.snr(
                self.image_membrane, self.mask
            )[0],
            constants.StatsIOFields.N_POINTS: self.data_gas.shape[1],
            constants.StatsIOFields.PCT_RBC_DEFECT: metrics.bin_percentage(
                self.image_rbc2gas_binned, np.array([1])
            ),
            constants.StatsIOFields.PCT_RBC_LOW: metrics.bin_percentage(
                self.image_rbc2gas_binned, np.array([2])
            ),
            constants.StatsIOFields.PCT_RBC_HIGH: metrics.bin_percentage(
                self.image_rbc2gas_binned, np.array([5, 6])
            ),
            constants.StatsIOFields.PCT_MEMBRANE_DEFECT: metrics.bin_percentage(
                self.image_membrane2gas_binned, np.array([1])
            ),
            constants.StatsIOFields.PCT_MEMBRANE_LOW: metrics.bin_percentage(
                self.image_membrane2gas_binned, np.array([2])
            ),
            constants.StatsIOFields.PCT_MEMBRANE_HIGH: metrics.bin_percentage(
                self.image_membrane2gas_binned, np.array([6, 7, 8])
            ),
            constants.StatsIOFields.PCT_VENT_DEFECT: metrics.bin_percentage(
                self.image_gas_binned, np.array([1])
            ),
            constants.StatsIOFields.PCT_VENT_LOW: metrics.bin_percentage(
                self.image_gas_binned, np.array([2])
            ),
            constants.StatsIOFields.PCT_VENT_HIGH: metrics.bin_percentage(
                self.image_gas_binned, np.array([5, 6])
            ),
        }

    def generate_figures(self):
        """Export image figures."""
        index_start, index_skip = plot.get_plot_indices(self.mask)
        plot.plot_montage_grey(
            image=np.abs(self.image_gas_highreso),
            path="tmp/montage_vent.png",
            index_start=index_start,
            index_skip=index_skip,
        )
        plot.plot_montage_grey(
            image=np.abs(self.image_membrane),
            path="tmp/montage_membrane.png",
            index_start=index_start,
            index_skip=index_skip,
        )
        proton_reg = img_utils.normalize(
            np.abs(self.image_proton),
            self.mask,
            method=constants.NormalizationMethods.PERCENTILE,
        )
        plot.plot_montage_color(
            image=plot.map_and_overlay_to_rgb(
                self.image_gas_binned, proton_reg, constants.CMAP.VENT_BIN2COLOR
            ),
            path="tmp/montage_gas_binned.png",
            index_start=index_start,
            index_skip=index_skip,
        )
        plot.plot_montage_color(
            image=plot.map_and_overlay_to_rgb(
                self.image_rbc2gas_binned, proton_reg, constants.CMAP.RBC_BIN2COLOR
            ),
            path="tmp/montage_rbc_binned.png",
            index_start=index_start,
            index_skip=index_skip,
        )
        plot.plot_montage_color(
            image=plot.map_and_overlay_to_rgb(
                self.image_membrane2gas_binned,
                proton_reg,
                constants.CMAP.MEMBRANE_BIN2COLOR,
            ),
            path="tmp/montage_membrane_binned.png",
            index_start=index_start,
            index_skip=index_skip,
        )
        plot.plot_histogram_ventilation(
            data=np.abs(self.image_gas_cor)[self.mask].flatten(),
            path="tmp/hist_vent.png",
        )
        plot.plot_histogram(
            data=np.abs(self.image_rbc2gas)[self.mask].flatten(),
            path="tmp/hist_rbc.png",
            color=constants.RBCHISTOGRAMFields.COLOR,
            xlim=constants.RBCHISTOGRAMFields.XLIM,
            ylim=constants.RBCHISTOGRAMFields.YLIM,
            num_bins=constants.RBCHISTOGRAMFields.NUMBINS,
            refer_fit=constants.RBCHISTOGRAMFields.REFERENCE_FIT,
        )
        plot.plot_histogram(
            data=np.abs(self.image_membrane2gas)[self.mask].flatten(),
            path="tmp/hist_membrane.png",
            color=constants.MEMBRANEHISTOGRAMFields.COLOR,
            xlim=constants.MEMBRANEHISTOGRAMFields.XLIM,
            ylim=constants.MEMBRANEHISTOGRAMFields.YLIM,
            num_bins=constants.MEMBRANEHISTOGRAMFields.NUMBINS,
            refer_fit=constants.MEMBRANEHISTOGRAMFields.REFERENCE_FIT,
        )

    def generate_pdf(self):
        """Generate HTML and PDF files."""
        path = os.path.join(
            self.config.data_dir,
            "report_clinical_{}.pdf".format(self.config.subject_id),
        )
        report.clinical(self.stats_dict, path=path)

    def write_stats_to_csv(self):
        """Write statistics to file."""
        io_utils.export_subject_csv(self.stats_dict, path="data/stats_all.csv")

    def save_subject_to_mat(self):
        """Save the instance variables into a mat file."""
        path = os.path.join(self.config.data_dir, self.config.subject_id + ".mat")
        io_utils.export_subject_mat(self, path)

    def save_files(self):
        """Save select images to nifti files and instance variable to mat."""
        io_utils.export_nii(self.image_rbc2gas_binned, "tmp/rbc_binned.nii")
        io_utils.export_nii(np.abs(self.image_gas_highreso), "tmp/gas_highreso.nii")
        io_utils.export_nii(self.image_gas_highsnr, "tmp/gas_highsnr.nii")
        io_utils.export_nii(np.abs(self.image_rbc), "tmp/rbc.nii")
        io_utils.export_nii(np.abs(self.image_membrane), "tmp/membrane.nii")
        io_utils.export_nii(self.mask.astype(float), "tmp/mask.nii")
        io_utils.export_nii(np.abs(self.image_dissolved), "tmp/dissolved.nii")
        if self.config.recon.recon_proton:
            io_utils.export_nii(np.abs(self.image_proton), "tmp/proton.nii")
