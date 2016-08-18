picotui
=======

Picotui is Text User Interface (TUI) widget library for Python.
You can learn more about it with the help of virtual Q&A session:

Q:
There're few TUI libraries for Python, why yet another one?
A:
Urwid is one well-known such TUI library. Here's entry from its FAQ:
"How do I create drop-downs, floating windows, and scroll bars?
You need to start writing some fairly complex widgets. This
functionality hasn't been added to Urwid yet." So, Urwid is a
widget library which doesn't have drop downs. Version 0.8.0 of
Urwid was imported into SVN (and later Git) in 2004. Urwid doesn't
have drop downs and stuff for 10+ years.

Q:
Hey, but you cut off the answer from Urwid FAQ. It says: "but if you
are willing to write it, we do accept patches". Why didn't you implement
those widgets for Urwid and contributed them?
A:
Why didn't you? No, wait, that's not productive. I didn't implement
them for Urwid because I don't like its architecture and the fact that
its widget set is rather weak (so its hard to write new widgets - there
are not enough examples to start from). And don't get me wrong, but the
fact that nobody wrote those widgets for Urwid during 10+ years, got to
mean something. However, I tried to hack on another, less, but still
known Python TUI library - Npyscreen. Its widget set is much more
advanced and usable. But - it still has some architectural choices
which makes extending it and overriding some behaviors problematic.
I also found its project management a bit unresponsive. So, after making
dozen of commits to my fork, I thought it's time to get some breath and
started picotui.

Q:
So, sun must shine bright in picotui land, and it must be the best library
out there?
A:
Alas, no. Let me start with the fact that most TUI libraries are based
on curses library for terminal screen management. It makes sure that if
you update screen, only the minimal set of updates is made. This was
very important at the era of 300 baud serial connections, let's count:
300 baud is about 30 bytes/s, and standard VT100 screen is 80*24 = ~2K.
Double that for attributes. So, transferring a complete screen to show
to user would take 2 mins. If you draw same screen twice (no changes in
content), it would take 4 mins. curses library cuts that back to mere 2
mins. So, alas, picotui doens't use curses. That's based on the fact
that picotui wants to be compatible with MicroPython, and its philosophy
is minimalism - if it's possible to do screen output without curses,
let's do just that. It's also grounded in the fact that nobody uses
300 baud modems any longer, most apps are run in local terminal emulator
with instant updates, most of the remaining are run over LANs which
also offer fast updates. Modern basic serial speed is 115200 which is
still too slow for real-time fullscreen updates though. That's why I
say alas. Beyond optimized screen updates, picotui lacks many other
things too: e.g., double-buffering (so redrawing previous screen
content behind pop-ups is up ot you), it lacks geometry managers, so
calculating coordinates is up to you, etc. Yes, just like that -
I lacked widgets the most, and that's what I implemented. The rest
is just KISS.

Q:
But that's really sad!
A:
Indeed, it is. The only good news is that now you have a choice: if
you want your app work well with 300 baud modems, you can use other
libraries, and if you want widgets, you can use picotui.


Known Issues
------------

Pay attention to what Unicode font you use in your console. Some Linux
distributions, e.g. Ubuntu, are known to have a broken Unicode font
installed by default, which causes various visual artifacts (specifically,
Ubuntu Mono font isn't really monospace - many Unicode pseudographic
characters have double (or so) width, box-drawing symbols have gaps, etc.)
