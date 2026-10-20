# Samba

The sanitized AD DC settings and operational notes are in
[`docs/samba-ad.md`](../docs/samba-ad.md). The example configuration is
[`smb.conf.example`](smb.conf.example).

The real realm, NetBIOS name, DNS forwarder, paths and account names are
private. Never commit the real Samba database, setup log, password or keytab.
