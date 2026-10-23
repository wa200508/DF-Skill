# Direction Finding RF Skill

A standalone RF skill that estimates direction of arrival from calibrated,
coherent receiver I/Q. It currently uses the **MUSIC** algorithm. The application
is named **Direction Finding RF Skill**; MUSIC is its numerical backend.

This repo owns the receiver application and algorithm. It does not contain or
depend on AirSim, Sionna, ray paths, transmitter waveforms or simulation truth.
The same receiver-facing interface accepts a live acquisition adapter or saved
I/Q replay. [airsim-rf](https://github.com/wa200508/airsim-rf) is one possible
sample source.

## Pull and run

The CI workflow tests and publishes `ghcr.io/wa200508/df-skill:latest`, plus
immutable `sha-<commit>` tags. The image runs on CPU without a GPU.

```bash
docker pull ghcr.io/wa200508/df-skill:latest
# receivers.json is the receiver-config.json from a saved capture, or your hardware layout.
docker run --rm --name df-skill \
  -p 127.0.0.1:8811:8811 -p 127.0.0.1:8812:8812 -p 127.0.0.1:8813:8813 \
  --mount "type=bind,src=$PWD/receivers.json,dst=/config/arrays.json,readonly" \
  ghcr.io/wa200508/df-skill:latest
```

HTTP diagnostics: `http://127.0.0.1:8812/status`. The receiver remains listening
until a source sends data; `/health` is ready when ingress is bound and processing
has not failed. For persistent results, mount a writable directory at `/results`
and append `--arrays /config/arrays.json --results-dir /results`. On rootless
Docker, use `--user 0:0` for a host-owned results mount; that UID maps to the
calling user, not host root. On rootful Docker use your host UID:GID when needed.

CI verifies anonymous pulls of each published image. The independent image's
public pull was checked successfully; no registry login is needed.

## Develop and test

```bash
git clone https://github.com/wa200508/DF-Skill.git
cd DF-Skill
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m pip install -e '.[test]'
pytest -q
python -m df_skill --arrays /path/to/receiver-config.json --results-dir results/run-1
```

Tests include known-bearing arrays and the real TCP/HTTP/gRPC service, saving
and replaying exact I/Q without importing a simulator.

## Inputs, results and playback

The existing **receiver TCP v2** protocol is retained: complex float32 input-
referred volts, channel IDs, acquisition timestamps, sample rate/carrier,
clipping metadata and coherent-window commits with acknowledgements.
[The wire contract](https://github.com/wa200508/airsim-rf/blob/main/docs/iq-stream.md)
is versioned independently of an acquisition source.

Receiver configuration is schema v1: sample_rate_hz, carrier_hz and two sites,
each with ordered channels, center_rf_m, yaw_rad, element_offsets_m and
calibration_complex pairs. This initial implementation requires two coherent
ULAs with at least three elements each, spacing no larger than half a wavelength,
and one dominant arrival per site. ULA front/back and elevation ambiguity remain.
The service examines at most 24,000 simultaneous samples per window.

Use a new skill process/results directory per experiment:
```bash
python -m df_skill.sample_recording inspect /path/to/iq --verify
python -m df_skill.sample_recording replay /path/to/iq --port 8811
# --speed 1 paces original acquisition time; default sends as fast as acknowledged.
```

The neutral adapter supports the existing per-channel SigMF cf32_le archive
layout. It also writes/opens the same stock-block GNU Radio starter graphs.
This does not change samples, phase or Doppler. It is not a universal SigMF
reader. No waveform regeneration is used.

Results contain bearings, spectra, spatial search, phase and per-window
acquisition timestamps. The existing `music_db` wire field is preserved for
observer compatibility; new application identity is `direction-finding-rf-skill`
and the algorithm is explicitly `MUSIC`.

## Code map

| Concern | Location |
|---|---|
| Service, coherent grouping, HTTP and gRPC | `src/df_skill/app.py` |
| MUSIC steering/covariance/PSD math | `src/df_skill/music.py` |
| Source-neutral I/Q framing and acknowledgements | `src/df_skill/sample_stream.py` |
| Offline sample archive/replay | `src/df_skill/sample_recording.py` |
| GNU Radio graph export | `src/df_skill/gnuradio_export.py` |
| Result journal | `src/df_skill/results.py` |
| Acquisition status/control protobuf | `src/df_skill/control/` |
| Standalone acquisition example | `examples/receiver-config.json` |

Environment defaults: `RF_IQ_PORT=8811`, `RF_HTTP_PORT=8812`,
`RF_CONTROL_PORT=8813`; CLI options override them. The consumer reports receiver
status but cannot tune or command acquisition hardware. Existing SQUALL-shaped
status endpoints are retained; native AMS-GRA MEL/VITA/UCI compliance is not
newly claimed. No GNU Radio flowgraph or simulator is required to run this skill.

## License and provenance

**Apache License 2.0**, matching the Hello World Starter Kit's public RF skill:
[upstream LICENSE](https://gitlab.com/open-arsenal/ams-gra/hello-world-sk/skills/rf-fm-demod/-/blob/main/LICENSE).
The current public skills group lists RF FM Demod and IR Search and Track;
no separate ESM-named public repo was found at extraction.

See [LICENSE](LICENSE), [NOTICE](NOTICE), the retained original MIT attribution
in [licenses/airsim-rf-MIT.txt](licenses/airsim-rf-MIT.txt), and upstream protocol
notices in `third_party/`. Selecting the same license does not imply Government
authorship of DF-Skill.
