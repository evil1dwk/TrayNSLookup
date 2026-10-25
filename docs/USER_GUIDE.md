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

## About

The About button at the bottom-left of the window opens the application icon,
version, creator credit, GitHub repository, and Report an issue links.

## Reverse lookups and structured results

Enter an IPv4 or IPv6 address directly. The app automatically selects PTR and
constructs its reverse DNS name. Domain input continues to use the selected
record type; manually entered reverse DNS names are also supported with PTR.

Results show Name, Type, Value, and TTL (seconds). Each server panel identifies
the requested resolver, the responding resolver, and total elapsed lookup time
in milliseconds. CNAME records in the answer are included. Errors appear in the
affected server panel. Column widths can be adjusted; long values have tooltips.

## Compare DNS servers

Enable Compare servers and use Select servers to choose at least two entries.
The list includes System default and your configured DNS servers. Run Lookup
queries the selected servers concurrently and shows their results side by side;
scroll horizontally when several panels exceed the window width.

The comparison summary checks record names, types, and values, ignoring TTL
and record order. A failed server makes the comparison incomplete. Different
answers may reflect DNS propagation, caching, split DNS, or load balancing;
the comparison does not determine which answer is correct. System default may
use one of the same resolvers you selected explicitly.

New history entries restore these structured panels, including comparisons.
Older saved results continue to open as text. Clear Results preserves history.
