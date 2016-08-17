#!/usr/bin/env python3

import sys, subprocess, time, tarfile
"""Python 3 script which will gather node information and create a partial html webpage
from that information for a 'heat' map of the queue. This partial page is a component to
be included from index.php on the current web-server. There are two other components,
header.html and footer.html for each: Debug and Long. Latest update:
Aug 17th, 2016 v0.8.1-beta-3
Exit codes: 0 - Good
            20 - Bad Pending Job status"""

class Node:
    """Class to hold representation of a node for the CRC at Notre Dame
    Note: Python doesn't have private data, but the direct variables of
    this class are treated as private, and as such there are methods created
    to obtain them."""
    
    def __init__(self, name, total_cores=0, used_cores=0, disabled=True):
        """Instantiation for Node class, must pass in the node name, everything else defaults to 0.
        Node defaults in the disabled state."""
        self.name = name
        self.total_cores = int(total_cores)
        self.used_cores = int(used_cores)
        self.free_cores = (int(self.total_cores) - int(self.used_cores))
        self.disabled = disabled
        self.num_jobs = 0
        self.load = 0
        self.job_list = []
        
    def __repr__(self):
        name = self.name
        return name
    
    def __str__(self):
        return self.name
        
    def add_job(self, job):
        """Method to add an instance of class Job to the job_list of a node."""
        self.job_list.append(job)
    
    def set_load(self, load):
        """Method to set the sys-load for a node"""
        self.load= load
        
    def get_load(self):
        """Method to obtain the sys-load info of a node. Returns a str"""
        return str(self.load)
    
    def get_num_jobs(self):
        """Method to obtain the number of jobs a node currently has running on it. Returns a str"""
        return str(self.num_jobs)
        
    def set_num_jobs(self, num):
        """Method to set the number of jobs running on a node """
        self.num_jobs = num
    
    def set_name(self, name):
        """Method to set the name of a node"""
        self.name = name
    
    def get_name(self):
        """Method to retrieve a node's name"""
        return self.name
    
    def get_free(self):
        """Method to retrieve the node's # of free cores"""
        return int(self.free_cores)
    
    def get_job_list(self):
        """Method to obtain the job-list of a node"""
        return self.job_list
    
    def get_used(self):
        """method to retrive a node's # of used cores"""
        return int(self.used_cores)
    
    def get_total(self):
        """Method to retrieve a node's # of total cores"""
        return int(self.total_cores)
    
    def set_cores(self, total_cores, used_cores):
        """Method to set all of the core information on a node. Just needs the total
        and the used cores, it will determine the number of free cores."""
        self.total_cores = int(total_cores)
        self.used_cores = int(used_cores)
        self.free_cores = int(total_cores) - int(used_cores)
        
    def set_disabled_switch(self, disabled):
        """Method to set whether or not the node is disabled. The parameter 'disabled'
        is a bool, so True or false or the equivilent ( 0 or 1 )"""
        self.disabled = disabled
        
    def get_disabled_switch(self):
        """Method to obtain the disable bool from a node"""
        return self.disabled
#^--------------------------------------------------------- class Node

class User:
    """Class to hold representation of a user in a specific queue for the CRC at Notre Dame."""
    
    def __init__(self, name, jobs=[],cores_used=[]):
        """Default instantiation for a user. Only need the name, everything else defaults
        to empty or 0."""
        
        self.name = str(name)
        self.jobs = jobs
        self.cores_used = cores_used
        self.node_list = []
        
    def __repr__(self):
        return 'User-{0}'.format(self.name)
    
    def __str__(self):
        return self.name
    
    def get_name(self):
        """Method to obtain name of user."""
        return self.name
    
    def get_job_list(self):
        """Method to obtain the job list of a user."""
        return self.jobs
    
    def get_core_info(self):
        """Method to obtain core info on a user."""
        return self.cores_used
    
    def get_node_list(self):
        """Method to obtain node_list of a user. The node_list is a list of the different nodes
        a user has jobs running on. May come in handy if a user page is created."""
        return self.node_list
#^--------------------------------------------------------- class User

