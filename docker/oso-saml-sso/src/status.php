<?PHP

//FIXME: This entire script should be discarded in favor of a single
//       python script that does two separate checks
//         - makes an HTTPS connection to HTTPD
//         - makes an SSH connection to SSHD
//       then rolls the status up into a single exit code

function die503($msg)
{
    header('HTTP/1.1 503 Service Temporarily Unavailable');
    header('Status: 503 Service Temporarily Unavailable');
    header('Retry-After: 2'); // 2  seconds
    echo "<h1>503 Service Temporarily Unavailable</h1>";
    die($msg);
}

// check to see if the ssh endpoint is up and running

$host = '127.0.0.1';
$port = '2222';
$timeout = '2';

$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP)
   or die503("Unable to reach SSH endpoint: Unable to create socket\n");

$time = time();
while (!@socket_connect($socket, $host, $port))
{
    $err = socket_last_error($socket);
    if ($err == 115 || $err == 114)
    {
        if ((time() - $time) >= $timeout)
        {
            socket_close($socket);
            die503("Unable to reach SSH endpoint: Connection timed out.\n");
        }
        sleep(0.1);
        continue;
    }
    @socket_close($socket);
    die503("Unable to reach SSH endpoint: ". socket_strerror($err) . "\n");
}

echo "OK";
