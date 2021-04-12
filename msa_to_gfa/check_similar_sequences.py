def check_similar_sequences(sequences):
    """
    takes a dictionary of sequences, removes the gaps and checks which sequences are similar
    return a dictionary of a group number as key and the similar sequence id as a list as vlaue

    :param sequences: a dictionary of sequences
    :return groups: a dictionary of a group number as key and members as a list as value
    """
    # I am doing it in probably a hacky way
    # However, this tool won't be dealing with huge amount of sequences in general
    # so having the sequences as keys (hashes) should be fine for use case of this tool
    seq_to_id = dict()
    for seq_name, seq in sequences.items():
        if seq not in seq_to_id:
            seq_to_id[seq] = [seq_name]
        else:
            seq_to_id[seq].append(seq_name)

    group = dict()
    idx = 0
    for seq, group_list in seq_to_id.items():
        group['group_' + str(idx)] = group_list
        idx += 1

    return group
