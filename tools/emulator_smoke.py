"""Headless Libretro/DeSmuME runner for repeatable ROM smoke checks.

Core download: https://buildbot.libretro.com/nightly/windows/x86_64/latest/
API: https://github.com/libretro/RetroArch/blob/master/libretro-common/include/libretro.h
The core is an optional local QA dependency, not part of the translation.
"""
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
from PIL import Image
from xros_text import ROOT


class Variable(C.Structure):
    _fields_ = [('key', C.c_char_p), ('value', C.c_char_p)]


class Game(C.Structure):
    _fields_ = [('path', C.c_char_p), ('data', C.c_void_p), ('size', C.c_size_t), ('meta', C.c_char_p)]


ENV = C.CFUNCTYPE(C.c_bool, C.c_uint, C.c_void_p)
VIDEO = C.CFUNCTYPE(None, C.c_void_p, C.c_uint, C.c_uint, C.c_size_t)
AUDIO = C.CFUNCTYPE(None, C.c_int16, C.c_int16)
BATCH = C.CFUNCTYPE(C.c_size_t, C.c_void_p, C.c_size_t)
POLL = C.CFUNCTYPE(None)
INPUT = C.CFUNCTYPE(C.c_int16, C.c_uint, C.c_uint, C.c_uint, C.c_uint)
LOG = C.CFUNCTYPE(None, C.c_int, C.c_char_p)
BUTTONS = {'B': 0, 'Y': 1, 'SELECT': 2, 'START': 3, 'UP': 4, 'DOWN': 5, 'LEFT': 6, 'RIGHT': 7, 'A': 8, 'X': 9, 'L': 10, 'R': 11}


