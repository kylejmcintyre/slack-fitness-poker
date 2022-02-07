# slack-fitness-poker

A Slack app/bot for playing Texas Hold 'Em where the currency is various workout tasks e.g. pushups. 
The intent is to make the workday more fun & active for remote teams. 

The app is ready to run on Heroku (Python+Postgres). However, it was coded with a minimalist mindset
and should be easy to run outside of Heroku. 

![Poker app](http://slack-fitness-poker.herokuapp.com/static/readme.png)

The game always consists of 4 players. One player initiates via `/game` and the first three people
in the channel to react to the invitation message join the game. Order of play is random
