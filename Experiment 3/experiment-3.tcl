#Create a simulator object
set ns [new Simulator]

set qtype [lindex $argv 0]

#Open the trace file (before you start the experiment!)
set tfname ""
append tfname "tracefiles/experiment-3-" $qtype "_output.tr"
puts "trace file = $tfname"
set tf [open $tfname w]
$ns trace-all $tf

set tcpname ""
append tcpname "tracefiles/experiment-3-" $qtype "_output.tcp"
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
$ns duplex-link $n1 $n2 10Mb 10ms $qtype
$ns duplex-link $n2 $n3 10Mb 10ms $qtype
$ns duplex-link $n3 $n4 10Mb 10ms $qtype
$ns duplex-link $n2 $n5 10Mb 10ms $qtype
$ns duplex-link $n3 $n6 10Mb 10ms $qtype

#Set Queue Size of link (n2-n3) to 10
$ns queue-limit $n2 $n3 10


#Setup a TCP connection
set tcp [new Agent/TCP/Reno]
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink/Sack1]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set fid_ 1
$tcp attach-trace $tcpfile
$tcp trace cwnd_

#Setup a FTP over TCP connection
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP


#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n5 $udp
set null [new Agent/Null]
$ns attach-agent $n6 $null
$ns connect $udp $null
$udp set fid_ 2

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ 5Mb
$cbr set random_ true


#Schedule events for the CBR and FTP agents
$ns at 0.1 "$cbr start"
$ns at 1.0 "$ftp start"
$ns at 9.0 "$ftp stop"
$ns at 9.5 "$cbr stop"

#Detach tcp and sink agents (not really necessary)
$ns at 9.5 "$ns detach-agent $n1 $tcp ; $ns detach-agent $n4 $sink"

#Call the finish procedure after 5 seconds of simulation time
$ns at 10.0 "finish"

#Run the simulation
$ns run

#Close the trace file (after you finish the experiment!)
close $tf
