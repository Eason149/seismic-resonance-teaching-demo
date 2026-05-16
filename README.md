# seismic-resonance-teaching-demo
A Python Signals-and-Systems teaching demo that models buildings as second-order LTI systems, visualizing seismic input, resonance, damping effects, and low/mid/high-rise response differences with figures, GIFs, and sonified WAV outputs.
# From Seismic Waves to Building Sway

Python classroom presentation project for **Signals and Systems**:
**“From Seismic Waves to Building Sway: Applying Signals and Systems to Structural Resonance Analysis.”**

## Course Connection
- Seismic wave `a_g(t)` = **input signal**
- Building (single-DOF mass-spring-damper) = **LTI system**
- Building relative displacement `x(t)` = **output signal**
- System behavior is analyzed through **differential equation**, **convolution/system response**, **Fourier transform**, **frequency response**, **resonance**, and **damping**.

## Mathematical Model

We model the building as a single-degree-of-freedom second-order system:

$$
m\ddot{x}(t)+c\dot{x}(t)+kx(t)=-m a_g(t)
$$

Normalize by \(m\):

$$
\ddot{x}(t)+2\zeta\omega_n\dot{x}(t)+\omega_n^2x(t)=-a_g(t)
$$

where

- $\omega_n=\sqrt{\frac{k}{m}}$ is the natural angular frequency.
- $\zeta=\frac{c}{2\sqrt{km}}$ is the damping ratio.

Transfer function:

$$
H(s)=\frac{X(s)}{A_g(s)}
=
\frac{-1}{s^2+2\zeta\omega_n s+\omega_n^2}
$$

Frequency response:

$$
H(j\omega)=
\frac{-1}{(\omega_n^2-\omega^2)+j2\zeta\omega_n\omega}
$$

Magnitude response:

$$
|H(j\omega)|=
\frac{1}{
\sqrt{
(\omega_n^2-\omega^2)^2+
(2\zeta\omega_n\omega)^2
}
}
$$

Interpretation:

- When the input spectrum overlaps the system natural frequency, the output becomes large. This is resonance.
- A larger $\zeta$ reduces vibration amplitude and ringing duration.

## Project Structure
```text
seismic_building_demo/
├── main.py
├── requirements.txt
├── README.md
└── src/
    ├── __init__.py
    ├── signal_generation.py
    ├── building_system.py
    ├── visualization.py
    ├── animation.py
    └── sonification.py
```

## How to Run
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Run all demos (one click):
```bash
python main.py
```

`main.py` automatically creates output folders and generates all figures, GIFs, and WAV files.

## Generated Outputs
Figures:
- `outputs/figures/01_seismic_input_waveform.png`
- `outputs/figures/02_seismic_frequency_spectrum.png`
- `outputs/figures/03_building_frequency_response.png`
- `outputs/figures/04_different_building_responses.png`
- `outputs/figures/04a_responses_real_scale.png`
- `outputs/figures/04b_responses_normalized.png`
- `outputs/figures/05_damping_comparison.png`

Animations:
- `outputs/animations/06_building_vibration_animation.gif`
- `outputs/animations/06a_resonance_building.gif`
- `outputs/animations/06b_damped_building.gif`
- `outputs/animations/06c_three_buildings_low_damping.gif`
- `outputs/animations/06d_three_buildings_high_damping.gif`

Audio:
- `outputs/audio/seismic_input.wav`
- `outputs/audio/building_response_resonance.wav`
- `outputs/audio/building_response_damped.wav`

## 中文图示说明（课堂讲解可直接用）
- `01_seismic_input_waveform.png`：模拟地震加速度输入 \(a_g(t)\) 的时域波形，展示“前弱-中强-后衰减”的震动过程。
- `02_seismic_frequency_spectrum.png`：输入信号的 FFT 频谱图（0-10 Hz），黑色标记点是主频，说明地震不仅有幅值还有频率结构。
- `03_building_frequency_response.png`：三类建筑（低层/中层/高层）的频率响应 \(|H(j\omega)|\)，峰值位置对应各自共振频率。
- `04a_responses_real_scale.png`：同一地震输入下三种建筑的真实位移响应对比，突出系统差异导致输出幅值不同。
- `04b_responses_normalized.png`：将三种输出归一化后比较形态差异，便于观察相位与衰减趋势。
- `04_different_building_responses.png`：输入与单个代表建筑输出的上下对照图，适合快速讲“输入-系统-输出”链路。
- `05_damping_comparison.png`：同一固有频率下不同阻尼比响应，阻尼小振得更大更久，阻尼大衰减更快。
- `06a_resonance_building.gif`：接近共振条件下的建筑摇晃动画，摆动明显。
- `06b_damped_building.gif`：提高阻尼后的动画版本，摆动幅值更小、稳定更快。
- `06c_three_buildings_low_damping.gif`：低阻尼下低层/中层/高层三栋建筑同屏对比，楼体几何尺寸固定。
- `06d_three_buildings_high_damping.gif`：高阻尼下低层/中层/高层三栋建筑同屏对比，通过更多阻尼器图标表示“增加阻尼器”。
- `06_building_vibration_animation.gif`：默认动画文件（与 06a 同步），便于快速展示。
- `seismic_input.wav`：地震输入信号声音化结果（非真实地震声音）。
- `building_response_resonance.wav`：共振版本建筑响应声音化结果。
- `building_response_damped.wav`：高阻尼版本建筑响应声音化结果。

## How to Use in Presentation
- Use Demo 1 and Demo 2 to explain “time domain vs frequency domain”.
- Use Demo 3 to show resonance peak and natural frequency matching.
- Use Demo 4 to emphasize: **same input, different systems, different outputs**.
- Use Demo 5 to demonstrate damping engineering intuition.
- Play Demo 7 WAVs and show Demo 6 GIFs for stronger classroom engagement.

## Sonification Explanation
The generated WAV files are **not real earthquake sounds**.  
They are a **sonification** for education:
- Original seismic/building signals are low-frequency and mostly inaudible.
- We convert them to audible signals by **time compression** (speed-up) and resampling to 44.1 kHz.
- This helps students hear differences in waveform texture and system response behavior.
- For classroom audibility, the damped-response audio may use a stronger speed-up mapping than resonance audio; this is an intentional perceptual mapping, not a physical acoustic recording.

## Dependencies
- numpy
- scipy
- matplotlib
- pillow
- soundfile

Note: this project uses `scipy.io.wavfile` for WAV writing by default, so it can still run even if `soundfile` is unavailable.

## Real Data Extension (Optional)
This project intentionally uses synthetic seismic signals so it runs offline and reliably in class.  
If you later want real records, possible sources include:
- PEER Ground Motion Database
- USGS Earthquake Data
- CESMD Strong Motion Data

## Presentation Demo Order
1. Show the seismic input waveform.
2. Show FFT spectrum and main frequency.
3. Show building frequency response and resonance peak.
4. Compare low-rise, mid-rise, and high-rise responses.
5. Compare low damping and high damping.
6. Play `seismic_input.wav`.
7. Play `building_response_resonance.wav`.
8. Play `building_response_damped.wav`.
9. Show building vibration animation.
10. Conclude: same input signal can produce different outputs through different systems.
