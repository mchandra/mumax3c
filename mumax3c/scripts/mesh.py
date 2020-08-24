import mumax3c as calculator


def mesh_script(system):
    mx3 = '// Mesh\n'
    if system.m.mesh.bc:
        repetitions = [0, 0, 0]
        for direction in system.m.mesh.pbc:
            # Need to figure out the way of setting up the repetitions.
            repetitions[df.util.axesdict(direction)] = 1
        mx3 += 'SetPBC({}, {}, {})\n'.format(*repetitions)
    mx3 +=  'SetGridSize({}, {}, {})\n'.format(*system.m.mesh.n)
    mx3 += 'SetCellSize({}, {}, {})\n\n'.format(*system.m.mesh.cell)
    mx3 += calculator.scripts.set_subregions(system)

    return mx3
