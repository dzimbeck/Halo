# Halo
BitHalo/BlackHalo/BitBay/Bitmessage public commit

This is a custom version of Bitmessage that integrates with BitHalo. Some of the modifications include reducing the limitation
on resending messages for users who are not connected while a message falls out of circulation. This gives a better chance to hear messages.
Also this system supports IMAP. It has a fully fledged system for handling and reading emails P2P with full public and private key encryption.
This way it preserves the users privacy even when used on top of common email providers. This is only a part of Halo's code the rest
can be found at the source link.

To build this, there is an SH and BAT file for installing dependencies. Notice some of those are Halo dependencies.
Halos obfuscated source code can be found at:
https://bithalo.org/bithalo.github.io/bithalo/downloads/BitHaloSource.html

That link contains the full Halo source with variable names changed. It also has building instructions and binaries.

This branch for now contains BitMHalo. This can be build static with the script or run directly from Python. Halo itself uses
Python 2.711. It's untested with Python 3. Halo also uses PyQT4. To build BitMHalo simply install Python and run the scripts.
