""" Template matching demo

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
    # for carrier generator 1. This template will be scaled
    N = pulsed.MAX_TEMPLATE_LEN
    t = np.arange(N) / pls.sampling_freq
    s = np.hanning(N)
    template_1 = pls.setup_template(output_port, s, envelope=1, use_scale=True)

    # setup a list of frequencies for carrier generator 1
    # Use the same frequency in all entries, but rotate phase
    NFREQ = pulsed.MAX_LUT_ENTRIES
    f = [100e6,] * NFREQ
    p = np.linspace(0, 4*2*np.pi, NFREQ)
    pls.setup_freq_lut(output_ports=output_port,
                       carrier=1,
                       frequencies=f,
                       phases=p)

    # setup a list of scales, decrease the scale with every iteration
    NSCALES = pulsed.MAX_LUT_ENTRIES
    scales = np.linspace(1.0, .01, NSCALES)
    pls.setup_scale_lut(output_ports=output_port, scales=scales)


    ######################################################################
    # Match templates, use a sine and a cosine at the same frequency as
    # the generated pulse to get a point in the I/Q-plane
    # Length of the match is half the length of the generated pulse
    t = np.arange(pulsed.MAX_TEMPLATE_LEN//2) * 0.25e-9
    ts = np.sin(2*np.pi*f[0]*t)
    tc = np.cos(2*np.pi*f[0]*t)
    match_pair = pls.setup_template_matching_pair(1, ts, tc)

    ######################################################################
    # define the sequence of pulses and data stores in time
    # At the end of the time sequence, increment frequency and scale index.
    T = 0.0
    pls.output_pulse(T, template_1)
    pls.store(T)

    # Perform a template match near the center of the output pulse
    T = 0.25e-6 + 210e-9
    pls.match(T, match_pair)

    # after the pulse, jump to next frequency and next scale.
    # Both are set to increment every time.
    T = 5e-6
    pls.next_frequency(T, output_port)
    pls.next_scale(T, output_port)

    # Repeat the time sequence over the entire lookup tables.
    # Both frequency and scale are incremented every time
    t_arr, data = pls.perform_measurement(period=10e-6,
                                          repeat_count=pulsed.MAX_LUT_ENTRIES,
                                          num_averages=1)

    match_data = pls.get_template_matching_data(match_pair)

# Plot a few of the time traces
fig, ax = plt.subplots(8, sharex=True, sharey=True, tight_layout=True, figsize=(12.8, 9.6))
for i in range(8):
    ax[i].plot(1e6 * t_arr, data[i*64, 0, :])
    ax[i].axis('off')
fig.show()

# Plot template match data as points in the I/Q plane
fig, ax = plt.subplots(sharex=True, sharey=True, tight_layout=True, figsize=(12.8, 9.6))
ax.scatter(match_data[0], match_data[1], s=15)
ax.plot(match_data[0], match_data[1])
fig.show()

