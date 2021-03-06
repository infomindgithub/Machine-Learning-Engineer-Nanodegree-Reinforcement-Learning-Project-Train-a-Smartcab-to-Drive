import random
import math
import itertools
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """ 

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5):
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment 
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor

        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed
        #------
        # additional parameters
        self.t = 0 # Initialize time
        
        random.seed(11082017)# good practice for regenerating the same set of random numbers
        
        # Define state status lists 
        
        self.state_status_lists = [
            #waypoint status
            ['left', 'right', 'forward'],
            #light status
            ['red', 'green'],
            #vehicle left status
            ['left', 'right', 'forward', None],
            #vehicle right status
            ['left', 'right', 'forward', None],
            #vehicle oncoming status
            ['left', 'right', 'forward', None]
        ]

        self.dq = dict((action_item, 0.0) for action_item in self.valid_actions)

        for state_tuple in itertools.product(*self.state_status_lists):
            self.Q[state_tuple] = self.dq.copy()
	#------
    def reset(self, destination=None, testing=True):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)
        
        ########### 
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0
        #---------------------
        if testing:
            self.epsilon = 0.0
            self.alpha = 0.0
        else:
            # for "default" simulation, use linearly decaying function for epsilon: epsilon= 1-alpha*t
            #self.epsilon = 1 - self.alpha*self.t
            #
            # for "improved" simulation, use negative exponential decay function for epsilon: epsilon = exp(-alpha*t)
            self.epsilon = math.exp(-self.alpha*self.t)
            #
            # Increment time
            self.t += 1
            
        return None
	#---------------------
    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint() # The next waypoint 
        inputs = self.env.sense(self)           # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        ########### 
        ## TO DO ##
        ###########
        # Set 'state' as a tuple of relevant status data for the agent. 
        #----------------------
        # Tuple order needs to be the same as that defined previously in "state status lists"       
        
        state = (waypoint, inputs['light'], inputs['left'], inputs['right'], inputs['oncoming'])

        return state
	#---------------------

    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        ########### 
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state

	#---------------------
        maximum_Q_value = max(self.Q[state].values())
        # Define a placeholder empty list
        maximum_Q_value_actions = []
        for action, Q in self.Q[state].items():
            if Q == maximum_Q_value:
                maximum_Q_value_actions.append(action) # append action to the list corresponding to themaximum Q-value

        return maximum_Q_value, maximum_Q_value_actions
	#---------------------

    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, check if the 'state' is not in the Q-table
	
	#---------------------
        if not self.learning:
            return
	#---------------------
	
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0
	
	#---------------------
        if not state in self.Q:
            self.Q[state] = self.dq.copy() # self.dq dictionary has been defined and initialized above.
        return
	#---------------------

    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = None

        ########### 
        ## TO DO ##
        ###########
        # When not learning, choose a random action
        # When learning, choose a random action with 'epsilon' probability
        #   Otherwise, choose an action with the highest Q-value for the current state
 	
 	#--------------------
        if not self.learning or random.random() <= self.epsilon:
            action = random.choice(self.valid_actions)
        else:
            Qmax, Qmax_actions = self.get_maxQ(state)
            action = random.choice(Qmax_actions)
 	return action
 	#--------------------
        


    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives an award. This function does not consider future rewards 
            when conducting learning. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')
	
	#---------------------
        if self.learning:
            self.Q[state][action] = reward * self.alpha + self.Q[state][action] * (1 - self.alpha)
	
        return
	#---------------------


    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn

        return
        

def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment()
    
    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    
    #---------------------
    # Uncomment the appropriate line below for choosing the type of simulation and alpha value
    
    # No learning (learning=False)
    #agent = env.create_agent(LearningAgent, learning=False, alpha=0.005, epsilon=1) # No learning agent, alpha value not used
    
    # Default learning agent - **Linear decay**
    #agent = env.create_agent(LearningAgent, learning=True, alpha=0.05, epsilon=1) # alpha = 0.05,   Default agent with linear decay: epsilon = 1-alpha*t
    #agent = env.create_agent(LearningAgent, learning=True, alpha=0.003, epsilon=1) # alpha = 0.003, Sensitivity study--Default agent: epsilon = 1-alpha*t
    #agent = env.create_agent(LearningAgent, learning=True, alpha=0.001, epsilon=1) # alpha = 0.001, Sensitivity study--Default agent: epsilon = 1-alpha*t
    #
    # Improved learning - **exponential decay**:
    agent = env.create_agent(LearningAgent, learning=True, alpha=0.005, epsilon=1) # alpha = 0.005, Improved learning agent: epsilon=exp(-alpha*t)
    #agent = env.create_agent(LearningAgent, learning=True, alpha=0.01, epsilon=1) # alpha = 0.01, Sensitivity study--Improved learning agent:epsilon=exp(-alpha*t)
    #agent = env.create_agent(LearningAgent, learning=True, alpha=0.001, epsilon=1) # alpha = 0.001, Sensitivity study--Improved learning agent:epsilon=exp(-alpha*t)
    #---------------------
    
    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    #---------------------
    #env.set_primary_agent(agent)
    env.set_primary_agent(agent, enforce_deadline=True)
    #---------------------
    
    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    
    #---------------------
    # Uncomment the statement below as appropriate:
    
    # Applicabe to learning agent (learning = True, optimized=True)
    sim = Simulator(env, update_delay=0.01, log_metrics=True, optimized=True, display=False)
    
    # Applicable to No learning case (learning=False, optimized=False)
    #sim = Simulator(env, update_delay=0.01, log_metrics=True, optimized=False, display=False)
    #---------------------
    
    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05 
    #   n_test     - discrete number of testing trials to perform, default is 0
    
    #---------------------
    #sim.run()
    sim.run(n_test=10, tolerance=0.005)	

if __name__ == '__main__':
    run()
