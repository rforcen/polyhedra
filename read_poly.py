import zipfile
from glob import iglob as dir
from math import sqrt
from os.path import join


def read_poly(fnme):
    ' read file and create a dict of tokens in string format'
    with open(fnme) as f:
        lines = f.read().splitlines()

        tok_dict, content, token = dict(), None, None

        for l in lines:
            if l[0] == ':':
                if token:
                    tok_dict[token] = content
                token = l[1:]
                content = []
            else:
                content += [l]

    return tok_dict


def extract_token(tok_dict, token):
    def n2(s):  # get 2 int from s
        return list(map(int, s.split(' ')))

    # vertices -> convert to [[x0,y0,z0]...[xn,yn,zn]]
    if token == 'vertices':
        v = tok_dict[token]
        nex, nv = n2(v[0])  # n coords, nv=numerical coords
        vert = [list(map(float, v[nv + i + 1].split(' '))) for i in range(nex - nv)]
        return vert
    elif token == 'solid':
        v = tok_dict[token]
        nf, nx = n2(v[0])  # nfaces, max coord/face
        faces = [list(map(int, v[i + 1].split(' ')[1:])) for i in range(nf)]
        return faces


def get_geometry(tok_dict):
    'from dict(d) return vertices,faces'

    def scale_center(v):
        # scale 0..1
        _max = [max(cc) for cc in zip(*v)]
        _min = [min(cc) for cc in zip(*v)]
        _dif = [abs(_max - _min) for _max, _min in zip(_max, _min)]

        for i in range(len(v)):
            v[i] = [(v[i][j] - _min[j]) / _dif[j] for j in range(len(v[i]))]
        # center
        centroid = [sum(cc) / len(v) for cc in zip(*v)]
        for i in range(len(v)):
            v[i] = [v[i][j] - centroid[j] for j in range(len(v[i]))]

    def normal(vert3):
        def normVect(v):
            len = sqrt(sum([c * c for c in v]))
            if len != 0:
                return [c / len for c in v]
            else:
                return [0., 0., 0.]

        pa = [x - y for x, y in zip(vert3[1], vert3[0])]
        pb = [x - y for x, y in zip(vert3[2], vert3[0])]
        n = [pa[i] * pb[j] - pa[j] * pb[i] for i, j in ((1, 2), (2, 0), (0, 1))]

        return normVect(n)

    def int2(s):  # get 2 int from list of string
        return list(map(int, s.split(' ')))

    vert, net, faces = [], [], []

    v = tok_dict['vertices']
    l = v[0].split(' ')  # cases: ## -> no solid only net | ## ## -> solid +  net
    if len(l) == 1:
        nv, nvs = int(l[0]), 0
    else:
        nv, nvs = int2(v[0])

    if len(l) == 2:  # solid
        vert = [list(map(float, v[i + 1 + nvs].split(' '))) for i in range(nv - nvs)]
    else:  # net
        vert = [list(map(lambda x: float(x.split('[')[0]), v[i + 1].split(' '))) for i in range(nv)]

    scale_center(vert)

    v = tok_dict['net']
    nf, nx = int2(v[0])  # nfaces, max coord/face
    net = [list(map(int, v[i + 1].split(' ')[1:])) for i in range(nf)]

    v = tok_dict.get('solid')
    if v:
        nf, nx = int2(v[0])  # nfaces, max coord/face
        faces = [list(map(lambda x: int(x) - nvs, v[i + 1].split(' ')[1:])) for i in range(nf)]

    normals = [normal([vert[ci] for ci in f]) for f in faces]

    return vert, faces, normals


def get_geo_from_file(fnme):
    return get_geometry(read_poly(fnme))


def all_dict_in_path(path):
    ad = [read_poly(f) for f in dir(join('polyhedra', '*'))]
    return list(filter(lambda d: d.get('solid'), ad))


def all_dict_in_zip(znme):
    with zipfile.ZipFile(znme) as z:
        zfiles = [zz.filename for zz in z.infolist() if zz.filename.startswith('polyhedra/')][1:]
        ad = [read_poly_fromz(z, f) for f in zfiles]
    return list(filter(lambda d: d.get('solid'), ad))


def read_poly_fromz(z, fnme):
    ' read zip file and create a dict of tokens in string format'
    with z.open(fnme,'r') as f:
        lines = f.read().splitlines()

        tok_dict, content, token = dict(), None, None

        for l in lines:
            l=l.decode("utf-8")
            if l[0] == ':':
                if token:
                    tok_dict[token] = content
                token = l[1:]
                content = []
            else:
                content += [l]

    return tok_dict


def list_all_polys():
    for f in dir(join('polyhedra', '*')):
        d = read_poly(f)
        v, n, f = get_geometry(d)
        print(d['name'][0])
        print(v, '\n', f)
        for _f in f:
            for _v in _f:
                print(v[_v])
            print()


if __name__ == '__main__':
    list_all_polys()
