from random import randint

class Academic:

    """
    An academic agent.

    Attributes:
    - id : unique identifier
    - research_quality : quality of research (random float in range 0 - 1)
    - applying: True if agent is currently applying for grants
    - grant_held : grant held for current year (boolean 1/0)
    - grant_count : number of grants received over total life
    - time_grant : time allocated to grant writing (initially random)
    - research : research produced this year
    - research_sum : cumulative research output (initially 0)
    - memory : memory, used for strategy update rules
    - postdoc_status : is the agent a postdoc (boolean 1/0)
    - former_postdoc : set to 1 if agent became permanent (boolean 1/0)
    - exited_postdoc : set to 1 if agent can't find job and exits (boolean 1/0)
    - num_postdocs : number of contracts over lifetime
    - contract_length : contract length remaining in semesters (max 10)
    - newb : are they a postdoc newb? (0.4 reduction in research time)

    Time allocated to research is currently assumed to be 1.0 - time_grant
    """

    def __init__(self, id, params, rng):

        self.params = params
        self.id = id
        self.research_quality = rng.random()
        self.applying = True
        self.grant_held = False
        self.tenured = True
        self.grant_count = 0 # total number of grants held
        self.set_random_time_grant(params['init_time'], rng)
        self.research = 0.0
        self.research_sum = 0.0
        self.memory = []    # grows at tail
        self.postdoc_status = 0
        self.former_postdoc = 0
        self.exited_postdoc = 0
        self.num_postdocs = 0
        self.contract_length = 100
        self.newb = 0
        self.made_redundant = False
        self.retired = False
        self.career_length = params['career_end']

    def retire(self):
        if self.career_length <= 10 and randint(1, 100) <= 20:
            self.made_redundant = True
            self.retired = True
            self.applying = False

    def set_random_time_grant(self, time_range, rng):

        """
        Randomise the time allocated to grant writing.

        Current modification limits to 0.1 increments.
        """
        # if self.postdoc_status == 1:
        #    self.time_grant = 0.0
        # else:
        self.time_grant = rng.random() / (1.0 / time_range)
        self.time_grant = int(self.time_grant * 10) / 10.0
            # agent must invest a minimum of 10% of their time 
            # (unless they drop out)
        if self.time_grant < 0.1:
            self.time_grant = 0.1

    
    def calc_research(self, time_grant, grant_held, grant_bonus, 
            research_quality):

        "Calculate agent research quality."

        if self.params['growing_pop'] == 1:
            if self.newb >= 1:
                return (1.0 - self.params['newb_time']) * research_quality
            elif self.grant_held:
                return ((1.0 - self.params['manager_penalty'] - time_grant) + (grant_held * grant_bonus)) * research_quality
            else:
                return ((1.0 - time_grant) + (grant_held * grant_bonus)) * \
                research_quality
        
        elif self.params['use_postdocs'] == 1:
            if self.newb >= 1:
                return (1.0 - self.params['newb_time']) * research_quality
            elif self.contract_length <= 2 and self.postdoc_status == 1:
                return (1.0 - self.params['jobhunt_time']) * research_quality
            elif self.grant_held:
                return ((1.0 - self.params['manager_penalty'] - time_grant) + (grant_held * grant_bonus)) * research_quality
            elif self.former_postdoc == 1 and self.params['mentored_pdrs'] == 1:
                return ((1.0 + self.params['mentoring_bonus'] - time_grant) + (grant_held * grant_bonus)) * research_quality
            else:
                return ((1.0 - time_grant) + (grant_held * grant_bonus)) * \
                research_quality
        else:
            return ((1.0 - time_grant) + (grant_held * grant_bonus)) * \
                research_quality                


    def produce_research(self, params):

        """
	Calculate an agent's research output for a single year.
	
	Also updates research_sum and memory.
	"""

        self.research = self.calc_research(self.time_grant, 
                self.grant_held, params['grant_bonus'], self.research_quality)
        self.research_sum += self.research
        self.update_memory(params)
        return self.research


    def get_mean_research(self, t):

        """
	Get agent's mean research output over the preceding t iterations.

	(or over less than t, if fewer iterations have occurred)
	"""

        output_values = [m[2] for m in self.memory[-t:]]
        if output_values == []:
            return 0.0
        else:
            return sum(output_values) / len(output_values)


    def update_memory(self, params):

        "Update an agent's memory with current strategy, success and output."

        self.memory.append((self.time_grant, self.grant_held, self.research))
        if len(self.memory) > params['memory_size']:
            del self.memory[0]


    def check_time_bounds(self):

        "Ensure that an agents time_grant allocation is between 0 and 1."

        if self.time_grant > 1.0: self.time_grant = 1.0
        elif self.time_grant < 0.0: self.time_grant = 0.0

        # must make a minimum effort to apply; time_grant can only be 0 if 
	# applying is False.
        if self.applying and self.time_grant < 0.1:
            self.time_grant = 0.1


    def check_reentry(self, params, rng):

        "Possibly reintroduce a previously dropped-out agent."
    
        if rng.random() < params['prob_reentry']:
            self.set_random_time_grant(params['reentry_range'], rng)
            self.applying = True
            self.memory = []


    def get_update_step(self, params):

        """
        Get update step size.
        """

        if params['self_update_width_fixed']:
            return params['self_update_width']
        else:
            return abs(rng.gauss(0.0, params['self_update_width']))


##############################################################################

    ### SELF LEARNING RULES ###

    def update_strategy_self_thermostat(self, params, rng):

        """
        Update agent strategy based on self learning.

        1. agents who do not hold a grant increase their time allocation
        2. agents who hold a grant decrease their time allocation

        WCSS paper - THERMOSTAT model
        """

        step = self.get_update_step(params)
            
        if not self.grant_held:
            #self.time_grant *= (1.0 + step)
            self.time_grant += step
        else:
            #self.time_grant *= (1.0 - step)
            self.time_grant -= step

        if (self.applying == False):
            self.check_reentry(params, rng)

        self.check_time_bounds()


    def update_strategy_self_memory(self, params, rng):

        """
        Update agent strategy based on self learning.

        1. agents who do not hold a grant, but who have held a grant recently 
            increase their time allocation
        2. agents who do not hold a grant, and who have not held a grant 
            recently stop applying (invest no time)
        3. agents who hold a grant and have consistently held a grant in 
            recent iterations decrease their time allocation
        4. agents who hold a grant, but who have not held a grant recently 
            hold their time constant

        Agents who have previously stopped applying have a probability of 
        re-entering competition at each iteration.

        WCSS paper - MEMORY model (with various memory / re-entry parameters)
        """

        step = self.get_update_step(params)
        recent = [x[1] for x in self.memory]
        r = params['run_length']

        if not self.grant_held:
            if len(recent) > r and recent[-r:] == [False]*r:
                self.time_grant = 0.0
                self.applying = False
            else:
                #self.time_grant *= (1.0 + step)
                self.time_grant += step
        else:
            if len(recent) > r and recent[-r:] == [True]*r:
                #self.time_grant *= (1.0 - step)
                self.time_grant -= step

        if (self.applying == False and self.made_redundant == False):
            self.check_reentry(params, rng)

        self.check_time_bounds()

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