class Job:
    """Class to hold representation of a job in a specific node for the CRC at Notre Dame."""
    
    def __init__(self, name, user, cores=0):
        """Default instantiation for a Job. Only need the name, and user everything else defaults
        to empty or 0."""
        self.name = str(name)
        self.cores = cores
        self.user = str(user)
        self.priority = 0
        self.id = 0
        return
        
    def __repr__(self):
        return 'Job-{0}'.format(self.name)
    
    def __str__(self):
        return self.name
    
    def get_name(self):
        """Method to obtain name of user."""
        return self.name
    
    def set_cores(self, cores):
        """Method to set the number of cores a job uses."""
        self.cores = cores
        return
    
    def get_core_info(self):
        """Method to obtain core info on a user."""
        return self.cores
    
    def get_priority(self):
        """Method to obtain the priority of a job. Returns a str"""
        return str(self.priority)
    
    def set_priority(self, pri):
        self.priority = pri
        return
    
    def get_user(self):
        """Method to obtain the user behind the job itself."""
        return self.user
    
    def get_id(self):
        """Method to get job id of a job"""
        return self.id
    
    def set_id(self, job_id):
        self.id = job_id
        return
#^--------------------------------------------------------- class Job

class Pending(Job):
    """Class to represent a Pending job in the SGE pending job-list. Class is child of Job class."""
    
    def set_status(self, status):
        """Method which sets the waiting status of the job. In qstat -f, hqw is error waiting, which will
        become 'Error' here, and qw is simply waiting turn, which will be 'Waiting' here. """
        if status == 'qw':
            status = 'Waiting'
        elif status == 'hqw':
            status = 'Held'
        elif status == 'Eqw':
            status = 'Error'
        else:
            #sys.exit(20)
            write_log(status, 20)
        self.status = status
        return
        
    def get_status(self):
        """Method to obtain the waiting status of a pending job."""
        return self.status
    
    def set_date(self, date):
        """Method to set the date which the job entered the pending state."""
        self.date = date
        return
    
    def get_date(self):
        """Method I wish was made a long time ago."""
        return self.date
#^--------------------------------------------------------- class Pending(Job)

#If you change the names here, don't forget to change them in cron job script and php files on webserver!
#If you are using a curl method of obtaining files, then make sure you change path to your www dir etc!
#(as in afs/crc.nd.edu/user/j/jdoe/www/index-long.html)
LONG_SAVE_FILE = 'index-long.html'
DEBUG_SAVE_FILE = 'index-debug.html'
PENDING_SAVE_FILE = 'pending.html'
SUB_NODE_FILE = 'sub-index.html'
LONG_SETUP_FILE = 'long_node_list.html'
DEBUG_SETUP_FILE = 'debug_node_list.html'

def main():
    """Main will parse cmd args to see if you're setting up or actually running. If you do not specify a cmd arg
    the script will pretend its a daemon and run continuously. I suggest './sge-graph.py &' to run it indefinitly"""
    global LONG_SAVE_FILE, DEBUG_SAVE_FILE, LONG_SETUP_FILE, DEBUG_SETUP_FILE, PENDING_SAVE_FILE 
    
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            print('Error: Too many args.')
            show_usage()
        
        elif sys.argv[1] != '--setup':
            print('Error: Incorrect usage with {0}.'.format(sys.argv[1]))
            show_usage()
            
        else:
            #alternative main
            setup_main()
    
    while True:
        qstat = subprocess.getoutput('qstat -f')
            
        node_list = []
        process_host(node_list, qstat, 'Long', True)
        tar_node_files(node_list, 'Long')
        node_list.clear()
        process_host(node_list, qstat, 'Debug', True)
        tar_node_files(node_list, 'Debug')
        node_list.clear()
        process_pending_jobs(qstat.split('#'.center(79, '#'))[2].split('\n'))
        time.sleep(140)
    sys.exit() #Fail safe incase pigs fly and True is not true ;)
#^--------------------------------------------------------- main()

def setup_main():
    """Alternative main to script if the --setup flag is specified"""
    qstat = subprocess.getoutput('qstat -f')
    node_list = []
    process_host(node_list, qstat, 'Long', False)
    node_list.clear()
    process_host(node_list, qstat, 'Debug', False)
    sys.exit()
#^--------------------------------------------------------- setup_main()
    
