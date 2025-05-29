import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from acconeer.exptool import a121
import time

def get_distances_m(config):
    # Calculate range (m) from config
    range_indices = np.arange(config.num_points) * config.step_length + config.start_point
    return range_indices * 2.5e-3

fs = 20             # Sampling frequency (frames per second)
duration = 10       # seconds
total_frames = fs * duration
sweeps_per_frame = 20

def main():


    client = a121.Client.open(serial_port="/dev/ttyUSB0")
    dist=float(input("Enter the range in meters : "))
    step_mm = 20
    start_m = 1.5
    points=(((dist+0.5)*1000)-start_m*1000)/(step_mm)

    config = a121.SensorConfig(
        profile=a121.Profile.PROFILE_3,
        start_point=(start_m/0.0025),
        num_points=points,
        step_length=(step_mm/2.5),
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
            
            result = client.get_next()
            sweep = result.frame
            iq = np.array(sweep)  # Shape: (sweeps_per_frame, num_points)
            amp = np.abs(iq)
            all_amp.append(amp)
            all_iq.append(iq)
            time.sleep(1/fs)
            elapsed = time.time() - start_time
            if elapsed >= duration:
              break
    except KeyboardInterrupt:
        print("[INFO] Data collection interrupted.")
    finally:
        client.stop_session()
        client.close()
        print("[INFO] Radar session closed.")

    iq_data = np.array(all_iq)  # Shape: (frames, sweeps_per_frame, num_points)
    return iq_data,all_amp,total_frames,distances



def profile_range(all_amp, distances):
    plt.figure(figsize=(10, 6))

    for i, amp_matrix in enumerate(all_amp):
        for j, row in enumerate(amp_matrix):
            color = plt.cm.viridis(j / amp_matrix.shape[0])  # different color for each row
            label = f"Array {i+1} - Row {j+1}" if i == 0 else None  # only label first group to avoid clutter
            plt.plot(distances, row, color=color, alpha=0.7, label=label)

    plt.title("Range Profiles (Amplitude vs. Distance)")
    plt.xlabel("Distance (m)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend(loc='upper right', fontsize=8, ncol=2)
    plt.tight_layout()
    plt.show()




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

def range_doppler_matrix(sweep_iq,num_points):
    jj


if __name__ == "__main__":
    iq_data,all_amp,total_frames,distances=main()

range_slow_matrix(all_amp,total_frames,distances)
profile_range(all_amp, distances)


