# Define an environment at OpenAI style

import random as rnd
import numpy as np

PENALTY_ROTATE=0
PENALTY_SETROW=0

class Passenger:
    def __init__(self, pid, group):
        self.id=pid
        self.group=group
        self.isWindower=str(self.id).endswith('w')
        self.position=None
        self.status=0 # 0:'QUEUED_TO_BOARD', 1:'NEXT_TO_BOARD', 2:'PLACED_IN_PLANE'

class PassengerList:
    def __init__(self, groups):
        self.groups=groups.copy()
        self.index_group=0
        self.index_passenger_ingroup=0
        self.completed=False
        self.groups[0][0].status=1
    
    def getTotalPassengerNumber(self):
        n = 0
        for g in self.groups:
            for p in g:
                n = n + 1
        return n
    
    def getNextAndUpdate(self):
        current_passenger = self.getNext()
        if current_passenger is None:
            return None
        else:
            self.index_passenger_ingroup = (self.index_passenger_ingroup + 1) % len(self.groups[self.index_group])
            if (self.index_passenger_ingroup == 0):
                self.index_group = (self.index_group + 1) % len(self.groups)
                if (self.index_group == 0):
                    self.completed = True
            if (self.completed==False):
                self.groups[self.index_group][self.index_passenger_ingroup].status=1
            return current_passenger
    
    def getNext(self):
        if (self.completed):
            return None
        else:
            return self.groups[self.index_group][self.index_passenger_ingroup]

    def canRotate(self):
        g = self.groups[self.index_group]
        if (g[self.index_passenger_ingroup].isWindower):
            return False
        else:
            size = len(g)
            for i in range(self.index_passenger_ingroup+1,size):
                if (g[i].isWindower):
                    return True
        return False
    
    def rotate(self):
        if (self.canRotate()):
            g = self.groups[self.index_group]
            size = len(g)
            p = g[self.index_passenger_ingroup]
            for i in range(self.index_passenger_ingroup+1,size):
                g[i-1]=g[i]
            g[size-1]=p
            return True
        else:
            return False

    def getGroupRemain(self, passenger):
        index=0
        for g in self.groups:
            if (passenger in g):
                remain = 0
                for r in g:
                    if (r.status!=2):
                        remain += 1
                return index, remain
            else:
                index += 1


class Plane:
    def __init__(self, plane_dims):
        self.plane_dims=plane_dims
        self.plane=[]
        for i in range(plane_dims[0]):
            row = [None for j in range(plane_dims[1])]
            self.plane.append(row)
    
    def roomInRow(self,row_num):
        if (self.plane[row_num][-1]==None):
            return True
        else:
            return False
    
    def setPassengerInRow(self, passenger, row_num):
        for i in range(self.plane_dims[1]):
            if (self.plane[row_num][i] is None):
                self.plane[row_num][i] = passenger
                passenger.position=(row_num,i)
                passenger.status=2
                return
            
    def getPosition(self, passenger):
        for i in range(self.plane_dims[0]):
            for j in range(self.plane_dims[1]):
                if (self.plane[i][j] is not None):
                    if (self.plane[i][j].id == passenger.id):
                        return (i,j)
        return (0, 0)

    # [(<free spaces>,<number of passenger from group Id>) ...]
    def getSpaceForGroup(self, groupId):
        spaceInRows = []
        for i in range(self.plane_dims[0]):
            freeSpaces = 0
            happenings = 0
            for j in range(self.plane_dims[1]):
                if (self.plane[i][j] is None):
                    freeSpaces += 1
                elif (self.plane[i][j].group==groupId):
                    happenings += 1
            #print("space for group " + str(groupId) + ":",freeSpaces,happenings)
            spaceInRows.append((freeSpaces,happenings))
        return spaceInRows
        
    
    def drawPlane(self):
        for i in range(self.plane_dims[0]):
            row=[(str(x.id) + " ") for x in self.plane[i]]
            print(row)

