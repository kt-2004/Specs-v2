import pandas as pd
# please store college name, stream name, stream description which must have skills, interested subjects in csv format.
data = pd.read_csv("D:\\Specs v2\\specs-venv\\specsV2\\sub\\static\\fashion_products.csv")
print(data.head())
from surprise import Dataset, Reader, SVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
#Content based code  starts below....
content_df = data[['Product ID', 'Product Name', 'Brand', 
                   'Category', 'Color', 'Size']]
content_df['Content'] = content_df.apply(lambda row: ' '.join(row.dropna().astype(str)), axis=1)

# Use TF-IDF vectorizer to convert content into a matrix of TF-IDF features
tfidf_vectorizer = TfidfVectorizer()
content_matrix = tfidf_vectorizer.fit_transform(content_df['Content'])

content_similarity = linear_kernel(content_matrix, content_matrix)

reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(data[['User ID', 
                                  'Product ID', 
                                  'Rating']], reader)

def get_content_based_recommendations(product_id, top_n):
    index = content_df[content_df['Product ID'] == product_id].index[0]
    similarity_scores = content_similarity[index]
    similar_indices = similarity_scores.argsort()[::-1][1:top_n + 1]
    recommendations = content_df.loc[similar_indices, 'Product ID'].values
    return recommendations
#Collabrative algo. starts below..
algo = SVD()
trainset = data.build_full_trainset()
algo.fit(trainset)

def get_collaborative_filtering_recommendations(user_id, top_n):
    testset = trainset.build_anti_testset()
    testset = filter(lambda x: x[0] == user_id, testset)
    predictions = algo.test(testset)
    predictions.sort(key=lambda x: x.est, reverse=True)
    recommendations = [prediction.iid for prediction in predictions[:top_n]]
    return recommendations
#MAIN CODE STARTS HERE...
def get_hybrid_recommendations(user_id, product_id, top_n):
    content_based_recommendations = get_content_based_recommendations(product_id, top_n)
    collaborative_filtering_recommendations = get_collaborative_filtering_recommendations(user_id, top_n)
    hybrid_recommendations = list(set(content_based_recommendations + collaborative_filtering_recommendations))
    return hybrid_recommendations[:top_n]
#USER THINGS ....
user_id = 6
product_id = 11 # please use skills and interested subjects of respective student when looking for recommendation
top_n = 10 #this is for getting result i.e here user want top 10 products ..
recommendations = get_hybrid_recommendations(user_id, product_id, top_n)
#iterate this for 3 times for most scored,middle ,least..
print(f"Hybrid Recommendations for User {user_id} based on Product {product_id}:")
for i, recommendation in enumerate(recommendations):
    print(f"{i + 1}. Product ID: {recommendation}")
    print(f"{i + 1}. Product ID: {recommendation}")
#recommendation of subjects must in desecending order like most scored,medium and least..
