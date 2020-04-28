# Language in News
## The Project:
For the final project at Flatiron School topic modeling, sentiment analysis, and clustering was used in order to identify possible differences between news sources.  The idea was to measure how many topics were in each article (a most probable topic was assigned to each sentence using LDA Mallet), how strong was the langauge used in each sentence of those articles (sentiment analysis with VADER sentiment analysis), and then clustering of articles based on topics and sentiment attached to those topics.  News articles on the Hong Kong protests were scraped from the South China Morning Post (SCMP), the Australian Broadcast Corporation (ABC), Reuters, CNN, and CCTV (Chinese state news media).

## The Data:
- Over 3000 initial articles were scraped
- Only the first 10 sentences of each article was used in order to limit the size differences of articles and to focus primarily on the "lede"
- After filtering articles in travel, business, op-ed, and fashion sections 1300+ articles were used as observations

## Initial EDA and Feature Engineering:
- Almost half of the articles were from SCMP and another quarter were from Reuters.  The remainder were from ABC, CNN, and CCTV.
- With LDA Mallet, the optimal number of topics based coherence scores (from the gensim CoherenceModel) was 4 topics without SCMP and 12 with SCMP.  The class imbalance appears to heavily skew optimal topic numbers toward the optimal number of topics for SCMP articles.  This is further compounded by the fact that SCMP is a local HK paper that may include a greater range of language and "topics" when reporting on the HK protests.  As a result, SCMP articles were dropped from the topic modeling portion (a sample of SCMP articles could have been taken as an alternative measure).
- The titles were manually labeled (from 0 to 3) as protests, economic, politics, government.  The following is a word cloud of the top words in each topic.  
![Word Cloud of Topics](images/topics.png)


- Sentiment was measured in sentence in each article and a topic sentiment score was summed for each article such that each article had a sentiment score for each of the 4 topics.
