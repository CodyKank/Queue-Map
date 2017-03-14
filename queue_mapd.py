#!/usr/bin/env python3

import sys, subprocess, time, tarfile, os
"""Python 3 script which will gather node information and create a partial html webpage
from that information for a 'heat' map of the queue. This partial page is a component to
be included from index.php on the current web-server. There are two other components,
header.html and footer.html for each: host group. There is also a pending job file.
Latest update: Mar 14, 2017.
Exit codes: 0 - Good
            20 - Bad Pending Job status
            21 - Bad memory translate
            22 - Temp ratio not within 0-100
            24 - Bad Queue-name"""


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
        self.total_mem = 0
        self.used_mem = 0
        self.free_mem = 0

    def __repr__(self):
        name = self.name
        return name

    def __str__(self):
        return self.name

    def add_job(self, job):
        """Method to add an instance of class Job to the job_list of a node."""
        self.job_list.append(job)
        self.num_jobs += 1
        return

    def get_total_mem(self):
        """Returns the total amount of memory a node contains as a STRING"""
        return self.total_mem

    def get_used_mem(self):
        """Returns the amount of memory(RAM) a node currently is using as a STRING"""
        return self.used_mem

    def get_free_mem(self):
        """Returns the amount of free RAM a node currently is using as a STRING"""
        return self.free_mem

    def set_total_mem(self, mem):
        """Method which sets the total memory (RAM) that this certain node has, which is found using qstat -F
        and parsing the node. The amount of total_mem will be stored as an string."""
        self.total_mem = mem
        return

    def set_used_mem(self, u_mem):
        """Method to set the amount of used memory (RAM) in a certain node. This info is found by parsing qstat -F.
        The amount of used_mem will be stored as an string."""
        self.used_mem = u_mem
        return

    def set_free_mem(self, default=0):
        """Method which sets the amount of free memory. If no amount of memory is specified, the funciton will calculate
        the free memory from the self.total_mem - self.used_mem. Thus, it is important to set those first. If an amount of
        memory is speified, that will be stored instead. self.free_mem is set as an string."""
        if default == 0:
            self.free_mem = (int(self.total_mem) - int(self.used_mem))
        else:
            self.free_mem = default
        return

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
        elif status == 'Rq':
            status = 'Running'
        else:
            self.write_pen_log(status, 20)
        self.status = status
        return

    def write__pen_log(self, info, code):
        """Method to write to a log if an error occurs and the program dies."""
        log_name = 'queue_mapd.log'
        file = open(log_name, 'a')
        date = subprocess.getoutput('date')

        if int(code) == 20:
            content = 'I am {0}, and have died because of bad pending job status, with {1} as the attempted status on {2}\n'.format(sys.argv[0], info, date)
        else:
            content = 'I am {0}, but I do not know how I got to the point of writing a log...\n'.format(sys.argv[0])

        file.write(content)
        sys.exit(code)

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

#Global file names etc
HOSTGROUPLIST = []
SETUPFILE = 'queue_mapd-setup.txt'
CORE_HOSTGROUPS = 'afs/crc.nd.edu/user/c/ckankel/www/queue_mapd-core.tar.gz'
MEM_HOSTGROUPS = 'afs/crc.nd.edu/user/c/ckankel/www/queue_mapd-mem.tar.gz'
NODEFILE = 'queue_mapd-nodes.tar.gz'
PENDING_SAVE_FILE = 'afs/crc.nd.edu/user/c/ckankel/www/pending-jobs.html'

LOG_NAME = 'queue_mapd.log'


def main():
    """Main will parse cmd args to see if you're setting up or actually running. If you do not specify a cmd arg
    the script will pretend its a daemon and run continuously. I suggest './queue_map.py &' to run it indefinitly"""
    global LOG_NAME, SETUPFILE, NODEFILE, HOSTGROUPLIST, MEM_HOSTGROUPS, CORE_HOSTGROUPS

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

    # This is a daemon, should run forever (unless its changed to chron job!!)

    while True:
        pen_bool = True # Making sure pending jobs are only calculated once per entire run!
        HOSTGROUPLIST = get_hg_list()
        for host in HOSTGROUPLIST:

            temp_stat = subprocess.getoutput('qstat -F')
            # This will make a list of 3 strings. [0] is all of the nodes and their info. [1] is junk. [2] is pen-jobs.
            temp_stat = temp_stat.split('\n###############################################################################\n')
            pending_jobs = temp_stat[2]
            qstat = temp_stat[0]
            del temp_stat

            node_list = []
            process_host(node_list, qstat, host, True)
            tar_node_files(node_list, host)
            node_list.clear()
            if pen_bool:
                process_pending_jobs(pending_jobs)
                pen_bool = False    # Flipping the switch
            del pending_jobs
        # tar together all of the HG's tar.gz's which contain all the node files
        tar_hostGroups()
        time.sleep(200)
    sys.exit() #Fail safe incase pigs fly and True is not true
