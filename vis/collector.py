#!/usr/bin/python

"""
An sFlow collector which passes received flow samples through dynamically loaded plugins.

Michael Fincham <michael@hotplate.co.nz>
"""

import imp
import multiprocessing
import os

import pdb
import sys

import sflow

plugins_directory = "plugins"

class ForkedPdb(pdb.Pdb):
    """
    A Pdb subclass that may be used from a forked multiprocessing child.

    Borrowed from <http://stackoverflow.com/a/23654936> for debugging.
    """

    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = file('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin

def plugin_name(plugin_path):
    """
    Given a path to a plugin (e.g. `plugins/00-foo.py') return the plugin's canonical name (e.g. `foo').
    """
    
    return plugin_path.split('/')[-1].split('.')[0].split('-')[-1]

def plugins(directory):
    """
    Return a dictionary of loaded plugins from `directory'.
    """
    
    return [
        imp.load_source(plugin_name(plugin_path), "%s/%s" % (directory, plugin_path)) 
        for plugin_path in sorted(os.listdir(directory)) if plugin_name(plugin_path) != '__init__' and plugin_path.endswith('.py')
    ]

def packet_processor(queue):
    """
    Multi-processing child process to handle sFlow packets and pass them through the loaded plugins in order.
    """
    
    plugins_list = plugins(plugins_directory)

    while True:
        packet = queue.get()    
        
        for sample in packet['samples']:
            for flow in sample['flows']:

                flow['sample'] = {k: v for k, v in sample.items() if not k == 'flows'}
                flow['metadata'] = {}

                for plugin in plugins_list:
                    flow = plugin.mangle_flow(flow)

if __name__ == '__main__':

    print "Starting collector..."

    # set up packet queue and packet processor
    packet_queue = multiprocessing.Queue()
    processor_process = multiprocessing.Process(
        target=packet_processor, args=(packet_queue,)
    )
    processor_process.start()

    sflow_collector = sflow.FlowCollector(bind_address='127.0.0.1')

    for packet in sflow_collector.receive():
        packet_queue.put(packet)

    processor_process.join()
