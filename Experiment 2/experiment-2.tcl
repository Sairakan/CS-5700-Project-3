#Create a simulator object
set ns [new Simulator]

set tcpclass1 [lindex $argv 0]
set tcpclass2 [lindex $argv 1]
set bitrate [lindex $argv 2]

#Open the trace file (before you start the experiment!)
set tfname ""
append tfname "tracefiles/" $tcpclass1 "-" $tcpclass2 "/experiment-2-" $tcpclass1 "-" $tcpclass2 "_output_" $bitrate ".tr"
puts "trace file = $tfname"
set tf [open $tfname w]
$ns trace-all $tf

set tcpname ""
append tcpname "tracefiles/" $tcpclass1 "-" $tcpclass2 "/experiment-2-" $tcpclass1 "-" $tcpclass2 "_output_" $bitrate ".tcp"
puts "tcp file = $tcpname"
set tcpfile [open $tcpname w]
Agent/TCP set trace_all_oneline_ true

#Define a 'finish' procedure
proc finish {} {
        global ns
        $ns flush-trace
        exit 0
}

#Create six nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#Create links between the nodes
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n3 $n4 10Mb 10ms DropTail
$ns duplex-link $n2 $n5 10Mb 10ms DropTail
$ns duplex-link $n3 $n6 10Mb 10ms DropTail

#Set Queue Size of link (n2-n3) to 10
$ns queue-limit $n2 $n3 10


#Setup a TCP connection
set tcp1 [
	if {$tcpclass1 eq "tahoe"} {
		new Agent/TCP
	} elseif {$tcpclass1 eq "reno"} {
		new Agent/TCP/Reno
	} elseif {$tcpclass1 eq "newreno"} {
		new Agent/TCP/Newreno
	} else {
		new Agent/TCP/Vegas
	}]
$ns attach-agent $n1 $tcp1
set sink1 [new Agent/TCPSink]
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1
$tcp1 set fid_ 1
$tcp1 attach-trace $tcpfile
$tcp1 trace cwnd_

#Setup a FTP over TCP connection
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
$ftp1 set type_ FTP

#Setup a TCP connection
set tcp2 [
	if {$tcpclass2 eq "tahoe"} {
		new Agent/TCP
	} elseif {$tcpclass2 eq "reno"} {
		new Agent/TCP/Reno
	} elseif {$tcpclass2 eq "newreno"} {
		new Agent/TCP/Newreno
	} else {
		new Agent/TCP/Vegas
	}]
$ns attach-agent $n5 $tcp2
set sink2 [new Agent/TCPSink]
$ns attach-agent $n6 $sink2
$ns connect $tcp2 $sink2
$tcp2 set fid_ 2
$tcp2 attach-trace $tcpfile
$tcp2 trace cwnd_

#Setup a FTP over TCP connection
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2
$ftp2 set type_ FTP


#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n2 $udp
set null [new Agent/Null]
$ns attach-agent $n3 $null
$ns connect $udp $null
$udp set fid_ 3

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ [append bitrate "Mb"]
$cbr set random_ false


#Schedule events for the CBR and FTP agents
$ns at 0.1 "$cbr start"
$ns at 1.0 "$ftp1 start"
$ns at 9.0 "$ftp1 stop"
$ns at 1.0 "$ftp2 start"
$ns at 9.0 "$ftp2 stop"
$ns at 9.5 "$cbr stop"

#Detach tcp and sink agents (not really necessary)
$ns at 9.5 "$ns detach-agent $n1 $tcp1 ; $ns detach-agent $n4 $sink1 ; $ns detach-agent $n5 $tcp2 ; $ns detach-agent $n6 $sink2"

#Call the finish procedure after 5 seconds of simulation time
$ns at 10.0 "finish"

#Run the simulation
$ns run

#Close the trace file (after you finish the experiment!)
close $tf
