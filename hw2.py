import logging
import socket
import sys
import ssl

TEST_CASES = [
    # 'http://www.example.com',  # most basic example (with no slash)
    # 'http://bombus.myspecies.info/node/24',  # another basic example
    # 'http://i.imgur.com/fyxDric.jpg',  # is an image
    # 'http://go.com/doesnotexist',  # causes 404
    # 'http://www.ifyouregisterthisforclassyouareoutofcontrol.com/', # NXDOMAIN
    # 'http://www.asnt.org:8080/Test.html', # nonstandard port
    # 'http://www.httpwatch.com/httpgallery/chunked/chunkedimage.aspx' # chunked encoding
    # 'https://www.cs.uic.edu/~ckanich/', # https
    # 'https://😻🍕.ws',  # utf-8 in the url
    # 'http://www.fieggen.com/shoelace',  # redirects to trailing slash

    #'http://www.washington.edu/'
    #'https://manpages.debian.org/about.html'
]


def retrieve_url(url):
    """
    return bytes of the body of the document at url
    """

    is_https = False
    if 'https' in url:
        is_https = True

    #print('Is https:',is_https)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print('Error: Creating socket')

    domain = ''
    content = ''
    port = 0

    # divide url
    url1 = url.replace('https://', '')
    url1 = url1.replace('http://', '')
    #url1 = url1.replace('www.', '')

    try:
        idx = url1.index('/')
        domain = url1[:idx]
        content = url1[idx:]
    except ValueError:
        domain = url1
        content = "/"

    # find port
    try:
        idx = domain.index(':')
        try:
            port = int(domain[idx + 1:])
            domain = domain[:idx]
        except ValueError:
            print('error:', ValueError)
    except ValueError:
        if is_https:
            port = 443
        else:
            port = 80

    # print(domain, content, port) # DEBUG PURPOSES

    if is_https:
        c = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ss = c.wrap_socket(s, server_hostname=domain)

    try:

        if is_https:
            ss.connect((domain, port))
        else:
            s.connect((domain, port))

        # get header, encode and send to server
        headermsg = 'HEAD {} HTTP/1.1\r\nHost: {}\r\n\r\n'.format(content, domain)
        string_bytes = headermsg.encode()

        if is_https:
            ss.send(string_bytes)
        else:
            s.sendall(string_bytes)

        # get 1st line of header
        if is_https:
            full_status = str(ss.recv(2048), 'utf-8')
            status = full_status[:15]
        else:
            full_status = str(s.recv(2048), 'utf-8')
            status = full_status[:15]
        #print('status:',status) # DEBUG PURPOSES
        #print(full_status) ########### DEBUG ###########

        if (status == "HTTP/1.1 200 OK"):
            bodymsg = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: Close\r\n\r\n'.format(content, domain)
            string_bytes = bytes(bodymsg, 'ascii')

            if is_https:
                ss.sendall(string_bytes)
            else:
                s.sendall(string_bytes)

            body_content = b''
            chunk_size = 0

            # store data
            while True:
                if is_https:
                    segment = ss.recv(1024)
                else:
                    segment = s.recv(1024)

                body_content += segment
                if(len(segment) < 1):
                    break

            try:
                # not polished body content
                #print(body_content)  ############ DEBUG ###############

                if b'Transfer-Encoding: chunked' in body_content:
                    # find first instance of \r\n after connection: \r\n\r\n
                    body_content = body_content[body_content.find(b'\r\n\r\n')+4:]
                    # get chunk size in bytes
                    chunk_size = body_content[:body_content.find(b'\r\n')]
                    chunk_size_dec = int(chunk_size, 16)
                    body_content = body_content[body_content.find(b'\r\n')+2:]
                    # clean end-new-lines aka footers
                    body_content = body_content[:body_content.find(b'\r\n0\r\n\r\n')]

                    body_len = len(body_content) # get len of the body so far
                    #how_many_chunks = int(body_len / chunk_size_dec)
                    st = '\r\n{}\r\n'.format(chunk_size.decode())
                    to_replace = st.encode()
                    how_many_chunks = body_content.count(to_replace) # count the full-size chunks
                    byte_count_size = (len(chunk_size)+4) * how_many_chunks  # \r\n + size + \r\n, where size is usually 4 bytes
                    body_len -= byte_count_size                      # remove the bytes of the chunk sizes within the body
                                                                     # '\r\n len \r\n' remove chunk separator
                    # DEBUG PURPOSES
                    #print('how many full chunks', how_many_chunks)
                    #print('Chunk size:', chunk_size, chunk_size_dec)
                    #print('body len', body_len)
                    try:
                        #body_content = body_content.replace(b'\r\n400\r\n', b'')
                        #body_content = body_content.replace(b'\r\n375\r\n', b'')
                        st = '\r\n{}\r\n'.format(chunk_size.decode())
                        to_replace = st.encode()
                        #print('to replace:', to_replace)   ##### DEBUG #####
                        body_content = body_content.replace(to_replace, b'')

                        # find last chunk, it's going to be len(body)%chunk_size
                        t = hex(body_len % chunk_size_dec)[2:]
                        remainder = hex(int(t, 16)-len(t)-4)[2:]
                        #print('Chunk remainder:', remainder) # DEBUG PURPOSES
                        st = "\r\n{}\r\n".format(remainder)
                        replace_remainder = st.encode()
                        #replace_reminder = ("\r\n{}\r\n".format(hex(body_len % chunk_size_dec))[2:]).encode()
                        body_content = body_content.replace(replace_remainder, b'')
                        #print('to replace, remainder', replace_remainder) # DEBUG PURPOSES
                    except IOError:
                        print('ERROR replacing chunk garbage', IOError)

                else:
                    if b'\r\n\r\n' in body_content:
                        #idx = body_content.find(b'Accept-Ranges: bytes\r\n\r\n')
                        #body_content = body_content[idx + 24:]
                        #body_content = body_content[body_content.find(b'\n')+1:]
                        body_content = body_content[body_content.find(b'\r\n\r\n') + 4:]
                        if b'\r\n' in body_content[:body_content.find(b'<!')] and b'<html>' not in body_content[:body_content.find(b'<!')]:
                            body_content = body_content[body_content.find(b'\r\n') + 2:]
                    elif b'<!D' in body_content:
                        idx = body_content.find(b'<!D')
                        body_content = body_content[idx:]
                    elif b'<!d' in body_content:
                        idx = body_content.find(b'<!d')
                        body_content = body_content[idx:]
                    else:
                        idx = body_content.find(b'<html>')
                        body_content = body_content[idx:]



                    if not is_https:
                        idx = body_content.find(b'</html>')
                        filler = body_content[idx + 7:]  # extra \r\n etc.. we need everything up to 1st \n
                        body_content = body_content[:idx + 7]
                        body_content += filler[:(filler.find(b'\n'))+1]

            except:
                print('Error in cleaning body')
                body_content = None

            #print(body_content) ############ DEBUG ###########
            #print('FILLER', filler)
            if is_https:
                ss.close()
            else:
                s.close()
            return body_content

        elif (status == "HTTP/1.1 301 Mo"):
            if "Location: " in full_status:
                idx = full_status.encode().find(b'http')
                new_url = full_status.encode()[idx:]
                idx = new_url.find(b'\r\n')
                new_url = new_url[:idx]
                # print('Redirecting to:', new_url.decode()) # redirect DEBUG
                if is_https:
                    ss.close()
                else:
                    s.close()
                return retrieve_url(new_url.decode())

        else:
            if is_https:
                ss.close()
            else:
                s.close()
            return None

    except:
        return None

    #return b"this is unlikely to be correct"


if __name__ == "__main__":
    sys.stdout.buffer.write(retrieve_url(sys.argv[1]))  # pylint: disable=no-member

#for i in TEST_CASES:
#    retrieve_url(i)
