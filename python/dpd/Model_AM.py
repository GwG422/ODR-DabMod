# -*- coding: utf-8 -*-
#
# DPD Computation Engine, model implementation for Amplitude and not Phase
#
# http://www.opendigitalradio.org
# Licence: The MIT License, see notice at the end of this file

import datetime
import os
import logging
import numpy as np
import matplotlib.pyplot as plt


def is_npfloat32(array):
    assert isinstance(array, np.ndarray), type(array)
    assert array.dtype == np.float32, array.dtype
    assert array.flags.contiguous
    assert not any(np.isnan(array))


def check_input_get_next_coefs(tx_dpd, rx_received):
    is_npfloat32(tx_dpd)
    is_npfloat32(rx_received)


def poly(sig):
    return np.array([sig ** i for i in range(1, 6)]).T


def fit_poly(tx_abs, rx_abs):
    return np.linalg.lstsq(poly(rx_abs), tx_abs, rcond=None)[0]


def calc_line(coefs, min_amp, max_amp):
    rx_range = np.linspace(min_amp, max_amp)
    tx_est = np.sum(poly(rx_range) * coefs, axis=1)
    return tx_est, rx_range


class Model_AM:
    """Calculates new coefficients using the measurement and the previous
    coefficients"""

    def __init__(self, c, learning_rate_am=1):
        self.c = c
        self.learning_rate_am = learning_rate_am
        self._plot_data = None

    def plot(self, plot_location, title):
        if self._plot_data is not None:
            tx_dpd, rx_received, coefs_am, coefs_am_new = self._plot_data

            tx_range, rx_est = calc_line(coefs_am, 0, 0.6)
            tx_range_new, rx_est_new = calc_line(coefs_am_new, 0, 0.6)

            sub_rows = 1
            sub_cols = 1
            fig = plt.figure(figsize=(sub_cols * 6, sub_rows / 2. * 6))
            i_sub = 0

            i_sub += 1
            ax = plt.subplot(sub_rows, sub_cols, i_sub)
            ax.plot(tx_range, rx_est,
                    label="Estimated TX",
                    alpha=0.3,
                    color="gray")
            ax.plot(tx_range_new, rx_est_new,
                    label="New Estimated TX",
                    color="red")
            ax.scatter(tx_dpd, rx_received,
                       label="Binned Data",
                       color="blue",
                       s=1)
            ax.set_title("Model_AM {}".format(title))
            ax.set_xlabel("TX Amplitude")
            ax.set_ylabel("RX Amplitude")
            ax.set_xlim(-0.5, 1.5)
            ax.legend(loc=4)

            fig.tight_layout()
            fig.savefig(plot_location)
            plt.close(fig)

    def get_next_coefs(self, tx_dpd, rx_received, coefs_am):
        """Calculate the next AM/AM coefficients using the extracted
        statistic of TX and RX amplitude"""
        check_input_get_next_coefs(tx_dpd, rx_received)

        coefs_am_new = fit_poly(tx_dpd, rx_received)
        coefs_am_new = coefs_am + \
                       self.learning_rate_am * (coefs_am_new - coefs_am)

        self._plot_data = (tx_dpd, rx_received, coefs_am, coefs_am_new)

        return coefs_am_new

# The MIT License (MIT)
#
# Copyright (c) 2017 Andreas Steger
# Copyright (c) 2018 Matthias P. Braendli
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
