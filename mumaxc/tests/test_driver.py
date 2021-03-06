import discretisedfield as df
import mumaxc as oc


class TestDriver:
    def setup(self):
        self.system = oc.System(name='tds')
        mesh = oc.Mesh((0, 0, 0),
                       (100e-9, 100e-9, 10e-9),
                       (10e-9, 10e-9, 10e-9))
        self.system.hamiltonian += oc.Exchange(1.5e-11)
        self.system.hamiltonian += oc.Demag()
        self.system.dynamics += oc.Precession(2.211e5)
        self.system.dynamics += oc.Damping(0.02)
        self.system.m = df.Field(mesh, value=(0, 1, 0), norm=8e5)
