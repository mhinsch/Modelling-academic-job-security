import Utils
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd
from random import Random
from Simulation import Simulation
import pylab, numpy, math, csv

def run_sim(params, exp_prefix, rng, sim=True):

    """
    Run multiple initialisations of a single set of experimental conditions.

    If sim=False, output is estimated, rather than simulated.  Currently, this
    is just used for evaluating the "fixed time investment" heuristic.
    """

    sum_roi_values = []
    roi_values = []
    total_r_values = []
    mean_tg_values = []
    corr_rq_held_values = []




    # for each initialisation
    for run in range(params['runs']):
        params['seed'] = rng.randint(0,99999999)
        params['prefix'] = exp_prefix + "%d/" % params['seed']
        print "   run #%d" % run

        # run experiment; either simulation or estimation
        exp = Simulation(params)
        if sim:
            exp.run()
        else:
            exp.test_flat(params['fixed_time'])

        roi_values.append(exp.calc_roi(1)[2])
        total_r_values.append(exp.calc_mean_total_output())
        mean_tg_values.append(exp.calc_mean_time_grant())
        corr_rq_held_values.append(exp.calc_mean_corr_rq_held())
        sum_roi_values.append(exp.calc_roi_sum)
        #roi_SEs.append(numpy.std(sum_roi_values))

        if params['write_output']:
            Utils.create_dir(params['prefix'])
            exp.write_output()
            dataFile.write(str(run + 1) + "," + str(params['use_postdocs']) + "," + str(params['growing_pop']) + "," + str(params['pdr_rq_counts']) + ","
                + str(params['mentored_pdrs']) + "," + str(exp.roi_sum[params['iterations'] - 1]) + "," + str(exp.roi_sum_pdr[params['iterations'] - 1]) +
                "," + str(total_r_values[run]) + "," + str(exp.mean_r[params['iterations'] - 1]) + "," + str(exp.mean_r_old_academic[params['iterations'] - 1]) + "," + str(exp.mean_r_postdoc[params['iterations'] - 1]) + ","
                + str(exp.mean_r_former_pdr[params['iterations'] - 1]) + ","  + str(mean_tg_values[run]) + "," + str(params['learning_type']) + "," + str(params['postdoc_chance']) + "," + str(exp.redundancies_total) + "\n")


    # calculate and write summary statistics
    summ_data = [roi_values, total_r_values,
            mean_tg_values, corr_rq_held_values]



    summ_stats = [
            pylab.mean(roi_values), pylab.std(roi_values),
            pylab.mean(total_r_values), pylab.std(total_r_values),
            pylab.mean(mean_tg_values), pylab.std(mean_tg_values),
            pylab.mean(corr_rq_held_values), pylab.std(corr_rq_held_values)]

    if params['write_output']:
        Utils.write_data_2d(summ_data, exp_prefix + 'summ_data.csv')
        Utils.write_data(summ_stats, exp_prefix + 'summ_stats.csv')

    return pylab.mean(roi_values), pylab.std(roi_values), total_r_values[-1]


def run_WCSS_sims(params, base_prefix, seed_rng):

    """
    Run basic simulations associated with the WCSS paper.
    """
    params['runs'] = 10

    # run THERMOSTAT model
    params['prefix'] = base_prefix + "thermostat/"
    params['learning_type'] = 'thermostat'
    print 'thermostat'
    run_sim(params, params['prefix'], seed_rng)

    # run MEMORY A model ("bad" parameters)
    params['prefix'] = base_prefix + "memory_A/"
    params['learning_type'] = 'memory'
    params['prob_reentry'] = 0.05
    params['run_length'] = 5
    print 'memory A'
    run_sim(params, params['prefix'], seed_rng)

    # run MEMORY B model ("good" parameters)
    params['prefix'] = base_prefix + "memory_B/"
    params['learning_type'] = 'memory'
    params['prob_reentry'] = 0.02
    params['run_length'] = 3
    print 'memory B'
    run_sim(params, params['prefix'], seed_rng)

    # run FIXED model
    params['prefix'] = base_prefix + "fixed/"
    print 'fixed'
    run_sim(params, params['prefix'], seed_rng, sim=False)

