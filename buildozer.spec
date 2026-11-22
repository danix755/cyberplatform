[app]
title = CyberPlatform
package.name = cyberplatform
package.domain = org.cart3r
source.dir = .
source.include_exts = py,kv,png,jpg,atlas,ttf,txt
version = 1.0.0
requirements = python3,kivy
orientation = landscape
fullscreen = 1
# Android permissions are not required for this offline game.
android.permissions =
android.api = 35
android.minapi = 23
android.archs = arm64-v8a
android.allow_backup = 0
android.release_artifact = apk

android.release_artifact = apk
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
