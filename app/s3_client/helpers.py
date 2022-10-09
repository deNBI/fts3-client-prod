def get_version_and_path_from_object_name(object_name: str):
    full_list = object_name.split("/")
    version = full_list[1]
    list_len = len(full_list)
    if list_len == 3:
        return version, None
    path = "/".join(full_list[index] for index in range(2, list_len - 1))
    return version, path
