"A grant application."
mutable struct Application
    "the id of the grant author"
	author_id :: Int
    "amount of time invested by the author"
	author_time :: Float64
    "research_quality of authoring academic"
	author_quality :: Float64
    "the quality of the grant, used for ranking"
	grant_quality :: Float64
end

Application(author, params) =
	Application(author.id, 
		author.time_grant, 
		author.research_quality, 
		calculate_grant_quality(author, params))
		
# no idea where this is used, but assuming it is for sorting
# using a closure at point of use seems more transparent
#    def __cmp__(self, other):
#        return cmp(other.grant_quality, self.grant_quality)


"""
Calculate quality of grant.

Three components:
- time invested in grant writing
- research output to date
- (optionally) applicants research quality
- random noise
"""
function calculate_grant_quality(author, params)
    if author.time_grant <= 0.0
        println("Postdoc?")
    end

    quality = params.weight_grant * 
            tanh(params.grant_slope * author.time_grant) 

    quality += (1 - params.weight_grant * 
            tanh(params.research_slope * author.research_sum) 

    if params.rq_counts
        quality += author.research_quality
	end
	
    noise = rand(Normal(0.0, params.grant_noise))

    quality *= (1.0 + noise)

    quality
end



