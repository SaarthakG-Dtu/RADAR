import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from acconeer.exptool import a121
import time

def get_distances_m(config):
    # Calculate range (m) from config
    range_indices = np.arange(config.num_points)*config.step_length  + config.start_point
    return range_indices * 2.5e-3

fs = 20             # Sampling frequency (frames per second)
duration = 10       # seconds
total_frames = fs * duration
sweeps_per_frame = 5

def main():

    client = a121.Client.open(serial_port="/dev/ttyUSB0")
    dist=float(input("Enter the range in meters : "))
    step_mm = 20
    start_m = 0.3
    points=(((dist+0.5)*1000)-start_m*1000)/(step_mm)

    config = a121.SensorConfig(
        profile=a121.Profile.PROFILE_3,
        step_length=(step_mm/2.5),
        start_point=(start_m/0.0025),
        num_points=points,
        sweeps_per_frame=sweeps_per_frame,
        frame_rate=fs
    )
    client.setup_session(config)
    client.start_session()
    distances = get_distances_m(config)
    print(f"[INFO] Collecting {duration} seconds of live radar data...")
    start_time = time.time()
    all_iq = []
    all_amp=[]

    try:
        for _ in range(total_frames):
            loop_start = time.time()
            result = client.get_next()
            sweep = result.frame
            iq = np.array(sweep)  # Shape: (sweeps_per_frame, num_points)
            amp = np.abs(iq)
            all_amp.append(amp)
            all_iq.append(iq)
            elapsed_loop = time.time() - loop_start
            time.sleep(max(0, (1/fs) - elapsed_loop))
    except KeyboardInterrupt:
        print("[INFO] Data collection interrupted.")
    finally:
        client.stop_session()
        client.close()
        print("[INFO] Radar session closed.")

    iq_data = np.array(all_iq)  # Shape: (frames, sweeps_per_frame, num_points)
    return iq_data,all_amp,total_frames,distances



def profile_range(all_amp, distances):
    plt.ion()  # Enable interactive mode
    fig, ax = plt.subplots()

    for i in range(len(all_amp)):  # One frame = one plot
        ax.clear()  # Clear previous frame
        for j in range(all_amp[i].shape[0]):  # 5 sweeps per frame
            ax.plot(distances, all_amp[i][j, :], label=f"Sweep {j+1}")
        ax.set_title(f"Range Profile - Frame {i+1}")
        ax.set_xlabel("Distance (m)")
        ax.set_ylabel("Amplitude")
        ax.grid(True)
        ax.legend(loc="upper right", fontsize="small", ncol=2)
        plt.pause(0.01)  # Pause briefly to display the frame

    plt.ioff()  # Turn off interactive mode

       



def range_slow_matrix(all_amp,num_frames,distances):

    rsm = np.vstack(all_amp)# Shape: (num_sweeps, num_points)

    # Plot Range-Slow Matrix with distance axis
    plt.figure()
    plt.imshow(
        rsm,
        extent=[ distances[0], distances[-1],0, num_frames*sweeps_per_frame],
        aspect='auto',
        origin='lower',
        cmap='hot'
    )
    plt.title("Range-Slow Matrix (Amplitude)")
    plt.xlabel("Distance (m)")
    plt.ylabel("Sweep Index (Slow Time)")    
    plt.colorbar(label="Amplitude")
    plt.show()


def arctangent_demodulation(iq_data):
    """
    Performs arctangent demodulation by computing the phase angle
    of averaged IQ per sweep over all range bins.
    """
    print(iq_data.shape)
    print(iq_data)
    frames, sweeps, points = iq_data.shape
    total_sweeps = frames * sweeps

    iq_flat = iq_data.reshape((total_sweeps, points))  # Shape: (total_sweeps, points)
    avg_iq_per_sweep = np.mean(iq_flat, axis=1)        # Shape: (total_sweeps,)

    phase = np.angle(avg_iq_per_sweep)
    unwrapped_phase = np.unwrap(phase)

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(unwrapped_phase)
    plt.title("Arctangent Demodulation (Averaged Phase vs Sweep Index)")
    plt.xlabel("Sweep Index")
    plt.ylabel("Phase (radians)")
    plt.grid(True)
    plt.show()


def range_doppler_matrix(sweep_iq,num_points):
    gg
   


if __name__ == "__main__":
    iq_data,all_amp,total_frames,distances=main()

profile_range(all_amp, distances)
range_slow_matrix(all_amp,total_frames,distances)
arctangent_demodulation(iq_data)

