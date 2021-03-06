
import cProfile , random
import threading, time ,sys, copy


'''
    agents      : 1,2,3,4
    position    : 1[0,x] 2[1,x] 3[2,x] 4[3,x]
    assignment  : [x,y]
    agent_view  : {agent_id : assignment }
    no_good     : {x : agent_view }
    messages    : [[agent_id , type_of_msg ,(agent_view/no_good)]]

'''

lock = threading.Lock()

class Agent(threading.Thread):
    next_id = 0
    WAIT_MESSAGE = 0
    OK_MESSAGE = 1
    NO_GOOD = 2
    KILL = False

    def __init__(self, network, board_size):
        self.id = board_size - Agent.next_id  
        print "initiation of agent",self.id
        super(Agent, self).__init__(name=self.id)
        Agent.next_id += 1
        
        self.fname = 'agent' + str(self.id)
        self.outfile = open(self.fname , 'w')
         
        self.successors = []
        self.parents = {}
        self.current_message = Agent.WAIT_MESSAGE # need to use this in code
        self.messages = []
        self.agent_view = {}    # for fast look up
        self.no_goods = {}    

        self.domain = [[self.id-1, i] for i in range(board_size)]
        self.current_pos = 0
        self.curr_pointer = 0
        self.assignment = self.domain[0]
        self.active = True
        self.settled = False
        self.board_s = board_size

        self.network = network
        self.network.add_agent(self)
         
    
    #=============================================================
    def process_messages(self):
        m = self.messages.pop(0)
        if m[1] == Agent.OK_MESSAGE:
            self.outfile.write('processing ok? msg\n')
            self.process_ok_message(m)
        elif m[1] == Agent.NO_GOOD:
            self.outfile.write('processing no_good msg\n')
            self.process_no_good_message(m)

    def process_ok_message(self, m):
        self.agent_view[m[0]] = m[2]  #(agent : pos)
        self.check_agent_view()

    def process_no_good_message(self, m):
        self.no_goods[len(self.no_goods)] = m[2]
        #dynamic linking
        print m[2]
        for _id in m[2].keys():
            if _id not in self.agent_view.keys() and _id != self.id:
                #add link to it
                a = self.network.get_agent(_id)
                print 'saikumar',a
                self.parents[_id] = a 
                a.successors.append(self)
                if _id != self.id:
                    self.agent_view[_id] = a.assignment
        self.check_agent_view()
    #==================================================================================
    def backtrack(self):
        print 'backtracking'
        self.outfile.write('backtracking\n')
        no_good = copy.copy(self.agent_view)
        if no_good:
            t =  max(self.agent_view.keys())
            self.outfile.write('sending no_goods to agent '+str(t)+'\n')
            self.send_message(Agent.NO_GOOD,t,no_good)
            self.agent_view.pop(t)
            self.check_agent_view()
        else:
            self.outfile.write('Ended here\n')
    #==================================================================================
    # else part need to be chanegd : if consistent do nothing
    def check_agent_view(self):
        self.outfile.write('check_agent_view\t: '+str(self.agent_view)+'\n')
        if not self.consistent_check(self.assignment) or not self.check_no_goods(self.assignment):
            self.outfile.write('not consistent\t: '+str(self.agent_view)+'\t'+str(self.assignment)+'\n')
            present = self.set_assignment()
            if not present:
                self.outfile.write('domain exhausted --> backtrack\n')                     #checking the domain
                self.backtrack()
            else:
                self.outfile.write('after chech_agent_view\t: '+str(self.assignment)+'\n')

    def set_assignment(self):
        d = False
        #all constraints --> saisfied and agent_view --> inconsistent with no_goods
        for i in self.domain:
            
            if self.consistent_check(i) and self.check_no_goods(i):
                self.assignment = i
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
        print 'here is the problem',d,D
        flag = True
        for i in d.keys():
            if D[i][1] != d[i][1] and D[i][0]!= d[i][0]:
                flag = False
        return flag

    # updates the position (val) and compares the agent_view to the no_goods
    def check_no_goods(self, val):
        d = True
        for aview in self.no_goods:
            for i in aview.keys():
                if i == self.id and aview[i] == val:
                    d = False 
                    break
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
        self.outfile.write('sending ok? msg\n')
        self.send_message(Agent.OK_MESSAGE)

    def run(self):
        
        self.outfile.write(self.fname +' is running\n')
        #if self.id >0:
        #    self.outfile.write('haha '+str(self.parents[Thread-1])+'\n')
        #'''
        int = 1
        while  int < 1000000:
            int += 1
            if self.active:
                #if it has some messages -> run 
                while len(self.messages) != 0:
                    self.process_messages()
                    self.outfile.write('pos\t\t: '+str(self.assignment)+'\n')
                    self.outfile.write('message\t: '+str(self.messages)+'\n')
                    self.outfile.write('agent_view\t: '+str(self.agent_view)+'\n')
                    self.outfile.write('no_goods\t: '+str(self.no_goods)+'\n')
                #if no constraint : send ok
                '''
                if len(self.no_goods) == 0:
                    self.outfile.write('sending ok? msg\n')
                    self.send_message(Agent.OK_MESSAGE)
                '''
                #self.check_agent_view()
                if len(self.messages) == 0:
                    self.active = False
            else:
                #self.check_agent_view()
                if len(self.messages) > 0:
                    self.active = True
        #'''

#================================================================================
class Network:
    def __init__(self):
        self.nodes = []

    def add_agent(self, a):
        for i in self.nodes:
            i.parents[a.id] = a  #parents is a dictionary
        for i in self.nodes:
            a.successors.append(i)  #successors is a list

        self.nodes.append(a)

    def get_agent(self,target_id):
        #pass
        for agent in self.nodes:
            if agent.id == target_id :
                return agent
        


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
    #[i.join() for i in agents]
    #program execution completed 
    print ("==================================================================")

def Solve_n_queens2(b):

    n = Network()

    agents = [Agent(n, b) for _ in range(b)]

    [i.outfile.write('parents \t: '+str(i.parents)+'\n') for i in agents]

    [i.outfile.write('successors\t: '+str(i.successors)+'\n') for i in agents]

    [i.init() for i in agents]

    print agents

    [i.outfile.write('messages\t: '+str(i.messages)+'\n') for i in agents]

    [i.start() for i in agents]

if __name__ == '__main__':
    n = input('Enter a number : ')
    Solve_n_queens2(n)

'''
    idea :  init lower priority agents first . put them in network.
            make links to all the lower agents and the current agents.

'''
