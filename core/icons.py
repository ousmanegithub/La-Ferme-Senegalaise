"""
A small, hand-drawn set of 24x24 line icons used across the site (via the
`icon_svg` template tag). Kept as plain inline SVG paths, no icon-font or
external icon package, so the whole visual language stays self-contained
and themeable with `currentColor`.
"""

ICONS = {
    # --- Brand / values ---------------------------------------------------
    "leaf": '<path d="M4 20c7-1 10-3 12-9 1.5-4.5 4-6 4-6s-1.5 4-3 6c-3 4-7 6-13 6 0 0 0 3 0 3z"/>'
            '<path d="M4 20c0-6 3-10 7-13"/>',
    "sun": '<circle cx="12" cy="12" r="4.5"/>'
           '<path d="M12 2.5v3M12 18.5v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2.5 12h3M18.5 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/>',
    "water": '<path d="M12 3c3 4 6 7.7 6 11.2A6 6 0 0 1 6 14.2C6 10.7 9 7 12 3z"/>',
    "shield": '<path d="M12 3l7 3v5.5c0 4.6-3 8.3-7 9.5-4-1.2-7-4.9-7-9.5V6l7-3z"/>'
              '<path d="M9 12l2 2 4-4"/>',
    "handshake": '<path d="M2 12l4-3 3 2 3-2 3 2 4-3"/>'
                 '<path d="M6 9v6l3 2 2-1 2 1 3-2V9"/>',
    "bolt": '<path d="M13 2 4 14h6l-1 8 9-12h-6l1-8z"/>',
    "home": '<path d="M4 11.5 12 4l8 7.5"/><path d="M6 10v9.5h12V10"/><path d="M10 19.5v-5h4v5"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/>'
             '<path d="M3.5 12h17M12 3.5c2.5 2.5 3.8 5.4 3.8 8.5s-1.3 6-3.8 8.5c-2.5-2.5-3.8-5.4-3.8-8.5S9.5 6 12 3.5z"/>',
    "seedling": '<path d="M12 21V11"/><path d="M12 12C12 8 9 6 5 6c0 4.5 3 7 7 6z"/>'
                '<path d="M12 11c0-3.5 2.5-5.5 6-5.5.2 3.8-2.2 6-6 5.5z"/>',
    # --- Contact / UI -------------------------------------------------------
    "phone": '<path d="M6 3h3l1.5 4L8 8.5c.9 2.3 2.7 4.1 5 5l1.5-2.5 4 1.5V16c0 1.7-1.3 3-3 3C9.7 19 5 14.3 5 8.5 5 6.7 4.9 4.7 6 3z"/>',
    "mail": '<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="M3.5 6.5 12 13l8.5-6.5"/>',
    "map-pin": '<path d="M12 21.5S5 14.9 5 9.8a7 7 0 0 1 14 0c0 5.1-7 11.7-7 11.7z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5.5l4 2"/>',
    "arrow-right": '<path d="M4 12h15.5"/><path d="M13.5 6l6 6-6 6"/>',
    "chevron-down": '<path d="M5.5 8.5 12 15l6.5-6.5"/>',
    "menu": '<path d="M3.5 6.5h17M3.5 12h17M3.5 17.5h17"/>',
    "close": '<path d="M5 5l14 14M19 5 5 19"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M20 20l-4.7-4.7"/>',
    "download": '<path d="M12 3.5v11.5"/><path d="M7 10.5l5 5 5-5"/><path d="M4.5 18.5h15"/>',
    "play": '<path d="M8 5.5v13l11-6.5z"/>',
    "quote": '<path d="M8.5 8.5c-2.5 1-4 3-4 6 0 1.7 1.3 3 3 3s3-1.3 3-3-1.2-2.9-2-3c0-1.3.7-2.3 2-3z"/>'
             '<path d="M17.5 8.5c-2.5 1-4 3-4 6 0 1.7 1.3 3 3 3s3-1.3 3-3-1.2-2.9-2-3c0-1.3.7-2.3 2-3z"/>',
    "check": '<path d="M4.5 12.5l5 5 10-11"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="M7.5 12.5l3 3 6-6.5"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 9.5h17M8 3v4M16 3v4"/>',
    "tag": '<path d="M11.5 3.5H4.5v7L14 20.5l7-7L11.5 3.5z"/><circle cx="8.2" cy="7.5" r="1.3"/>',
    "building": '<rect x="4" y="3" width="10" height="18" rx="1"/><rect x="14" y="9" width="6" height="12" rx="1"/>'
                '<path d="M7 7h1M11 7h1M7 11h1M11 11h1M7 15h1M11 15h1"/>',
    "arrow-up-right": '<path d="M7 17 17 7"/><path d="M9 7h8v8"/>',
    "star": '<path d="M12 3.5l2.5 5.4 5.8.6-4.4 4 1.2 5.8-5.1-3-5.1 3 1.2-5.8-4.4-4 5.8-.6z"/>',
    # --- Social ---------------------------------------------------------
    "facebook": '<path d="M14 21v-7.5h2.5l.5-3.2H14V8.2c0-.9.3-1.6 1.7-1.6h1.5V3.8C16.9 3.7 15.8 3.5 14.6 3.5c-2.5 0-4.3 1.5-4.3 4.4v2.4H8v3.2h2.3V21z"/>',
    "instagram": '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/>'
                 '<circle cx="17.2" cy="6.8" r="0.9" fill="currentColor" stroke="none"/>',
    "linkedin": '<rect x="3.5" y="3.5" width="17" height="17" rx="2.5"/>'
                '<circle cx="8" cy="8.2" r="1" fill="currentColor" stroke="none"/>'
                '<path d="M8 11v6.5M12 11v6.5M12 13.8c0-1.8 1.2-2.8 2.6-2.8 1.6 0 2.4 1.1 2.4 3v3.5"/>',
    "youtube": '<rect x="2.5" y="6" width="19" height="12" rx="3"/><path d="M10.5 9.5l5 2.5-5 2.5z" fill="currentColor" stroke="none"/>',
    "tiktok": '<path d="M14 3.5c.4 2.3 1.9 3.8 4.2 4v2.7c-1.5 0-2.9-.5-4.2-1.4v6.4a5 5 0 1 1-5-5c.3 0 .6 0 1 .1v2.7a2.3 2.3 0 1 0 1.6 2.2V3.5z"/>',
    "whatsapp": '<path d="M7 17.5 4 20l2.6-2.9A8 8 0 1 1 12 20a8 8 0 0 1-5-1.7z"/>'
                '<path d="M9 9.3c0-.6.5-.8.9-.8h.6c.3 0 .5.2.6.5l.6 1.6c.1.2 0 .5-.1.6l-.6.7c.4 1 1.1 1.8 2.1 2.2l.7-.6c.2-.1.4-.2.6-.1l1.6.6c.3.1.5.3.5.6v.6c0 .4-.3.9-.9.9-2.9 0-6.6-3.2-6.6-6.8z"/>',
}
