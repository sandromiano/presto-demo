
import numpy as np
import matplotlib.pyplot as plt

from vivace import pulsed


with pulsed.Pulsed(ext_ref_clk=False, force_reload=False, address="192.168.42.50", port=3490) as pls:
    ######################################################################
    # Select inputs to store and the duration of each store
    pls.set_store_ports([1,])
    pls.set_store_duration(2e-6)

    ######################################################################
    # Sinewave generator, template as envelope

    # The template defines the envelope, specify that it is an envelope
    # for carrier generator 1. This template will be scaled
    N = 4088
    t = np.arange(N)*0.25e-9
    s = np.hanning(N)
    template_1 = pls.setup_template(1, s, envelope=1, use_scale=True)

    # setup a list of frequencies for carrier generator 1
    NFREQ = 8
    f = np.linspace(10e6, 100e6, NFREQ)
    p = np.zeros(NFREQ)
    pls.setup_freq_lut(output_ports=1, carrier=1, frequencies=f, phases=p)

    # setup a list of scales
    NSCALES = 8
    scales = np.linspace(1.0, .01, 8)
    pls.setup_scale_lut(output_ports=1, scales=scales, repeat_count=NFREQ)


    ######################################################################
    # define the sequence of pulses and data stores in time
    # At the end of the time sequence, increment frequency and scale index.
    # Since repeat_count for the scale lut is 8, scale index will actuallyi
    # increment after 8 pulses.
    pls.output_pulse(0, template_1)
    pls.store(0)
    pls.next_frequency(5e-6, 1)
    pls.next_scale(5e-6, 1)

    # repeat the time sequence 64 times. Run the total sequence 100 times and average the results.
    t_arr, data = pls.perform_measurement(period=10e-6, repeat_count=NFREQ*NSCALES, num_averages=100)

fig, ax = plt.subplots(8, 8, sharex=True, sharey=True)
for freq in range(NFREQ):
    for scale in range(NSCALES):
        ax[freq, scale].plot(t_arr, data[scale*NFREQ+freq, 0, :])
fig.show()


