# -*- coding: utf-8 -*-

# Copyright (C) 2014, A. Murat Eren
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.

#
# This program generates XML input files for Gephi, an open source network visualization
# and exploration platform. Learn more from https://gephi.org/
# 

import sys


def get_samples_dict_from_environment_file(environment_file_path):
    samples_dict = {}
    for oligo, sample, count in [l.strip().split('\t') for l in open(environment_file_path).readlines()]:
        if samples_dict.has_key(sample):
            if samples_dict[sample].has_key(oligo):
                samples_dict[sample][oligo] += int(count)
            else:
                samples_dict[sample][oligo] = int(count)
        else:
            samples_dict[sample] = {oligo: int(count)}
    return samples_dict


def get_oligos_sorted_by_abundance(samples_dict, oligos = None, min_abundance = 0):
    samples = samples_dict.keys()
    samples.sort()

    if oligos == None:
        oligos = []
        map(lambda o: oligos.extend(o), [v.keys() for v in samples_dict.values()])
        oligos = list(set(oligos))

    abundant_oligos = []
    
    for oligo in oligos:
        percent_abundances = []

        for sample in samples:
            sum_sample = sum(samples_dict[sample].values())
            if samples_dict[sample].has_key(oligo):
                percent_abundances.append((samples_dict[sample][oligo] * 100.0 / sum_sample,\
                                           samples_dict[sample][oligo], sum_sample, sample))

        percent_abundances.sort(reverse = True)

        for abundance_percent, abundance_count, sample_size, sample in percent_abundances:
            abundant_oligos.append((sum([x[1] for x in percent_abundances]), oligo))
            break

    return [x[1] for x in sorted(abundant_oligos) if x[0] > min_abundance]


def HTMLColorToRGB(colorstring, scaled = True):
    """ convert #RRGGBB to an (R, G, B) tuple """
    colorstring = colorstring.strip()
    if colorstring[0] == '#': colorstring = colorstring[1:]
    if len(colorstring) != 6:
        raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]

    if scaled:
        return (r / 255.0, g / 255.0, b / 255.0)
    else:
        return (r, g, b)


def get_unit_counts_and_percents(units, samples_dict):
    unit_percents = {}
    unit_counts = {}

    sample_totals = {}
    for sample in samples_dict:
        sample_totals[sample] = sum(samples_dict[sample].values())

    for sample in samples_dict:
        counts = []
        percents = []
        for unit in units:
            if samples_dict[sample].has_key(unit):
                counts.append(samples_dict[sample][unit])
                percents.append(samples_dict[sample][unit] * 100.0 / sample_totals[sample])
            else:
                counts.append(0)
                percents.append(0.0)
                
        unit_counts[sample] = counts
        unit_percents[sample] = percents

    return (unit_counts, unit_percents)


def get_sample_mapping_dict(mapping_file_path):
    mapping_dict = {}
    mapping_file = open(mapping_file_path)
    
    header_line = mapping_file.readline()
    categories = header_line.strip('\n').split('\t')[1:]
    for category in categories:
        mapping_dict[category] = {}
    
    for fields in [line.strip('\n').split('\t') for line in mapping_file.readlines()]:
        sample = fields[0]
        mappings = fields[1:]
        
        for i in range(0, len(categories)):
            category = categories[i]
            mapping = mappings[i]
            
            if mapping == '':
                mapping_dict[categories[i]][sample] = None
                continue
            else:
                mapping_dict[categories[i]][sample] = mapping        
            
    mapping_file.close()
    return mapping_dict



