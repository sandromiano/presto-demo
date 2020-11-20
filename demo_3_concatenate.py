import numpy as np
import matplotlib.pyplot as plt

from vivace import pulsed

with pulsed.Pulsed(ext_ref_clk=False, force_reload=False, address="192.168.42.50", port=3490) as pls:
    ######################################################################
    # Select inputs to store and the duration of each store
    pls.set_store_ports([1, 2])
    pls.set_store_duration(4e-6)

    ######################################################################
    # create a long pulse using multiple templates
    N = 14000
    t = np.arange(N)*0.25e-9
    f = 55e6
    s = np.sin(2*np.pi*f*t) * np.hanning(N)
    template_1 = pls.setup_template(1, s)

    ######################################################################
    # create a long pulse from sections using long_drive
    # See demo_4 for setup_freq_lut and carrier
    pls.setup_freq_lut(2, 1, [55e6], [0])

    template_2 = pls.setup_long_drive(output_port=2, carrier=1, duration=3.5e-6, amplitude=1.0,
                                      rise_time=1.0e-6, fall_time=1.0e-6)

    ######################################################################
    # define the sequence of pulses and data stores in time
    # output the long pulse and store the beginning of the pulses
    pls.select_frequency(0, 0, 1)
    pls.output_pulse(0e-6, template_1)
    pls.output_pulse(0e-6, template_2)
    pls.store(0)

    t_arr, data = pls.perform_measurement(period=100e-6, repeat_count=1, num_averages=1)

fig, ax = plt.subplots(2, sharex=True, sharey=True)
ax[0].plot(t_arr, data[0, 0, :], label=f"port 0")
ax[0].legend()
ax[1].plot(t_arr, data[0, 1, :], label=f"port 1")
ax[1].legend()
fig.show()
