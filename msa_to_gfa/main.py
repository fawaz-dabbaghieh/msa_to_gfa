#!/usr/bin/env python3
import pdb
import sys
import os
import argparse
import logging
import json
from msa_to_gfa.check_similar_sequences import check_similar_sequences
from msa_to_gfa.fasta_reader import read_fasta_gen
from msa_to_gfa.msa_to_gfa import msa_graph
from msa_to_gfa.graph_io import write_gfa, read_gfa

parser = argparse.ArgumentParser(description='Build GFA v1 from MSA')
subparsers = parser.add_subparsers(help='Available subcommands', dest="subcommands")

parser._positionals.title = 'Subcommands'
# parser._optionals.title = 'Global Arguments'


parser.add_argument("--log", metavar="LOG_FILE", dest="log_file",
                    default="log.log", type=str, help="Log file name/path. Default = out_log.log")

parser.add_argument("--dir", metavar="OUTDIR", dest="out_dir",
                    default=".", type=str, help="Output directory where to put the output files, default: .")

########################## Constructing GFA from MSA ###############################
gfa_from_msa = subparsers.add_parser("build_graph", help="Command for building the GFA from a given MSA")

gfa_from_msa.add_argument("-f", "--in_msa", metavar="MSA_PATH", dest="in_msa",
                          default=None, type=str, help="Input MSA in FASTA format")

gfa_from_msa.add_argument("--compact", dest="compact",
                          action="store_true",
                          help="If this give, the graph will be compacted before writing")

gfa_from_msa.add_argument("-o", "--out", metavar="OUT_GFA", dest="out_gfa",
                          default="gfa_out.gfa", type=str, help="Output GFA name, default: gfa_out.gfa")

# parser.add_argument("--all_paths", dest="all_paths",
#                     action="store_true",
#                     help="If this is given, then all paths of original sequences will be added as p lines to the GFA")

gfa_from_msa.add_argument("-n", "--seq_name_tsv", metavar="SEQ_NAMES", dest="seq_names",
                          default=None, type=str, help="A tsv with two columns, first is sequence names"
                                                       ", second is a shortened or abbreviated name")

gfa_from_msa.add_argument("-c", "--nodes_info", metavar="COLORS", dest="nodes_dict",
                          default=None, type=str, help="Output JSON file with nodes information")


########################## Add paths to the graph ###############################
add_paths = subparsers.add_parser("add_paths", help="Add paths to the graph that was built")

add_paths.add_argument("-g", "--gfa", metavar="GFA", dest="gfa",
                       default=None, type=str, help="input graph to add paths to")

add_paths.add_argument("--in_groups", metavar="IN_GROUPS", dest="in_groups",
                       default=None, type=str, help="the groups json file")

add_paths.add_argument("--all_groups", dest="all_groups", action="store_true",
                       help="Adds all paths to the GFA file given")

add_paths.add_argument("--some_groups", metavar="SOME_GROUPS", dest="some_groups",
                       default=None, type=str, help="adds only the specified paths")

args = parser.parse_args()