class Emulator:
    def __init__(self, rom, directory):
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path_bytes = str(self.directory).encode('utf-8')
        self.variables = {}
        self.pixel_format = 0
        self.last_frame = None
        self.buttons = set()
        self.pointer = None
        self.frames = 0
        self.core = C.CDLL(str(ROOT / '.tools/desmume/desmume_libretro.dll'))
        # DeSmuME calls the log interface unconditionally during startup.
        # The Win64 callback ignores its optional printf arguments.
        self.log_callback = LOG(lambda level, fmt: None)
        self.callbacks = [ENV(self.environment), VIDEO(self.video), AUDIO(lambda a, b: None), BATCH(lambda data, n: n), POLL(lambda: None), INPUT(self.input)]
        for name, callback in zip(['environment', 'video_refresh', 'audio_sample', 'audio_sample_batch', 'input_poll', 'input_state'], self.callbacks):
            function = getattr(self.core, 'retro_set_' + name)
            function.argtypes = [type(callback)]
            function(callback)
        self.core.retro_load_game.argtypes = [C.POINTER(Game)]
        self.core.retro_load_game.restype = C.c_bool
        self.core.retro_serialize_size.restype = C.c_size_t
        self.core.retro_serialize.argtypes = [C.c_void_p, C.c_size_t]
        self.core.retro_serialize.restype = C.c_bool
        self.core.retro_unserialize.argtypes = [C.c_void_p, C.c_size_t]
        self.core.retro_unserialize.restype = C.c_bool
        self.core.retro_init()
        self.rom_data = Path(rom).read_bytes()
        self.rom_buffer = C.create_string_buffer(self.rom_data)
        self.rom_name = str(Path(rom).resolve()).encode('utf-8')
        game = Game(self.rom_name, C.cast(self.rom_buffer, C.c_void_p), len(self.rom_data), None)
        if not self.core.retro_load_game(C.byref(game)):
            raise RuntimeError('Core could not load ROM')

    def environment(self, command, pointer):
        command &= 0xffff
        if command == 3:
            C.cast(pointer, C.POINTER(C.c_bool))[0] = True
            return True
        if command in (9, 30, 31):
            C.cast(pointer, C.POINTER(C.c_char_p))[0] = self.path_bytes
            return True
        if command == 10:
            self.pixel_format = C.cast(pointer, C.POINTER(C.c_uint))[0]
            return self.pixel_format in (0, 1, 2)
        if command == 15:
            variable = C.cast(pointer, C.POINTER(Variable)).contents
            key = variable.key.decode()
            value = self.variables.get(key)
            if value is None:
                return False
            variable.value = value
            return True
        if command == 16:
            variables = C.cast(pointer, C.POINTER(Variable))
            i = 0
            while variables[i].key:
                key = variables[i].key.decode()
                choices = variables[i].value.decode().split('; ', 1)[-1].split('|')
                preferred = {
                    'desmume_num_cores': '1',
                    'desmume_internal_resolution': '256x192',
                    'desmume_screens_layout': 'top/bottom',
                    'desmume_use_external_bios': 'disabled',
                    'desmume_boot_into_bios': 'disabled',
                    'desmume_pointer_mouse': 'enabled',
                    'desmume_pointer_type': 'touch',
                }.get(key, choices[0])
                self.variables[key] = (preferred if preferred in choices else choices[0]).encode()
                i += 1
            return True
        if command == 27:
            C.cast(pointer, C.POINTER(C.c_void_p))[0] = C.cast(self.log_callback, C.c_void_p).value
            return True
        if command in (17, 52):
            C.cast(pointer, C.POINTER(C.c_bool))[0] = False
            return True
        if command in (37, 61, 63):
            C.cast(pointer, C.POINTER(C.c_uint))[0] = 0
            return True
        if command == 47:
            C.cast(pointer, C.POINTER(C.c_uint))[0] = 3
            return True
        if command in (6, 11, 18, 35, 36):
            return True
        return False

    def video(self, data, width, height, pitch):
        if data:
            self.last_frame = (C.string_at(data, height * pitch), width, height, pitch)

    def input(self, port, device, index, button):
        if port != 0:
            return 0
        if device == 1:
            return int(button in self.buttons)
        if device == 6 and self.pointer:
            if button == 0:
                return self.pointer[0]
            if button == 1:
                return self.pointer[1]
            if button == 2:
                return 1
        return 0

    def run(self, frames, button=None, touch=None):
        self.buttons = {BUTTONS[b.upper()] for b in (button or '').split('+') if b}
        self.pointer = touch
        for _ in range(frames):
            self.core.retro_run()
            self.frames += 1
        self.buttons = set()
        self.pointer = None

    def snapshot(self, name):
        if not self.last_frame:
            raise RuntimeError('No video frame received')
        raw, width, height, pitch = self.last_frame
        if self.pixel_format == 1:
            image = Image.frombytes('RGB', (width, height), raw, 'raw', 'BGRX', pitch, 1)
        else:
            pixels = []
            for y in range(height):
                for x in range(width):
                    index = y * pitch + x * 2
                    value = int.from_bytes(raw[index:index + 2], 'little')
                    if self.pixel_format == 2:
                        pixels.extend((((value >> 11) & 31) * 255 // 31, ((value >> 5) & 63) * 255 // 63, (value & 31) * 255 // 31))
                    else:
                        pixels.extend((((value >> 10) & 31) * 255 // 31, ((value >> 5) & 31) * 255 // 31, (value & 31) * 255 // 31))
            image = Image.frombytes('RGB', (width, height), bytes(pixels))
        path = self.directory / f'{name}.png'
        image.save(path)
        print(json.dumps({'snapshot': str(path), 'frames': self.frames, 'frame_sha256': hashlib.sha256(raw).hexdigest()}), flush=True)

    def save(self, path):
        size = self.core.retro_serialize_size()
        buffer = C.create_string_buffer(size)
        if not self.core.retro_serialize(buffer, size):
            raise RuntimeError('Cannot save emulator state')
        Path(path).write_bytes(buffer.raw)

    def load(self, path):
        data = Path(path).read_bytes()
        buffer = C.create_string_buffer(data)
        if not self.core.retro_unserialize(buffer, len(data)):
            raise RuntimeError('Cannot load emulator state')

    def close(self):
        self.core.retro_unload_game()
        self.core.retro_deinit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path)
    parser.add_argument('--directory', type=Path, default=ROOT / 'build/qa')
    parser.add_argument('--sequence', type=Path, required=True)
    parser.add_argument('--load-state', type=Path)
    parser.add_argument('--save-state', type=Path)
    args = parser.parse_args()
    emulator = Emulator(args.rom, args.directory)
    try:
        if args.load_state:
            emulator.load(args.load_state)
        for step in json.loads(args.sequence.read_text(encoding='utf-8')):
            emulator.run(step.get('frames', 1), step.get('button'), step.get('touch'))
            if 'snapshot' in step:
                emulator.snapshot(step['snapshot'])
            if 'state' in step:
                emulator.save(args.directory / step['state'])
        if args.save_state:
            emulator.save(args.save_state)
    finally:
        emulator.close()
