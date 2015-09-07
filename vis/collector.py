#!/usr/bin/env python

"""
An sFlow collector which passes received flow samples through dynamically loaded plugins.

Michael Fincham <michael@hotplate.co.nz>
"""

import imp
import multiprocessing
import os
import config

import sflow

plugins_directory = "plugins"

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

def setup_plugins(directory, config):
    """
    Setup any plugins that need setup
    """

    plugins_list = plugins(plugins_directory)
    for plugin in plugins_list:
        try:
            plugin.setup(config)
        except AttributeError:
            pass

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

    config = config.Config()
    config.load()

    # Setup plugins
    plugins_list = plugins(plugins_directory)
    setup_plugins(plugins_directory, config)

    # set up packet queue and packet processor
    packet_queue = multiprocessing.Queue()
    processor_process = multiprocessing.Process(
        target=packet_processor, args=(packet_queue,)
    )
    processor_process.start()

    sflow_collector = sflow.FlowCollector(bind_address='0.0.0.0')

    for packet in sflow_collector.receive():
        packet_queue.put(packet)

    processor_process.join()