#^--------------------------------------------------------- main()

def setup_main():
    """Alternative main to script if the --setup flag is specified"""
    qstat = subprocess.getoutput('qstat -F')
    hg_list = get_hg_list()
    node_list = []
    for host in hg_list:
        process_host(node_list, qstat, host, False)
        node_list.clear()
    # cleaning up our mess in the current dir, removing all files that tar-ed
    for item in HOSTGROUPLIST:
        os.remove((item + '.txt').replace('@',''))
    sys.exit()
#^--------------------------------------------------------- setup_main()

def get_hg_list():
    """Function for obtaining the list of HG's supplied by qconf
    Returns a list of the available host groups recognized and
    reported by qconf"""
    qconf = subprocess.getoutput("qconf -shgrpl").split('\n')
    qconf_list = []
    for line in qconf:
        qconf_list.append(line)
    return qconf_list
#^--------------------------------------------------------- get_hg_list()

def process_host(node_list, qstat, hg, html_switch):
    """Gathers information from the host from hostgroup 'hg'. If html_switch is true,
    then html will be generated to represent this host group, and its nodes will
    be passed into another function to have html generated as well. """

    if hg:
        # The '@' is required here but it is already included if using qconf -shgrpl
        desired_host_list = (subprocess.getoutput("qconf -shgrp_resolved " + hg)).split()
        # If there aren't any nodes to a specified host group, we don't want to make a page for it
        if desired_host_list is None:
            return
        host_info_list = []
        for host in desired_host_list:
            if qstat.find(host) != (-1):
            #Searches the list of strings for the index of the occurance of the specified host, then
            #grabs the string of the host we want.
                q_search = qstat.split('\n---------------------------------------------------------------------------------\n')
                for node in q_search:
                    if node.find(host) != (-1):
                        host_info_list.append(node)

    #Start out with everything at 0, and will count up as encountered.
    total_nodes = 0
    total_cores = 0
    used_cores = 0
    empty_nodes = 0
    disabled_cores = 0
    for host in host_info_list:
        temp_node = Node(((host.split()[0].replace('long@', ''))).replace('gpu@',''))
        cores = host.split()[2].replace('/', ' ').split()
        host_used_cores = cores[1]
        host_total_cores = cores[2]
        # If within the first line of the node there is a 'd' at the end, disable it
        if len(host.split('\n')[0].split()) == 6 and ((host.split('\n')[0]).split()[5] == 'd' or (host.split('\n')[0]).split()[5] == 'au' or (host.split('\n')[0]).split()[5] == 'E'):
            temp_node.set_disabled_switch(True)
            disabled_cores += int(host_total_cores)
            # If node is in error, with au and E cannot get memory usage
            temp_node.set_total_mem('NA')
            temp_node.set_used_mem('NA')
            temp_node.set_free_mem('NA')
        else:
            # If node is not in an error state, find the core and memory usage
            # so [25] is line 25 down from the start of that node which contains total_mem
            temp_node.set_disabled_switch(False)
            used_cores += int(host_used_cores)
            total_cores += int(host_total_cores)
            total_mem = host.split('\n')[25]
            total_mem = total_mem[total_mem.find('=') +1 :]
            used_mem = host.split('\n')[26]
            used_mem = used_mem[used_mem.find('=') +1 :]
            free_mem = host.split('\n')[27]
            free_mem = free_mem[free_mem.find('=') + 1 :]
            temp_node.set_total_mem(total_mem)
            temp_node.set_used_mem(used_mem)
            temp_node.set_free_mem(free_mem)
        if host_used_cores == 0:
            empty_nodes += 1
        temp_node.set_cores(host_total_cores, host_used_cores)

        total_nodes += 1
        node_list.append(temp_node)

    #If --setup is not specified, its most likely acting as daemon so make the html info
    if html_switch:
        create_html(node_list, total_cores, used_cores, total_nodes, empty_nodes, disabled_cores, hg, qstat)

    #If --setup is supplied, then html_switch will be false and so we don't need to make html, just want Hg and node names
    else:
        write_setup_files(node_list, hg)
        create_HG_list()
        tar_setup_files()

    return