def process_host(node_list, qstat, queue_name, html_switch):
    """Modified method form sge_check.py to gather host information."""
        
    if queue_name == 'Long':
        desired_host_list = (subprocess.getoutput("qconf -shgrp_resolved " + '@general_access')).split()
        host_info_list = []
        for host in desired_host_list:
            if qstat.find(host) != (-1):
            #Searches the long string for the index of the occurance of the specified host, then
            #parses it the string for just that one line with the host that we want.
                host_info_list.append((qstat[qstat.find(host):].split('\n'))[0])
    else:
        host_info_list = (subprocess.getoutput("qstat -f | grep debug@")).split('\n')
        
    #Start out with everything at 0, and will count up as encountered.
    total_nodes = 0
    total_cores = 0
    used_cores = 0
    empty_nodes = 0
    disabled_cores = 0
    for host in host_info_list:
        temp_node = Node((host.split()[0]))
        cores = host.split()[2].replace('/', ' ').split()
        host_used_cores = cores[1]
        host_total_cores = cores[2]
        if len(host.split()) == 6 and host.split()[5] == 'd':
            temp_node.set_disabled_switch(True)
            disabled_cores += int(host_total_cores)
        else:    
            temp_node.set_disabled_switch(False)
            used_cores += int(host_used_cores)
            total_cores += int(host_total_cores)
        if host_used_cores == 0:
            empty_nodes += 1
        temp_node.set_cores(host_total_cores, host_used_cores)
        total_nodes += 1
        node_list.append(temp_node)
        
    #If --setup is not specified, its most likely acting as daemon so make the html info
    if html_switch:
        create_html(node_list, total_cores, used_cores, total_nodes, empty_nodes, disabled_cores, queue_name, qstat)
        
    else:
        write_setup_files(node_list, queue_name)

    return
#^--------------------------------------------------------- process_host(node_list)
  
def create_html(node_list, total_cores, used_cores, total_nodes, empty_nodes, disabled_cores, queue_name, qstat):
    """Method to create html for the Debug/Long Queues."""
    
    index_header = '<br>\n' + '<table style="width:25%">'.rjust(37) + '\n' + '<tr>'.rjust(24) + '\n' \
                   + '<th><center>Queue Name</center></th>'.rjust(45) + '\n' + '<th><center>Nodes</center></th>'.rjust(40) + '\n' \
                   + '</tr>'.rjust(25) + '\n' + '<tr>'.rjust(24) + '\n' +  '<td>{0}</td>'.format(queue_name + ' Queue').rjust(47) + '\n' \
    + '<td>{0}</td>\n'.format(total_nodes).rjust(40) + '</tr>'.rjust(25) + '\n' + '</table>'.rjust(20) + '\n'

    index_legend = '<table style="width:25%">'.rjust(37) + '\n' + '<tr>'.rjust(24) + '\n' \
                + '<td>Free Cores<div class="box green"></div></td>'.rjust(76) + '\n' + '<td>{0}</td>'.format((int(total_cores) - int(used_cores))).rjust(40) + '\n' \
                + '</tr>'.rjust(25) + '\n' + '<tr>'.rjust(24) + '\n' + '<td>Used Cores<div class="box blue"></div></td>'.rjust(75) + '\n' \
                + '<td>{0}</td>'.format(used_cores).rjust(41) + '\n' + '</tr>'.rjust(25) + '\n' + '<tr>'.rjust(24) + '\n' \
                + '<td>Disabled Cores<div class="box red"></div></td>'.rjust(75) + '\n' + '<td>{0}</td>'.format(disabled_cores).rjust(41) + '\n' \
                + '</tr>'.rjust(25) + '\n' + '<tr>'.rjust(24) + '\n' \
                + '<td>Total Cores:</td>'.rjust(49) + '\n' + '<td>{0}</td>'.format(total_cores).rjust(41) + '\n' \
                + '</tr>'.rjust(25) + '\n' + '</table>'.rjust(20)
    
    if queue_name == 'Long':
        other_queue = 'Debug'
    else:
        other_queue = 'Long'
    link_to_others = '\n<a href="../{0}" title="{0} Queue">{0} Queue</a>\n'.format(other_queue)
    link_to_others += '<a href="../Pending" title="Go to Pending Jobs">Pending Jobs</a>\n'
    
    open_core = "<a class=\"core green\" href='{0}' title=\"{0}\"></a>\n" #will need .format(node_name)
    taken_core = "<a class=\"core blue\" href='{0}' title=\"{0}\"></a>\n" #will need .format(node_name)
    disabled_node= "<a class=\"core red\" href='{0}' title=\"{0}\"></a>\n" #will need .format(node_name)
    
    index_table = '\n<br><table style="width:100%; padding: 0px">'.rjust(38) + '\n' + '<tr>\n<td>'
    
    for node in node_list:
        if node.get_disabled_switch():
            for i in range(1, node.total_cores +1):
                index_table += disabled_node.format(node.get_name())
            continue
        if node.get_free():
            for i in range(1, (node.free_cores) +1):
                index_table += open_core.format(node.get_name())
        used = node.get_used()
        if used:
            for i in range(1, (node.used_cores) +1):
                index_table += taken_core.format(node.get_name())
    index_table += '\n</td>\n</tr>\n</table>\n'
    date = subprocess.getoutput("date")
    index_table += '<div class="info"><p><center>Information current as of {0}</center></p></div>\n'.format(str(date))
    write_index_html(index_header, index_legend, index_table, queue_name, link_to_others)
    del index_header
    del index_legend
    del index_table
    del link_to_others
    
    process_nodes(node_list, qstat)
    return
