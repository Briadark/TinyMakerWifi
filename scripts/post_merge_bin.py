Import("env")
import os

# Po USB (env:tinymaker) buildo sujungia bootloader + partition table + app
# i viena "firmware-full.bin" - pirmam flash'inimui per USB (0x0 adresu).
# "firmware.bin" (vien app) lieka OTA/wireless atnaujinimams.

def merge_full_bin(source, target, env):
    build_dir = env.subst("$BUILD_DIR")
    app_bin = str(target[0])
    bootloader_bin = os.path.join(build_dir, "bootloader.bin")
    partitions_bin = os.path.join(build_dir, "partitions.bin")
    full_bin = os.path.join(build_dir, "firmware-full.bin")

    if not (os.path.exists(bootloader_bin) and os.path.exists(partitions_bin)):
        print("[post_merge_bin] bootloader.bin/partitions.bin nerasti, firmware-full.bin praleistas")
        return

    esptool_py = os.path.join(
        env.PioPlatform().get_package_dir("tool-esptoolpy"), "esptool.py"
    )

    env.Execute(
        " ".join(
            [
                '"%s"' % env.subst("$PYTHONEXE"),
                '"%s"' % esptool_py,
                "--chip", "esp32",
                "merge_bin",
                "-o", '"%s"' % full_bin,
                "--flash_mode", "dio",
                "--flash_freq", "40m",
                "--flash_size", "4MB",
                "0x1000", '"%s"' % bootloader_bin,
                "0x8000", '"%s"' % partitions_bin,
                "0x10000", '"%s"' % app_bin,
            ]
        )
    )
    print("[post_merge_bin] firmware-full.bin atnaujintas: %s" % full_bin)

env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", merge_full_bin)