#^--------------------------------------------------------- process_host(node_list)

def create_html(node_list, total_cores, used_cores, total_nodes, empty_nodes, disabled_cores, hostGroup, qstat):
    """Method to create html for the parameter hostGroup. This html will be named """

    index_header = '<br>\n' + '<table style="width:25%">'.rjust(37) + '\n' + '<tr>'.rjust(24) + '\n' \
                   + '<th><center>HostGroup Name</center></th>'.rjust(45) + '\n' + '<th><center>Nodes</center></th>'.rjust(40) + '\n' \
                   + '</tr>'.rjust(25) + '\n' + '<tr>'.rjust(24) + '\n' +  '<td>{0}</td>'.format(hostGroup).rjust(47) + '\n' \
    + '<td>{0}</td>\n'.format(total_nodes).rjust(40) + '</tr>'.rjust(25) + '\n' + '</table>'.rjust(20) + '\n'

    index_legend = '<table style="width:25%">'.rjust(37) + '\n' + '<tr>'.rjust(24) + '\n' \
                + '<td>Free Cores<div class="box green"></div></td>'.rjust(76) + '\n' + '<td>{0}</td>'.format((int(total_cores) - int(used_cores))).rjust(40) + '\n' \
                + '</tr>'.rjust(25) + '\n' + '<tr>'.rjust(24) + '\n' + '<td>Used Cores<div class="box blue"></div></td>'.rjust(75) + '\n' \
                + '<td>{0}</td>'.format(used_cores).rjust(41) + '\n' + '</tr>'.rjust(25) + '\n' + '<tr>'.rjust(24) + '\n' \
                + '<td>Disabled Cores<div class="box red"></div></td>'.rjust(75) + '\n' + '<td>{0}</td>'.format(disabled_cores).rjust(41) + '\n' \
                + '</tr>'.rjust(25) + '\n' + '<tr>'.rjust(24) + '\n' \
                + '<td>Total Cores:</td>'.rjust(49) + '\n' + '<td>{0}</td>'.format(total_cores).rjust(41) + '\n' \
                + '</tr>'.rjust(25) + '\n' + '</table>'.rjust(20)


    #link_to_others = '\n<a href="../../" title="{0} Page">{0} Page</a>\n'.format('main')
    #link_to_others += '<a href="../Pending" title="Go to Pending Jobs">Pending Jobs</a>\n'
    filter_link = '<a href="../{0}-memory" title="Apply Memory Filter">Memory View</a>\n'.format(hostGroup)

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
    write_index_html(index_header, index_legend, index_table, hostGroup, link_to_others, filter_link)
    create_memory_html(node_list, index_header, hostGroup, link_to_others)
    del link_to_others
    del index_header
    del index_table
    del index_legend
    process_nodes(node_list, qstat)
    return
#^--------------------------------------------------------- create_html(. . .)