#^--------------------------------------------------------- create_html(. . .)

def process_nodes(node_list, qstat):
    """Method which goes through each node and gathers information from them to be made into
    html and displayed on the Queue 'heat' map."""
    qstat_nodes = qstat.split('#'.center(79, '#'))[0] #[2] would be pending jobs!

    for node in node_list:
        node_info = (qstat_nodes[qstat_nodes.find(node.get_name()):].split('-'.center(81, '-')))[0]
        node.set_load(node_info.split()[3])
        #because of qstat, there will always be an extra element, and the element of the name itself which is not a job!
        bad_node_info = node_info.split('\n')
        good_node_info =  []
        for element in bad_node_info:
            if element != '':
                good_node_info.append(element)
        del node_info
        del bad_node_info
        node.set_num_jobs(len(good_node_info) -1)
        if int(node.get_num_jobs()) > 0:
            for i in range(1, int(node.get_num_jobs()) + 1 ):
                temp = good_node_info[i].split()
                job = Job(temp[2], temp[3], temp[7])
                job.set_priority(temp[1])
                job.set_id(temp[0])
                node.add_job(job)
    create_node_html(node_list)
    return
#^--------------------------------------------------------- process_nodes(node_list, qstat)

def process_pending_jobs(pend_list):
    """Method which takes in a string of the qstat-pending jobs, and processes that string to
    be made into html for the pending-jobs page(v0.9-beta-2)."""
    
    pending_job_list = []
    for job in pend_list:
        if job == '':
            continue
        temp = job.split()
        #Splitting qstat-section of job creates easy way to parse the job-details!
        pend_job = Pending(temp[2], temp[3], temp[7])
        pend_job.set_priority(temp[1])
        pend_job.set_status(temp[4])
        pend_job.set_date(temp[5])
        pending_job_list.append(pend_job)
    del pend_list
    create_pending_html(pending_job_list)
    return
#^--------------------------------------------------------- process_pending_jobs(pend_list)  
    
def create_pending_html(pending_job_list):
    """Method to create the actual html for the pending job page. This does not include the header and footer which should
    already be within the directory this html will be trying to go to. """
    
    pending_content = '\n' + '<table class="pending">' + '\n' + '<th>Job Name</th>' + '\n' + '<th>Priority</th>' + '\n' + '<th>User</th>' \
    + '<th>Status</th>' + '\n' + '<th>Num Cores</th>' + '\n' + '<th>Date Submitted</th>' + '\n'
    
    for job in pending_job_list:
        pending_content += '<tr>' + '\n' + '<td>{0}</td>'.format(job.get_name()) + '\n' + '<td>{0}</td>'.format(job.get_priority()) + '\n' \
        + '<td>{0}</td>'.format(job.get_user()) + '\n' + '<td>{0}</td>'.format(job.get_status()) + '\n' + '<td>{0}</td>'.format(job.get_core_info()) \
        + '\n' + '<td>{0}</td>'.format(job.get_date()) + '\n' + '</tr>' + '\n'
        
    pending_content += '</table>' + '\n'
    write_pending(pending_content)
    return
