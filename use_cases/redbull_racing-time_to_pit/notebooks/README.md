# RedBull-Racining-TimeToPit


### Experiment with Machine Learning and Win a Race Simulation with Red Bull Racing
<font color="gray">
<p style="margin-left:3%; margin-right:10%;font-size:16px;">
 
Explore data, deploy a predictive machine learning model … and win a simulated Red Bull Race against your peers.
 
You’re the race strategist at Red Bull Racing. Your mission? The night before the race, you’ll have to use machine learning to predict which factors contribute to determining the fastest race.
 
But there are multiple factors that go into predicting the fastest race, including different tire compounds, qualifying performance, historical data on which laps are chosen for pit stops, and expected weather conditions.
 
What are the variables that make all the difference?
 
In this two-hour workshop, you’ll have the opportunity to experiment with predictive models and choose which variables you think will determine a winning race. You’ll also learn about the steps of creating a machine learning model and become familiar with the entire process, and discover how to tie data science results back to the business.
 
Then … you get to try your own simulated race. We’ll run a simulation to see who has the best time, and who will win the best race of all time—the one you helped design.

<p style="font-size:20px;">
<font color="red">
Proposed solution:
<font color="gray">
<p style="font-size:14px;">
    
* regression:  available data up until the race are used for regressing StintLen when stintNumber==1
* classification: available data up until the race and normalzied stintLen from past events are used. In this case we bucketized StintLen (5 buckets) and label of buckets are served as class label

