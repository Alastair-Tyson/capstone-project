# capstone-project

Cricket is a sport of winners and losers, but how can you quantify how well a team is doing with respect to their chances of winning? In football you improve your chances of winning by scoring a goal and in tennis by winning points. But in cricket it is a but more challenging as the two teams do not accumulate runs at the same time. On top of this, scoring runs doesn't necessarily mean you ahve improved your chances of winning. Scoring 3 runs in an over, when the required rate is 7 per over will actually decrease the team's chances of winning. And how do you account for wickets lost? The more batsmen you have left will have an impact on your winning chances also.

In this project I aimed to produce a method that will give insight into how much a batting team has improved their chances of winning by reviewing their performance in a given over. I intended to predict the end of innings score using a regression model and then find the likelihood of it being a winning score using a classification model. Finally, I would display these results in an online app. My sole focus would be Twenty over cricket.

Data Collection and EDA:

I used ESPN cricinfo as my data source and built a web scraper using BeautifulSoup and Selenium to collect the data. I wanted the score at the end of each over as well an info about where and when the game was played. As cricinfo provides ball by ball text commentary it was the ideal data source. 

Cricinfo has a page for each Twenty20 match, detailing the score at the end of each over. When opened, the page only displays the last 4 overs but the rest are shown as you scroll down, hence the need for the Selenium driver. However, every 8 overs the page refuses to scroll down unless you scroll up first (a security measure to block bots?). To overcome this I built a for loop into the driver that checked if it had reached over one, if not it was to scroll up a small amount before trying to scroll down again.

As I was interested in predicting the outcome of games I only wanted to use matches were the full compliment of overs were available to both teams. In other words, no rain affected matches. In all I was able to use over 4100 matches in my investigation, covering 19 countries and over 200 stadiums.

A major consideration for my project was that the method I produced had to be as simple as possible- both in terms of useability and interpretation. As such I wanted to have as few features as possible in each model. 

In terms of features I used the score and wickets lost at the end of each over, as well as what time of day the game was played and where it was held. As previously mentioned I had 19 countries and 203 different stadia which I wanted to incorporate. However, to use these I would have to use dummy variables which would have gone against my desire for as few features as possible. Instead, I considered the average run rate per country and stadium. 

Run rate is the total runs divided by the total overs, and can be calculated for each stadium and country. By using these I was able to create a feature that would not only help train the model how many runs to expect each match, but also be unique to each stadium/country creating an alternative to dummy variables. To avoid data leakage I calculated the run rate for each country and stadium accurate to the date it was played (I couldn't use match data from 2018 to predict scores in 2015). I also performed this process seperately for the 1st and 2nd innings, as will be explained in the next paragraph.

A Twenty20 cricket match has two innings: 1st a team will bat setting a total, not knowing if it is enough to win the match. The 2nd team will then try and beat this total and as they know what a winning score is will bat accordingly. As such a team will bat differently dpeending on whether they bat first or second. Further, a 1st innings will usually only end early if the batting team loses all their wickets. A 2nd innings may close early because the batting team has scored enough runs to win- another reason to model the 1st and 2nd innings seperately. 

A benfit of keeping the innings seperate is that it reduced the need for interaction features between innings and score. I extended this further by choosing to build a model for each over of an innings, as again it would remove the need for interaction features. This meant overall that I would have 42 regression models and 42 classification models- one for the end of each over plus two for the start of each innings. 

Regression:

The first part of my method was to predict the score at the end of a batting team's innings. This should be possible from any point of a game, including the start. As said previously, I wanted to make a model for each over of each innings to reduce the amount of features I would need to use. The trade off would be that overs earlier in an innings would be less accurate than those later. For consistency, each model of an innings would use the same technique and features.

I investigated several different regression techniques, but found Linear Regression in the 1st innings to be the most appropriate. Over to over it performed just as well as regularisation and ensemble methods, both in terms of r squared and minimising error. This was pleasing to me as a simple model would allow for simple interpretation of the coefficients. 

The second innings models were different on two counts. Firstly, there was an additional feature called 'target' which was the score the 1st innings team achieved. Secondly, I found that the GradientBoost ensemble method was the most effective for predicting end of innings score, particularly during the later overs. This was the only time I sacrificed simplicity for a more accurate model.

For both innings the models improved accuracy the closer you got to the end. This was to be expected. With these regression models built, I then started the process of classification.

Classification:

For each predicted score I wanted to know what the likelihood was of it being a winning score. To do this I would build a classification model (with match outcome as a target) for each over (similar to the regression stage) and use predict_proba to return the likelihood of it being predicted a win. 

For features, I used the same time and geographic features as before but instead of using runs/wickets at the end of each over I used the predicted score from the regression model. The 2nd innings models again used the 1st innings total as a predictor. 

In both 1st and 2nd innings the basic Logistic Regression technique proved to be the most appropriate. Again it performed just as well as more robust ensemble methods and was much simpler for interpretation.  Again, the accuracy scores (precision and recall also) improved the closer you got to the end of the game.

Interpretation of method:

This method was not about producing the likelihood of a team winning a cricket match, but identifying if a batting team's most recent over had improved their chances of winning. In terms of use, you need to compare the likelihood of being predicted a win from over to over. If there is an increase you can be sure the batting team has improved their chances of winning. 

Application:

To display these results I built an interactive application using dash and deployed to AWS Elastic Beanstalk. The app has two functions, first it displays how my method would have fared during any of the 4100 games I used in the study. Second, it allows you to enter current match information and receive the predicted score and likelihood of winning. To be of most use, it is important to copare the change in likelihood over to over.

App can be found here: http://tysondashboard-dev.eu-west-2.elasticbeanstalk.com/
