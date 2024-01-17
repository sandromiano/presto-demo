""" Create one baseband output template and sample it. 

Connect one output port directly to one input port.
"""
import matplotlib.pyplot as plt
import numpy as np

from presto import pulsed
from presto.utils import sin2

# Any port on Vivace
# Any port on Presto wide, wamp and low
# Ports 5-8 on Presto-8-QC
# Ports 9-16 on Presto-16-QC
output_port = 9
input_port = 9

ADDRESS = "192.168.20.19"  # set address/hostname of Vivace/Presto here
EXT_REF = False  # set to True to use external 10 MHz reference

with pulsed.Pulsed(
    ext_ref_clk=EXT_REF,
    address=ADDRESS,
    adc_mode=pulsed.AdcMode.Direct,
    dac_mode=pulsed.DacMode.Direct,
) as pls:
    ######################################################################
    # Select input ports to store and the duration of each store
    pls.set_store_ports(input_port)
    pls.set_store_duration(2000e-9)  # 2000 ns

    ######################################################################
    # create a 200 ns long template on output_port
    # make a sine wave with a square window
    duration = 200e-9
    N = int(round(duration * pls.get_fs("dac")))
    t = np.linspace(0, duration, N, endpoint=False)
    freq = 40e6
    phase = -np.pi / 2
    data = sin2(N) * np.cos(2 * np.pi * freq * t + phase)
    template_1 = pls.setup_template(output_port, group=0, template=data, envelope=False)

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
