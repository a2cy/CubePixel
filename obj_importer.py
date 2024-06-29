import json
from pathlib import Path

# cut down version of ursina's obj importer

folder = Path("./")

for file_path in folder.glob(f'**/*.obj'):
    with file_path.open('r') as file:
        lines = file.readlines()

    verts = []
    tris = []

    uv_indices = []
    uvs = []

    for i, l in enumerate(lines):
        if l.startswith('v '):
            parts = [float(v) for v in l[2:].strip().split(' ')]
            vert = parts[:3]
            vert[0] = -vert[0]
            verts.append(vert)

        elif l.startswith('vt '):
            uv = l[3:].strip()
            uv = uv.split(' ')
            uv.append("0.0")
            uvs.append([float(e) for e in uv])

        elif l.startswith('f '):
            l = l[2:]
            l = l.split(' ')

            tri = tuple(int(t.split('/')[0])-1 for t in l if t != '\n')

            if len(tri) == 3:
                tris.extend(tri)

            uv = tuple(int(t.split('/')[1])-1 for t in l)
            if len(uv) == 3:
                uv_indices.extend(uv)


    vertices=[verts[t] for t in tris]
    uvs=[uvs[uid] for uid in uv_indices]

    data = {"vertices": vertices, "uvs": uvs}

    with open(f"./{file_path.stem}.json", "w+") as file:
            json.dump(data, file)