def main():

    if len(sys.argv) < 2:
        print("You need to provide inputs. try -h or --help for help")
        sys.exit()

    if args.subcommands is None:
        print("You need to provide a subcommand first, check -h, --help")
        sys.exit(1)

    if not args.log_file:
        log_file = "out_log.log"
    else:
        log_file = args.log_file

    logging.basicConfig(filename=log_file, filemode='w',
                        format='[%(asctime)s] %(message)s',
                        level=getattr(logging, "INFO"))

    if not os.path.exists(args.out_dir):
        print("Error! Please check the log file...")
        logging.error(f"The directory {args.out_dir} provided does not exist")
        sys.exit()

    # putting arguments in log file
    logging.info(" ".join(["argument given:"] + sys.argv))

    ##################################################### MSA to GFA section
    if args.subcommands == "build_graph":
        if not args.in_msa:
            print("Error! Please check the log file...")
            logging.error("You did not provide input msa file, -f, check -h for help")
            sys.exit()

        # reading sequence names if provided
        seq_names = dict()
        sequences = dict()
        seq_len = 0

        for sqe_id, seq in read_fasta_gen(args.in_msa):
            seq_len = len(seq)
            break

        if args.seq_names:
            if os.path.exists(args.seq_names):
                # getting the names mappings
                with open(args.seq_names) as in_file:
                    for line in in_file:
                        line = line.strip().split("\t")
                        seq_names[line[0]] = line[1]

                # saving sequences from MSA with the mapped names
                for seq_id, seq in read_fasta_gen(args.in_msa):
                    if not seq_len == len(seq):
                        print("Error! Please check the log file...")
                        logging.error(f"The sequence {seq_id} has a different length compared to previous sequences, "
                                      f"aborting")
                        sys.exit(1)
                    try:
                        sequences[seq_names[seq_id]] = seq
                    except KeyError:
                        print("Error! Please check the log file...")
                        logging.error(f"The sequence {seq_id} was not found in the mapping table")
                        sys.exit(1)
            else:
                print("Error! Please check the log file...")
                logging.error("File {} provided as sequence names tsv does not exist".format(args.seq_names))
                sys.exit(1)
        else:
            for seq_id, seq in read_fasta_gen(args.in_msa):
                sequences[seq_id] = seq

        groups = check_similar_sequences(sequences)
        # building graph
        logging.info("constructing graph...")
        graph = msa_graph(sequences, groups)
        # graph.colors = seq_names

        if args.compact:
            logging.info("compacting linear paths in graph...")
            # Compacting just merges stretches of single nodes together
            graph.compact()

        logging.info("sorting the graph toplogocially...")
        # I use topological sorting to write the paths in order
        graph.sort()  # topological sorting
        output_groups_file = args.out_gfa.split(".")[0] + "_groups.json"
        if len(output_groups_file.split(os.path.sep)) > 1:
            pass
        else:
            output_groups_file = os.path.join(args.out_dir, output_groups_file)

        # outputting groups info
        logging.info("outputting paths and groups as a JSON file...")
        graph.output_groups(output_groups_file)  # adds paths to graph
        logging.info("writing graph...")

        # outputting graph
        if len(args.out_gfa.split(os.path.sep)) > 1:
            out_gfa = args.out_gfa
        else:
            out_gfa = os.path.join(args.out_dir, args.out_gfa)
        write_gfa(graph, out_gfa)

        # outputting nodes info
        if args.nodes_dict:
            logging.info("writing nodes info json file...")
            if len(args.nodes_dict.split(os.path.sep)) > 1:
                nodes_info_file = args.nodes_dict
            else:
                nodes_info_file = os.path.join(args.out_dir, args.nodes_dict)
            graph.nodes_info(nodes_info_file)

    ##################################################### paths section
    if args.subcommands == "add_paths":

        if args.gfa is not None:
            if os.path.exists(args.gfa):
                in_graph = read_gfa(args.gfa, False)
                out_graph_name = args.gfa.split(".")[0] + "_with_paths.gfa"

            else:
                print("Error! Please check the log file...")
                logging.error(f"The file {args.gfa} provided does not exist!")
                sys.exit(1)
        else:
            print("Error! Please check the log file...")
            logging.error("You did not provide an input GFA with add_paths -g, --gfa")
            sys.exit(1)
        if (args.some_groups is not None) and args.all_groups:
            print("Error! Please check the log file...")
            logging.error("You cannot give both --all_groups and --some_groups, you need to specify one")
            sys.exit(1)

        if (args.some_groups is None) and not args.all_groups:
            print("Error! Please check the log file...")
            logging.error("You need to provide either --all_groups or --some_groups")
            sys.exit(1)

        if args.in_groups is not None:
            if os.path.exists(args.in_groups):
                with open(args.in_groups, "r") as in_file:
                    try:
                        # all_groups has two keys, all_paths with seq_id as key and list of nodes for path as value
                        # and a groups key with group id as key and a list of seq_id as value
                        all_groups = json.load(in_file)
                    except json.decoder.JSONDecodeError:
                        print("Error! Please check the log file...")
                        logging.error("For some reason the JSON file is corrupted...")
                        sys.exit(1)
            else:
                print("Error! Please check the log file...")
                logging.error(f"The file {args.in_groups} provided does not exist...")
                sys.exit(1)

        if args.all_groups:
            for g_name, g_list in all_groups['groups'].items():
                # any seq in the g_list represents the whole group
                in_graph.groups[g_name] = all_groups['all_paths'][g_list[0]]

        if args.some_groups:
            if os.path.exists(args.some_groups):
                with open(args.some_groups) as in_file:
                    for l in in_file:
                        current_group = l.strip()
                        # in case the user provided a group id
                        if current_group in all_groups['groups']:
                            in_graph.groups[current_group] = all_groups['all_paths'][all_groups['groups'][current_group][0]]

                        # in case the user provided a sequence id
                        elif current_group in all_groups['all_paths']:
                            in_graph.groups[current_group] = all_groups['all_paths'][current_group]

                        else:
                            print("Check warnings in log file...")
                            logging.warning(f"couldn't add the group {current_group} because it was not found in the"
                                            f" the JSON file provided")
            else:
                print("Error! Please check the log file...")
                logging.error(f"The file {args.some_groups} provided does not exist...")
                sys.exit(1)

        if len(out_graph_name.split(os.path.sep)) > 1:
            pass
        else:
            out_graph_name = os.path.join(args.out_dir, out_graph_name)
        write_gfa(in_graph, out_graph_name, output_groups=True)

    logging.info("finished...")


if __name__ == "__main__":
    main()
