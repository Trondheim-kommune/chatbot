inp = open("no_50k.txt", "r")
out = open("no_50k.json", "w")

out.write('{')
for line in inp.readlines():
    w = line.strip().split(' ')
    out.write('"{}": {},'.format(w[0], w[1]))
out.write('}')

inp.close()
out.close()
