from elasticsearch import Elasticsearch

from utils.feature_extraction import FeatureExtractor

INDEX_NAME = 'open-images'
SOURCE_NO_VEC = ['imageId', 'title', 'author', 'tags', 'labels', 'imgUrl']
es = Elasticsearch(["http://localhost:9200"])
fe = FeatureExtractor("data/pca.pkl")