def generate_gexf_network_file(units, samples_dict, unit_percents, output_file, sample_mapping_dict = None,
                               unit_mapping_dict = None, project = None, sample_size=8, unit_size=2,
                               skip_sample_labels = False, skip_unit_labels = False):
    output = open(output_file, 'w')

    samples = sorted(samples_dict.keys())
    sample_mapping_categories = sorted([k for k in sample_mapping_dict.keys() if k != 'colors']) if sample_mapping_dict else None
    unit_mapping_categories = sorted([k for k in unit_mapping_dict.keys() if k not in ['colors', 'labels']]) if unit_mapping_dict else None
    
    output.write('''<?xml version="1.0" encoding="UTF-8"?>\n''')
    output.write('''<gexf xmlns:viz="http:///www.gexf.net/1.1draft/viz" xmlns="http://www.gexf.net/1.2draft" version="1.2">\n''')
    output.write('''<meta lastmodifieddate="2010-01-01+23:42">\n''')
    output.write('''    <creator>Poor Man's GEXF Generator</creator>\n''')
    if project:
        output.write('''    <creator>Network description for %s</creator>\n''' % (project))
    output.write('''</meta>\n''')
    output.write('''<graph type="static" defaultedgetype="undirected">\n\n''')

    if sample_mapping_dict:
        output.write('''<attributes class="node" type="static">\n''')
        for i in range(0, len(sample_mapping_categories)):
            category = sample_mapping_categories[i]
            output.write('''    <attribute id="%d" title="%s" type="string" />\n''' % (i, category))
        output.write('''</attributes>\n\n''')

    if unit_mapping_dict:
        output.write('''<attributes class="edge">\n''')
        for i in range(0, len(unit_mapping_categories)):
            category = unit_mapping_categories[i]
            output.write('''    <attribute id="%d" title="%s" type="string" />\n''' % (i, category))
        output.write('''</attributes>\n\n''')

    output.write('''<nodes>\n''')
    for sample in samples:
        if skip_sample_labels:
            output.write('''    <node id="%s">\n''' % (sample))
        else:
            output.write('''    <node id="%s" label="%s">\n''' % (sample, sample))
        output.write('''        <viz:size value="%d"/>\n''' % sample_size)
        if sample_mapping_dict and sample_mapping_dict.has_key('colors'):
            output.write('''        <viz:color r="%d" g="%d" b="%d" a="1"/>\n''' %\
                                             HTMLColorToRGB(sample_mapping_dict['colors'][sample], scaled = False))

        if sample_mapping_categories:
            output.write('''        <attvalues>\n''')
            for i in range(0, len(sample_mapping_categories)):
                category = sample_mapping_categories[i]
                output.write('''            <attvalue id="%d" value="%s"/>\n''' % (i, sample_mapping_dict[category][sample]))
            output.write('''        </attvalues>\n''')

        output.write('''    </node>\n''')

    for unit in units:
        if skip_unit_labels:
            output.write('''    <node id="%s">\n''' % (unit))
        else:
            if unit_mapping_dict and unit_mapping_dict.has_key('labels'):
                output.write('''    <node id="%s" label="%s">\n''' % (unit, unit_mapping_dict['labels'][unit]))
            else:
                output.write('''    <node id="%s">\n''' % (unit))
        output.write('''        <viz:size value="%d" />\n''' % unit_size)

        if unit_mapping_categories:
            output.write('''        <attvalues>\n''')
            for i in range(0, len(unit_mapping_categories)):
                category = unit_mapping_categories[i]
                output.write('''            <attvalue id="%d" value="%s"/>\n''' % (i, unit_mapping_dict[category][unit]))
            output.write('''        </attvalues>\n''')

        output.write('''    </node>\n''')

    output.write('''</nodes>\n''')
    
    edge_id = 0
    output.write('''<edges>\n''')
    for sample in samples:
        for i in range(0, len(units)):
            unit = units[i]
            if unit_percents[sample][i] > 0.0:
                if unit_mapping_dict:
                    output.write('''    <edge id="%d" source="%s" target="%s" weight="%f">\n''' % (edge_id, unit, sample, unit_percents[sample][i]))
                    output.write('''        <attvalues>\n''')
                    for i in range(0, len(unit_mapping_categories)):
                        category = unit_mapping_categories[i]
                        output.write('''            <attvalue id="%d" value="%s"/>\n''' % (i, unit_mapping_dict[category][unit]))
                    output.write('''        </attvalues>\n''')
                    output.write('''    </edge>\n''')
                else:
                    output.write('''    <edge id="%d" source="%s" target="%s" weight="%f" />\n''' % (edge_id, unit, sample, unit_percents[sample][i]))


                edge_id += 1
    output.write('''</edges>\n''')
    output.write('''</graph>\n''')
    output.write('''</gexf>\n''')
    
    output.close()