def run_Alife_sims(params, base_prefix, seed_rng):
    """
    Run sims for Alife XV paper.
    """
    params['runs'] = 50

    #run MEMORY, growing pop model
    params['prefix'] = base_prefix + "memory_growingPop"
    params['learning_type'] = 'memory'
    params['use_postdocs'] = 0
    params['growing_pop'] = 1
    params['pdr_rq_counts'] = 0
    params['mentored_pdrs'] = 0
    print 'Growing population, no postdocs'
    run_sim(params, params['prefix'], seed_rng)


    #run MEMORY version, postdocs, no RQ/mentors
    params['prefix'] = base_prefix + "memory_noRQnoM"
    params['learning_type'] = 'memory'
    params['use_postdocs'] = 1
    params['growing_pop'] = 0
    params['pdr_rq_counts'] = 0
    params['mentored_pdrs'] = 0
    print 'Memory, postdocs, no RQ or mentors'
    run_sim(params, params['prefix'], seed_rng)

    #run MEMORY version, postdocs, RQ, no mentors
    params['prefix'] = base_prefix + "memory_RQnoM"
    params['learning_type'] = 'memory'
    params['use_postdocs'] = 1
    params['growing_pop'] = 0
    params['pdr_rq_counts'] = 1
    params['mentored_pdrs'] = 0
    print 'Memory, postdocs, RQ no mentors'
    run_sim(params, params['prefix'], seed_rng)

    #run MEMORY version, postdocs, RQ and mentors
    params['prefix'] = base_prefix + "memory_RQM"
    params['learning_type'] = 'memory'
    params['use_postdocs'] = 1
    params['growing_pop'] = 0
    params['pdr_rq_counts'] = 1
    params['mentored_pdrs'] = 1
    print 'Memory, postdocs, RQ and mentors'
    run_sim(params, params['prefix'], seed_rng)

    #run MEMORY version, postdocs, no RQ, with mentors
    params['prefix'] = base_prefix + "memory_noRQM"
    params['learning_type'] = 'memory'
    params['use_postdocs'] = 1
    params['growing_pop'] = 0
    params['pdr_rq_counts'] = 0
    params['mentored_pdrs'] = 1
    print 'Memory, postdocs, no RQ, with mentors'
    run_sim(params, params['prefix'], seed_rng)

def run_Alife_thermo(params, base_prefix, seed_rng):
    """
    Run sims for Alife XV paper with thermostat.
    """
    params['runs'] = 25

    #run thermo, growing pop model
    params['prefix'] = base_prefix + "thermo_growingPop"
    params['learning_type'] = 'thermostat'
    params['use_postdocs'] = 0
    params['growing_pop'] = 1
    params['pdr_rq_counts'] = 0
    params['mentored_pdrs'] = 0
    print 'Growing population, no postdocs'
    run_sim(params, params['prefix'], seed_rng)


    #run thermo version, postdocs, no RQ/mentors
    params['prefix'] = base_prefix + "thermo_noRQnoM"
    params['learning_type'] = 'thermostat'
    params['use_postdocs'] = 1
    params['growing_pop'] = 0
    params['pdr_rq_counts'] = 0
    params['mentored_pdrs'] = 0
    print 'Thermo, postdocs, no RQ or mentors'
    run_sim(params, params['prefix'], seed_rng)

    #run thermo version, postdocs, RQ, no mentors
    params['prefix'] = base_prefix + "thermo_RQnoM"
    params['learning_type'] = 'thermostat'
    params['use_postdocs'] = 1
    params['growing_pop'] = 0
    params['pdr_rq_counts'] = 1
    params['mentored_pdrs'] = 0
    print 'Thermo, postdocs, RQ no mentors'
    run_sim(params, params['prefix'], seed_rng)

    #run thermo version, postdocs, RQ and mentors
    params['prefix'] = base_prefix + "thermo_RQM"
    params['learning_type'] = 'thermostat'
    params['use_postdocs'] = 1
    params['growing_pop'] = 0
    params['pdr_rq_counts'] = 1
    params['mentored_pdrs'] = 1
    print 'Thermo, postdocs, RQ and mentors'
    run_sim(params, params['prefix'], seed_rng)

    #run thermo version, postdocs, no RQ, with mentors
    params['prefix'] = base_prefix + "thermo_noRQM"
    params['learning_type'] = 'thermostat'
    params['use_postdocs'] = 1
    params['growing_pop'] = 0
    params['pdr_rq_counts'] = 0
    params['mentored_pdrs'] = 1
    print 'Thermo, postdocs, no RQ, with mentors'
    run_sim(params, params['prefix'], seed_rng)

