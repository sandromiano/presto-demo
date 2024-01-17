""" Create a long template by concatenating multiple shorter templates.

Also demonstrate the convenience method setup_long_drive.

Connect one output to one input.
"""
import matplotlib.pyplot as plt
import numpy as np

from presto import pulsed

# Any port on Vivace
# Any port on Presto wide, wamp and low
# Ports 5-8 on Presto-8-QC
# Ports 9-16 on Presto-16-QC
output_port = 9
input_port = 9

ADDRESS = "192.168.20.19"  # set address/hostname of Vivace here
EXT_REF = False  # set to True to use external 10 MHz reference

with pulsed.Pulsed(
    ext_ref_clk=EXT_REF,
    address=ADDRESS,
    adc_mode=pulsed.AdcMode.Direct,
    dac_mode=pulsed.DacMode.Direct,
) as pls:
    ######################################################################
    # Select inputs to store and the duration of each store
    store_duration = 9.5e-6
    pls.set_store_ports(input_port)
    pls.set_store_duration(store_duration)

    ######################################################################
    # create a long pulse using multiple templates on port 1
    N = 14000  # longer than pulsed.MAX_TEMPLATE_LEN = 4088!
    t = np.arange(N) / pls.get_fs("dac")
    freq = 55e6
    data = np.sin(2 * np.pi * freq * t) * np.hanning(N)
    # setup_template will split the template into 4 segments
    template_1 = pls.setup_template(output_port, 0, data)
    pls.setup_scale_lut(output_port, 0, 1.0)

    ######################################################################
    # create a long pulse from sections using long_drive
    # See demo_3 for setup_freq_lut and carrier
    group = 1
    freq = 55e6
    phase = 0.0
    pls.setup_freq_lut(output_port, group, freq, phase)  # see demo_3
    pls.setup_scale_lut(output_port, group, 1.0)

    # a pulse with the sampe lenght, with 1 us rise time and 1 us fall time
    duration = N / pls.get_fs("dac")
    template_2 = pls.setup_long_drive(
        output_port=output_port,
        group=group,
        duration=duration,
        amplitude=1.0,
        rise_time=1.0e-6,
        fall_time=1.0e-6,
        envelope=True,
    )

    ######################################################################
    # define the sequence of pulses and data stores in time
    # output the long pulse and store the beginning of the pulses
    T = 0.0
    pls.output_pulse(T, template_1)
    pls.store(T)
    T += store_duration + 2e-9
    pls.select_frequency(T, 0, output_port, group)  # see demo_4
    pls.reset_phase(T, output_ports=output_port)
    pls.output_pulse(T, template_2)
    pls.store(T)

    pls.run(period=100e-6, repeat_count=1, num_averages=1)
    t_arr, data = pls.get_store_data()

fig, ax = plt.subplots(2, sharex=True, sharey=True)
ax[0].plot(1e6 * t_arr, data[0, 0, :], label=f"template")
ax[0].legend()
ax[1].plot(1e6 * t_arr, data[1, 0, :], label=f"long_drive")
ax[1].legend()
ax[1].set_xlabel("Time [us]")
fig.show()
