pibooth-gallery-qr
==================

Pibooth plugin that displays a QR code on the wait screen pointing to a
local LAN photo gallery served by a companion HTTP service. The gallery
shows photos taken during the **current pibooth session** (since the
last pibooth startup) and serves them in a mobile-friendly grid with a
full-screen lightbox.

Use case
--------

Allow guests at an event to scan the QR with their phone (on the same
Wi-Fi as the photobooth) and browse the photos from the current session
without needing internet, Nextcloud, or any third-party service.

How it works
------------

Two pieces:

1. **The plugin** ``pibooth_gallery_qr``: on ``pibooth_startup`` it writes
   a session marker file. On ``state_wait_enter`` it blits a QR code
   onto the wait screen pointing to ``http://<host>:<port>/``.

2. **The gallery service** (``gallery.py`` shipped in the source repo):
   a tiny stdlib HTTP server that reads the session marker, serves the
   ``*_pibooth.jpg`` files of the configured directory whose mtime is
   greater than or equal to the marker's mtime, and renders them with a
   click-to-fullscreen lightbox.

Install the plugin via pip and run the service via systemd. See the
source repo for an example unit file.

Configuration
-------------

The plugin adds a ``[GALLERY_QR]`` section::

    [GALLERY_QR]
      activate = True            # enable the plugin (writes session marker)
      show_qr = True             # display the QR on the wait screen
      host =                     # empty = autodetect (default route IP)
      port = 8081
      session_file = /tmp/pibooth-session-start
      qr_position = bottom-left  # top-left, top-right, bottom-left, bottom-right, center
      qr_size = 5                # 3-10
      qr_margin = 10             # px from screen edge

License
-------

MIT
