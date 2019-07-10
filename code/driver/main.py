# coding=utf-8
import sys
import os
import arguments
import translate
import subprocess
import re
import utils
from planner import encoder
from planner import modifier
from planner import search

val_path = '/bin/validate'

def main(BASE_DIR):

    ## Parse planner args
    args = arguments.parse_args()

    # print args.domain
    ## Run PDDL translator (from TFD)
    prb = args.problem
    if args.domain:
        domain = args.domain
        task = translate.pddl.open(prb, domain)
    else:
        task = translate.pddl.open(prb)
        domain = utils.getDomainName(prb)


    ## Compute initial horizon estimate
    ## querying a satisficing planner
    ## here: ENHSP by Enrico Scala

    hplan = BASE_DIR+'/enhsp/enhsp'
    val = BASE_DIR+'/bin/validate'

    print('Start horizon computation...')

    try:
        out = subprocess.check_output([hplan, '-o', domain, '-f', prb, '-s', 'gbfs', '-ties', 'smaller_g', '-h', 'haddabs'])

    except subprocess.CalledProcessError as e:
        sys.exit()


    ## Extract plan length from output of ENHSP
    match = re.search('Plan-Length:(\d+)', out)
    if match:
        initial_horizon = int(match.group(1))
        print('Intial horizon: {}'.format(initial_horizon))

    else:
        ## Computing horizon with GBFS failed for some reason
        print('Could not determine initial horizon with GBFS...')

        ## Print output of ENHSP for diagnosis and exit
        print(out)
        sys.exit()

    ## Compose encoder and search
    ## according to user flags

    e = encoder.EncoderSAT(task, modifier.LinearModifier(), initial_horizon).encode()
    s = search.LinearSearch(e, initial_horizon)
    plan = s.do_search()

    ## VALidate and print plan -> Controllare il codice di validate, non ho idea di che faccia, probabilemente non è pensato per come dobbiamo risolverla
    try:
        if plan.validate(val, domain, prb):
            print('\nPlan found!')
            print('\nCost: {}\n'.format(plan.cost))
            for k,v in plan.plan.items():
                print('Step {}: {}'.format(k, v))
        else:
            print('Plan not valid, exiting now...')
            sys.exit()
    except:
        print('Could not validate plan, exiting now...')
        sys.exit()

if __name__ == '__main__':
    main("/home/federico/Scrivania/finalProject/code")
