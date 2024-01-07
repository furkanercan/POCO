def readfile_polar_rel_idx(filepath):
    vec_polar_rel_idx = []

    try:
        with open(filepath, 'r') as file:
            # Read each line from the file and append it to the vector
            for line in file:
                values = line.split()
                vec_polar_rel_idx.extend([int(x) for x in values])
                # content = file.read()
                # vec_polar_rel_idx = [int(x) for x in content.split()]
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return vec_polar_rel_idx