#^--------------------------------------------------------- create_pending_html(pending_job_list)

def write_pending(content):
    """Method to write to a file the html for the pending job page"""
    
    file = open(PENDING_SAVE_FILE, 'w')
    file.write(content)
    file.close()
    return
#^--------------------------------------------------------- write_pending(content)

def create_node_html(node_list):
    """Method to create the html for all individual nodes. To save time and headaches,
    all of the files created here will be tar-ed up and compressed, waiting to be gathered
    by the cronjob on the webserver."""
    
    node_header = "<h1>{0}'s Status</h1>" + '\n' + '<a href="../../Debug">Debug Queue</a>' + '\n' \
    + '<a href="../../Long">Long Queue</a>' #Need to .format(Node-name)
    
    for node in node_list:    
        if node.get_disabled_switch():
            status = 'Disabled'
        else:
            status = 'Running'
            
        node_table = '<table style="width:25%">' + '\n' + '<tr>' + '\n' + '<th>Node Name:</th>' + '\n' + '<center><td>{0}</td></center>'.format(node.get_name()) \
        + '\n' + '</tr>' + '\n' + '<tr>' + '\n' + '<th>Jobs Running:</th>' + '\n' + '<td>{0}</td>'.format(node.get_num_jobs()) + '\n' + '</tr>'\
        + '\n' + '<tr>'+ '\n' + '<th>Node Status:</th>' + '\n' + '<td>{0}</td>'.format(status) + '\n' + '</tr>' + '\n' + '<tr>' + '\n' + \
        '<th><a class="core green" href=\'#\' title="{0}"></a>Free Cores:</th>'.format('Open Cores') + '\n'+'<td>{0}</td>'.format(node.get_free()) \
        + '\n' + '/<tr>' + '\n' + '<tr>' + '\n' + '<th><a class="core blue" href=\'#\' title="{0}"></a>Used Cores:</th>'.format('Used Cores') + '\n'+'<td>{0}</td>'.format(node.get_used()) \
        + '\n' + '</tr>' + '\n' + '<tr>' + '\n' + '<th>Total Cores:</th>' + '\n' + '<td>{0}</td>'.format(node.get_total()) + '\n' + '</tr>' + '</table>'
        
        node_job_header = ''
        if int(node.get_num_jobs()) > 0:
            node_job_header = '\n' + '<table style="width:25%">' + '\n' + '<tr>' + '\n' + '<th>Jobs Running on Node</th></table>' + '\n' '</tr>' + '\n' \
            + '<table style="width:25%">' + '\n' +'<tr>' + '\n' + '<td>Job Name</td>' + '\n' + '<td>Job ID</td>' + '\n' \
            + '<td>Num Cores</td>' + '\n' + '<td>User</td>' + '\n' + '</tr>' + '\n'
            
            for job in node.get_job_list():
                node_job_header += ('\n' + '<tr>' + '\n' + '<td>{0}</td>'.format(job.get_name()) + '\n' + '<td>{0}</td>'.format(job.get_id()) + '\n' \
                + '<td>{0}</td>'.format(job.get_core_info()) + '\n' + '<td>{0}</td>'.format(job.get_user()) +'\n' + '</tr>')
            node_job_header += '\n' + '</table>' + '\n'
        
        if node.get_disabled_switch():
            node_table += '<p>This node has been disabled by the CRC Staff. This is not a cause for alarm. Do not alert CRC Support unless every node' \
            + ' has this message.</p>'
        
        open_core = "<a class=\"big_core green\" href='#' title=\"Free Core\"></a>\n"
        taken_core = "<a class=\"big_core blue\" href='#' title=\"Used Core\"></a>\n"
        disabled_node= "<a class=\"big_core red\" href='#' title=\"Node Disabled\"></a>\n"
        
        #Will need to change after upgrade, or if using for different machines!!!!!!!!!!!!!
        if int(node.get_total()) == 12:
            div_class = 'longer_node_cores'
        else:
            div_class = 'shorter_node_cores'
        node_map = '\n<br><div class="{0}">'.format(div_class).rjust(38) + '\n' + '<center>'
        
        if node.get_disabled_switch():
            #Remember, the latter digit is non-inclusive in Python! (so add 1 to it)
            for i in range(1, node.get_total() + 1):    
                node_map += disabled_node
        else:    
            for i in range(1, node.get_used() + 1):
                node_map += taken_core
            for j in range(1, node.get_free() +1):
                node_map += open_core
        node_map += '</center>\n</div>\n'
        
        date = subprocess.getoutput("date")
        node_map += '<div class="info"><p><center>Information current as of {0}</center></p></div>\n'.format(str(date))    
        write_node_html(node.get_name(), node_header.format(node.get_name()), node_table, node_job_header, node_map)
    return