def run_Alife_sweep1(params, base_prefix, seed_rng):
    """
    Run sweep of promotion chance values.
    """

    params['runs'] = 50

    #run MEMORY version, promotion chance 15 percent
    params['prefix'] = base_prefix + "memory_chance15_"
    params['learning_type'] = 'memory'
    params['use_postdocs'] = 1
    params['growing_pop'] = 0
    params['pdr_rq_counts'] = 1
    params['mentored_pdrs'] = 0
    params['postdoc_chance'] = 0.15
    print 'Memory, postdocs promo 15 percent'
    run_sim(params, params['prefix'], seed_rng)

    #run MEMORY version, promotion chance 25 percent
    params['prefix'] = base_prefix + "memory_chance25_"
    params['learning_type'] = 'memory'
    params['use_postdocs'] = 1
    params['growing_pop'] = 0
    params['pdr_rq_counts'] = 1
    params['mentored_pdrs'] = 0
    params['postdoc_chance'] = 0.25
    print 'Memory, postdocs promo 25 percent'
    run_sim(params, params['prefix'], seed_rng)

    #run MEMORY version, promotion chance 50 percent
    params['prefix'] = base_prefix + "memory_chance50_"
    params['learning_type'] = 'memory'
    params['use_postdocs'] = 1
    params['growing_pop'] = 0
    params['pdr_rq_counts'] = 1
    params['mentored_pdrs'] = 0
    params['postdoc_chance'] = 0.50
    print 'Memory, postdocs promo 50 percent'
    run_sim(params, params['prefix'], seed_rng)

    #run MEMORY version, promotion chance 75 percent
    params['prefix'] = base_prefix + "memory_chance75_"
    params['learning_type'] = 'memory'
    params['use_postdocs'] = 1
    params['growing_pop'] = 0
    params['pdr_rq_counts'] = 1
    params['mentored_pdrs'] = 0
    params['postdoc_chance'] = 0.75
    print 'Memory, postdocs promo 50 percent'
    run_sim(params, params['prefix'], seed_rng)

    #run MEMORY version, promotion chance 100 percent
    params['prefix'] = base_prefix + "memory_chance100_"
    params['learning_type'] = 'memory'
    params['use_postdocs'] = 1
    params['growing_pop'] = 0
    params['pdr_rq_counts'] = 1
    params['mentored_pdrs'] = 0
    params['postdoc_chance'] = 1.0
    print 'Memory, postdocs promo 100 percent'
    run_sim(params, params['prefix'], seed_rng)



def init_params():

    params = {}

    # simulation parameters
    params['write_output'] = False    # whether or not to write output on individual runs
    params['prefix'] = '/Users/u0030612/Documents/results/test/Alife/mem_scenarios_50r_highaccept/'    # where to write output
    params['runs'] = 1    # number of runs per parameter combination
    params['random_seed'] = True    # whether to use random seed (or fixed)
    params['use_postdocs'] = 1 # whether to include postdocs in sim
    params['growing_pop'] = 0 # use growing population, no postdocs scenario
    params['pdr_rq_counts'] = 1 # does postdoc RQ count in promotions
    params['mentored_pdrs'] = 1 # do postdocs gain RQ due to mentoring
    params['seed'] = 1234    # seed to use (if random_seed==False)
    params['pop_size'] = 100    # initial number of academic agents
    params['iterations'] = 100    # number of iterations to simulate
    params['init_time'] = 0.5    # upper bound on initial academic time_grant values
    params['fixed_time'] = 0.1    # ie, for legislated time alloc
    params['postdoc_chance'] = 0.15 # chance for PDR promotion
    params['mentoring_bonus'] = 0.20 # bonus to RQ for promoted postdocs (from being mentored/maturing)
    params['newb_time'] = 0.4 # time spent on being a new postdoc/academic
    params['jobhunt_time'] = 0.3 # time spent on job-hunting in final 2 semesters of contract
    params['career_end'] = 60 #semesters before agent has to retire
    params['use_retirement'] = True

    # grant parameters
    params['weight_grant'] = 1.0    # weighting on grant quality, rather than track record
    params['grant_slope'] = 2.0    # slope constant in tanh function
    params['research_slope'] = 2.0    # slope constant in tanh function
    params['grant_noise'] = 0.1    # std dev of gaussian noise on grant quality
    params['rq_counts'] = True    # is research_quality involved in grant_quality?
    params['grant_bonus'] = 1.5    # G: bonus to research output arising from grants
    params['grant_proportion'] = 0.3    # P: proportion of population who can obtain grants
    params['grant_pools'] = 1    # number of pools for grant evaluation
    params['manager_penalty'] = 0.00 # management time deducted from successful grant applicants
    params['limited_funding'] = True #are grants limited?
    params['starting_grant_fund'] = 30 #starting funds available, 1 unit equals 1 funded project
    params['yearly_increase'] = 0.02 #percentage increase per timestep in limited funding case

    # self learning parameters
    params['learning_type'] = 'memory'   # options 'thermostat', 'memory'
    params['self_update_width'] = 0.1    # "learning rate"
    params['self_update_width_fixed'] = True    # Are learning steps of fixed width? (or random)
    params['memory_size'] = 12    # number of memory steps to store (NB: this is NOT window length!)
    params['run_length'] = 12    # W: number of memory steps to consider (THIS is window length!)
    params['prob_reentry'] = 0.02    # E: probability of re-entering population after dropping out
    params['reentry_range'] = 0.2    # upper bound on re-entry time_grant values

    return params


