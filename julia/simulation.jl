import pylab
from Population import Population
import Utils

class Simulation:

    """
    A single experimental run, together with data and derived statistics.
    """

    def __init__(self, params):

        self.params = params
        self.init_stats()
        self.sim = Population(params)
        self.colours = Utils.create_colour_dict(len(self.sim.agents))
        self.plot_colours = Utils.create_plot_colour_dict()
        self.endgame = int(self.params['iterations'] * 0.9)

    def init_stats(self):

        "Initialise data structures for storing data."""

        self.all_stats = []     # for endgame iterations
        self.final_stats = []   # for final iteration
        self.alloc = []
        self.accept = []

        self.all_tg = []
        self.tg_g = []
        self.tg_fg = []
        self.tg_ng = []
        
        self.all_r = []
        self.r_g = []
        self.r_fg = []
        self.r_ng = []
        self.r_pdr = []
        self.r_former_pdr = []
        self.r_old_academic = []

        self.all_rq = []
        self.rq_g = []
        self.rq_ng = []
        self.rq_fail = []
        self.rq_na = []
        self.rq_pdr = []
        self.rq_former_pdr = []
        self.rq_old_academic = []

        self.corr_rq_tg = []
        self.corr_rq_apply = []
        self.corr_rq_held = []

        self.pdr_total = []
        self.academic_total = []
        self.exited_total = []
        self.accepted_grants = []
        self.dynamic_roi = []
        self.roi_sum = []
        self.roi_sum_pdr = []


    def run(self):

        "Run the experiment."
        iterations = 0
        for t in xrange(self.params['iterations']):
            iterations += 1
            self.sim.int_academic_count()
            self.sim.produce_applications()
            self.sim.evaluate_applications()
            self.sim.produce_research()
            if self.params['use_postdocs'] == 1:
                self.sim.hire_postdocs(self.params)
            self.sim.update_strategies()
            if self.params['growing_pop'] == 1:
                self.sim.update_newbies()
            if self.params['use_postdocs'] == 1:
                self.sim.update_postdocs()
            if self.params['use_retirement'] == True:
                self.sim.update_careers()
            self.save_base_stats(t)
            if self.params['write_output']:
                self.save_plot_stats()
            print('Total agents: {}'.format(len(self.sim.agents)))
            self.sim.current_postdocs()
            self.accepted_grants.append(self.sim.acceptance_rate()[0])
            #print(self.accepted_grants)
            
            # self.dynamic_roi.append(self.calc_roi_dynamic(self.accepted_grants[t])[2])
            # print('Current ROI result: {}'.format(self.dynamic_roi[t]))
            self.roi_sum.append(self.calc_roi_sum(self.accepted_grants[t]))
            #print('Current ROI sum: {}'.format(self.roi_sum[t]))
            self.roi_sum_pdr.append(self.calc_roi_no_pdr(self.accepted_grants[t]))
            #print('Current ROI, no PDRs: {}'.format(self.roi_sum_pdr[t]))
            self.sim.clear_all()


    
    def calc_mean_total_output(self):

        total_r_sum = 0
        count = 0
        for snap in self.all_stats:
            for a in snap:
                total_r_sum += a[5]
            count += 1
        #assert count == 0, "Div by zero, dipshit"
        if not count == 0:   
            return total_r_sum / count
        else:
            return 0    

    def calc_mean_time_grant(self):

        mean_tg_sum = 0
        count = 0
        for snap in self.all_stats:
            for a in snap:
                mean_tg_sum += a[3]
                count += 1
        return mean_tg_sum / count


    def calc_mean_corr_rq_held(self):
        
        corr_rq_held_sum = 0
        count = 0
        for snap in self.all_stats:
            rq_list = []
            held_list = []
            for a in snap:
                rq_list.append(a[1])
                held_list.append(a[4])
            corr_rq_held_sum += pylab.corrcoef(rq_list, held_list)[0][1]
            count += 1
        return corr_rq_held_sum / count
        
    
    def calc_roi(self, funding_units):

        "Calculate estimated return on investment obtained."

        total_r = self.calc_mean_total_output()
        no_funding = self.sim.estimate_output(0.0, 0.0, 0.0, 'max')
        roi = (total_r - no_funding) / funding_units
        return total_r, no_funding, roi

    def calc_roi_dynamic(self, funding_units):

        "Calculated estimated ROI for dynamic population each timestep."

        total_r = self.calc_mean_total_output()
        no_funding = self.sim.estimate_output(0.0, 0.0, 0.0, 'max')
        roi = ((total_r - no_funding)) / funding_units
        return total_r, no_funding, roi

    def calc_roi_sum(self, funding_units):

        "Calculate ROI - amount of extra total research bought per grant."
        
        res_values = [a.research for a in self.sim.agents if not a.made_redundant]
        total_res = sum(res_values)
        total_res_nof = self.sim.estimate_output_sum()
        roi = ((total_res - total_res_nof) - funding_units) / funding_units
        if len(res_values)>= 300 and roi >= -2.5:
            print('ROI jumps here: {} {} {}'.format(roi, total_res, total_res_nof))
            #quit()
        return roi

    def calc_roi_no_pdr(self, funding_units):

        "Calculate ROI - amount of research bought by employing PDRs."

        res_values2 = [a.research for a in self.sim.agents if not a.made_redundant and a.postdoc_status == 0 and a.former_postdoc == 0]
        total_res2 = sum(res_values2)
        total_res_nof2 = self.sim.estimate_output_sum()
        roi = ((total_res2 - total_res_nof2) - funding_units) / funding_units
        return roi
        
    def calc_redundancies(self):
        #return total redundancies
        self.redundancies_total = len([a for a in self.sim.agents if a.made_redundant == True])
        
        
