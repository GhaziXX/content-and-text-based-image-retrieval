from utils.initializers import *
from pydantic import BaseModel
from typing import Dict, Optional
import numpy as np


class ElasticSearch(BaseModel):
    
    def search_by_text_query(self, 
                             query: str, 
                             fields: Optional[Dict[str,int]] = {"labels":5, "tags":1, "title":2}, 
                             use_fuzzy: Optional[bool] = False,
                             size: Optional[int] = 5, 
                             from_: Optional[int] = 0
                             ):
        
        fields_with_boost = [f"{i[0]}^{i[1]}" for i in fields.items()]
        q = {
            "multi_match": {
            "query": query,
            "fields": fields_with_boost,
            "fuzziness": "AUTO"
            }
        } if use_fuzzy else {
            "multi_match": {
            "query": query,
            "fields": fields_with_boost
            }
        }

        return es.search(index=INDEX_NAME, query=q, size=size, _source=SOURCE_NO_VEC, from_ = from_)
    
    def search_by_image_query(self, 
                              image_id: Optional[str] = None, 
                              image_link: Optional[str] = None, 
                              image: np.array = None,
                              size: Optional[int] = 5, 
                              from_: Optional[int] = 0,
                              condidates: Optional[int] = 100
                              ):
        if not image_id and not image_link and image.size == 0:
            return {"Response":404, "Error":"Please make sure that you entered at least an image link or image id or uploaded an image"}
        
        if (image_id and image_link) or (image_id and image.size != 0) or (image.size != 0 and image_link) or (image.size != 0 and image_id and image_link):
            return {"Response":404, "Error":"Please make sure that you entered ONLY one of the following: image link, image id, image"}

        if image_id:
            image_link = None
            image = None
            query = {
                "elastiknn_nearest_neighbors": {
                "vec": {
                    "index": INDEX_NAME,
                    "field": "featureVec",
                    "id": image_id
                },
                "field": "featureVec",
                "model": "lsh",
                "similarity": "l2",
                "candidates": condidates
                }
            }
        
        elif image_link:
            image_id = None
            image = None
            features = fe.get_from_link(image_link)
            query = {
                "elastiknn_nearest_neighbors": {
                "vec": {
                    "values": features
                },
                "field": "featureVec",
                "model": "lsh",
                "similarity": "l2",
                "candidates": condidates
                }
            }
            
        elif image.size != 0:
            image_id = None
            image_link = None
            features = fe.get_from_image(image)
            query = {
                "elastiknn_nearest_neighbors": {
                "vec": {
                    "values": features
                },
                "field": "featureVec",
                "model": "lsh",
                "similarity": "l2",
                "candidates": condidates
                }
            }
        
        return es.search(index=INDEX_NAME, query=query, size=size, _source=SOURCE_NO_VEC, from_=from_)
    
    def search_by_text_image_query(self, 
                                   query: str, 
                                   fields: Optional[Dict[str,int]] = {"labels":5, "tags":1, "title":2}, 
                                   use_fuzzy: Optional[bool] = False,
                                   image_id: Optional[str] = None, 
                                   image_link: Optional[str] = None, 
                                   image: np.array = None,
                                   condidates: Optional[int] = 100,
                                   size: Optional[int] = 5, 
                                   from_: Optional[int] = 0):
        
        if not image_id and not image_link and image.size == 0:
            return {"Response":404, "Error":"Please make sure that you entered at least an image link or image id or uploaded an image"}
        
        if (image_id and image_link) or (image_id and image.size != 0) or (image.size != 0 and image_link) or (image.size != 0 and image_id and image_link):
            return {"Response":404, "Error":"Please make sure that you entered ONLY one of the following: image link, image id, image"}
        
        fields_with_boost = [f"{i[0]}^{i[1]}" for i in fields.items()]
        mm = {
            "query": query,
            "fields": fields_with_boost,
            "fuzziness": "AUTO"
            } if use_fuzzy else {
            "query": query,
            "fields": fields_with_boost
            }

        if image_id:
            fetch_res = es.get(index=INDEX_NAME, id=image_id)
            features = fetch_res['_source']['featureVec']['values']
        
            query = {
                "function_score": {
                "query": {
                    "bool": {
                    "filter": {
                        "exists": {
                        "field": "featureVec"
                        }
                    },
                    "must": {
                        "multi_match": mm
                    }
                },
                "boost_mode": "replace",
                "functions": [{
                    "elastiknn_nearest_neighbors": {
                    "field": "featureVec",
                    "similarity": "l2",
                    "model": "lsh",
                    "candidates": condidates,
                    "vec": {
                        "values": features
                    }
                    },
                    "weight": 2
                }]
                }
                }
            }
        elif image.size != 0:
            features = fe.get_from_image(image)
            query = {
                "function_score": {
                "query": {
                    "bool": {
                    "filter": {
                        "exists": {
                        "field": "featureVec"
                        }
                    },
                    "must": {
                        "multi_match": mm
                    }
                    }
                },
                "boost_mode": "replace",
                "functions": [{
                    "elastiknn_nearest_neighbors": {
                    "field": "featureVec",
                    "similarity": "l2",
                    "model": "lsh",
                    "candidates": condidates,
                    "vec": {
                        "values": features
                    }
                    },
                    "weight": 2
                }]
                }
            }
        elif image_link:
            features = fe.get_from_link(image_link)
            query = {
                "function_score": {
                "query": {
                    "bool": {
                    "filter": {
                        "exists": {
                        "field": "featureVec"
                        }
                    },
                    "must": {
                        "multi_match": mm
                    }
                    }
                },
                "boost_mode": "replace",
                "functions": [{
                    "elastiknn_nearest_neighbors": {
                    "field": "featureVec",
                    "similarity": "l2",
                    "model": "lsh",
                    "candidates": condidates,
                    "vec": {
                        "values": features
                        }
                    },
                    "weight": 2
                }]
                }
            }

        return es.search(index=INDEX_NAME, query=query, size=size, _source=SOURCE_NO_VEC, from_=from_)
    