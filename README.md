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
|Dailynews| 369,783 | 131,192,911 | 295,579 | 448.2| 443.85 |
|Matichon|76,432| 30,262,305 | 147,374 | 205.3 | 154.16 |
|Sanook|17,931|6,874,537|60,782||113.10|
|NHK Thai|780|||||

## Methods

1. Word/Document Frequency
    
    >1.0 top 50 words

    >1.1 Zipf's Law

    >1.2 Mann–Whitney U-test

    >1.3 χ<sup>2</sup> score

    >1.4 tf-idf

    tf-idf weighting has many variations. -> [Stanford NLP](https://nlp.stanford.edu/IR-book/html/htmledition/document-and-query-weighting-schemes-1.html)

2. Vectorization
    > 3.1 word frequency vector (20 - 20000 dimension)
    
    > 3.2 doc2vec

    > 3.3 corpus2vec

    > 3.4 word2vec

3. Entropy

## Results

1. Word/Document Frequency
    >1.0 top 50 words

    word frequency with stopwords

    |||
    |:-:|:-|
    |Thairath|ที่ และ ใน มี ไม่ ได้ ของ ว่า จะ เป็น การ ให้ ไป ก็ มา กับ จาก แต่ คน นาย โดย นี้ ต้อง แล้ว ไทย อยู่ ปี เพื่อ ยัง ซึ่ง เมื่อ อย่าง กัน ด้วย หรือ เพราะ น. วันที่ เรา ทีม เรื่อง ๆ ทำ ใช้ ถึง ประเทศ ส่วน อีก จึง กว่า|
    |Daily News||
    |Matichon||
    |Sanook||
    |NHK Thai||

    word frequency without stopwords

    |||
    |:-:|:-|
    |Thairath|คน ไทย ปี น. วันที่ ทีม เรื่อง ทำ ประเทศ บาท อ. ดี ์ จ. เวลา บ้าน ล้าน พื้นที่ ผม ประชาชน ที่จะ เมือง รัฐบาล ตัว สำหรับ รถ พระ เจ้าหน้าที่ งาน สร้าง ที่ผ่านมา เดือน ส อายุ ดู รายงาน จังหวัด ตำรวจ จำนวน พรรค ออกมา บริเวณ กล่าวว่า เล่น ชาติ ตรวจสอบ น้ำ เข้ามา เกม บริษัท|
    |Daily News||
    |Matichon||
    |Sanook||
    |NHK Thai||

    document frequency

    |||
    |:-:|:-|
    |Thairath|ที่ ใน และ มี ได้ ของ ว่า เป็น ให้ จะ ไม่ ไป การ กับ มา จาก โดย เมื่อ นี้ แต่ ซึ่ง แล้ว วันที่ ยัง อยู่ เพื่อ ก็ อย่าง ด้วย คน ต้อง ปี ถึง หรือ กัน อีก เพราะ ส่วน นาย ทั้ง กว่า ทำให้ ไทย ทำ จึง ใช้ ขึ้น ทาง ๆ ก่อน|
    |Daily News||
    |Matichon||
    |Sanook||
    |NHK Thai||

2. Vectorization

3. Entropy

||stop, punct|stop, ~~punct~~|~~stop~~, punct|~~stop~~, ~~punct~~|
|:-:|:-:|:-:|:-:|:-:|
|Thairath|11.50|11.45|12.44|12.58|
|Dailynews|11.34|11.24|12.52|12.52|
|Matichon|11.31|11.21|12.49|12.48|
|Sanook|11.00|10.92|12.17|12.16|
|NHK Thai|9.99|9.89|10.81|10.72|


