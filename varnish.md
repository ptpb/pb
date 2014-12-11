If specified, the `VARNISH_BASE` configuration option is used is used
to invalidate varnish's cache when necessary. This should be the URL
of the varnish instance; see
[config.yaml.example](config.yaml.example).

This depends on a varnish configuration that processes `BAN` requests
over HTTP:

```vcl
acl purge {
        "localhost";
}

sub vcl_recv {
        if (req.method == "BAN") {
                if (!client.ip ~ purge) {
                        return(synth(405, "Not allowed."));
                }

                ban("req.http.host == " + req.http.host +
                " && req.url ~ " + req.url);

                return(synth(200, "Ban added."));
        }
}
```

Enjoy.
