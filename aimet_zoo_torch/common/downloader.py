#!/usr/bin/env python3
# -*- mode: python -*-
# =============================================================================
#  @@-COPYRIGHT-START-@@
#
#  Copyright (c) 2022 of Qualcomm Innovation Center, Inc. All rights reserved.
#
#  @@-COPYRIGHT-END-@@
# =============================================================================
""" Downloader and downlowder progress bar class for downloading and loading weights and encodings"""

import os
import tarfile
from pathlib import Path
import shutil
from shutil import copy2
from urllib.request import urlretrieve
import urllib.request
import progressbar
import gdown# pylint: disable=import-error



class Downloader:
    """
    Parent class for inheritance of utility methods used for downloading and loading weights and encodings
    """
    # pylint: disable=too-many-instance-attributes
    # 16 is reasonable in this case.
    def __init__(
            self,
            url_pre_opt_weights: str = None,
            url_post_opt_weights: str = None,
            url_adaround_encodings: str = None,
            url_aimet_encodings: str = None,
            url_aimet_config: str = None,
            tar_url_pre_opt_weights: str = None,
            tar_url_post_opt_weights: str = None,
            url_zipped_checkpoint: str = None,
            model_dir: str = "",
            model_config: str = "",
    ):# pylint: disable=too-many-arguments
        """
        :param url_pre_opt_weights:       url hosting pre optimization weights as a state dict
        :param url_post_opt_weights:      url hosting post optimization weights as a state dict
        :param url_adaround_encodings:    url hosting adaround encodings
        :param url_aimet_encodings:       url hosting complete encodings (activations + params)
        :param url_aimet_config:          url with aimet config to be used by the Quantization Simulation
        :param model_dir:                 path to model's directory within AIMET Model Zoo
        :param model_config:              configuration name for pre-trained model, used to specify the directory for saving weights and encodings
        """

        self.url_pre_opt_weights = url_pre_opt_weights
        self.url_post_opt_weights = url_post_opt_weights
        self.url_adaround_encodings = url_adaround_encodings
        self.url_aimet_encodings = url_aimet_encodings
        self.url_aimet_config = url_aimet_config
        self.tar_url_pre_opt_weights = tar_url_pre_opt_weights
        self.tar_url_post_opt_weights = tar_url_post_opt_weights
        self.url_zipped_checkpoint = url_zipped_checkpoint
        self._download_storage_path = (
            Path(model_dir + "/weights/" + model_config + "/")
            if model_config
            else Path(model_dir + "/weights/")
        )
        self.path_pre_opt_weights = (
            str(self._download_storage_path) + "/pre_opt_weights"
            if self.url_pre_opt_weights
            else None
        )
        self.path_post_opt_weights = (
            str(self._download_storage_path) + "/post_opt_weights"
            if self.url_post_opt_weights
            else None
        )
        self.path_adaround_encodings = (
            str(self._download_storage_path) + "/adaround_encodings"
            if self.url_adaround_encodings
            else None
        )
        self.path_aimet_encodings = (
            str(self._download_storage_path) + "/aimet_encodings"
            if self.url_aimet_encodings
            else None
        )
        self.path_aimet_config = (
            str(self._download_storage_path) + "/aimet_config"
            if self.url_aimet_config
            else None
        )
        self.path_zipped_checkpoint = (
            str(self._download_storage_path) + "/zipped_checkpoint.zip"
            if self.url_zipped_checkpoint
            else None
        )
        self.extract_dir = (
            self.path_zipped_checkpoint.split(".zip")[0]
            if self.path_zipped_checkpoint
            else None
        )

    def _download_from_url(self, src: str, dst: str, show_progress=False):
        """Receives a source URL or path and a storage destination path, evaluates the source, fetches the file, and stores at the destination"""
        if not os.path.exists(self._download_storage_path):
            os.makedirs(self._download_storage_path)
        if src is None:
            return "Skipping download, URL not provided on model definition"
        if src.startswith("https://drive.google.com"):
            gdown.download(url=src, output=dst, quiet=True, verify=False)
        elif src.startswith("http"):
            if show_progress:
                urlretrieve(src, dst, DownloadProgressBar())
            else:
                urlretrieve(src, dst)
        else:
            assert os.path.exists(
                src
            ), "URL passed is not an http, assumed it to be a system path, but such path does not exist"
            copy2(src, dst)
        return None

    def _download_pre_opt_weights(self, show_progress=False):
        """downloads pre optimization weights"""
        self._download_from_url(
            src=self.url_pre_opt_weights,
            dst=self.path_pre_opt_weights,
            show_progress=show_progress,
        )

    def _download_post_opt_weights(self, show_progress=False):
        """downloads post optimization weights"""
        self._download_from_url(
            src=self.url_post_opt_weights,
            dst=self.path_post_opt_weights,
            show_progress=show_progress,
        )

    def _download_adaround_encodings(self):
        """downloads adaround encodings"""
        self._download_from_url(
            src=self.url_adaround_encodings, dst=self.path_adaround_encodings
        )

    def _download_aimet_encodings(self):
        """downloads aimet encodings"""
        self._download_from_url(
            src=self.url_aimet_encodings, dst=self.path_aimet_encodings
        )

    def _download_aimet_config(self):
        """downloads aimet configuration"""
        self._download_from_url(src=self.url_aimet_config, dst=self.path_aimet_config)

    def _download_tar_pre_opt_weights(self):
        self._download_tar_decompress(tar_url=self.tar_url_pre_opt_weights)

    def _download_tar_post_opt_weights(self):
        self._download_tar_decompress(tar_url=self.tar_url_post_opt_weights)

    def _download_compressed_checkpoint(self):
        """download a zipped checkpoint file and unzip it"""
        self._download_from_url(
            src=self.url_zipped_checkpoint, dst=self.path_zipped_checkpoint
        )
        file_format = "".join(self.url_zipped_checkpoint.split("/")[-1].split(".")[1:][::-1])
        if not os.path.exists(self.extract_dir):
            os.makedirs(self.extract_dir)
        shutil.unpack_archive(
            filename=self.path_zipped_checkpoint,
            extract_dir=self.extract_dir,
            format=file_format,
        )

    def _download_tar_decompress(self, tar_url):
        """ "download tarball and decompress into downloaded_weights folder"""
        if not os.path.exists(self._download_storage_path):
            os.mkdir(self._download_storage_path)
        download_tar_name = (
            str(self._download_storage_path) + "/downloaded_weights.tar.gz"
        )
        urllib.request.urlretrieve(tar_url, download_tar_name, DownloadProgressBar())
        with tarfile.open(download_tar_name) as pth_weights:
            pth_weights.extractall(self._download_storage_path)
            folder_name = pth_weights.getnames()[0]
            download_path = str(self._download_storage_path) + "/" + str(folder_name)
            new_download_path = str(self._download_storage_path) + "/downloaded_weights"
            if os.path.exists(new_download_path):
                shutil.rmtree(new_download_path)
            os.rename(download_path, new_download_path)


class DownloadProgressBar:
    """Downloading progress bar to show status of downloading"""

    def __init__(self):
        self.dpb = None

    def __call__(self, b_num, b_size, size):
        widgets = [
            "\x1b[33mDownloading weights \x1b[39m",
            progressbar.Percentage(),
            progressbar.Bar(marker="\x1b[32m#\x1b[39m"),
        ]
        if not self.dpb:
            self.dpb = progressbar.ProgressBar(
                widgets=widgets, maxval=size, redirect_stdout=True
            )
            self.dpb.start()

        processed = b_num * b_size
        if processed < size:
            self.dpb.update(processed)
        else:
            self.dpb.finish()