if __name__ == '__main__':

    params = init_params()
    Utils.create_dir(params['prefix'])
    seed_rng = Random(params['seed'])

    # WCSS SIMULATIONS
    #run_WCSS_sims(params, params['prefix'], seed_rng)

    # SINGLE TEST RUN
    dataFile = open(params['prefix'] + "roi_test.csv",'w')
    dataFile.write("Run Number" + "," + "Use_PDRs" + "," + "Growing_Pop" + "," + "RQ_counts" + "," + "Mentored_PDRs" + "," +
        "ROI" + "," + "ROI no PDRs" + "," + "Total RO" + "," + "Mean RO Old Farts" + "," + "Mean RO PDR" + "," + "Mean RO FPDR" + "," +
        "Mean TG" + "," + "Learning Type" + "," + "Promo Chance" + "\n")
    run_sim(params, params['prefix'], seed_rng, sim=True)
    dataFile.close()

    #Alife XV simulations, thermo
    # dataFile = open(params['prefix'] + "roi_test.csv",'w')
    # dataFile.write("Run_Number" + "," + "Use_PDRs" + "," + "Growing_Pop" + "," + "RQ_counts" + "," + "Mentored_PDRs" + "," +
    #    "ROI" + "," + "ROI_no_PDRs" + "," + "Total_RO" + "," + "Mean_RO_all" + "," + "Mean_RO_Old_Farts" + "," + "Mean_RO_PDR" + "," + "Mean_RO_FPDR" + "," +
    #    "Mean_TG" + "," + "Learning_Type" + "," + "Promo_Chance" + "," + "Total_Sacked" + "\n")
    # root_dir = params['prefix']
    # run_Alife_thermo(params, params['prefix'], seed_rng)
    # dataFile.close()

    #Alife XV simulations, memory
