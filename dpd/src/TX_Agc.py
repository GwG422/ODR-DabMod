# -*- coding: utf-8 -*-
#
# Automatic Gain Control
#
# http://www.opendigitalradio.org
# Licence: The MIT License, see notice at the end of this file

import datetime
import os
import logging
import time

logging_path = os.path.dirname(logging.getLoggerClass().root.handlers[0].baseFilename)

import numpy as np
import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt

import src.Adapt as Adapt

#TODO fix for float tx_gain
class TX_Agc:
    def __init__(self,
                 adapt,
                 max_txgain=89,
                 tx_median_target=0.1,
                 tx_median_threshold_max=0.12,
                 tx_median_threshold_min=0.08):
        """
        In order to avoid digital clipping, this class increases the
        TX gain and reduces the digital gain. Digital clipping happens
        when the digital analog converter receives values greater than
        it's maximal output. This class solves that problem by adapting
        the TX gain in a way that the peaks of the TX signal are in a
        specified range. The TX gain is adapted accordingly. The TX peaks
        are approximated by estimating it based on the signal median.

        :param adapt: Instance of Adapt Class to update
               txgain and coefficients
        :param max_txgain: limit for TX gain
        :param tx_median_threshold_max: if the median of TX is larger
                than this value, then the digital gain is reduced
        :param tx_median_threshold_min: if the median of TX is smaller
                than this value, then the digital gain is increased
        :param tx_median_target: The digital gain is reduced in a way that
                the median TX value is expected to be lower than this value.
        """
        assert isinstance(adapt, Adapt.Adapt)
        self.adapt = adapt
        self.max_txgain = max_txgain
        self.txgain = self.max_txgain

        assert tx_median_threshold_max > tx_median_target,\
            "The tolerated tx_median has to be larger then the goal tx_median"
        self.tx_median_threshold_tolerate_max = tx_median_threshold_max
        self.tx_median_threshold_tolerate_min = tx_median_threshold_min
        self.tx_median_target = tx_median_target

    def adapt_if_necessary(self, tx):
        tx_median = np.median(np.abs(tx))
        if tx_median > self.tx_median_threshold_tolerate_max or\
           tx_median < self.tx_median_threshold_tolerate_min:
            delta_db = 20 * np.log10(self.tx_median_target / tx_median)
            new_txgain = self.adapt.get_txgain() - delta_db
            assert new_txgain < self.max_txgain,\
                "TX_Agc failed. New TX gain of {} is too large.".format(
                    new_txgain
                )
            self.adapt.set_txgain(new_txgain)
            txgain = self.adapt.get_txgain()

            digital_gain_factor = 10 ** (delta_db / 20.)
            digital_gain = self.adapt.get_digital_gain() * digital_gain_factor
            self.adapt.set_digital_gain(digital_gain)

            logging.info(
                "digital_gain = {}, txgain_new = {}, "\
                "delta_db = {}, tx_median {}, "\
                "digital_gain_factor = {}".
                    format(digital_gain, txgain, delta_db,
                           tx_median, digital_gain_factor))

            time.sleep(1)
            return True
        return False

# The MIT License (MIT)
#
# Copyright (c) 2017 Andreas Steger
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
