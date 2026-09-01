#!/bin/bash

simulation_path=/home/bandrews/Wormhole/projects/PFC/simulation/simulate.py

# generate the config in the working directory
write_config () {
    q0=$1
    D=$2
    alpha=$3
    bi=$4
    config_name=$5

    cat > ${config_name} << EOF
alpha: ${alpha}
b: ${bi}
phi0: 0.25
phif: -0.7
phi_var: 0.004
D: ${D}
q0: ${q0}
dt: 0.001
nsteps: 2
drain: False
drain_start: 10000
drain_stop: 50000
dim: 2
nx: 200
ny: 200
dx: 0.784
dy: 0.784
log_file: "q0${q0}_D${D}_alpha${alpha}_b${bi}.log"
trajectory_file: "q0${q0}_D${D}_alpha${alpha}_b${bi}.h5"
trajectory_write_interval: 1 # in number of steps
EOF
    }

# test for writing config
# write_config 1 1 1 1 config_test.yaml

# param arrays to sweep through
declare -a q0=( 0.1 ) #1 10 )
declare -a D=( 0.1 ) #1 2 )
declare -a alpha=( 1 2 ) #2 5 10 20 )
declare -a b=( -2 -1 ) #-1 -0.67 -0.33333333 0 )

# need to generate loops such that N simultaneous jobs are executed at a time
njobs=2
job_count=0 # counter for jobs
jobs_completed=0
commands=()
for q in ${q0[@]}
do
    for d in ${D[@]}
    do
        for a in ${alpha[@]}
        do
            for bi in ${b[@]}
            do
                echo $q $d $a $bi
                ((job_count++))
                write_config $q $d $a $bi config_${job_count}.yaml
                commands+=("python ${simulation_path} config_${job_count}.yaml")
                if [ $job_count = $njobs ]
                then
                    parallel --jobs ${job_count} ::: "${commands[@]}"
                    jobs_completed=$((jobs_completed + job_count))
                    echo ${jobs_completed}
                    job_count=0
                    commands=()
                    rm config_*
                fi
            done
        done
    done
done

# have to do the final set of calculations, if the last array has fewer than njobs elements
if [ $job_count -gt 0 -a $job_count -lt $njobs ]
then
    parallel --jobs ${job_count} ::: "${commands[@]}"
    jobs_completed=$((jobs_completed + job_count))
    echo ${jobs_completed}
    rm config_*
fi
