from math import tanh

class Application:

    """
    A grant application.

    Attributes:
    - author_id : the id of the grant author
    - author_time : amount of time invested by the author
    - author_quality : research_quality of authoring academic
    - grant_quality : the quality of the grant, used for ranking
    """

    def __init__(self, author, params, rng):
        self.author_id = author.id
        self.author_time = author.time_grant
        self.author_quality = author.research_quality
        self.grant_quality = self.calculate_grant_quality(author, params, rng)


    def __cmp__(self, other):
        return cmp(other.grant_quality, self.grant_quality)


    def calculate_grant_quality(self, author, params, rng):

        """
        Calculate quality of grant.

        Three components:
        - time invested in grant writing
        - research output to date
        - (optionally) applicants research quality
        - random noise
        """

        if author.time_grant <= 0.0:
            print "Postdoc?"

        quality = params['weight_grant'] * \
                tanh(params['grant_slope'] * author.time_grant) 

        quality += (1 - params['weight_grant']) * \
                tanh(params['research_slope'] * author.research_sum) 
   
        if params['rq_counts']:
            quality += author.research_quality

        noise = rng.normalvariate(0.0, params['grant_noise'])

        quality *= (1.0 + noise)

        return quality

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################


