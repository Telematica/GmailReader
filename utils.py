import json

def utils_write_json_file(
    struct: list,
    filename='./secrets/labels.json'
) -> None:
    try:
        with open(filename, 'w') as f:
            json.dump(struct, f, indent=4)
    except FileNotFoundError:
        raise FileNotFoundError(f"The directory for the file {filename} does not exist.")
    except IOError as e:
        raise IOError(f"An error occurred while writing to the file {filename}: {e}")