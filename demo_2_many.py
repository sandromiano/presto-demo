""" Max out templates!

Create 16 templates on each port, and output all 128 of them.
Set different window functions on each port, and different frequencies on each template.
Sample the maximum sampling length on all inputs, 16 times.

This example stresses the input/output bandwidth of Vivace.

Connect all outputs to all inputs in loop-back: Out 1 to In 1, Out 2 to In 2, ...
"""
import matplotlib.pyplot as plt
import numpy as np

from vivace import pulsed

ADDRESS = "192.168.42.50"  # set address/hostname of Vivace here
EXT_REF = False  # set to True to use external 10 MHz reference

with pulsed.Pulsed(ext_ref_clk=EXT_REF, address=ADDRESS) as pls:
    # Select inputs to store and the duration of each store
    pls.set_store_ports([1, 2, 3, 4, 5, 6, 7, 8])  # all ports
    pls.set_store_duration(pulsed.MAX_STORE_DURATION)  # 4096 ns

    ######################################################################
    # create a 16 4088-sample-long templates on each output
    N = pulsed.MAX_TEMPLATE_LEN
    t = np.arange(N) / pls.sampling_freq
    # use some window functions available in NumPy
    window = (
        np.bartlett(N),
        np.blackman(N),
        np.hamming(N),
        np.hanning(N),
        np.kaiser(N, 0),
        np.kaiser(N, 5),
        np.kaiser(N, 6),
        np.kaiser(N, 8.6),
    )
    templates = [[] for _ in range(8)]
    for port in range(1, 9):  # loop through all output ports
        for template_index in range(16):  # loop through all templates
            freq = 10e6 + 1e6 * template_index
            s = np.sin(2 * np.pi * freq * t) * window[port - 1]
            templates[port - 1].append(pls.setup_template(port, s))

    ######################################################################
    # define the sequence of pulses and data stores in time
    # The hardware can average ~1 Gsample/s, when this much data is
    # stored simultaneously the stores must be separated in time for the
    # averaging to keep up
    samples_per_store = pulsed.MAX_STORE_DURATION * pls.sampling_freq * 8  # 8 ports,
    spacing = samples_per_store / 1e9  # to keep up with 1 Gsample/s averaging
    for template_index in range(16):
        T = template_index * spacing  # time for output/input event
        for port in range(1, 9):
            pls.output_pulse(T, templates[port - 1][template_index])
        pls.store(T)

    # actually perform the measurement
    t_arr, data = pls.perform_measurement(period=spacing * 16,
                                          repeat_count=1,
                                          num_averages=1)

fig, ax = plt.subplots(8, 16, sharex=True, sharey=True)
for port in range(8):
    for store in range(16):
        ax[port, store].plot(t_arr, data[store, port, :])
        ax[port, store].axis('off')
fig.tight_layout()
fig.show()
