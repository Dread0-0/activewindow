#!/usr/bin/env bash

sqlite3 $HOME/.local/window.db <<EOF
CREATE TABLE windows (id INTEGER PRIMARY KEY AUTOINCREMENT, winname TEXT, epoch REAL);
EOF

pip3 install -r requirements.txt
