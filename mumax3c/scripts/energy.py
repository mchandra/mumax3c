import sys
import numbers
import numpy as np
import mumax3c as calculator
import discretisedfield as df
import micromagneticmodel as mm


def energy_script(system):
    mx3 = ''
    for term in system.energy:
        mx3 += globals()[f'{term.name}_script'](system)

    # Demagnetisation in mumax3 is enabled by default.
    if mm.Demag() not in system.energy:
        mx3 += "enabledemag = false\n\n"

    # mumax complains if exchange is not included
    if mm.Exchange() not in system.energy:
        mx3 += 'Aex = 1e-20\n'

    return mx3


def exchange_script(system):
    mx3 = '// Exchange energy\n'
    mx3 += calculator.scripts.set_parameter(parameter=system.energy.exchange.A,
                                            name='Aex',
                                            system=system)
    return mx3


def zeeman_script(system):
    # mx3 file takes B, not H.
    H = system.energy.zeeman.H
    if isinstance(H, dict):
        B = dict()
        for key, value in H.items():
            B[key] = np.multiply(value, mm.consts.mu0)
    else:
        B = np.multiply(H, mm.consts.mu0)

    mx3 = '// Zeeman\n'
    mx3 += calculator.scripts.set_parameter(parameter=B,
                                            name='B_ext',
                                            system=system)
    return mx3


def demag_script(system):
    mx3 = '// Demag\n'
    mx3 += 'enabledemag = true\n\n'
    return mx3


def dmi_script(system):
    mx3 = ''
    if system.energy.dmi.crystalclass.lower() in ['t', 'o']:
        name = 'Dbulk'
        dmiparam = system.energy.dmi.D
    elif system.energy.dmi.crystalclass.lower() == 'cnv':
        name = 'Dind'
        # In mumax3 D = -D for interfacial DMI
        dmiparam = -system.energy.dmi.D
    else:
        msg = (f'The {system.energy.dmi.crystalclass} crystal class '
               'is not supported in mumax3.')
        raise ValueError(msg)

    mx3 += '// DMI\n'
    mx3 += calculator.scripts.set_parameter(parameter=dmiparam,
                                            name=name,
                                            system=system)
    return mx3


def uniaxialanisotropy_script(system):
    mx3 = "// UniaxialAnisotropy\n"
    # Only including first order for now
    mx3 += calculator.scripts.set_parameter(parameter=system.energy.uniaxialanisotropy.K,
                                            name='Ku1',
                                            system=system)
    mx3 += "anisu = vector({}, {}, {})\n\n".format(*system.energy.uniaxialanisotropy.u)

    return mx3


def cubicanisotropy_script(system):
    mx3 = "// CubicAnisotropy\n"
    mx3 += calculator.scripts.set_parameter(parameter=system.energy.cubicanisotropy.K,
                                            name='Kc1',
                                            system=system)
    mx3 += "anisC1 = vector({}, {}, {})\n".format(*system.energy.cubicanisotropy.u1)
    mx3 += "anisC2 = vector({}, {}, {})\n\n".format(*system.energy.cubicanisotropy.u2)

    return mx3


def magnetoelastic_script(term):
    B1mx3, B1name = oc.scripts.setup_scalar_parameter(term.B1, 'mel_B1')
    B2mx3, B2name = oc.scripts.setup_scalar_parameter(term.B2, 'mel_B2')
    ediagmx3, ediagname = oc.scripts.setup_vector_parameter(
        term.e_diag, 'mel_ediag')
    eoffdiagmx3, eoffdiagname = oc.scripts.setup_vector_parameter(
        term.e_offdiag, 'mel_eoffdiag')

    mx3 = ''
    mx3 += B1mx3
    mx3 += B2mx3
    mx3 += ediagmx3
    mx3 += eoffdiagmx3
    mx3 += '# MagnetoElastic\n'
    mx3 += 'Specify YY_FixedMEL {\n'
    mx3 += f'  B1 {B1name}\n'
    mx3 += f'  B2 {B2name}\n'
    mx3 += f'  e_diag_field {ediagname}\n'
    mx3 += f'  e_offdiag_field {eoffdiagname}\n'
    mx3 += '}\n\n'

    return mx3
