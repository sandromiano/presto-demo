""" Use templates as envelopes for the carrier generator.

Connect Out 1 to In 1.
"""
import matplotlib.pyplot as plt
import numpy as np

from vivace import pulsed

input_port = 1
output_port = 1

ADDRESS = "192.168.42.50"  # set address/hostname of Vivace here
EXT_REF = False  # set to True to use external 10 MHz reference

with pulsed.Pulsed(ext_ref_clk=EXT_REF, address=ADDRESS) as pls:
    ######################################################################
    # Select inputs to store and the duration of each store
    pls.set_store_ports(input_port)
    pls.set_store_duration(2e-6)

    ######################################################################
    # Sinewave generator, template as envelope

    # The template defines the envelope, specify that it is an envelope
    # for carrier generator 1
    N = pulsed.MAX_TEMPLATE_LEN
    t = np.arange(N) / pls.sampling_freq
    s = np.hanning(N)
    template_1 = pls.setup_template(output_port, s, envelope=1)

    # setup a list of frequencies for carrier generator 1
    f = np.logspace(6, 8, 10)  # 1 MHz to 100 MHz, logarithmically
    p = np.zeros(10)
    pls.setup_freq_lut(output_ports=output_port,
                       carrier=1,
                       frequencies=f,
                       phases=p)

    ######################################################################
    # define the sequence of pulses and data stores in time
    for i in range(10):
        T = 10e-6 * i
        pls.output_pulse(T, template_1)
        pls.store(T)
        pls.next_frequency(T + 5e-6, output_port)

    t_arr, data = pls.perform_measurement(period=500e-6,
                                          repeat_count=1,
                                          num_averages=1)

fig, ax = plt.subplots(10, figsize=(6.4, 9.6), sharex=True, sharey=True, tight_layout=True)
for i in range(10):
    ax[i].plot(1e6 * t_arr, data[i, 0, :], label=f"{f[i] / 1e6:.1f} MHz")
    ax[i].legend(loc="upper right")
ax[-1].set_xlabel("Time [us]")
fig.show()