#    dataFile = open(params['prefix'] + "roi_test.csv",'w')
#    dataFile.write("Run_Number" + "," + "Use_PDRs" + "," + "Growing_Pop" + "," + "RQ_counts" + "," + "Mentored_PDRs" + "," +
#       "ROI" + "," + "ROI_no_PDRs" + "," + "Total_RO" + "," + "Mean_RO_all" + "," + "Mean_RO_Old_Farts" + "," + "Mean_RO_PDR" + "," + "Mean_RO_FPDR" + "," +
#       "Mean_TG" + "," + "Learning_Type" + "," + "Promo_Chance" + "," + "Total_Sacked" + "\n")
#    root_dir = params['prefix']
#    run_Alife_sims(params, params['prefix'], seed_rng)
#    dataFile.close()
#    plt.clf()
#    fields = ['Use_PDRs', 'Growing_Pop', 'RQ_counts', 'Mentored_PDRs', 'Total_RO', 'Mean_RO_all', 'ROI_no_PDRs', 'Total_Sacked']
#    df = pd.read_csv(root_dir + 'roi_test.csv', usecols=fields)
#    means = df.groupby(['Use_PDRs', 'Growing_Pop', 'RQ_counts', 'Mentored_PDRs']).mean()
#    deviation = df.groupby(['Use_PDRs', 'Growing_Pop', 'RQ_counts', 'Mentored_PDRs']).std()
#    print(means)
#    print(deviation)
#    scenarioList = ['Growing Pop', 'NoRQnoM', 'noRQM', 'RQnoM', 'RQM']
#    fig = means['Total_RO'].plot(kind='bar', title = 'Output in Postdoc Scenarios', yerr=deviation.Total_RO, color=['Orange', 'Salmon', 'Violet', 'Chocolate', 'LightSteelBlue'], alpha=0.5, rot=0)
#    fig.set_xlabel("Scenarios",fontsize=12)
#    fig.set_ylabel("Research Output",fontsize=12)
#    fig.set_xticklabels(scenarioList)
#    fig2 = fig.get_figure()
#    fig2.savefig(root_dir + 'memRunSet_totalRO.pdf')
#    fig2.savefig(root_dir + 'memRunSet_totalRO.png')
#
#    plt.clf()
#    fig_r = means['Mean_RO_all'].plot(kind='bar', title = 'Mean Output in Postdoc Scenarios', yerr=deviation.Mean_RO_all, color=['Orange', 'Salmon', 'Violet', 'Chocolate', 'LightSteelBlue'], alpha=0.5, rot=0)
#    fig_r.set_xlabel("Scenarios",fontsize=12)
#    fig_r.set_ylabel("Mean Research Output",fontsize=12)
#    fig_r.set_xticklabels(scenarioList)
#    fig2_r = fig.get_figure()
#    fig2_r.savefig(root_dir + 'memRunSet_meanRO.pdf')
#    fig2_r.savefig(root_dir + 'memRunSet_meanRO.png')
#
#    plt.clf()
#    fig_roi = means['ROI_no_PDRs'].plot(kind='bar', title='ROI in Postdoc Scenarios', yerr=deviation.ROI_no_PDRs, facecolor='g', alpha=0.5, rot=0)
#    fig_roi.set_xlabel("Scenarios", fontsize=12)
#    fig_roi.set_ylabel("Return on Investment", fontsize=12)
#    fig_roi.set_xticklabels(scenarioList)
#    fig2_roi = fig.get_figure()
#    fig2_roi.savefig(root_dir + 'memRunSet_ROI.pdf')
#    fig2_roi.savefig(root_dir + 'memRunSet_ROI.png')
#
#    plt.clf()
#    scenarioListR = ['NoRQnoM', 'noRQM', 'RQnoM', 'RQM']
#    df_R = df[df.Growing_Pop != 1]
#    means_R = df_R.groupby(['Use_PDRs', 'RQ_counts', 'Mentored_PDRs']).mean()
#    deviation_R = df_R.groupby(['Use_PDRs','RQ_counts', 'Mentored_PDRs']).std()
#    fig_sacked = means_R['Total_Sacked'].plot(kind='bar', title='Redundancies in Postdoc Scenarios', yerr=deviation_R.Total_Sacked, facecolor='r', alpha=0.5, rot=0)
#    fig_sacked.set_xlabel("Scenarios", fontsize=12)
#    fig_sacked.set_ylabel("Redundancies", fontsize=12)
#    fig_sacked.set_xticklabels(scenarioListR)
#    fig2_sacked = fig.get_figure()
#    fig2_sacked.savefig(root_dir + 'memRunSet_sacked.pdf')
#    fig2_sacked.savefig(root_dir + 'memRunSet_sacked.png')

    #Alife XV promo chance sweep
    # dataFile = open(params['prefix'] + "roi_test.csv",'w')
    # dataFile.write("Run_Number" + "," + "Use_PDRs" + "," + "Growing_Pop" + "," + "RQ_counts" + "," + "Mentored_PDRs" + "," +
    #    "ROI" + "," + "ROI_no_PDRs" + "," + "Total_RO" + "," + "Mean_RO_all" + "," + "Mean_RO_Old_Farts" + "," + "Mean_RO_PDR" + "," + "Mean_RO_FPDR" + "," +
    #    "Mean_TG" + "," + "Learning_Type" + "," + "Promo_Chance" + "," + "Total_Sacked" + "\n")
    # root_dir = params['prefix']
    # run_Alife_sweep1(params, params['prefix'], seed_rng)
    # dataFile.close()
    # plt.clf()
    # promoChanceList = [15, 25, 50, 75, 100]
    # fields = ['Promo_Chance', 'Total_RO', 'Mean_RO_all', 'ROI_no_PDRs', 'Total_Sacked']
    # df = pd.read_csv(root_dir + 'roi_test.csv', usecols=fields)
    # means = df.groupby('Promo_Chance').mean()
    # deviation = df.groupby('Promo_Chance').std()
    # print(means)
    # print(deviation)
    # fig = means['Total_RO'].plot(kind='bar', title = 'Promotion Chance vs Output', yerr=deviation.Total_RO, facecolor='c', alpha=0.5, rot=0)
    # fig.set_xlabel("Promotion Chance",fontsize=12)
    # fig.set_ylabel("Research Output",fontsize=12)
    # fig.set_xticklabels(promoChanceList)
    # fig2 = fig.get_figure()
    # fig2.savefig(root_dir + 'promoRunSet_totalRO.pdf')
    # fig2.savefig(root_dir + 'promoRunSet_totalRO.png')

    # plt.clf()
    # fig_r = means['Mean_RO_all'].plot(kind='bar', title = 'Promotion Chance vs Mean Output', yerr=deviation.Mean_RO_all, facecolor='m', alpha=0.5, rot=0)
    # fig_r.set_xlabel("Promotion Chance",fontsize=12)
    # fig_r.set_ylabel("Mean Research Output",fontsize=12)
    # fig_r.set_xticklabels(promoChanceList)
    # fig2_r = fig.get_figure()
    # fig2_r.savefig(root_dir + 'promoRunSet_meanRO.pdf')
    # fig2_r.savefig(root_dir + 'promoRunSet_meanRO.png')

    # plt.clf()
    # fig_roi = means['ROI_no_PDRs'].plot(kind='bar', title='Promotion Chance vs ROI', yerr=deviation.ROI_no_PDRs, facecolor='g', alpha=0.5, rot=0)
    # fig_roi.set_xlabel("Promotion Chance", fontsize=12)
    # fig_roi.set_ylabel("Return on Investment", fontsize=12)
    # fig_roi.set_xticklabels(promoChanceList)
    # fig2_roi = fig.get_figure()
    # fig2_roi.savefig(root_dir + 'promoRunSet_ROI.pdf')
    # fig2_roi.savefig(root_dir + 'promoRunSet_ROI.png')

    # plt.clf()
    # df_R = df[df.Promo_Chance != 1]
    # means_R = df_R.groupby(['Promo_Chance']).mean()
    # deviation_R = df_R.groupby(['Promo_Chance']).std()
    # fig_sacked = means_R['Total_Sacked'].plot(kind='bar', title='Redundancies vs Promotion Chance', yerr=deviation_R.Total_Sacked, facecolor='r', alpha=0.5, rot=0)
    # fig_sacked.set_xlabel("Promotion Chance", fontsize=12)
    # fig_sacked.set_ylabel("Redundancies", fontsize=12)
    # fig_sacked.set_xticklabels(promoChanceList)
    # fig2_sacked = fig.get_figure()
    # fig2_sacked.savefig(root_dir + 'promoRunSet_sacked.pdf')
    # fig2_sacked.savefig(root_dir + 'promoRunSet_sacked.png')

        # #runs for sensitivity analysis using GEM-SA
    # researchMeans = []
    # researchSEs = []

    # params['write_output'] = False

    # sim_runs = 20
    # gemFile = open(params['prefix'] + "GEMSA data new.txt",'w')
    # meansFile = open(params['prefix'] + "GEMSA means new.txt", 'w')
    # outFile = open(params['prefix'] + "GEMSA outputs new.txt", 'w')

    # postdocChanceList = [ 0.15, 0.25, 0.50, 0.75, 1.0 ]
    # mentoringBonusList = [ 0.30, 0.40, 0.50, 0.60, 0.70 ]
    # newbTimeList = [ 0.1, 0.3, 0.5, 0.7 ]
    # jobhuntTimeList = [ 0.1, 0.3, 0.5, 0.7 ]

    # dataFile = open(params['prefix'] + "roi_test.csv",'w')
    # dataFile.write("Run_Number" + "," + "Job_Stress" + "," + "Use_PDRs" + "," + "Growing_Pop" + "," + "RQ_counts" + "," + "Mentored_PDRs" + "," +
    #    "ROI" + "," + "ROI_no_PDRs" + "," + "Total_RO" + "," + "Mean_RO_all" + "," + "Mean_RO_Old_Farts" + "," + "Mean_RO_PDR" + "," + "Mean_RO_FPDR" + "," +
    #    "Mean_TG" + "," + "Learning_Type" + "," + "Promo_Chance" + "," + "Total_Sacked" + "\n")
    # root_dir = params['prefix']

    # for variableChance in postdocChanceList:
    #    for variableMentoring in mentoringBonusList:
    #        for variableNewb in newbTimeList:
    #            for variableJobHunting in jobhuntTimeList:
    #                params['postdoc_chance'] = variableChance
    #                params['mentoring_bonus'] = variableMentoring
    #                params['newb_time'] = variableNewb
    #                params['jobhunt_time'] = variableJobHunting
    #                print "Trying postdoc chance: ", variableChance
    #                print "Trying mentoring bonus: ", variableMentoring
    #                print "Trying newb time: ", variableNewb
    #                print "Trying jobhunting time: ", variableJobHunting
    #                researchList = []
    #                researchSum = 0.0
    #                meansFile.write(str(variableChance) + "\t" + str(variableMentoring) + "\t" + str(variableNewb) + "\t" + str(variableJobHunting) + "\n")
    #                for i in range ( 0, sim_runs ):
    #                    print i,
    #                    researchOut = run_sim(params, root_dir, seed_rng, sim=True)[2]
    #                    researchList.append(researchOut)
    #                    researchSum += researchOut
    #                    print researchOut
    #                    gemFile.write(str(variableChance) + "\t" + str(variableMentoring) + "\t" + str(variableNewb) + "\t" + str(variableJobHunting) + "\t" + str(researchOut) + "\n")
    #                researchMeans.append(pylab.mean(researchList))
    #                outFile.write(str(researchSum/sim_runs) + "\n")
    #                researchSEs.append(pylab.std(researchList) / math.sqrt(sim_runs))

    # dataFile.close()
    # gemFile.close()
    # meansFile.close()
    # outFile.close()

   # #runs for sensitivity analysis using GEM-SA -- NO MENTORING
   #  researchMeans = []
   #  researchSEs = []

   #  params['write_output'] = False
   #  params['mentored_pdrs'] = 0

   #  sim_runs = 60
   #  gemFile = open(params['prefix'] + "GEMSA data new.txt",'w')
   #  meansFile = open(params['prefix'] + "GEMSA means new.txt", 'w')
   #  outFile = open(params['prefix'] + "GEMSA outputs new.txt", 'w')

   #  postdocChanceList = [ 0.15, 0.25, 0.50, 0.75, 1.0 ]
   #  newbTimeList = [ 0.1, 0.3, 0.5, 0.7, 0.9 ]
   #  jobhuntTimeList = [ 0.1, 0.3, 0.5, 0.7, 0.9 ]

   #  dataFile = open(params['prefix'] + "roi_test.csv",'w')
   #  dataFile.write("Run_Number" + "," + "Job_Stress" + "," + "Use_PDRs" + "," + "Growing_Pop" + "," + "RQ_counts" + "," + "Mentored_PDRs" + "," +
   #     "ROI" + "," + "ROI_no_PDRs" + "," + "Total_RO" + "," + "Mean_RO_all" + "," + "Mean_RO_Old_Farts" + "," + "Mean_RO_PDR" + "," + "Mean_RO_FPDR" + "," +
   #     "Mean_TG" + "," + "Learning_Type" + "," + "Promo_Chance" + "," + "Total_Sacked" + "\n")
   #  root_dir = params['prefix']

   #  for variableChance in postdocChanceList:
   #      for variableNewb in newbTimeList:
   #          for variableJobHunting in jobhuntTimeList:
   #             params['postdoc_chance'] = variableChance
   #             params['newb_time'] = variableNewb
   #             params['jobhunt_time'] = variableJobHunting
   #             print "Trying postdoc chance: ", variableChance
   #             print "Trying newb time: ", variableNewb
   #             print "Trying jobhunting time: ", variableJobHunting
   #             researchList = []
   #             researchSum = 0.0
   #             meansFile.write(str(variableChance) + "\t" + str(variableNewb) + "\t" + str(variableJobHunting) + "\n")
   #             for i in range ( 0, sim_runs ):
   #                 print i,
   #                 researchOut = run_sim(params, root_dir, seed_rng, sim=True)[2]
   #                 researchList.append(researchOut)
   #                 researchSum += researchOut
   #                 print researchOut
   #                 gemFile.write(str(variableChance) + "\t" + str(variableNewb) + "\t" + str(variableJobHunting) + "\t" + str(researchOut) + "\n")
   #             researchMeans.append(pylab.mean(researchList))
   #             outFile.write(str(researchSum/sim_runs) + "\n")
   #             researchSEs.append(pylab.std(researchList) / math.sqrt(sim_runs))

   #  dataFile.close()
   #  gemFile.close()
   #  meansFile.close()
   #  outFile.close()

    #runs for sensitivity analysis using GEM-SA -- INCLUDING MENTORING SWITCH
