# /usr/bin/env python3
# -*- mode: python -*-
# =============================================================================
# @@-COPYRIGHT-START-@@
#
# Copyright (c) 2023 of Qualcomm Innovation Center, Inc. All rights reserved.
# Changes from QuIC are licensed under the terms and conditions at
# https://github.com/quic/aimet-model-zoo/blob/develop/LICENSE.pdf
#
# @@-COPYRIGHT-END-@@
# =============================================================================

""" acceptance test for mobilenet_v2_tf2_quanteval image classification"""

import pytest
from aimet_zoo_tensorflow.mobilenet_v2_tf2.evaluators import mobilenet_v2_tf2_quanteval

@pytest.mark.cuda 
@pytest.mark.object_detection
# pylint:disable = redefined-outer-name
@pytest.mark.parametrize("model_config", ["mobilenetv2_w8a8"])
def test_quanteval_mobilenet_v2(model_config, tiny_imageNet_root_path):
    """mobilenet_v2_tf2 image classification acceptance test"""

    if tiny_imageNet_root_path is None:
        pytest.fail(f'Dataset path is not set')

    mobilenet_v2_tf2_quanteval.main(
        [
            "--model-config",
            model_config,
            "--dataset-path",
            tiny_imageNet_root_path,
        ]
    )



