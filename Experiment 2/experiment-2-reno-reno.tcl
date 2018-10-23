#Create a simulator object
set ns [new Simulator]

set bitrate [lindex $argv 0]

#Open the trace file (before you start the experiment!)
set filename "tracefiles/tahoe/experiment-2-reno-reno_output_"
append filename $bitrate ".tr"
puts "trace file = $filename"
set tf [open $filename w]
$ns trace-all $tf

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
set tcp1 [new Agent/TCP/Reno]
$ns attach-agent $n1 $tcp1
set sink1 [new Agent/TCPSink]
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1
$tcp1 set fid_ 1

#Setup a FTP over TCP connection
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
$ftp1 set type_ FTP

#Setup a TCP connection
set tcp2 [new Agent/TCP/Reno]
$ns attach-agent $n5 $tcp2
set sink2 [new Agent/TCPSink]
$ns attach-agent $n6 $sink2
$ns connect $tcp2 $sink2
$tcp2 set fid_ 2

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
$ns at 1.0 "$ftp start"
$ns at 9.0 "$ftp stop"
$ns at 9.5 "$cbr stop"

#Detach tcp and sink agents (not really necessary)
$ns at 9.5 "$ns detach-agent $n1 $tcp ; $ns detach-agent $n4 $sink"

#Call the finish procedure after 5 seconds of simulation time
$ns at 10.0 "finish"

#Print CBR packet size and interval
puts "CBR flow rate = [$cbr set rate_]"

#Run the simulation
$ns run

#Close the trace file (after you finish the experiment!)
close $tf
