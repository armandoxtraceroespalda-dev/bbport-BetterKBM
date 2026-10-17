"""Windows-only mouse bridge, hosted by the port's bundled Python (--script).

Only mouse buttons/wheel are inspected, and only Bloodborne's own foreground
window with a hidden cursor receives translated keys. No game files are patched.
"""
import ctypes as C
import hashlib
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import threading
import traceback

HERE = Path(__file__).resolve().parent
PORT = HERE.parent
sys.path.insert(0, str(HERE))
from control_logic import Controls

U32, I32, UPTR, IPTR = C.c_uint32, C.c_int32, C.c_size_t, C.c_ssize_t
user32 = C.WinDLL('user32', use_last_error=True)
kernel32 = C.WinDLL('kernel32', use_last_error=True)


class POINT(C.Structure):
    _fields_ = [('x', I32), ('y', I32)]


class MOUSEINPUT(C.Structure):
    _fields_ = [('dx', I32), ('dy', I32), ('mouseData', U32), ('dwFlags', U32),
                ('time', U32), ('dwExtraInfo', UPTR)]


class KEYBDINPUT(C.Structure):
    _fields_ = [('wVk', C.c_uint16), ('wScan', C.c_uint16), ('dwFlags', U32),
                ('time', U32), ('dwExtraInfo', UPTR)]


class HARDWAREINPUT(C.Structure):
    _fields_ = [('uMsg', U32), ('wParamL', C.c_uint16), ('wParamH', C.c_uint16)]


class INPUTUNION(C.Union):
    _fields_ = [('mi', MOUSEINPUT), ('ki', KEYBDINPUT), ('hi', HARDWAREINPUT)]


class INPUT(C.Structure):
    _fields_ = [('type', U32), ('data', INPUTUNION)]


class CURSORINFO(C.Structure):
    _fields_ = [('cbSize', U32), ('flags', U32), ('hCursor', C.c_void_p),
                ('ptScreenPos', POINT)]


class MSLLHOOKSTRUCT(C.Structure):
    _fields_ = [('pt', POINT), ('mouseData', U32), ('flags', U32),
                ('time', U32), ('dwExtraInfo', UPTR)]


HOOKPROC = C.WINFUNCTYPE(IPTR, C.c_int, UPTR, IPTR)
user32.SetWindowsHookExW.argtypes = [C.c_int, HOOKPROC, C.c_void_p, U32]
user32.SetWindowsHookExW.restype = C.c_void_p
user32.CallNextHookEx.argtypes = [C.c_void_p, C.c_int, UPTR, IPTR]
user32.CallNextHookEx.restype = IPTR
user32.UnhookWindowsHookEx.argtypes = [C.c_void_p]
user32.UnhookWindowsHookEx.restype = C.c_int
user32.GetForegroundWindow.restype = C.c_void_p
user32.GetWindowThreadProcessId.argtypes = [C.c_void_p, C.POINTER(U32)]
user32.GetWindowThreadProcessId.restype = U32
user32.GetCursorInfo.argtypes = [C.POINTER(CURSORINFO)]
user32.GetAsyncKeyState.argtypes = [C.c_int]
user32.GetAsyncKeyState.restype = C.c_short
user32.SendInput.argtypes = [U32, C.POINTER(INPUT), C.c_int]
user32.SendInput.restype = U32
kernel32.OpenProcess.argtypes = [U32, C.c_int, U32]
kernel32.OpenProcess.restype = C.c_void_p
kernel32.QueryFullProcessImageNameW.argtypes = [C.c_void_p, U32, C.c_wchar_p, C.POINTER(U32)]
kernel32.QueryFullProcessImageNameW.restype = C.c_int
kernel32.CloseHandle.argtypes = [C.c_void_p]
kernel32.GetModuleHandleW.argtypes = [C.c_wchar_p]
kernel32.GetModuleHandleW.restype = C.c_void_p
kernel32.CreateMutexW.argtypes = [C.c_void_p, C.c_int, C.c_wchar_p]
kernel32.CreateMutexW.restype = C.c_void_p
user32.MessageBoxW.argtypes = [C.c_void_p, C.c_wchar_p, C.c_wchar_p, U32]

