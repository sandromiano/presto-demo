""" Create one output template and sample it.

Connect one output port directly to one input port.
"""
import matplotlib.pyplot as plt
import numpy as np

from presto import pulsed

output_port = 1
input_port = 1

ADDRESS = "192.168.42.50"  # set address/hostname of Vivace here
EXT_REF = False  # set to True to use external 10 MHz reference

with pulsed.Pulsed(ext_ref_clk=EXT_REF, address=ADDRESS) as pls:
    ######################################################################
    # Select input ports to store and the duration of each store
    pls.set_store_ports(input_port)
    pls.set_store_duration(800e-9)  # 800 ns

    ######################################################################
    # create a 512-sample-long template on output_port
    # make a sine wave with a Hanning window
    N = 512
    t = np.arange(N) / pls.get_fs('dac')
    freq = 55e6
    data = np.sin(2 * np.pi * freq * t) * np.hanning(N)
    template_1 = pls.setup_template(output_port, group=0, template=data)

    ######################################################################
    # setup scale for the (output, group). only one scale used
    pls.setup_scale_lut(output_port, group=0, scales=1.0)

    ######################################################################
    # define the sequence of pulses and data stores in time
    # at time zero, output the template and start a store window
    T = 0.0
    pls.output_pulse(T, template_1)
    pls.store(T)

    ######################################################################
    # Actually run the sequence, only run once with no averaging
    pls.run(period=10e-6, repeat_count=1, num_averages=1)
    t_arr, data = pls.get_store_data()

fig, ax = plt.subplots(tight_layout=True)
ax.plot(1e9 * t_arr, data[0, 0, :], label="store 0, port 0")
ax.set_xlabel("Time [ns]")
ax.set_ylabel("Input signal [FS]")
ax.legend()
fig.show()