def main(environment_file, sample_mapping_file = None, unit_mapping_file = None, min_abundance = 0, min_sum_normalized_percent = 1,
         sample_size = 8, unit_size = 2, skip_unit_labels = False, skip_sample_labels = False):
    samples_dict = get_samples_dict_from_environment_file(environment_file)
    oligos = get_oligos_sorted_by_abundance(samples_dict, min_abundance = min_abundance)
    unit_counts, unit_percents = get_unit_counts_and_percents(oligos, samples_dict)
    
    if sample_mapping_file:
        sample_mapping = get_sample_mapping_dict(sample_mapping_file)

    if unit_mapping_file:
        unit_mapping = get_sample_mapping_dict(unit_mapping_file)
    
    output_file = '.'.join(environment_file.split('.')[:-1]) + '.gexf'
    generate_gexf_network_file(oligos,
                               samples_dict, 
                               unit_percents, 
                               output_file, 
                               sample_mapping_dict = sample_mapping if sample_mapping_file else None,
                               unit_mapping_dict = unit_mapping if unit_mapping_file else None,
                               sample_size = sample_size,
                               unit_size = unit_size,
                               skip_sample_labels = skip_sample_labels,
                               skip_unit_labels = skip_unit_labels)



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generates a Gephi input file')
    parser.add_argument('environment_file', metavar = 'FILE',
                        help = 'Environment file that is generated by the pipeline')
    parser.add_argument('--sample-mapping', metavar = 'FILE', default = None,
                        help = 'Providing a sample mapping file will make Gephi file much more\
                                useful.')
    parser.add_argument('--unit-mapping', metavar = 'FILE', default = None,
                        help = 'Structurally, unit mapping is identical to sample mapping file,\
                                instead, it describes properties of units.')
    parser.add_argument('--sample-size', metavar = 'INT', type = int, default = 8,
                        help = 'Sample node size. Default: %(default)d')
    parser.add_argument('--unit-size', metavar = 'INT', type = int, default = 2,
                        help = 'Unit node size. Default: %(default)d')
    parser.add_argument('--min-abundance', metavar = 'INT', type = int, default = 0,
                        help = 'Minimum abundance of a unit to be included in the network.\
                                It usually a good idea to give some cut-off since each unit\
                                (whether it is an oligotype or an MED node) is going to be a\
                                part of the network (total number of reads divided by 10,000 might\
                                be a good start).')
    parser.add_argument('--min-sum-normalized-percent', metavar = 'INT', type = int, default = 1,
                        help = 'This defines the minimum sum normalized percent for an oligotype or MED\
                                node in a sample to form an edge in the network. Sum normalization takes\
                                an oligotype or MED node, generates a vector from its percent occurence in all\
                                samples, then normalizes the percent abundances so the total of the vector adds\
                                up to 100%%. The default is %(default)s, but it might be a good idea to set it\
                                to 0 for samples with a lot of samples (such as more than 100 samples).')
    parser.add_argument('--skip-sample-labels', action = 'store_true', default = False,
                    help = 'Leave sample labels blank.')
    parser.add_argument('--skip-unit-labels', action = 'store_true', default = False,
                    help = 'Leave unit labels blank.')


    args = parser.parse_args()

    
    sys.exit(main(args.environment_file, args.sample_mapping, args.unit_mapping, args.min_abundance, args.min_sum_normalized_percent,
                  sample_size = args.sample_size, unit_size = args.unit_size, skip_unit_labels = args.skip_unit_labels,
                  skip_sample_labels = args.skip_sample_labels))