SCAN = {'light': (0x44, False), 'heavy': (0x57, False), 'firearm': (0x58, False),
        'up': (0x48, True), 'down': (0x50, True),
        'left': (0x4B, True), 'right': (0x4D, True)}


def send_key(key, down):
    scan, extended = SCAN[key]
    flags = 0x0008 | (0x0001 if extended else 0) | (0 if down else 0x0002)
    event = INPUT(type=1, data=INPUTUNION(ki=KEYBDINPUT(0, scan, flags, 0, 0)))
    if user32.SendInput(1, C.byref(event), C.sizeof(INPUT)) != 1:
        raise OSError('Windows no pudo enviar la tecla. Abre juego y complemento con el mismo nivel de permisos.')


class Bridge:
    def __init__(self, root):
        self.root = root
        self.controls = Controls(send_key)
        self.enabled = True
        self.stopping = False
        self.last_window = None
        self.is_game = False
        self.error = None
        self.wheel_rest = 0
        self.callback = HOOKPROC(self.mouse_hook)
        self.hook = user32.SetWindowsHookExW(14, self.callback, kernel32.GetModuleHandleW(None), 0)
        if not self.hook:
            raise C.WinError(C.get_last_error())
        self.poll()

    def active(self):
        if not self.enabled or self.stopping:
            return False
        hwnd = user32.GetForegroundWindow()
        if hwnd != self.last_window:
            self.last_window = hwnd
            self.is_game = False
            pid = U32()
            user32.GetWindowThreadProcessId(hwnd, C.byref(pid))
            handle = kernel32.OpenProcess(0x1000, 0, pid.value)
            if handle:
                try:
                    text = C.create_unicode_buffer(32768)
                    length = U32(len(text))
                    if kernel32.QueryFullProcessImageNameW(handle, 0, text, C.byref(length)):
                        self.is_game = os.path.normcase(os.path.abspath(text.value)) == os.path.normcase(
                            str((PORT / 'bin' / 'bb-probe.exe').resolve()))
                finally:
                    kernel32.CloseHandle(handle)
        if not self.is_game:
            return False
        cursor = CURSORINFO(cbSize=C.sizeof(CURSORINFO))
        # A visible cursor means launcher, overlay, text entry, or mouse look off.
        return bool(user32.GetCursorInfo(C.byref(cursor))) and not (cursor.flags & 1)

    def mouse_hook(self, code, message, address):
        try:
            if code >= 0 and message in (0x0201, 0x0202, 0x0204, 0x0205, 0x020A):
                event = C.cast(address, C.POINTER(MSLLHOOKSTRUCT)).contents
                if not (event.flags & 1):
                    if self.active():
                        shift = bool(user32.GetAsyncKeyState(0x10) & 0x8000)
                        if message == 0x0201:
                            self.controls.press('left', shift)
                        elif message == 0x0202:
                            self.controls.release('left')
                        elif message == 0x0204:
                            self.controls.press('right', shift)
                        elif message == 0x0205:
                            self.controls.release('right')
                        elif message == 0x020A:
                            self.wheel_rest += C.c_int16(event.mouseData >> 16).value
                            # Avoid runaway pulse queues from free-spinning wheels.
                            steps = max(-4, min(4, int(self.wheel_rest / 120)))
                            if steps:
                                self.wheel_rest = 0
                                self.controls.wheel(steps > 0, shift)
                    else:
                        self.controls.cancel()
                        self.wheel_rest = 0
        except Exception as exc:
            self.error = str(exc)
            self.enabled = False
        # Preserve native mouse motion and all clicks for overlays/other programs.
        return user32.CallNextHookEx(self.hook, code, message, address)

    def poll(self):
        if self.stopping:
            return
        try:
            if self.active():
                self.controls.tick()
            else:
                self.controls.cancel()
                self.wheel_rest = 0
        except Exception as exc:
            self.error = str(exc)
            self.enabled = False
        self.root.after(10, self.poll)

    def close(self):
        self.stopping = True
        try:
            self.controls.cancel()
        finally:
            user32.UnhookWindowsHookEx(self.hook)