def create_memory_html(node_list, header, hostGroup, link_to_others):
    """Method which creates the partial html page for the memory-mapped version/filter
    for this particular queue. It takes the same legend as the core-mapped version uses,
    it only changes the way the nodes appear. It will color nodes with high percentage memory
    usage as red, medium as yellow, moderate as green, and low as blue.
    >=90% = red, 70%-89% = yellow, 36%-69% = green, 0-35 = blue. Gray means the node is disabled."""

    # All of these nodes will link to the normal node-page for themselves located within their Host-group directory
    red_node = "<a class=\"rect_node red\" href='../" + hostGroup + "/{0}' title=\"{0}\"></a>\n" #will need .format(node_name)
    yellow_node = "<a class=\"rect_node yellow\" href='../" + hostGroup + "/{0}' title=\"{0}\"></a>\n" #will need .format(node_name)
    green_node = "<a class=\"rect_node green\" href='../" + hostGroup + "/{0}' title=\"{0}\"></a>\n" #will need .format(node_name)
    blue_node = "<a class=\"rect_node blue\" href='../" + hostGroup + "/{0}' title=\"{0}\"></a>\n" #will need .format(node_name)
    gray_node = "<a class=\"rect_node gray\" href='../" + hostGroup + "/{0}' title=\"{0}\"></a>\n" #will need .format(node_name)

    filter_link ='<a href="../{0}" title="Apply Core Filter">Core View</a>\n'.format(hostGroup)

    mem_table = '\n<br><table style="width:100%; padding: 0px">\n' + '<tr>\n<td>'

    # Start all at zero, and increment as we find them.
    num_red = 0
    num_yellow = 0
    num_green = 0
    num_blue = 0
    num_gray = 0   #Disabled is gray for memory nodes. change disabled cores to gray instead of red as well? (above)
    for node in node_list:
        #Need to draw each node to screen using rectangle. Not the cores, just the node themselves!
        if node.get_disabled_switch():
            mem_table += gray_node.format(node.get_name())
            num_gray += 1
        else:
            temp_total = translate_memory(node.get_total_mem(), node)
            temp_used = translate_memory(node.get_used_mem(), node)
            temp_ratio = int((temp_used/temp_total)*100.0)
            if temp_ratio <= 35:
                mem_table += blue_node.format(node.get_name())
                num_blue += 1
            elif temp_ratio >35 and temp_ratio <= 69:
                mem_table += green_node.format(node.get_name())
                num_green += 1
            elif temp_ratio >69 and temp_ratio <=89:
                mem_table += yellow_node.format(node.get_name())
                num_yellow += 1
            elif temp_ratio >89 and temp_ratio <=100:
                mem_table += red_node.format(node.get_name())
                num_red += 1
            else:
                # Halt and catch fire, bad data
                write_to_log('create_memory_html', 22, temp_ratio)

    mem_table += '\n</td>\n</tr>\n</table>\n'
    date = subprocess.getoutput("date")
    mem_table += '<div class="info"><p><center>Information current as of {0}</center></p></div>\n'.format(str(date))

    legend = '<table style="width:25%">\n' + '<tr><th>Memory Usage</th>\n' + '<th>Nodes</th></tr>\n' + '<tr>\n<td>90-100%(Very High)<div class="box red"</div>' \
             + '</td>\n' + '<td>{0}</td>'.format(str(num_red)) + '\n</tr>\n' + '<tr>\n' + '<td>70-89%(High)<div class="box yellow"</div>' \
             + '</td>\n' + '<td>{0}</td>'.format(str(num_yellow)) + '\n</tr>\n' + '<tr>\n' + '<td>36-69%(Moderate)<div class="box green"</div>' \
             + '</td>\n' + '<td>{0}</td>'.format(str(num_green)) + '\n</tr>\n' + '<tr>\n' + '<td>0-35%%(Low)<div class="box blue"</div>' \
             + '</td>\n' + '<td>{0}</td>'.format(str(num_blue)) + '\n</tr>\n' + '<tr>\n' + '<td>Disabled Node<div class="box gray"</div>' \
             + '</td>\n' + '<td>{0}</td>'.format(str(num_gray)) + '\n</tr>\n'

    write_memory_html(header, link_to_others, filter_link, legend, mem_table, hostGroup)
    return
#^--------------------------------------------------------- create_memory_html(node_list, header, legend, table)

def write_memory_html(header, link_to_others, filter_link, legend, mem_table, hostGroup):
    """Writes the html for the memory filtered version of the queue-map. Results will be
    written to a file named after the hostGroup + -mem."""


    fileName = (hostGroup.replace('@', '')) + '-mem'
    file = open(fileName, 'w')
    file.write(link_to_others)
    file.write(filter_link)
    file.write(header)
    file.write(legend)
    file.write(mem_table)
    file.close()
    return
#^--------------------------------------------------------- write_memory_html(eader, link, filter, mem_table)

def translate_memory(mem, node):
    """Method to translate human readable memory into a reasonably rounded off interger version of it,
    in GB (this is for HTC/HPC so there will at least be a gigabyte for total.) Will take in mem as the
    memory to be translated, and return good_memory as the translated memory. Assumes it will receive
    a string ending in either G or M to represent Gigabyte and Megabyte respectively. Will return a
    float to represent the memory passed in. If a NA is received then string NA will be returned."""

    if mem.find('M') != (-1):
        # Getting rid of the M for megabyte and translating into a Gigabyte (small number!)
        mem = (float(mem.replace('M','')) /1024.0)
        return mem
    elif mem.find('G') != (-1):
        # Getting rid of G for gigabyte, and returning the float.
        mem = float(mem.replace('G',''))
        return mem
    elif mem == 'NA':
        return mem
    else:
        # Halt and catch fire
        write_to_log('translate_memory', 21, str(mem), True, node)
#^--------------------------------------------------------- translate_memory(mem)

