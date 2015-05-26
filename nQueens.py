
import cProfile , random
import threading, time ,sys, copy

lock = threading.Lock()

class Agent(threading.Thread):
    next_id = 0
    WAIT_MESSAGE = 0
    OK_MESSAGE = 1
    NO_GOOD = 2
    KILL = False

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
    
    #=============================================================
    def process_messages(self):
        m = self.messages.pop(0)
        if m[1] == Agent.OK_MESSAGE:
            self.process_ok_message(m)
        elif m[1] == Agent.NO_GOOD:
            self.process_no_good_message(m)

    def process_ok_message(self, m):
        self.agent_view[m[0]] = m[2]
        self.check_agent_view()

    def fetch(self,fetch_id):
        for agent in self.network:
            if agent.id == fetch_id:
                return i
    
    def process_no_good_message(self, m):
        self.no_goods[len(self.no_goods)] = m[2]
        for _id in m[2].keys():
            
            if _id not in self.agent_view.keys(): #and _id not in self.parents:
                a = fetch(_id)
                self.parents[_id] = a 
                a.successors.append(self)
                self.agent_view[_id] = a.assignment

        self.check_agent_view()
        '''
        old = self.assignment
        self.check_agent_view()
        if old == self.assignment:
            self.parents[m[0]].messages.append([self.id, Agent.OK_MESSAGE, self.assignment])
        '''

    #original
    def process_no_good_message2(self, m):
        self.no_goods[len(self.no_goods)] = m[2]

        #dynamic linking
        for view in self.no_goods.values():
            for _id in view.keys():
                if _id not in self.agent_view.keys():
                    #add link to it
                    a = fetch(_id)
                    self.parents[_id] = a 
                    a.successors.append(self.self)
                    self.agent_view[_id] = a.assignment
        old = self.assignment
        check_agent_view()
        if old == self.assignment:
            self.parents[m[0]].messages.append([self.id, Agent.OK_MESSAGE, self.assignment])

    #==================================================================================
    def backtrack(self):
        lock.acquire()
        lock.release()
        if self.agent_view:
            t =  max(self.agent_view.keys())   #min priority parent
            
            self.send_message(Agent.NO_GOOD,self.parents[t],self.agent_view)
            self.agent_view.pop(t)
            self.check_agent_view()
        else:
            self.settled = True
            Agent.KILL = True

    #orig2
    def backtrack3(self):
        for i in self.no_goods.values():
            if not i:
                #broadcast and terminate
                Agent.KILL = True   
                #print 'no solution=========================\n'
        for view in self.no_goods.values():
            least_prior_id = max(view.keys())
            #least_assign = view[least_prior_id]
            send_message(Agent.NO_GOOD,self.parents[least_prior_id], view)
            #remove that element from self agent view
            self.agent_view.pop(least_prior_id)
        self.check_agent_view()
        self.send_message(Agent.OK_MESSAGE)
    #original
    def backtrack2(self):
        #print 'backtracking agent '+str(self.id)+'\n'
        if self.no_goods :  
            v = copy.copy(self.agent_view)
            t = max(self.agent_view)
            self.agent_view.pop(t)
            
            self.send_message(agent.NO_GOOD, str(t), v)
            self.check_agent_view()
        else:
            #need to check this condition
            self.settled = True
            #print '\n-no solution------------------------\n'
            Agent.KILL = True
    #==================================================================================
    # else part need to be chanegd : if consistent do nothing
    def check_agent_view(self):
        #print 'agent'+ str(self.id)+' checking its view \n'
        if not self.consistent_check(self.assignment) or not self.check_no_goods(self.assignment):
            present = self.set_assignment()
            if not present:
                self.backtrack()
        #else: 
        #    self.send_message(Agent.OK_MESSAGE)

    def set_assignment(self):
        #print 'setting an assignment : agent '+str(self.id)+'\n'
        d = False
        #all constraints --> saisfied and agent_view --> inconsistent with no_goods
        #else:
        for i in self.domain:
            self.assignment = i
            if self.consistent_check(i) and self.check_no_goods(i):
                d = True
                break
        if d:
            self.send_message(Agent.OK_MESSAGE)
        return d
    
    def consistent_check(self, val):
        #print 'consistency checking : agent '+str(self.id)+'\n'
        d = True
        for i in self.agent_view.values():
            if self.n_queens(i, val):
                d = False
                break
        return d

    def partof(self,d,D):
        flag = True
        for i in d.keys():
            if D[i] != d[i]:
                flag = False
        return flag

    # updates the position (val) and compares the agent_view to the no_goods
    def check_no_goods(self, val):
        #print 'check no_goods :  agent '+str(self.id)+'\n'
        d = True

        for aview in self.no_goods.values():
            temp_dict = copy.copy(self.agent_view)
            #buggy
            temp_dict[self.id] = val
            if self.partof(temp_dict,aview) and val in aview.values():
                d = False 
        return d
 
    def n_queens(self, c, val):
        d = False
        if c[1] == val[1] and  c[0] != val[0]:
            d = True
        if d:
            return d
        if (c[0] - val[0]) - (c[1] - val[1]) == 0:
            d = True
        if (c[0] - val[0]) + (c[1] - val[1]) == 0:
            d = True
        return d
#=====================================================================================

        # selecting  parent is crucial 
    def send_message(self, value, parent=None, view=None):
        if value == Agent.OK_MESSAGE:
            for i in self.successors:
                i.messages.append([self.id, Agent.OK_MESSAGE, self.assignment])
        elif value == Agent.NO_GOOD:
            s = self.parents[parent]
            s.messages.append([self.id, Agent.NO_GOOD, view])

    def init(self):
        self.send_message(Agent.OK_MESSAGE)

    def run(self):
        while  True:
            if self.active:
                #if it has some messages -> run 
                while len(self.messages) != 0:
                    self.process_messages()

                #if no constraint : send ok
                #if len(self.no_goods) == 0:
                #    self.send_message(Agent.OK_MESSAGE)
                
                #self.check_agent_view()
                if len(self.messages) == 0:
                    self.active = False
            else:
                if len(self.messages) > 0:
                    self.active = True

#================================================================================
class Network:
    def __init__(self):
        self.nodes = []

    def add_agent(self, a):
        for i in self.nodes:
            i.parents[a.name] = a   #parents is a dictionary
        for i in self.nodes:
            a.successors.append(i)  #successors is a list

        self.nodes.append(a)

#================================================================================
def Solve_n_queens(b): # b is board size
    
    n = Network()

    agents = [Agent(n, b) for _ in range(b)]


    [i.init() for i in agents]

    [i.start() for i in agents]

    agents = agents[::-1]

    #four = [1,3,0,2]
    #five = [0,2,4,1,3]

    s = True
    while s:
        t = [i.assignment for i in agents]
        time.sleep(2)
        print t
        c = True
        #if all the agents are setteled then exit
        for i in agents:
            c = c and i.settled
            if c:
                break
        if c:
            break
    [i.join() for i in agents]
    #program execution completed 
    print ("==================================================================")

def Solve_n_queens2(b):

    n = Network()

    agents = [Agent(n, b) for _ in range(b)]


    [i.init() for i in agents]

    [i.start() for i in agents]

    agents = agents[::-1]

    print agents

if __name__ == '__main__':
    n = input('Enter a number : ')
    Solve_n_queens(n)




'''
    idea :  init lower priority agents first . put them in network.
            make links to all the lower agents and the current agents.
'''