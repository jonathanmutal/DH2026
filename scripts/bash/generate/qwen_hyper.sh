temperatures=(0.0 0.2 0.4 0.6 0.8 1.0)
top_ps=(0.0 0.2 0.4 0.6 0.8 1.0)
repetition_penalities=(1.0 1.05)

for temp in "${temperatures[@]}"
do
  for top_p in "${top_ps[@]}"
  do
    for r_p in "${repetition_penalities[@]}"
    do
      sbatch ./scripts/slurm/generate/qwen3.sh ${temp} ${top_p} ${r_p}
    done
  done
done
