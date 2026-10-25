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

The About button at the bottom-left of either tab opens the application icon,
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

Use the DNS Server selection menu to choose one or more entries.
One selection runs a single-server lookup; multiple selections compare answers.
Selections are saved immediately and restored on restart.
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

## Additional record types

The Record Type menu includes SOA, SRV, CAA, and HTTPS alongside the existing
record types. Enter the full service name for SRV (for example,
`_ldap._tcp.example.com`). HTTPS is a DNS record type; choosing it does not change
the DNS query transport to HTTPS. Values are shown in standard DNS text form.

## Copy and export

Use Copy Selected to copy selected table rows (including the responding server),
or selected text from an older history entry. Ctrl/Cmd-click or Shift-click can
select multiple rows. Copy All copies the complete displayed query, including all
servers and errors. Export saves the complete displayed result as text, CSV, or
JSON; it does not export the entire history. CSV has one row per record and keeps
failed-server errors as rows. JSON preserves the complete structured query.
Older text-only results are preserved as a single result field in CSV/JSON.

## Search and rerun history

In History, type a domain or IP fragment, filter by requested/responding DNS
server, choose a query type, or enable Date range. Dates include both endpoints.
Filters combine, and the count shows how many saved lookups match. Reset Filters
shows everything again. Entries without date/type/server metadata are excluded
when the corresponding filter is enabled; older timestamps are read from text
where available.

View Result opens the selected saved result. Run Again restores a structured
query's original record type and resolvers, including resolvers removed since the
query was saved, and updates the server selector. A legacy text-only entry uses
the current type and selected servers because its original metadata is unavailable.
Clear History still deletes all saved entries after confirmation, including entries
hidden by filters. Clearing the displayed results does not delete history.
