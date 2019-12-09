# Thai News Corpora

## Motivation 

- There is no standard method to compare corpora.
- In other words, we still have room for trying new methods.
- How to combine existing methods and new methods?
- What characteristics do each method show?

## Data

||article|token|vocaburary|token/article|token/vocab|
|:-:|:-:|:-:|:-:|:-:|:-:|
|Thairath|842,351| 422,109,688 | 803,014 | 501.1 | 525.6 |
|Dailynews|369,783|131,192,911|295,579||443.85|
|Matichon|42,641|16,818,774|109,103||154.16|
|Sanook|17,931|6,874,537|60,782||113.10|
|NHK Thai|630|||||

## Methods

1. word frequency
    
    >1.1 Zipf's Law

    >1.2 Mann–Whitney U-test

    >1.3 χ<sup>2</sup> score

2. vectorization
    > word frequency vector (20 - 20000 dimension)
    
    > doc2vec

    > corpus2vec

    > word2vec

3. Entropy

## Results

3. Entropy

||stop, punct|stop, ~~punct~~|~~stop~~, punct|~~stop~~, ~~punct~~|
|:-:|:-:|:-:|:-:|:-:|
|Thairath|11.50|11.45|12.44|12.58|
|Dailynews|11.39|11.29|12.55|12.54|
|Matichon|11.34|11.24|12.49|12.48|
|Sanook|11.00|10.92|12.17|12.16|
|NHK Thai|||||


