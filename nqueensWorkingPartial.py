
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
        self.counter = 1
        #create agent's context
        self.id = board_size - Agent.next_id  
        print "initiation of agent",self.id
        super(Agent, self).__init__(name=self.id)
        Agent.next_id += 1
        
        self.fname = 'agent' + str(self.id)
        self.outfile = open(self.fname , 'w')


        self.successors = []
        self.parents = {}

        self.messages = []
        self.agent_view = {}
        self.no_goods = {-1:{0:[-1,-1]}}
        self.recent_no_good = []

        self.domain = [[self.id-1,i] for i in range(board_size)]
        self.board_size = board_size
        self.assignment = self.domain[0]
        self.active = True

        self.network = network
        self.network.add_agent(self)
    
    def __str__(self):
        print 'Agent '+str(self.id)+'-----------------'
        print 'pos',self.assignment
        print 'msg',self.messages
        print 'view',self.agent_view
        print 'no_goods',self.no_goods
        ls = '---------------------------------------'    
        return ls
    #=============================================================
    def process_messages(self):
        m = self.messages.pop(0)
        if m[1] == Agent.OK_MESSAGE:
            self.outfile.write('processing ok? msg from agent'+str(m[0])+'\n')
            self.process_ok_message(m)
        elif m[1] == Agent.NO_GOOD:
            self.outfile.write('processing no_good msg recieved from agent'+str(m[0])+'\t'+str(m)+'\n')
            self.process_no_good_message(m)

    def process_ok_message(self, m):
        #self.counter = 0
        self.agent_view[m[0]] = m[2]  #(agent : pos)
        self.check_agent_view()

    def process_no_good_message(self, m):
        if not m[2] in self.no_goods.values():
            self.no_goods[len(self.no_goods)] = m[2]
        self.recent_no_good = m[2]
        present = True
        if self.considered():
            present = self.set_assignment()

        if not present:
            self.outfile.write('2domain exhausted --> backtrack\n')
            self.backtrack()
    #==================================================================================
    def backtrack(self):
        no_good = copy.copy(self.agent_view)
        if no_good:
            t = max(self.agent_view.keys())
            self.outfile.write('sending no_goods to agent '+str(t)+'\t'+str(self.agent_view)+'\n')
            self.send_message(Agent.NO_GOOD,t,no_good)
            self.agent_view.pop(t)
            self.check_agent_view()
        else:
            self.outfile.write('Ended here\n')
            print "end here"

                
    #==================================================================================
    # else part need to be chanegd : if consistent do nothing
    def check_agent_view(self):
        self.outfile.write('check_agent_view\t: '+str(self.agent_view)+'\n')
        if not self.consistent_check(self.assignment):
            self.outfile.write('not consistent\t: '+str(self.agent_view)+'\t'+str(self.assignment)+'\n')
            present = True
            present = self.set_assignment()
            if not present:
                print '-------domain exhausted for agent'+str(self.id)+' '+str(self.assignment)
                self.outfile.write('domain exhausted --> backtrack\n')
                if self.counter <=5:
                    self.outfile.write('therefore backtracking\n')
                    self.counter +=1
                    self.backtrack()
                else:
                    self.outfile.write('bactracking limit exceeded\n')
        self.outfile.write('after chech_agent_view\t: '+str(self.assignment)+'\n')

    def set_assignment(self,flag = 0):
        d = False
        for i in self.domain:
            if self.consistent_check(i) and i[1]!= self.assignment[1] and self.check_no_goods(i):
                self.assignment = i
                d = True
                break
        if d:
            self.outfile.write('sending ok? msg\n')
            self.send_message(Agent.OK_MESSAGE)
        return d
    def considered(self):
        d = True
        ls = [i for i in range(1,self.id)]
        for i in ls:
            if i not in self.agent_view.keys():
                d = False
                break
        return d
    def consistent_check(self, val):
        #print 'consistency checking : agent '+str(self.id)+'\n'
        d = True
        for i in self.agent_view.values():
            if self.n_queens(i, val):
                d = False
                break
        return d

    # updates the position (val) and compares the agent_view to the no_goods
    def check_no_goods(self, val):
        mview = copy.copy(self.agent_view)
        mview[self.id] = val
        if mview in self.no_goods.values():
            return False
        return True
        
    def check(self,aview):
        d = True
        for i in self.agent_view.keys():
            if i in aview.keys() and self.agent_view[i][1] != aview[i][0]:
                d = True
            else:
                d = False
                break
        return d
    def check_no_goods2(self, val):
        d = True
        for i in self.agent_view.values():
            for aview in self.no_goods.values():
                if val in aview.values() and aview[self.id] == val and i in aview.values():
                    d  = False
                    self.outfile.write('check_no_goods\t: Failed -> change the assignment\n')
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
        #print str(self)

    def run(self):

        self.outfile.write(self.fname +' is running\n')
        int = 1
        while  int < 1000000:
            int += 1
            #self.outfile.write('state\t: '+str(self.active)+'\n')
            if self.active:
                while len(self.messages) > 0:
                    self.process_messages()
                    self.outfile.write('-----------------------------------\n')
                    self.outfile.write('pos\t\t: '+str(self.assignment)+'\n')
                    self.outfile.write('message\t: '+str(self.messages)+'\n')
                    self.outfile.write('agent_view\t: '+str(self.agent_view)+'\n')
                    self.outfile.write('no_goods\t: '+str(self.no_goods)+'\n')
                    self.outfile.write('-----------------------------------\n')
                if len(self.messages) == 0:
                    self.active = False
                    #self.send_message(Agent.OK_MESSAGE)
            else:
                if len(self.messages) > 0:
                    self.active = True

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

def Solve_n_queens(b):

    n = Network()

    agents = [Agent(n, b) for _ in range(b)]

    [i.outfile.write('parents \t: '+str(i.parents)+'\n') for i in agents]
    [i.outfile.write('successors\t: '+str(i.successors)+'\n') for i in agents]
    [i.outfile.write('-------------------------------------------\n') for i in agents]

    [i.init() for i in agents]

    print agents

    for i in agents:
        print str(i)

    [i.outfile.write('messages\t: '+str(i.messages)+'\n') for i in agents]

    [i.start() for i in agents]



if __name__ == '__main__':
    n = input('Enter a number : ')
    Solve_n_queens(n)