#    researchMeans = []
#    researchSEs = []
#
#    params['write_output'] = False
#
#    sim_runs = 2 #20
#    gemFile = open(params['prefix'] + "GEMSA data new.txt",'w')
#    meansFile = open(params['prefix'] + "GEMSA means new.txt", 'w')
#    outFile = open(params['prefix'] + "GEMSA outputs new.txt", 'w')
#
#    postdocChanceList = [ 0.15, 0.25, 0.50, 0.75, 1.0 ]
#    mentoringBonusList = [ 0.30, 0.40, 0.50, 0.60, 0.70 ]
#    newbTimeList = [ 0.1, 0.3, 0.5, 0.7 ]
#    jobhuntTimeList = [ 0.1, 0.3, 0.5, 0.7 ]

    #dataFile = open(params['prefix'] + "roi_test.csv",'w')
    #dataFile.write("Run_Number" + "," + "Job_Stress" + "," + "Use_PDRs" + "," + "Growing_Pop" + "," + "RQ_counts" + "," + "Mentored_PDRs" + "," +
    #    "ROI" + "," + "ROI_no_PDRs" + "," + "Total_RO" + "," + "Mean_RO_all" + "," + "Mean_RO_Old_Farts" + "," + "Mean_RO_PDR" + "," + "Mean_RO_FPDR" + "," +
    #    "Mean_TG" + "," + "Learning_Type" + "," + "Promo_Chance" + "," + "Total_Sacked" + "\n")