def scan_gpus(results):
    devices = []
    try:
        for index in range(8):
            env = os.environ.copy()
            env['BB_GPU_ID'] = str(index)
            result = subprocess.run([str(PORT / 'bin' / 'bb-gpu-capabilities.exe')],
                                    env=env, cwd=str(PORT), capture_output=True,
                                    creationflags=0x08000000, timeout=8)
            text = (result.stdout + result.stderr).decode('utf-8', errors='replace')
            if 'outside the device list' in text:
                break
            match = re.search(r'GPU scene scaling: (.+?)(?: supports live presets| lacks blit support)', text)
            if not match:
                break
            devices.append((index, match.group(1)))
    except (OSError, subprocess.TimeoutExpired):
        pass
    results.put(devices)


def main():
    import tkinter as tk
    from tkinter import ttk, messagebox
    if not (PORT / 'Bloodborne.exe').is_file() or not (HERE / 'profile.ini').is_file():
        raise RuntimeError('Extrae este paquete dentro de la carpeta que contiene Bloodborne.exe.')
    if C.sizeof(INPUT) != 40:
        raise RuntimeError('Este complemento necesita el port de 64 bits.')
    mutex_name = 'Local\\BloodborneDS3_' + hashlib.sha256(str(PORT).casefold().encode()).hexdigest()[:20]
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    mutex_error = C.get_last_error()
    if not mutex:
        raise C.WinError(mutex_error)
    if mutex_error == 183:
        kernel32.CloseHandle(mutex)
        user32.MessageBoxW(None, 'El complemento ya está abierto. Busca su ventana en la barra de tareas.',
                           'Bloodborne · controles DS3', 0x40)
        return
    root = tk.Tk()
    root.title('Bloodborne · controles estilo Dark Souls 3')
    root.geometry('710x690')
    root.minsize(680, 660)
    frame = ttk.Frame(root, padding=22)
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='Bloodborne · controles DS3', font=('Segoe UI', 19, 'bold')).pack(anchor='w')
    ttk.Label(frame, text='Teclado y ratón · combinaciones con Shift · perfil independiente').pack(anchor='w', pady=(4, 15))
    status = tk.StringVar(value='Listo. Mantén esta ventana abierta; puedes minimizarla.')
    ttk.Label(frame, textvariable=status, wraplength=625).pack(anchor='w', pady=(0, 12))
    gpu_var = tk.StringVar(value='Mantener selección actual')
    gpu_box = ttk.Combobox(frame, textvariable=gpu_var, state='readonly',
                           values=['Mantener selección actual'])
    gpu_box.pack(fill='x', pady=(0, 10))
    gpu_map = {}
    bridge = Bridge(root)
    launch_state = {'process': None}

    def launch(play=False):
        env = os.environ.copy()
        env['BB_INPUT_CONFIG'] = str(HERE / 'profile.ini')
        if gpu_var.get() in gpu_map:
            env['BB_GPU_ID'] = str(gpu_map[gpu_var.get()])
        try:
            launch_state['process'] = subprocess.Popen(
                [str(PORT / 'Bloodborne.exe'), *(['--play'] if play else [])],
                cwd=str(PORT), env=env, creationflags=0x08000000)
            status.set('Controles listos. Inicia el juego desde el launcher que acaba de abrirse.'
                       if not play else 'Iniciando con tu configuración guardada. Mantén abierto el complemento.')
            open_button.configure(state='disabled')
            play_button.configure(state='disabled')
        except OSError as exc:
            messagebox.showerror('No se pudo iniciar', str(exc), parent=root)

    buttons = ttk.Frame(frame)
    buttons.pack(fill='x', pady=(0, 15))
    open_button = ttk.Button(buttons, text='Abrir launcher con este perfil', command=launch)
    open_button.pack(side='left', padx=(0, 8))
    play_button = ttk.Button(buttons, text='Jugar directamente', command=lambda: launch(True))
    play_button.pack(side='left')
    enabled = tk.BooleanVar(value=True)

    def toggle():
        bridge.enabled = enabled.get()
        bridge.controls.cancel()

    ttk.Checkbutton(frame, text='Activar combinaciones del ratón', variable=enabled, command=toggle).pack(anchor='w')
    table = ttk.Treeview(frame, columns=('key', 'action'), show='headings', height=13)
    table.heading('key', text='Control')
    table.heading('action', text='Acción en Bloodborne')
    table.column('key', width=240, stretch=False)
    table.column('action', width=355)
    rows = [('W / A / S / D', 'Moverse'), ('Ratón', 'Mover la cámara'),
            ('Clic izquierdo', 'Ataque ligero'), ('Shift + clic izquierdo', 'Ataque fuerte; mantener para cargar'),
            ('Clic derecho / Ctrl izquierdo', 'Arma de fuego / parry'), ('F', 'Transformar arma (L1)'),
            ('Espacio', 'Esquivar; mantener para correr'), ('Alt izquierdo', 'Caminar despacio mientras se mantiene'),
            ('E / Enter', 'Interactuar / confirmar'), ('Q / clic central', 'Fijar objetivo / centrar cámara'),
            ('R / C', 'Objeto rápido / vial de sangre'), ('Rueda abajo', 'Cambiar objeto rápido'),
            ('Shift + rueda arriba / abajo', 'Cambiar arma derecha / izquierda')]
    for row in rows:
        table.insert('', 'end', values=row)
    table.pack(fill='both', expand=True, pady=(12, 10))
    ttk.Label(frame, wraplength=625, text='Esc: menú · G: gestos · Tab: efectos personales · '
              'Rueda arriba: balas de sangre (consume vida). F7 libera/captura el ratón. '
              'En menús del juego: E confirma y Espacio/Retroceso vuelve.').pack(anchor='w')
    ttk.Label(frame, wraplength=625, text='Cierra antes cualquier launcher anterior. Abre el juego con los botones de esta '
              'ventana. No cambies los bindings en la pestaña Controls del launcher mientras uses este perfil.').pack(anchor='w', pady=(10, 0))
    results = queue.Queue()
    threading.Thread(target=scan_gpus, args=(results,), daemon=True).start()

    def update_ui():
        if bridge.error:
            status.set('Complemento pausado: ' + bridge.error)
            enabled.set(False)
        process = launch_state['process']
        if process and process.poll() is not None:
            launch_state['process'] = None
            open_button.configure(state='normal')
            play_button.configure(state='normal')
        try:
            devices = results.get_nowait()
        except queue.Empty:
            pass
        else:
            values = ['Mantener selección actual']
            selected = None
            inherited = os.environ.get('BB_GPU_ID')
            for index, name in devices:
                label = str(index) + ' · ' + name
                values.append(label)
                gpu_map[label] = index
                if '4090' in name and inherited is None:
                    selected = label
                elif str(index) == inherited:
                    selected = label
            gpu_box.configure(values=values)
            if selected and launch_state['process'] is None:
                gpu_var.set(selected)
        root.after(250, update_ui)

    def close():
        if launch_state['process'] is not None or bridge.is_game:
            if not messagebox.askokcancel('Cerrar complemento',
                    'El juego seguirá abierto, pero dejarán de funcionar los ataques del ratón y las combinaciones. '
                    'Puedes minimizar esta ventana para seguir jugando. ¿Cerrar?', parent=root):
                return
        try:
            bridge.close()
        finally:
            kernel32.CloseHandle(mutex)
            root.destroy()

    root.protocol('WM_DELETE_WINDOW', close)
    update_ui()
    root.mainloop()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        detail = traceback.format_exc()
        try:
            (HERE / 'error.log').write_text(detail, encoding='utf-8')
        except OSError:
            pass
        user32.MessageBoxW(None, 'No se pudo abrir el complemento.\n\n' + detail[-1600:],
                           'Bloodborne · controles DS3', 0x10)
        raise SystemExit(1)
