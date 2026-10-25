# User guide

Start TrayNSLookup and left-click its tray icon to open the window. Right-click
the icon for Open, Manage DNS Servers, and Quit. Closing the lookup window keeps
the app running; use Quit to exit.

## Lookups

Enter a domain, select a record type and DNS server, and choose Run Lookup (or
press Enter). The system-default option uses the operating system resolver.
For PTR records, enter the reverse DNS name, such as `8.8.8.8.in-addr.arpa`.
Results and error messages appear in the Results tab below the query controls.
Clear Results empties the displayed output without deleting saved history.
The query controls remain visible when switching between Results and History.

Use the gear button to add, edit, or remove custom DNS servers. Enter resolver
IP addresses, one per row, and save.

## History and settings

The History tab lists saved lookups with the newest first. Double-click an
entry or choose View Result to display it. Clear History asks for confirmation.

Settings, history, and window geometry are stored in
`~/.traynslookup_config.json`. This path and its format are unchanged by the
repository restructuring. Delete the file while the app is closed to reset it.