#^--------------------------------------------------------- create_node_html(node_list)

def tar_node_files(node_list, Queue):
    """Tar-ing the html files of the nodes we created. This is a reason here
    why this script should be running in its own directory."""
    
    if Queue == 'Long':
        save_name = '/afs/crc.nd.edu/user/c/ckankel/www/sub-long.tar.gz'
    else:
        save_name = '/afs/crc.nd.edu/user/c/ckankel/www/sub-debug.tar.gz'
        
    tar = tarfile.open(save_name, 'w:gz')
    for node in node_list:
        tar.add(node.get_name())
    tar.close()
    return
#^--------------------------------------------------------- tar_node_files()

def write_node_html(name, header, table, jobs, n_map):
    """Method to create the actual file for a node to be displayed on the web-server.
    Each file will simply be named the same name as the node which caused it."""
    
    file = open(name, 'w')
    file.write(header)
    file.write(table)
    file.write(jobs)
    file.write(n_map)
    file.close()
    return
#^--------------------------------------------------------- write_node_html(name, header, table)

def write_index_html(header, legend, table, queue_name, link_to_queue):
    """Method to write to a file the html code generated for the Debug/Long Queues."""
    if queue_name == 'Long':    
        file = open(LONG_SAVE_FILE, 'w')
    else:
        file = open(DEBUG_SAVE_FILE, 'w')
        
    file.write(link_to_queue)
    file.write(header)
    file.write(legend)
    file.write(table)
    file.close()
    return
#^--------------------------------------------------------- write_html(node_list, queue_name)

def write_setup_files(node_list, queue_name):
    """Method to write the name of the nodes to a file to be read by the setup script
    to initially create the directories on the webserver so you don't have to by hand."""
    if queue_name == 'Long':
        file = open(LONG_SETUP_FILE, 'w')
    else:
        file = open(DEBUG_SETUP_FILE, 'w')
        
    for node in node_list:
        file.write(node.get_name())
        file.write('\n')
    return
#^--------------------------------------------------------- write_setup_files(node_list)

def write_log(info, code):
    """Method to write to a log if an error occurs and the program dies."""
    log_name = 'queue_mapd.log'
    file = open(log_name, 'a')
    date = subprocess.getoutput('date')
    
    if int(code) == 20:
        content = 'I am {0}, and have died because of bad pending job status, with {1} as the attempted status on {2}'.format(sys.argv[0], status, date)
    else:
        content = 'I am {0}, but I do not know how I got to the point of writing a log...'.format(sys.argv[0])
    
    file.write(content)
    sys.exit(code)
#^--------------------------------------------------------- write_log(info, code)

def show_usage():
    """Method to display how to use this script on stdout"""
    
    print('Correct usage: {0} [--option]\n'.format(str(sys.argv[0])))
    print('Creates html for the CRC Queue map webpage.'.center(80))
    print('    {0}'.format(sys.argv[0]).ljust(40) + 'Runs as daemon, will create html pages and sleep for 2 minutes.')
    print('    {0} --setup'.format(sys.argv[0]).ljust(40) + 'Creates the correct pages to be consumed by setup script.')
    print('Modified from sge_check.py'.center(80))
    sys.exit()
#^--------------------------------------------------------- show_usage()
    
# Standard boilerplate to call the main() function.
if __name__ == '__main__':
  main()