#    root_dir = params['prefix']
#
#    for variableChance in postdocChanceList:
#        for variableMentoring in mentoringBonusList:
#            for variableNewb in newbTimeList:
#                for variableJobHunting in jobhuntTimeList:
#                    params['postdoc_chance'] = variableChance
#                    params['mentoring_bonus'] = variableMentoring
#                    params['newb_time'] = variableNewb
#                    params['jobhunt_time'] = variableJobHunting
#                    print "Trying postdoc chance: ", variableChance
#                    print "Trying mentoring bonus: ", variableMentoring
#                    print "Trying newb time: ", variableNewb
#                    print "Trying jobhunting time: ", variableJobHunting
#                    researchList = []
#                    researchSum = 0.0
#                    meansFile.write(str(variableChance) + "\t" + str(variableMentoring) + "\t" + str(variableNewb) + "\t" + str(variableJobHunting) + "\n")
#                    for i in range ( 0, sim_runs ):
#                        print i,
#                        researchOut = run_sim(params, root_dir, seed_rng, sim=True)[2]
#                        researchList.append(researchOut)
#                        researchSum += researchOut
#                        print researchOut
#                        gemFile.write(str(variableChance) + "\t" + str(variableMentoring) + "\t" + str(variableNewb) + "\t" + str(variableJobHunting) + "\t" + str(researchOut) + "\n")
#                    researchMeans.append(pylab.mean(researchList))
#                    outFile.write(str(researchSum/sim_runs) + "\n")
#                    researchSEs.append(pylab.std(researchList) / math.sqrt(sim_runs))
#
#    #dataFile.close()
#    gemFile.close()
#    meansFile.close()
#    outFile.close()


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