class PlaneEnv:
    def __init__(self, file_name):
        self.file_name=file_name
        self.reset()

    def reset(self):
        file = open(self.file_name, 'r')
        
        # read plane dimensions
        plane_dims=[int(x) for x in file.readline().replace('\n','').split(' ')]
        
        # read Groups
        self.Groups = []
        more_groups = True
        index_group=0
        while more_groups:
            line = file.readline()
            if line is not '':
                passengers = [Passenger(x, index_group) for x in line.replace('\n','').split(' ')]
                self.Groups.append(passengers)
            else:
                more_groups = False
            index_group += 1
        self.passengerList = PassengerList(self.Groups)
        
        # End reading
        file.close()

        # Creating Empty Plane
        self.plane = Plane(plane_dims)
        
        # set actions
        self.actions=[]
        for i in range(plane_dims[0]):
            self.actions.append(i) # insert passanger at i row
        self.actions.append(plane_dims[0]) # state for rotating passanger in group
        
        return np.zeros(11*self.passengerList.getTotalPassengerNumber())
            
    # retrieve number of actions
    def action_space_n(self):
        return len(self.actions)
    
    # retrieve a random action.
    def action_space_sample(self):
        valid_action = False
        action = None
        while valid_action==False:
            action = self.actions[rnd.randint(0,self.action_space_n()-1)]
            if (action < self.action_space_n()-1):
                if (self.plane.roomInRow(action)):
                    valid_action = True
            elif (action == self.action_space_n()-1 & self.passengerList.canRotate() ):
                valid_action = True
        return action
    
    # Run a step. Return: observation (std normalized), reward, done
    def step(self, action):
        #print("action: ",action)
        invalid_action_1=False
        invalid_action_2=False
        invalid_action_3=False
        hasBeenRotated=False
        # Action execution
        if (action == self.action_space_n()-1):
            hasBeenRotated=True
            if (self.passengerList.canRotate()):
                #print('any rotation?')
                self.passengerList.rotate()
            else:
                #print("WARN: rotate group " + self.index_group + " is not possible!")
                invalid_action_1=True
        else:
            if ( self.plane.roomInRow(action) ):
                passenger = self.passengerList.getNextAndUpdate()
                if (passenger is not None):
                    self.plane.setPassengerInRow(passenger, action)
                else:
                    #print("WARN: there is no more passenger for boarding")
                    invalid_action_2=True
            else:
                #print("WARN: there is not room in row " + str(action))
                return self.step(self.action_space_sample())
                #invalid_action_3=True

        # Check if episode is finished
        done = self.passengerList.completed

        # Reward evaluation. Only after the end
        reward = 0
        if (done):
            for group in self.Groups:
                reward = reward + self.__groupedLevel__(group)
            reward = reward + self.__windowLevel__()
        else:
            if (hasBeenRotated == True):
                reward = self.__penaltyAfterRotate__()
            else:
                reward = self.__penaltyAfterRowSet__(action)

        
        info={'ia1':invalid_action_1,'ia2':invalid_action_2,'ia3':invalid_action_3}
        return (self.__s2x__(), reward, done, info)
    
    # Transform state in gaussian normalized vector X
    # each passanger in original order: p0 p1 S0 S1 S2 W G0 G1 G2 G3 .. Gn
    def __s2x__(self):
        p_x = []
        nGroups = len(self.Groups)
        g_index = 0
        for group in self.Groups:
            for p in group:
                # Position
                (posX, posY)=self.plane.getPosition(p)
                p_x.append(posX)
                p_x.append(posY)
                
                # state
                stsoh = self.__one_hot__(p.status,3)
                p_x = self.__append__(p_x, stsoh)
                
                # window
                if (p.isWindower == True):
                    p_x.append(1)
                else:
                    p_x.append(0)
                
                # group
                goh = self.__one_hot__(g_index,nGroups)
                p_x = self.__append__(p_x, goh)
            g_index = g_index + 1
        return np.array(p_x)
    
    def __one_hot__(self, value, labels):
        targets = np.array([value])
        ohm = np.zeros((targets.shape[0], labels))
        #empty one-hot matrix
        ohm[np.arange(targets.shape[0]), targets] = 1
        return ohm[0].tolist()
    
    def __append__(self, init, add):
        for c in add:
            init.append(c)
        return init

    # Group Percentage of grouping
    def __groupedLevel__(self, group):
        id_group = [x.id for x in group]
        #print('-> id_group: ' + str(id_group))
        g_partial = []
        g_total = len(id_group)
        for i in range(self.plane.plane_dims[0]):
            g_row = 0
            for j in range(self.plane.plane_dims[1]):
                if (self.plane.plane[i][j] is not None):
                    if (self.plane.plane[i][j].id in id_group):
                        #print('---> id: ' + str(i) + ', ' + str(self.plane.plane[i][j].id))
                        g_row = g_row + 1
            g_partial.append(g_row)
        return float(max(g_partial)/g_total)*100
    
    # Percentage of passangers in window
    def __windowLevel__(self):
        w_ok = 0
        w_total = 0
        for i in range(self.plane.plane_dims[0]):
            for j in range(self.plane.plane_dims[1]):
                if (self.plane.plane[i][j].isWindower is not None):
                    if (self.plane.plane[i][j].isWindower):
                        w_total = w_total + 1
                        if (j == 0):
                            w_ok = w_ok + 1
        return float(w_ok/w_total)*100

    def __penaltyAfterRotate__(self):
        #print('__penaltyAfterRotate__')
        isThereWindower=False
        g=self.passengerList.groups[self.passengerList.index_group]
        for p in g:
            if(p.isWindower):
                isThereWindower=True
        if (isThereWindower == False):
            return PENALTY_ROTATE
        else:
            return 0

    def __penaltyAfterRowSet__(self, action):
        #print('__penaltyAfterRotate__')
        row=self.plane.plane[action]
        p_prev=None
        row_index=0
        for p in row:
            if (p is None):
                break
            row_index += 1
            p_prev=p
        i,g_size_remain=self.passengerList.getGroupRemain(p_prev)

        spaceInRows=self.plane.getSpaceForGroup(i)
        sir = np.array(spaceInRows)
        #print("group: ",i," size remain: ",g_size_remain,", spaces in rows: ",spaceInRows)

        # penalty conditions
        if ( (p_prev.isWindower==True) & p_prev.position[1]!=0 & (sir[:,0].max() == self.plane.plane_dims[1]) ): 
            return PENALTY_SETROW

        if ( ((g_size_remain) > sir[0][0]) & ((g_size_remain + 1) <= sir[:,0].max()) ):
            return PENALTY_SETROW

        return 0
