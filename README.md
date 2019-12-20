# Thai News Corpora

# Motivation 

- There is no standard method to compare corpora.
- In other words, we still have room for trying new methods.
- How to combine existing methods and new methods?
- What characteristics do each method show?

# Data

||article|token|vocaburary|token/article|token/vocab|
|:-:|:-:|:-:|:-:|:-:|:-:|
|Thairath|842,351| 422,109,688 | 803,014 | 501.1 | 525.6 |
|Dailynews| 369,783 | 131,192,911 | 295,579 | 448.2| 443.85 |
|Matichon|76,432| 30,262,305 | 147,374 | 205.3 | 154.16 |
|Sanook|17,931|6,874,537|60,782|383.4|113.10|
|NHK Thai|780|||||

# Methods

1. Word/Document Frequency
    
    >[1.1 top 50 words](#11-top-50-words)
    
    >[1.2 bigram](#12-bigram)

    >[1.3 Zipf's Law](#13-zipfs-law)
    
    >[1.4 Relationship between vacabulary and text length](#14-relationship-between-vacabulary-and-text-length)

    >1.5 Mann–Whitney U-test

    >[1.6 χ<sup>2</sup> score](#16-χ<sup>2</sup>-score)

    >1.7 tf-idf

    tf-idf weighting has many variations. -> [Stanford NLP](https://nlp.stanford.edu/IR-book/html/htmledition/document-and-query-weighting-schemes-1.html)

2. Vectorization
    >[2.1 Cosine Similarity of Word Frequency Vector (20 - 20000 dimension)](#21-cosine-similarity-of-word-frequency-vector)
    
    > 2.2 doc2vec

    > 2.3 corpus2vec

    > 2.4 word2vec

3. Entropy

# Results

## 1. Word/Document Frequency
    
### 1.1 Top 50 words

word frequency with stopwords

|||
|:-:|:-|
|Thairath|ที่ และ ใน มี ไม่ ได้ ของ ว่า จะ เป็น การ ให้ ไป ก็ มา กับ จาก แต่ คน นาย โดย นี้ ต้อง แล้ว ไทย อยู่ ปี เพื่อ ยัง ซึ่ง เมื่อ อย่าง กัน ด้วย หรือ เพราะ น. วันที่ เรา ทีม เรื่อง ๆ ทำ ใช้ ถึง ประเทศ ส่วน อีก จึง กว่า|
|Daily News|ที่ และ ใน มี ได้ ของ การ ไม่ ว่า จะ เป็น ให้ ไป ก็ มา จาก กับ โดย ซึ่ง แต่ นาย ต้อง นี้ เพื่อ คน เมื่อ ปี แล้ว อยู่ ไทย ยัง อย่าง หรือ ด้วย วันที่ เพราะ กัน เรื่อง ใช้ ประเทศ จึง ๆ ทำ ส่วน ทำให้ ถึง เรา ทาง อีก คือ|
|Matichon|ที่ และ ใน มี การ ได้ ของ ว่า เป็น ไม่ จะ ให้ ไป จาก มา ก็ โดย กับ ซึ่ง นาย เพื่อ คน ต้อง แต่ ปี เมื่อ หรือ นี้ อยู่ แล้ว ยัง วันที่ ไทย อย่าง ด้วย จึง เรื่อง ใช้ คือ ทำ ทาง ทั้ง เพราะ ประเทศ พื้นที่ สามารถ กัน เรา ถึง กว่า|
|Sanook|และ ได้ ไม่ ว่า มี ใน ของ เป็น ไป ก็ จะ ให้ มา การ กับ คน แล้ว แต่ อยู่ จาก เรา โดย ซึ่ง นาย นี้ ยัง เขา ปี กัน ต้อง จึง ๆ เพื่อ เพราะ เมื่อ พบ อย่าง ด้วย ถูก เลย หรือ กว่า ดังกล่าว ทาง บ้าน ตน คือ เรื่อง อีก ทำให้|
|NHK Thai|ที่ ของ ใน และ ได้ ว่า การ ญี่ปุ่น จะ มี นาย เป็น นี้ วัน สหรัฐ ให้ เมื่อ กับ จาก ซึ่ง โดย ไม่ เพื่อ ระบุ ปี คน ขึ้น ยัง จีน ต่อ กล่าวว่า เขา ไป แห่ง อย่าง ตุลาคม ด้าน ทาง เกาหลีใต้ ถูก ที่จะ หรือ พฤศจิกายน อยู่ รัฐบาล ประธานาธิบดี เดือน ใช้ กล่าว ดังกล่าว|

word frequency without stopwords

|||
|:-:|:-|
|Thairath|คน ไทย ปี น. วันที่ ทีม เรื่อง ทำ ประเทศ บาท อ. ดี ์ จ. เวลา บ้าน ล้าน พื้นที่ ผม ประชาชน ที่จะ เมือง รัฐบาล ตัว สำหรับ รถ พระ เจ้าหน้าที่ งาน สร้าง ที่ผ่านมา เดือน ส อายุ ดู รายงาน จังหวัด ตำรวจ จำนวน พรรค ออกมา บริเวณ กล่าวว่า เล่น ชาติ ตรวจสอบ น้ำ เข้ามา เกม บริษัท|
|Daily News|คน ปี ไทย วันที่ เรื่อง ประเทศ ทำ บาท ดี พื้นที่ ประชาชน เวลา ์ ที่จะ ล้าน ทีม จ. อ. ผม รัฐบาล น. สำหรับ ที่ผ่านมา เมือง เจ้าหน้าที่ บ้าน สร้าง ตัว งาน กล่าวว่า พระ รายงาน รถ เดือน จำนวน อายุ ตรวจสอบ โครงการ ต่อไป จังหวัด เข้ามา บริเวณ ส เดินทาง ดู ออกมา เงิน ถนน น้ำ บริษัท|
|Matichon|คน ปี วันที่ ไทย เรื่อง ทำ ประเทศ พื้นที่ อ. ประชาชน บาท จ. เวลา จังหวัด ที่จะ เจ้าหน้าที่ ดี บ้าน กล่าวว่า สร้าง สำหรับ ทีม จำนวน เมือง น. ล้าน งาน น้ำ ์ ตรวจสอบ โครงการ ท่าน ที่ผ่านมา ตัว บริเวณ อายุ พระ ผม บริษัท เดือน เดินทาง เงิน รายงาน รถ พล ต่อไป รัฐบาล เข้ามา ชัย ระบบ|
|Sanook|ปี บ้าน เรื่อง ผม ทำ เจ้าหน้าที่ อายุ รถ จ. ตัว แม่ อ. น้อง วันที่ ภาพ ตรวจสอบ เวลา เมือง ไทย บริเวณ ออกมา ทราบ ดี โพสต์ พื้นที่ ลูก แจ้ง บาท ที่ผ่านมา เข้ามา ดู เสียชีวิต พี่ ตำรวจ บอ จังหวัด เดินทาง สำหรับ ์ รายงาน พรรค สภ. งาน สาว ประเทศ เจ้าหน้าที่ตำรวจ ที่จะ ประชาชน เงิน เด็ก|
|NHK Thai|ญี่ปุ่น สหรัฐ ระบุ ปี คน จีน กล่าวว่า ตุลาคม เกาหลีใต้ ที่จะ พฤศจิกายน รัฐบาล ประธานาธิบดี เดือน ชิ เจ้าหน้าที่ ประเทศ เกาหลีเหนือ ต่าง ๆ จังหวัด เรื่อง นา พระ ข้อตกลง ฮ่องกง เมือง ผู้นำ เรียกร้อง รัฐมนตรี กรุง โตเกียว ทรัมป์ สำหรับ รายงาน บริษัท สมเด็จ ล้าน โลก อาเบะ ฮา ราว พื้นที่ การประชุม ส บรรดา ข้อมูล ธันวาคม ชาติ นิวเคลียร์ วันที่|

document frequency with stopwords

|||
|:-:|:-|
|Thairath|ที่ ใน และ มี ได้ ของ ว่า เป็น ให้ จะ ไม่ ไป การ กับ มา จาก โดย เมื่อ นี้ แต่ ซึ่ง แล้ว วันที่ ยัง อยู่ เพื่อ ก็ อย่าง ด้วย คน ต้อง ปี ถึง หรือ กัน อีก เพราะ ส่วน นาย ทั้ง กว่า ทำให้ ไทย ทำ จึง ใช้ ขึ้น ทาง ๆ ก่อน|
|Daily News|ที่ และ ใน มี ว่า ได้ ของ เป็น การ ให้ จะ ไม่ จาก ไป โดย เมื่อ กับ มา ซึ่ง เพื่อ นี้ แต่ วันที่ ยัง อยู่ แล้ว อย่าง ก็ ปี ด้วย ต้อง คน นาย หรือ ส่วน ถึง จึง อีก เพราะ ทั้ง กัน ทำให้ ใช้ ประเทศ ทาง ไทย เรื่อง กว่า นำ ทำ|
|Matichon|ที่ และ ใน มี ได้ ว่า ของ เป็น การ ให้ จะ โดย เมื่อ จาก ไม่ ไป วันที่ กับ มา ซึ่ง เพื่อ นี้ ยัง แล้ว แต่ อยู่ นาย ปี ด้วย คน หรือ อย่าง ต้อง ก็ จึง ทั้ง ถึง ทาง อีก ส่วน กว่า นำ ใช้ สามารถ ทำให้ เวลา ทำ ตาม ไทย เพราะ|
|Sanook|ที่ และ ว่า มี ได้ ใน เป็น ของ ไม่ ไป ให้ จะ มา การ กับ จาก โดย ซึ่ง แล้ว แต่ คน อยู่ ก็ ยัง เมื่อ นี้ ปี เพื่อ ด้วย อย่าง จึง กัน ต้อง เพราะ ดังกล่าว ถูก พบ นาย กว่า อีก ถึง หรือ ก่อน ทำให้ ทาง นำ ๆ หลัง หนึ่ง อายุ|
|NHK Thai|ที่ ใน ของ และ ได้ ว่า การ มี วัน จะ เป็น นี้ เมื่อ โดย ให้ ซึ่ง ญี่ปุ่น กับ จาก เพื่อ ไม่ ระบุ ยัง นาย ต่อ ไป ปี อย่าง ขึ้น กล่าวว่า แห่ง ตุลาคม หรือ ทาง ด้าน ที่จะ คน อยู่ พฤศจิกายน สหรัฐ เดือน ถูก รัฐบาล กล่าว หนึ่ง กำลัง มา ดังกล่าว เขา ต่าง ๆ|

document frequency without stopwords

|||
|:-:|:-|
|Thairath|วันที่ คน ปี ไทย ทำ เรื่อง เวลา ดี ประเทศ สำหรับ น. ที่จะ ที่ผ่านมา ์ รายงาน ตัว เมือง บาท อ. บ้าน ต่อไป จ. ออกมา สร้าง ดู ทีม พื้นที่ กล่าวว่า เดือน เข้ามา ประชาชน จำนวน ล้าน งาน เจ้าหน้าที่|
|Daily News|วันที่ ปี คน ประเทศ ไทย เรื่อง ทำ ที่ผ่านมา เวลา สำหรับ ที่จะ ดี รายงาน ต่อไป กล่าวว่า ์ บาท น. ประชาชน อ. เมือง ตัว พื้นที่ จ. สร้าง เจ้าหน้าที่ เดือน จำนวน เข้ามา บ้าน ออกมา ล้าน ดู เดินทาง งาน ตรวจสอบ อย่างไรก็ตาม รัฐบาล|
|Matichon|วันที่ ปี คน เวลา ทำ ไทย เรื่อง กล่าวว่า อ. สำหรับ ประเทศ ที่จะ พื้นที่ ที่ผ่านมา น. จ. ดี ประชาชน ต่อไป จำนวน รายงาน เจ้าหน้าที่ สร้าง บาท เมือง จังหวัด ตัว บ้าน เดินทาง เข้ามา ์ บริเวณ ตรวจสอบ อายุ งาน เดือน แจ้ง รอง|
|Sanook|คน ปี อายุ ทำ วันที่ เวลา ตัว ที่ผ่านมา เรื่อง จ. เจ้าหน้าที่ อ. ทราบ บ้าน ออกมา ตรวจสอบ บริเวณ ต่อไป แจ้ง รายงาน สำหรับ เข้ามา ดี เมือง ภาพ ดู เดินทาง พื้นที่ น. ที่จะ โพสต์ ระบุ บอ รถ จังหวัด เกิดขึ้น สภ. ต. หน้า สาว แม่ เข้าไป เจ้าหน้าที่ตำรวจ|
|NHK Thai|ญี่ปุ่น ระบุ ปี กล่าวว่า ตุลาคม ที่จะ คน พฤศจิกายน สหรัฐ เดือน รัฐบาล ต่าง ๆ เจ้าหน้าที่ ประเทศ เรื่อง เรียกร้อง ชิ กรุง สำหรับ จีน ประธานาธิบดี บรรดา รายงาน โตเกียว จังหวัด ราว ธันวาคม วันที่ อังคาร เมือง ผู้นำ นา ศุกร์ ส พฤหัสบดี ฮา กันยายน พุธ วันอาทิตย์ โลก พื้นที่ จันทร์ รัฐมนตรี คาด ประกาศ ผู้คน ข้อตกลง ข้อมูล ทางการ บริษัท|

NHK Thai: word frequency without stopwords
![wordcloud](https://user-images.githubusercontent.com/44984892/70881665-d510f000-1fff-11ea-8c99-2320b19a85fa.png)

### 1.2 bigram
**Thairath**

|||bigram count|
|:-:|:-:|-:|
| ล้าน | บาท | 279255 |
| ประเทศ | ไทย | 251553 |
| ทีม | ชาติ | 158305 |
| น. | วันที่ | 106391 |
| สำนัก | ข่าวต่างประเทศ | 84361 |
| อ. | เมือง | 83851 |
| ข่าวต่างประเทศ | รายงาน | 82266 |
| ผู้สื่อข่าว | รายงาน | 74790 |
| อ. | ประยุทธ์ | 71867 |
| ชาติ | ไทย | 69908 |

**Daily News**

|||bigram count|
|:-:|:-:|-:|
| ล้าน | บาท | 95139 |
| ประเทศ | ไทย | 85176 |
| ผู้สื่อข่าว | รายงาน | 33726 |
| น. | วันที่ | 27348 |
| สำนัก | ข่าวต่างประเทศ | 27131 |
| ทีม | ชาติ | 26970 |
| ข่าวต่างประเทศ | รายงาน | 26879 |
| อ. | เมือง | 22671 |
| ผบ | ก. | 20013 |
| อ. | ประยุทธ์ | 18580 |

**Matichon**

|||bigram count|
|:-:|:-:|-:|
| ล้าน | บาท | 18277 |
| ประเทศ | ไทย | 17065 |
| น. | วันที่ | 12034 |
| ผู้สื่อข่าว | รายงาน | 10596 |
| อ. | ประยุทธ์ | 8757 |
| อ. | เมือง | 8240 |
| รัฐมนตรี | ว่าการ | 7500 |
| จันทร์ | โอชา | 5683 |
| ทีม | ชาติ | 5613 |
| ประยุทธ์ | จันทร์ | 5561 |

**Sanook**

|||bigram count|
|:-:|:-:|-:|
| ผู้สื่อข่าว | รายงาน | 1514 |
| อ. | เมือง | 1374 |
| สภ. | เมือง | 1261 |
| ล้าน | บาท | 1223 |
| ประเทศ | ไทย | 1042 |
| ทราบ | ชื่อ | 1022 |
| สอบสวน | สภ. | 1010 |
| ประชา | รัฐ | 897 |
| พลัง | ประชา | 857 |
| เมือง | จ. | 834 |

**NHK Thai**

|||bigram count|
|:-:|:-:|-:|
| สมเด็จ | พระ | 215 |
| รัฐบาล | ญี่ปุ่น | 131 |
| กรุง | โตเกียว | 127 |
| พระ | จักรพรรดิ | 107 |
| ญี่ปุ่น | ระบุ | 97 |
| โดนัลด์ | ทรัมป์ | 94 |
| ประธานาธิบดี | โดนัลด์ | 82 |
| พระ | สันตะปาปา | 72 |
| ชินโซ | อาเบะ | 70 |
| รัฐมนตรี | ต่างประเทศ | 66 |



### 1.3 Zipf's Law
<a href="https://www.codecogs.com/eqnedit.php?latex=f(w)&space;=&space;\frac{c}{r^k}&space;\\\\&space;f(w)&space;=&space;\frac{c}{(r&plus;\rho)^k}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?f(w)&space;=&space;\frac{c}{r^k}&space;\\\\&space;f(w)&space;=&space;\frac{c}{(r&plus;\rho)^k}" title="f(w) = \frac{c}{r^k} \\\\ f(w) = \frac{c}{(r+\rho)^k}" /></a>

![wordfreq](https://user-images.githubusercontent.com/44984892/70882789-69308680-2003-11ea-8784-84006d04f8b1.png)

### 1.4 Relationship between vacabulary and text length
<a href="https://www.codecogs.com/eqnedit.php?latex=V&space;=&space;L^k" target="_blank"><img src="https://latex.codecogs.com/gif.latex?V&space;=&space;L^k" title="V = L^k" /></a>

![LR_tr](https://user-images.githubusercontent.com/44984892/71268711-26aed700-2380-11ea-997b-a4d57c92838c.png)
![LR_dn](https://user-images.githubusercontent.com/44984892/71268715-2a425e00-2380-11ea-9635-673702a6677f.png)
![LR_mc](https://user-images.githubusercontent.com/44984892/71268720-2ca4b800-2380-11ea-94a3-21b88ea21b32.png)
![LR_sn](https://user-images.githubusercontent.com/44984892/71268723-2f071200-2380-11ea-986e-bd8f3ed3b82b.png)
![LR_nhk](https://user-images.githubusercontent.com/44984892/71268725-32020280-2380-11ea-8d4d-43b8e790e78d.png)

result of linear regression (log10-log10 plot)

||R<sup>2</sup>|coefficient *k*|intercept|
|:-:|-:|-:|-:|
|Thairath|0.959|0.769|2.183|
|Dailynews|0.956|0.778|2.133|
|Matichon|0.961|0.758|2.333|
|Sanook|0.939|0.695|4.954|
|NHK Thai|0.882|0.759|2.152|

### 1.6. χ<sup>2</sup> score
χ<sup>2</sup> score of 7000 dimensions

|| Thairath | Dailynews | Matichon | Sanook |
|:-:|-:|-:|-:|-:|
|Thairath | - | 4.87e+6 | 3.76e+06 |1.57e+06|
|Dailynews  | - | - | 2.51e+06 |1.83e+06|
|Matichon   | - | - | - | 1.37e+06 |
|Sanook     | - | - | - | - |


## 2. Vectorization

### 2.1 Cosine Similarity of Word Frequency Vector
![freq_vec](https://user-images.githubusercontent.com/44984892/70881016-c1fd2080-1ffd-11ea-870f-6ad503d8082d.png)

cosine similarity of frequency vectors of 7000 dimensions

|| Thairath | Dailynews | Matichon | Sanook | NHK Thai |
|:-:|-:|-:|-:|-:|-:|
|Thairath | 1 | 0.982269 | 0.958436 |0.868301  |0.486154|
|Dailynews  | - | 1 | 0.976292  |0.865390  |0.523170|
|Matichon   | - | - | 1 | 0.865427 |0.514641|
|Sanook     | - | - | - | 1 | 0.430216|
|NHK Thai   | - | - | - | - | 1 |

## 3. Entropy

||stop, punct|stop, ~~punct~~|~~stop~~, punct|~~stop~~, ~~punct~~|
|:-:|:-:|:-:|:-:|:-:|
|Thairath|11.50|11.45|12.44|12.58|
|Dailynews|11.34|11.24|12.52|12.52|
|Matichon|11.31|11.21|12.49|12.48|
|Sanook|11.00|10.92|12.17|12.16|
|NHK Thai|9.99|9.89|10.81|10.72|




