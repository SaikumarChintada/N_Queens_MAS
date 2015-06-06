__author__ = 'brandon'

import cProfile
import threading
import time
import copy


class Agent(threading.Thread):
    next_id = 0
    WAIT_MESSAGE = 0
    OK_MESSAGE = 1
    NO_GOOD = 2

    def __init__(self, network, board_size):
        self.id = board_size - Agent.next_id
        super(Agent, self).__init__(name=self.id)
        Agent.next_id += 1
        self.successors = []
        self.parents = {}
        self.current_message = Agent.WAIT_MESSAGE
        self.messages = []
        self.agent_view = {}
        self.domain = [[self.id-1, i] for i in range(board_size)]
        self.curr_pointer = 0
        self.assignment = self.domain[self.curr_pointer]
        self.network = network
        self.active = True
        self.network.add_agent(self)
        self.no_goods = {}
        self.board_s = board_size
        self.settled = False

    def process_messages(self):
        m = self.messages.pop(0)

        if m[1] == Agent.OK_MESSAGE:
            self.process_ok_message(m)
        elif m[1] == Agent.NO_GOOD:
            self.process_no_good_message(m)

    def process_ok_message(self, m):
        self.agent_view[m[0]] = m[2]

    def process_no_good_message(self, m):
        self.no_goods[len(self.no_goods)] = m[2]

    def backtrack(self):
        v = copy.copy(self.agent_view)
        t = max(self.agent_view)
        self.agent_view.pop(t)
        self.send_message(Agent.NO_GOOD, str(t), v)
        self.check_agent_view()

    def check_agent_view(self):
        if not self.consistent_check(self.assignment) or not self.check_no_goods(self.assignment):
            no_value = self.set_assignment()
            if not no_value:
                self.backtrack()
        else:
            self.send_message(Agent.OK_MESSAGE)

    def set_assignment(self):
        d = False
        if self.consistent_check(self.assignment) and self.check_no_goods(self.assignment):
            d = True
        else:
            for i in self.domain:
                self.assignment = i
                if self.consistent_check(i) and self.check_no_goods(i):
                    d = True
                    break
        if d:
            self.send_message(Agent.OK_MESSAGE)
        return d

    def consistent_check(self, val):
        d = True

        for i in self.agent_view.values():
            if self.n_queens(i, val):
                d = False
                break
        return d

    def check_no_goods(self, val):
        d = True

        for i in self.no_goods.values():
            temp_dict = copy.copy(self.agent_view)
            temp_dict[self.id] = val
            if i == temp_dict:
                d = False
                break
        return d

    def send_message(self, value, parent=None, view=None):
        if value == Agent.OK_MESSAGE:
            for i in self.successors:
                i.messages.append([self.id, Agent.OK_MESSAGE, self.assignment])
        elif value == Agent.NO_GOOD:
            s = self.parents[parent]
            s.messages.append([self.id, Agent.NO_GOOD, view])

    def n_queens(self, c, val):
        d = False
        if c[1] == val[1] or c[0] == val[0]:
            d = True

        if d:
            return d

        if (c[0] - val[0]) - (c[1] - val[1]) == 0:
            d = True

        if (c[0] - val[0]) + (c[1] - val[1]) == 0:
            d = True

        return d

    def init(self):
        self.send_message(Agent.OK_MESSAGE)

    def run(self):
        while True:
            if self.active:
                while len(self.messages) != 0:
                    self.process_messages()
                if len(self.no_goods) == 0:
                    self.send_message(Agent.OK_MESSAGE)
                self.check_agent_view()
                if len(self.messages) == 0:
                    self.active = False
            else:
                if len(self.messages) > 0:
                    self.active = True


class Network:
    def __init__(self):
        self.nodes = []

    def add_agent(self, a):
        for i in self.nodes:
            i.parents[a.name] = a
        for i in self.nodes:
            a.successors.append(i)

        self.nodes.append(a)


def main():
    n = Network()
    b = 4

    agents = [Agent(n, b) for _ in range(b)]

    [i.init() for i in agents]

    [i.start() for i in agents]

    agents = agents[::-1]

    four = [[0, 1], [1, 3], [2, 0], [3, 2]]
    five = [[0, 0], [1, 2], [2, 4], [3, 1], [4, 3]]

    s = True
    while s:
        t = [i.assignment for i in agents]
        time.sleep(2)
        print t

        c = True
        for i in agents:
            c = c and i.settled
            if not c:
                break
        if c:
            break

    print 'final', t


main()

#cProfile.run("main()")