def write_to_log(loc_from, code, prob_var, nodeSwitch=False, node=None):
    """Method which writes to a log named as a global--LOG_NAME. It takes the name of the function as a STRING--loc_from and the
    intened exit code as code as an INT, and it takes prob_var as a STRING (for easy printing!)"""

    date = subprocess.getoutput("date")
    file = open(LOG_NAME, 'a') # Appending the log, to keep a better history of what has happened.
    file.write('DATE: {0}\n-----------------------------------\n'.format(date))
    file.write('I am {0}, and I had an issue with the var: {1}.\n'.format(loc_from, prob_var))
    if nodeSwitch:
        file.write('\nThe node causing problems is: {0}\n'.format(node.get_name()))
        file.write("This node's memory is as follows:\n")
        file.write("Total Memory: {0}\nUsed Memory: {1}\nFree Memory: {2}\n".format(node.get_total_mem(), node.get_used_mem(), node.get_free_mem()))

    file.close()
    sys.exit(code)
#^--------------------------------------------------------- write_to_log(loc_from, code, prob_var)

def process_nodes(node_list, qstat):
    """Method which goes through each node and gathers information from them to be made into
    html and displayed on the Queue 'heat' map."""

    #Run through each node and add the jobs
    for node in node_list:
        node_stat = qstat[qstat.find(node.get_name()):]
        # In qstat -F, qf:min_cpu . . . . is the last item before the jobs are listed, 28 is how many char's that string is (don't want it)
        node_stat= node_stat[node_stat.find('qf:min_cpu_interval=00:05:00') + 28\
                             :node_stat.find('\n---------------------------------------------------------------------------------\n')]
        # There is always an extra '\n' in here, so subtract 1 to get rid of it
        num_jobs = len(node_stat.split('\n')) -1
        # If there are any jobs, parse them and gather info
        if num_jobs > 0:
            # Python is non-inclusive for the right operand, and we want to skip another extra '\n' so start at 1, and want to go num_jobs
            for i in range(1, num_jobs + 1):
                info = node_stat.split('\n')[i].split()
                temp_job = Job(info[2], info[3], info[7])
                temp_job.set_id(info[0])
                temp_job.set_priority(info[1])
                node.add_job(temp_job)
    create_node_html(node_list)
    return
#^--------------------------------------------------------- process_nodes(node_list, qstat)

def process_pending_jobs(pending):
    """Method which takes in a string of the qstat-pending jobs, and processes that string to
    be made into html for the pending-jobs page(v0.9-beta-2)."""

    pend_list = pending.split('\n')
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

    """file = open(PENDING_SAVE_FILE, 'w')
    file.write(content)
    file.close()"""
    pass
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

        # Finding memory status in relation to the ratio of used-mem : total-mem
        total_mem = translate_memory(node.get_total_mem(), node)
        used_mem = translate_memory(node.get_used_mem(), node)
        if isinstance(total_mem, str):
            mem_status = "<a class=\"core gray\" href='#' title=\"NA\"></a>Error: NA\n"
        else:
            ratio = int((used_mem/total_mem)*100.0)
            if ratio <= 35:
                mem_status = "<a class=\"core blue\" href='#' title=\"Low\"></a>Low\n"
            elif ratio >35 and ratio <= 69:
                mem_status = "<a class=\"core green\" href='#' title=\"Moderate\"></a>Moderate\n"
            elif ratio >69 and ratio <=89:
                mem_status = "<a class=\"core yellow\" href='#' title=\"High\"></a>High\n"
            elif ratio >89 and ratio <=100:
                mem_status = "<a class=\"core red\" href='#' title=\"Danger\"></a>Very High\n"
            else:
                # HCF
                write_to_log('create_node_html', 22, str(ratio))

        mem_info = '<table style="width:25%">\n' + '<tr>\n' + '<th>Memory Usage</th>\n' + '<th>{0}</th>\n'.format(mem_status) \
        + '<th>{0}%</th>\n'.format(str(ratio)) + '<tr>\n' + '<td>Total Memory</td>\n' + '<td>Used Memory</td>\n' + '<td>Free Memory</td>\n' + '</tr>\n' + '<tr>\n' + \
        '<td>{0}</td>\n'.format(node.get_total_mem()) + '<td>{0}</td>\n'.format(node.get_used_mem()) + '<td>{0}</td>\n'.format(node.get_free_mem())\
        + '</tr>\n' + '</table>\n'
        node_job_header += mem_info

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

