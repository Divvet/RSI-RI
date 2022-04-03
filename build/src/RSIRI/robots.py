import PyKDL


def vec(vals):
    return PyKDL.Vector(vals[0], vals[1], vals[2])


joints = [{'segment': 'link1', 'joint': 'joint_a1', 'RotAxis': vec([0, 0, -1]), 'origin': vec([0, 0, 0.4])},
          {'segment': 'link2', 'joint': 'joint_a2', 'RotAxis': vec([0, 1, 0]), 'origin': vec([0.025, 0, 0])},
          {'segment': 'link3', 'joint': 'joint_a3', 'RotAxis': vec([0, 1, 0]), 'origin': vec([0.455, 0, 0])},
          {'segment': 'link4', 'joint': 'joint_a4', 'RotAxis': vec([-1, 0, 0]), 'origin': vec([0, 0, 0.035])},
          {'segment': 'link5', 'joint': 'joint_a5', 'RotAxis': vec([0, 1, 0]), 'origin': vec([0.42, 0, 0])},
          {'segment': 'link6', 'joint': 'joint_a6', 'RotAxis': vec([-1, 0, 0]), 'origin': vec([0.08, 0, 0])}]


def jntarray(q):
    qjnt = PyKDL.JntArray(6)
    for i in range(6):
        qjnt[i] = q[i]
    return qjnt


q_lower = jntarray([-2.96705972839, -3.31612557879, -2.09439510239, -3.22885911619, -2.09439510239, -6.10865238198])
q_upper = jntarray([2.96705972839, 0.785398163397, 2.72271363311, 3.22885911619, 2.09439510239, 6.10865238198])


def make_segment(joint):
    jt = PyKDL.Joint(joint['joint'], joint['origin'], joint['RotAxis'], PyKDL.Joint.RotAxis)
    seg = PyKDL.Segment(joint['segment'], jt, PyKDL.Frame(joint['origin']))
    return seg


chain = PyKDL.Chain()

for joint in joints:
    chain.addSegment(make_segment(joint))

fk_kdl = PyKDL.ChainFkSolverPos_recursive(chain)
ik_v_kdl = PyKDL.ChainIkSolverVel_pinv(chain)
ik_p_kdl = PyKDL.ChainIkSolverPos_NR_JL(chain, q_lower, q_upper, fk_kdl, ik_v_kdl)


def fk(q):
    frame = PyKDL.Frame()
    fk_kdl.JntToCart(q, frame)
    return frame


def ik(frame, q_guess):
    q_res = PyKDL.JntArray(6)
    ik_p_kdl.CartToJnt(q_guess, frame, q_res)
    return q_res


if __name__ == '__main__':
    q = jntarray([0.1, 0.0, 0.0, 0.0, 0.0, 0.0])
    frame = fk(q)
    q_guess = jntarray([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    print(ik(frame, q_guess))
