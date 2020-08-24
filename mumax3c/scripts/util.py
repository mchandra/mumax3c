import numbers
import numpy as np
import discretisedfield as df


def set_subregions(system):
    names = system.m.mesh.subregions.keys()
    subregions_dict = dict(zip(names, range(len(names))))

    norm = system.m.norm
    max_region_number = 256
    def value_fun(pos):
        tol = 1e-3
        if norm(pos) < tol:
            return max_region_number - 1
        else:
            for name, subregion in system.m.mesh.subregions.items():
                if pos in subregion:
                    return subregions_dict[name]

            if not system.m.mesh.subregions:  # subregions are not defined
                return 0
            else:
                msg = f'Point {pos} does not belong to any region.'
                raise ValueError(msg)

    # Region field. Where the value is 255, Ms=0. In other regions Ms is const.
    # Other regions are annotated with 0, 1, 2,... according to the subregions
    # in field.mesh.
    rf = df.Field(system.m.mesh, dim=1, value=value_fun)
    rf.write('subregions.omf')

    return 'regions.LoadFile("subregions.omf")\n'


def set_parameter(parameter, name, system):
    mx3 = ''
    if isinstance(parameter, numbers.Real):
        mx3 += f'{name} = {parameter}\n'

    elif isinstance(parameter, (list, tuple, np.ndarray)):
        mx3 += '{} = vector({}, {}, {})\n'.format(name, *parameter)

    elif isinstance(parameter, dict):
        names = system.m.mesh.subregions.keys()
        subregions_dict = dict(zip(names, range(len(names))))

        for key, value in parameter.items():
            if isinstance(value, numbers.Real):
                mx3 += f'{name}.setregion({subregions_dict[key]}, {value})\n'

            elif isinstance(value, (list, tuple, np.ndarray)):
                mx3 += (f'{name}.setregion({subregions_dict[key]}, '
                        'vector({}, {}, {}))\n'.format(*value))
    
    elif isinstance(parameter, df.Field):
        # - Strategy is to write to disk and load the data. 
        # - Only meant to be called during initialization.
        # - Terrible for spatiotemporally varying parameters.
        parameter.write(f'{name}.ovf')

        mx3 += (f'{name}.Add(LoadFile("{name}.ovf"), 1)') # Assuming constant in time

    else:
        msg = f'Cannot use {type(parameter)} to set parameter.'
        raise TypeError(msg)

    return mx3
