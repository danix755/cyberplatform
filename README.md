# CYBERPLATFORM — Android project

This is a touchscreen-focused Android port of the neon platformer concept.
It uses Kivy rather than Pygame because Kivy provides a practical route to
Android packaging with Buildozer / python-for-android.

## Run on a computer first

1. Install Python 3.10 or newer.
2. Install Kivy:

   ```bash
   python -m pip install kivy
   ```

3. Run:

   ```bash
   python main.py
   ```

The desktop preview window is configured at 960×540. Android uses the
device's landscape screen.

## Build an Android APK

Buildozer's Android toolchain is designed for Linux. The easiest supported
route is a Linux computer or an Ubuntu environment (for example, WSL2 on
Windows). Install the Android build dependencies following the current
Buildozer installation guide:

https://buildozer.readthedocs.io/en/latest/installation.html

Then, from this project directory:

```bash
python3 -m pip install --user buildozer
buildozer android debug
```

The first build downloads Android SDK/NDK and other build components and
can take a while. When successful, the APK is placed in `bin/`.

For a release build, configure signing and follow Buildozer's release
instructions. Do not distribute an unsigned debug APK as a production release.

## Mobile controls

- Hold ◀ to move left.
- Hold ▶ to move right.
- Hold JUMP to request a jump (tap while grounded).
- Tap Ⅱ to pause or resume.
- Tap START GAME / PLAY AGAIN on the title or end screen.

## Gameplay

- Collect yellow energy crystals for points.
- Avoid pink patrol drones; landing on top defeats them.
- Touch the green checkpoint to update your respawn point.
- Reach the purple beacon at the far end to clear the sector.
- You have three energy points.

## Project files

- `main.py` — Kivy game, rendering, physics, touch controls and game states.
- `buildozer.spec` — Android package configuration.
- `README.md` — setup and build instructions.

## Notes

This project is an Android-ready source project, not a precompiled APK.
An APK must be compiled with Buildozer and the Android SDK/NDK on a
supported build machine. Test the resulting APK on your target Android
device before sharing it.


## Easiest build option: GitHub Actions (no Android SDK installation)

The project includes `.github/workflows/android.yml`. To build in GitHub's
cloud runner:

1. Sign in to GitHub and create a new repository named `cyberplatform`.
2. Upload the contents of this ZIP to the repository (make sure
   `.github/workflows/android.yml` is included; enable viewing hidden files
   if your file picker hides `.github`).
3. Open the repository's **Actions** tab.
4. Select **Build CYBERPLATFORM Android APK** and click **Run workflow**.
   A push to the `main` branch also triggers a build.
5. When the run finishes successfully, open the run and download the
   `cyberplatform-debug-apk` artifact.
6. Extract the artifact ZIP to get the `.apk`, then install it on your
   Android device. Android may ask you to allow installation from that
   source.

This workflow builds a debug APK. It is suitable for personal testing;
a Play Store release needs a signed release build.
