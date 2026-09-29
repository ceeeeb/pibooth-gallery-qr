# -*- coding: utf-8 -*-

"""Pibooth plugin: display a QR code on the wait screen pointing to the
local gallery service. Writes a session marker file at startup so the
gallery service knows which directory to serve and from which timestamp."""

import os
import socket

import pygame
import qrcode

import pibooth
from pibooth.utils import LOGGER

__version__ = "1.0.1"

SECTION = "GALLERY_QR"


def _detect_ip():
    """Return the IP of the default-route interface (no internet required)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def _write_session(session_file, photos_dir):
    """Touch the session file with the current photos directory as content."""
    os.makedirs(os.path.dirname(session_file) or ".", exist_ok=True)
    with open(session_file, "w") as f:
        f.write(photos_dir)


def _build_qr_surface(url, box_size):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode)


class _GalleryQRState:
    """Holds runtime state shared between hooks."""
    url = ""
    qr_image = None
    qr_position = "bottom-left"
    qr_margin = 10
    show_qr = True


@pibooth.hookimpl
def pibooth_configure(cfg):
    cfg.add_option(SECTION, 'activate', True,
                   "Enable the local gallery plugin (writes session marker)",
                   "Enable", ['True', 'False'])
    cfg.add_option(SECTION, 'show_qr', True,
                   "Display the QR code on the wait screen",
                   "Show QR", ['True', 'False'])
    cfg.add_option(SECTION, 'host', '',
                   "Host or IP for the gallery URL (empty = autodetect)",
                   "Host", '')
    cfg.add_option(SECTION, 'port', 8081,
                   "Gallery service port",
                   "Port", '8081')
    cfg.add_option(SECTION, 'session_file', '/tmp/pibooth-session-start',
                   "Marker file: mtime is session-start, content is the photos dir",
                   "Session file", '/tmp/pibooth-session-start')
    cfg.add_option(SECTION, 'qr_position', 'bottom-left',
                   "QR code position (top-left, top-right, bottom-left, bottom-right, center)",
                   "QR Position", ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'])
    cfg.add_option(SECTION, 'qr_size', 5,
                   "QR code box_size (3-10)",
                   "QR Size", '5')
    cfg.add_option(SECTION, 'qr_margin', 10,
                   "QR code margin from screen edge in pixels",
                   "QR Margin", '10')


@pibooth.hookimpl
def pibooth_startup(app, cfg):
    app.gallery_qr = None
    if not cfg.getboolean(SECTION, 'activate'):
        LOGGER.info("Gallery QR disabled")
        return

    photos_dir = cfg.get('GENERAL', 'directory').strip()
    if not photos_dir:
        LOGGER.error("Gallery QR: [GENERAL] directory is empty")
        return

    session_file = cfg.get(SECTION, 'session_file').strip()
    try:
        _write_session(session_file, photos_dir)
    except OSError as e:
        LOGGER.error("Gallery QR: cannot write session file %s: %s", session_file, e)
        return

    host = cfg.get(SECTION, 'host').strip() or _detect_ip()
    port = cfg.getint(SECTION, 'port')
    url = f"http://{host}:{port}/"

    state = _GalleryQRState()
    state.url = url
    state.show_qr = cfg.getboolean(SECTION, 'show_qr')
    if state.show_qr:
        box_size = max(3, min(10, cfg.getint(SECTION, 'qr_size')))
        state.qr_image = _build_qr_surface(url, box_size)
        state.qr_position = cfg.get(SECTION, 'qr_position')
        state.qr_margin = cfg.getint(SECTION, 'qr_margin')
    app.gallery_qr = state

    LOGGER.info("Gallery QR ready: %s (session=%s, show_qr=%s)",
                url, photos_dir, state.show_qr)


@pibooth.hookimpl
def state_wait_enter(cfg, app, win):
    state = getattr(app, 'gallery_qr', None)
    if state is None or not state.show_qr or state.qr_image is None:
        return

    win_rect = win.get_rect()
    qr_rect = state.qr_image.get_rect()
    margin = state.qr_margin
    positions = {
        "top-left": (margin, margin),
        "top-right": (win_rect.width - qr_rect.width - margin, margin),
        "bottom-left": (margin, win_rect.height - qr_rect.height - margin),
        "bottom-right": (win_rect.width - qr_rect.width - margin,
                         win_rect.height - qr_rect.height - margin),
        "center": ((win_rect.width - qr_rect.width) // 2,
                   (win_rect.height - qr_rect.height) // 2),
    }
    x, y = positions.get(state.qr_position, (margin, margin))
    win.surface.blit(state.qr_image, (x, y))
