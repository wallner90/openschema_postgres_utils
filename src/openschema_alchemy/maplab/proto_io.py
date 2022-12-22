from maplab.vimap.proto import VImap


def to_db(session, input_dir, map_name):
    vimap = VImap(input_dir)

    print(vimap.message.missions[0])