def tar_node_files(node_list, host):
    """Tar-ing the html files of the nodes we created. This is a reason here
    why this script should be running in its own directory. This creates a tar gz
    archive of all of the nodes within this current HG only."""

    """if Queue == 'Long':
        save_name = '/afs/crc.nd.edu/user/c/ckankel/www/sub-long.tar.gz'
    else:
        save_name = '/afs/crc.nd.edu/user/c/ckankel/www/sub-debug.tar.gz'"""

    save_name = '/afs/crc.nd.edu/user/c/ckankel/temp/{0}.tar.gz'.format(host)

    tar = tarfile.open(save_name, 'w:gz')
    for node in node_list:
        realName = node.get_name().replace('long@', '')
        realName = node.get_name().replace('debug@', '') # just in case its the debug HG
        realName = realName.replace('.crc.nd.edu','') + '.html' # the files are all saved as nodeName.html i.e. d6copt130.html
        tar.add(realName)
    tar.close()
    return
#^--------------------------------------------------------- tar_node_files()

def tar_hostGroups():
    """Tar-ing all of the hostgroup tar files which contain the nodes and the nodes' html files
    which will be displayed on the web server. The curl queue files bash script will grab these.
    Saves the result of this to the global NODEFILE"""

    tar = tarfile.open(NODEFILE, 'w:gz')
    for host in HOSTGROUPLIST:
        hostName = host + '.tar.gz'
        tar.add(hostName)
    tar.close()
    return
#^--------------------------------------------------------- tar_hostGroups()

def write_node_html(name, header, table, jobs, n_map):
    """Method to create the actual file for a node to be displayed on the web-server.
    Each file will simply be named the same name as the node which caused it."""

    name = name.replace('long@', '')
    name = name.replace('debug@', '')
    name = name.replace('.crc.nd.edu', '')
    name = name + '.html'
    file = open(name, 'w')
    file.write(header)
    file.write(table)
    file.write(jobs)
    file.write(n_map)
    file.close()
    return
#^--------------------------------------------------------- write_node_html(name, header, table)

def write_index_html(header, legend, table, hostGroup, link_to_queue, filter_link):
    """Method to write to a file the html code generated for the Debug/Long Queues."""

    hostName = hostGroup.replace('@','')
    file = open(hostName, 'w')
    file.write(link_to_queue)
    file.write(filter_link)
    file.write(header)
    file.write(legend)
    file.write(table)
    file.close()
    return
#^--------------------------------------------------------- write_html(node_list, queue_name)

def write_setup_files(node_list, queue_name):
    """Method to write the **name** of the nodes to a file to be read by the setup script
    to initially create the directories on the webserver so you don't have to by hand.
    This makes a .txt file named after the HG these nodes came from. It will need to be tarred together with
    the rest of the files created!"""

    #The files need to be named what the HG is, so the bash script can make the proper dir's etc
    file = open(queue_name.replace('@','') + '.txt', 'w')
    for node in node_list:
        nodeName = node.get_name()
        # Getting rid of prefixes that are present by default
        nodeName = nodeName.replace('long@', '')
        nodeName = nodeName.replace('debug@', '')
        nodeName = nodeName.replace('.crc.nd.edu', '')
        # Adding the prefix of the Hg the node belongs to
        file.write(nodeName)
        file.write('\n')
    file.close()
    HOSTGROUPLIST.append(queue_name)
    return
#^--------------------------------------------------------- write_setup_files(node_list)

def tar_setup_files():
    """Function to tar the setup files together into one file. This will create queue_mapd-setup.txt"""
    saveName = '/afs/crc.nd.edu/user/c/ckankel/www/{0}'.format(NODEFILE)
    tar = tarfile.open(saveName, 'w:gz')
    for host in HOSTGROUPLIST:
        tar.add(host.replace('@','') + '.txt')
    tar.close()
    return
#^--------------------------------------------------------- tar_setup_files()

def create_HG_list():
    """Function to create queue_mapd-setup.txt from the HOSTGROUPLIST to be read by the setup script
    which will create all necesarry directoires for all of the host-groups"""
    save_name = '/afs/crc.nd.edu/user/c/ckankel/www/{0}'.format(SETUPFILE)

    with open(save_name, 'w+') as file: # Allowing python to handle closing
        for group in HOSTGROUPLIST:
            file.write(group.replace('@',''))
            file.write('\n')
    # file is now closed automatically, even if exception is raised
    return
#^--------------------------------------------------------- create_HG_list()

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
