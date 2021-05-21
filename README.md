A Barebones HTTP/1.1 Client

In this programming exercise, you will create a barebones web client. While
python includes a basic http client module `http.client`, this assignment will
serve as a learning experience for translating a protocol into an
implementation. Your deliverable will be a client which only implements the
`GET` method and follows the basics of the HTTP/1.1 specification, enough to
download files as one would with the command line program `curl`.

## HTTP/1.1 Features

[HTTP/1.0](https://tools.ietf.org/search/rfc1945) describes the most basic
functionality that an HTTP client is required to do. HTTP/1.1 includes several
new features that extend the protocol. For this assignment, you will only be
required to implement these additional features:

  * Include a `Host:` header
  * Correctly interpret `Transfer-encoding: chunked`
  * Include a `Connection: close` header, or handle persistent connections

These new features are described in James Marshall's excellent [HTTP Made Really Easy](https://www.jmarshall.com/easy/http/#http1.1clients) under the HTTP/1.1
clients subsection.

Note that the RFCs are your friends: if you're having trouble with
`Transfer-encoding`, check [the RFC][http] for hints!


## Basic HTTP functionality

As seen in class, HTTP is a stateless request-response protocol that consists
of an initial line, zero or more headers, and zero or more bytes of content.
Your program will implement a function, `retrieve_url`, which takes a url (as
a `str`) as its only argument, and uses the HTTP protocol to retrieve and
return the body's bytes (do not decode those bytes into a string). Consult
the book or your class notes for the basics of the HTTP protocol.

You may assume that the URL will not include a fragment, query string, or
authentication credentials. You are not required to follow any redirects -
only return bytes when receiving a `200 OK` response from the server. If for
any reason your program cannot retrieve the resource correctly, `retrieve_url`
should return `None`.


```python
TEST_CASES = [
    'http://www.example.com',  # most basic example (with no slash) 
    'http://bombus.myspecies.info/node/24',  # another basic example
    'http://i.imgur.com/fyxDric.jpg',  # is an image
    'http://go.com/doesnotexist',  # causes 404
    'http://www.ifyouregisterthisforclassyouareoutofcontrol.com/', # NXDOMAIN
    'http://www.asnt.org:8080/Test.html', # nonstandard port
    'http://www.httpwatch.com/httpgallery/chunked/chunkedimage.aspx' # chunked encoding 
]
```

## Allowable sources

You may not use any libraries which implement parts or the whole of the `HTTP`
specification - you must perform the basic request and response
parsing/generation yourself, as well as the chunked content encoding.

Do not import or use any python libraries, or third party code, beyond
what is imported in the skeleton / `hw2.py` file in your repo.

These resources may be useful:
  * [Python standard library documentation](https://docs.python.org/3/library/)
  * [HTTP Made Easy](https://www.jmarshall.com/easy/http/)
  * [HTTP/1.1 RFC](https://www.ietf.org/rfc/rfc2616.txt)

Using _any_ code from another source, even a single line, even with a citation,
is not allowed. This includes using any implementation code from the standard
library itself. I highly recommend not even Googling for solutions to portions
of this homework - as soon as you've seen an alternate implementation, it is
very hard to write one's own.
