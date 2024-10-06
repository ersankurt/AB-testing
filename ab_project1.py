
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# !pip install statsmodels
import statsmodels.stats.api as sms
from scipy.stats import ttest_1samp, shapiro, levene, ttest_ind, mannwhitneyu, \
    pearsonr, spearmanr, kendalltau, f_oneway, kruskal
from statsmodels.stats.proportion import proportions_ztest

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 10)
pd.set_option('display.float_format', lambda x: '%.5f' % x)
pd.set_option('display.expand_frame_repr', False)




# İş Problemi


# Facebook bir süre önce mevcut "maximumbidding" adı verilen teklif verme türüne alternatif
# olarak yeni bir teklif türü olan "average bidding"’i tanıttı. Bir firma //////////.com,
# bu yeni özelliği test etmeye karar verdi ve averagebidding'in maximumbidding'den daha fazla dönüşüm
# getirip getirmediğini anlamak için bir A/B testi yapmak istiyor.A/B testi 1 aydır devam ediyor ve
# //////////.com şimdi bizden bu A/B testinin sonuçlarını analiz etmemizi bekliyor.
# ////////.com için nihai başarı ölçütü Purchase'dır. Bu nedenle, istatistiksel testler için Purchase metriğine odaklanacağız.


#####################################################
# Veri Seti Hikayesi
#####################################################

# Bir firmanın web site bilgilerini içeren bu veri setinde kullanıcıların gördükleri ve tıkladıkları
# reklam sayıları gibi bilgilerin yanı sıra buradan gelen kazanç bilgileri yer almaktadır.Kontrol ve Test
# grubu olmak üzere iki ayrı veri seti vardır. Bu veri setleri ab_testing.xlsxexcel’inin ayrı sayfalarında yer
# almaktadır. Kontrol grubuna Maximum Bidding, test grubuna AverageBidding uygulanmıştır.

# ******: Reklam görüntüleme sayısı
# C****: Görüntülenen reklama tıklama sayısı
# Purchase: Tıklanan reklamlar sonrası satın alınan ürün sayısı
# ******: Satın alınan ürünler sonrası elde edilen kazanç


#  Veriyi Hazırlama ve Analiz Etme

#  ab_tes****_****.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz. Kontrol ve test grubu verilerini ayrı değişkenlere atayınız.



dataframe_control = pd.read_excel("-" , sheet_name="Control Group")
dataframe_test = pd.read_excel("-" , sheet_name="Test Group")

df_control = dataframe_control.copy()
df_test = dataframe_test.copy()


# Kontrol ve test grubu verilerini analizi.


def check_df(dataframe, head=5):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### Head #####################")
    print(dataframe.head())
    print("##################### Tail #####################")
    print(dataframe.tail())
    print("##################### NA #####################")
    print(dataframe.isnull().sum())
    print("##################### Quantiles #####################")
    print(dataframe.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)

check_df(df_control)
check_df(df_test)


# Analiz işleminden sonra concat metodu ile kontrol ve test grubu verilerini birleştirdik.

df_control["group"] = "control"
df_test["group"] = "test"

df = pd.concat([df_control,df_test], axis=0,ignore_index=False)
#grupları axis=0 ile alt alta birleştirip indexi devam ettirdik.

df.head()
df.tail()

#  A/B Testinin Hipotezinin Tanımlanması


# H0 : M1 = M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında fark yoktur.)
# H1 : M1!= M2 (                                                             fark vardır.)


# Kontrol ve test grubu için purchase(kazanç) ortalamalarını analizi

df.groupby("group").agg({"Purchase": "mean"})



# Hipotez Testinin Gerçekleştirilmesi

# Hipotez testi yapılmadan önce varsayım kontrolleri
# Bunlar Normallik Varsayımı ve Varyans Homojenliğidir.

# Kontrol ve test grubunun normallik varsayımına uyup uymadığını Purchase değişkeni üzerinden ayrı ayrı test ediniz

# Normallik Varsayımı
# H0: Normal dağılım varsayımı sağlanmaktadır.
# H1: Normal dağılım varsayımı sağlanmamaktadır

test_stat, pvalue = shapiro(df.loc[df["group"] == "control", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value=0.5891
# HO reddedilemez.
# Control grubunun değerleri normal dağılım varsayımını sağlamaktadır.
# Eğer standart normal dağılım sağlanmasaydı nonparametrik test olan mannwhitneyu testine geçmeliydik.

# Varyans Homojenliği :
# H0: Varyanslarhomojendir.
# H1: Varyanslarhomojen Değildir.


test_stat, pvalue = levene(df.loc[df["group"] == "control", "Purchase"],
                           df.loc[df["group"] == "test", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# p-value=0.1083
# HO reddedilemez. Control ve Test grubunun değerleri varyans homejenliği varsayımını sağlamaktadır.
# Varyanslar Homojendir.

# Normallik Varsayımı ve Varyans Homojenliği sonuçları sağladığı için bağımsız iki örneklem t testi (parametrik test) yapılmalıdır.

# H0: M1 = M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında ist. ol.anl.fark yoktur.)
# H1: M1 != M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında ist. ol.anl.fark vardır)
# p<0.05 HO RED , p>0.05 HO REDDEDİLEMEZ

test_stat, pvalue = ttest_ind(df.loc[df["group"] == "control", "Purchase"],
                              df.loc[df["group"] == "test", "Purchase"],
                              equal_var=True)

print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# Test Stat = -0.9416, p-value = 0.3493

#SONUÇ VE YORUM
#varsayımlar sağladığı için parametrik test olan bağımsız iki örneklem testini kullandık eğer
# varsayımlar sağlamasaydı non-parametrik test olan mannwhitneyu testi kullanmalıydık
#Test sonucunda elde edilen p_value > 0.05 olduğundan H0 hipotezi REDDEDİLEMEZ yani kontrol ve test grubu satın alma
# ortalamaları arasında istatistiki olarak anlamlı bir fark yoktur. var gibi gözüken fark tesadüfi olabilir.
# /////////.com a tavsiyem her iki durumda da istatiksel olarak anlamlı fark yoktur.
# diğer değişkenler ve gözlemlerin hedef değişkenler ile etkileşimleri takibe alınması.



