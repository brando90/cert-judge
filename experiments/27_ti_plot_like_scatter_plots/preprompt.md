# Create a figure code that I can reuse just like it exists to plot scatter plots in matplot lib but for my TT_2'

self ref: `/Users/brandomiranda/cert-judge/experiments/27_ti_plot_like_scatter_plots/preprompt.md`

See `/Users/brandomiranda/cert-judge/experiments/27_ti_plot_like_scatter_plots/cert_judge_notes` that contains all my growing notes and agent prompt for this task.

The high level idea is with whatever we have here -- I'd like to run our currrent cert-judge stuff (or a subset of it, since it's just a test we don't need all the ai judges), to test the TI_2' (Trust Index 2') 
plot that we are creating. Similar to how "to see correlations we plot a scatter plot and report the corr in the legend" -- I want to do 
what I suggested in the notes, plot a single figure that isn't too crowaded with the scatter plot + the histogram or KE (eg lightly coloured, ideally in one plot)
and a legend with the TI eg legend{TI_2'= (corr * std)^ 0.5} so the legend for the concrete experiment would be Legend(TI2' = (0.9 * (1-0.1) )^0.5).
Actually I'm realizing we don't even need to rerun judgements -- we already had data from the paper version we are submitting to ICLR or the previous workshops that got accepted.

Go!

---
## small udpate: uutils or certjudge implemenation of TI scatter plot (we need a name for this lol current name TI scatter plot? but it's really corr of proxy to target + stability of proxy)

PS: trying to decide where the code should go. uutils or certjudge? I was thinking the plot stuff could go in uutils (then we can push to pypi etc) and the certjudge specific stuff could go in certjudge.
The TI_2' is a general thing that can be used for anything really (a replacement to correlations really in general), but the specific ai judge cert judge data eg Corr(S^, S^*) so that general corr and stf code
can go in uutils, it's not specific to cert-judge. Makes sense how I'm thinking about it? 