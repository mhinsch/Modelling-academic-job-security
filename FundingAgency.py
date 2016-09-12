class FundingAgency:

    """
    The funding body.

    Collects applications and allocates grants.  Typically there will only
    be one instance of this per simulation.
    
    Agents are sorted into a given number of pools, and the top agents from
    each pool are awarded grants.  If the number of pools is one, then agents
    are competing against the entire population.
    """

    def __init__(self, params):
        self.pools = []
	# allocate individuals to pools
        for p in xrange(params['grant_pools']):
            self.pools.append([])
	# store data on successful applications
        self.successful_app_stats = []
        self.num_grants = params['starting_grant_fund']


    def add_application(self, new_app, rng):

        """
        Add new_app to a randomly chosen pool.
        """

        self.pools[rng.randint(0, len(self.pools)-1)].append(new_app)


    def clear_applications(self):

        """
        Clear all current applications.
        """

        for i in range(len(self.pools)):        
            self.pools[i] = []


    def rank_applications(self):
        for p in self.pools:        
            p.sort()


    def get_grant_recipients(self, params, size):

        """
        Return a list of authors whose applications were successful.
        """

        num_grants = params['grant_proportion'] * (0.75 * size)
        print('Number of grants available: {}'.format(num_grants))

        per_pool = [int(num_grants / params['grant_pools'])] * \
                params['grant_pools']

        leftover = int(num_grants % params['grant_pools'])

        for i in range(leftover):
            per_pool[i] += 1

        success = []
        for i in range(params['grant_pools']):
            success.extend([app for 
                app in self.pools[i][:per_pool[i]]])
            self.successful_app_stats.extend([(app.author_quality, 
                app.author_time) for app in self.pools[i][:per_pool[i]]])

        return [app.author_id for app in success]

    def get_grant_recipients_pdr(self, params, size):

        """
        Return a list of authors whose applications were successful.
        """

        num_grants = params['grant_proportion'] * size

        per_pool = [int(num_grants / params['grant_pools'])] * \
                params['grant_pools']

        leftover = int(num_grants % params['grant_pools'])

        for i in range(leftover):
            per_pool[i] += 1

        success = []
        for i in range(params['grant_pools']):
            success.extend([app for 
                app in self.pools[i][:per_pool[i]]])
            self.successful_app_stats.extend([(app.author_quality, 
                app.author_time) for app in self.pools[i][:per_pool[i]]])

        return [app.author_id for app in success]

    def init_grants(self):
        self.num_grants = params['starting_grant_fund']
        
    def update_grants(self, params):
        self.num_grants += self.num_grants * params['yearly_increase']
        self.num_grants = int(self.num_grants)
        
    def get_recipients_limited(self, params, size):
        """
        Return a list of successful applications in limited funding case.
        """
        self.update_grants(params)
        #print("Possible grants available: {}".format(self.num_grants))
        per_pool = [int(self.num_grants / params['grant_pools'])] * \
                params['grant_pools']

        leftover = int(self.num_grants % params['grant_pools'])

        for i in range(leftover):
            per_pool[i] += 1

        success = []
        for i in range(params['grant_pools']):
            success.extend([app for 
                app in self.pools[i][:per_pool[i]]])
            self.successful_app_stats.extend([(app.author_quality, 
                app.author_time) for app in self.pools[i][:per_pool[i]]])

        return [app.author_id for app in success] 

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
