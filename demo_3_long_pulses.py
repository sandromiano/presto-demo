""" Create a long template by concatenating multiple shorter templates.

Also demonstrate the convenience method setup_long_drive.

Connect Out 1 to In 1 and Out 2 to In 2.
"""
import matplotlib.pyplot as plt
import numpy as np

from presto import pulsed

ADDRESS = "192.168.42.50"  # set address/hostname of Vivace here
EXT_REF = False  # set to True to use external 10 MHz reference

with pulsed.Pulsed(
    ext_ref_clk=EXT_REF,
    address=ADDRESS,
    adc_mode=pulsed.AdcMode.Direct,
    adc_fsample=pulsed.AdcFSample.G3_2,
    dac_mode=pulsed.DacMode.Direct,
    dac_fsample=pulsed.DacFSample.G6_4,
) as pls:
    ######################################################################
    # Select inputs to store and the duration of each store
    pls.set_store_ports([1, 2])
    pls.set_store_duration(9.5e-6)

    ######################################################################
    # create a long pulse using multiple templates on port 1
    N = 14000  # longer than pulsed.MAX_TEMPLATE_LEN = 4088!
    t = np.arange(N) / pls.get_fs("dac")
    freq = 55e6
    data = np.sin(2 * np.pi * freq * t) * np.hanning(N)
    port = 1
    # setup_template will split the template into 4 segments
    template_1 = pls.setup_template(port, 0, data)
    pls.setup_scale_lut(port, 0, 1.0)

    ######################################################################
    # create a long pulse from sections using long_drive
    # See demo_4 for setup_freq_lut and carrier
    port = 2
    group = 0
    freq = 55e6
    phase = 0.0
    pls.setup_freq_lut(port, group, freq, phase)  # see demo_4
    pls.setup_scale_lut(port, group, 1.0)

    # a pulse with the sampe lenght, with 1 us rise time and 1 us fall time
    duration = N / pls.get_fs("dac")
    template_2 = pls.setup_long_drive(
        output_port=port,
        group=group,
        duration=duration,
        amplitude=1.0,
        rise_time=1.0e-6,
        fall_time=1.0e-6,
    )

    ######################################################################
    # define the sequence of pulses and data stores in time
    # output the long pulse and store the beginning of the pulses
    T = 0.0
    pls.select_frequency(T, 0, port, group)  # see demo_4
    pls.reset_phase(T, output_ports=2)
    pls.output_pulse(T, template_1)
    pls.output_pulse(T, template_2)
    pls.store(T)

    pls.run(period=100e-6, repeat_count=1, num_averages=1)
    t_arr, data = pls.get_store_data()

fig, ax = plt.subplots(2, sharex=True, sharey=True)
ax[0].plot(1e6 * t_arr, data[0, 0, :], label=f"port 0")
ax[0].legend()
ax[1].plot(1e6 * t_arr, data[0, 1, :], label=f"port 1")
ax[1].legend()
ax[1].set_xlabel("Time [us]")
fig.show()
